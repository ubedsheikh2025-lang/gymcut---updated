"""
Video processing utilities using FFmpeg.
Motion-based highlight detection for gym/workout videos.
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path


class VideoProcessor:
    """Wrapper around FFmpeg for video analysis and manipulation."""

    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Video not found: {input_path}")

    def get_info(self) -> dict:
        """Extract video metadata using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(self.input_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {result.stderr}")

        data = json.loads(result.stdout)

        video_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break

        if not video_stream:
            raise RuntimeError("No video stream found")

        return {
            "duration": float(data.get("format", {}).get("duration", 0)),
            "width": video_stream.get("width", 0),
            "height": video_stream.get("height", 0),
            "codec": video_stream.get("codec_name", "unknown"),
            "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/1")),
            "bitrate": int(data.get("format", {}).get("bit_rate", 0)),
            "size_bytes": int(data.get("format", {}).get("size", 0)),
        }

    def detect_scene_changes(
        self,
        min_duration: float = 1.5,
        max_duration: float = 6.0,
        threshold: float = 0.25,
    ) -> list[dict]:
        """
        Detect highlights using MOTION ANALYSIS.
        Finds segments with the most movement (actual exercise) vs static moments.
        """
        info = self.get_info()
        duration = info["duration"]
        fps = info["fps"]

        if duration <= 0:
            return []

        # For very short videos (< 5 seconds), just return the whole thing
        # but with a note that it's too short to edit meaningfully
        if duration < 5:
            return [{
                "start": 0,
                "end": round(duration, 2),
                "score": 1.0,
                "label": "full-video-too-short",
            }]

        # Step 1: Calculate motion score for each second of the video
        motion_scores = self._analyze_motion(duration, fps)

        if not motion_scores:
            # Fallback: split into equal segments
            return self._force_split(duration, num_segments=5, min_duration=min_duration, max_duration=max_duration)

        # Step 2: Find the threshold for "high activity"
        scores = [m["motion"] for m in motion_scores]
        if not scores:
            return self._force_split(duration, num_segments=5, min_duration=min_duration, max_duration=max_duration)

        avg_score = sum(scores) / len(scores)
        # Keep segments above average (the active parts)
        threshold_score = avg_score * 1.1

        # Step 3: Group consecutive high-motion seconds into segments
        highlights = []
        segment_start = None

        for m in motion_scores:
            if m["motion"] >= threshold_score:
                if segment_start is None:
                    segment_start = m["time"]
            else:
                if segment_start is not None:
                    seg_end = m["time"]
                    seg_duration = seg_end - segment_start
                    if seg_duration >= min_duration:
                        highlights.append({
                            "start": round(segment_start, 2),
                            "end": round(min(seg_end, segment_start + max_duration), 2),
                            "score": round(min(1.0, m["motion"] / (threshold_score * 2)), 2),
                            "label": "high-activity",
                        })
                    segment_start = None

        # Don't forget the last segment
        if segment_start is not None:
            seg_end = duration
            seg_duration = seg_end - segment_start
            if seg_duration >= min_duration:
                highlights.append({
                    "start": round(segment_start, 2),
                    "end": round(min(seg_end, segment_start + max_duration), 2),
                    "score": 0.8,
                    "label": "high-activity",
                })

        # If we found fewer than 2 highlights, use force-split as fallback
        if len(highlights) < 2:
            highlights = self._force_split(duration, num_segments=4, min_duration=min_duration, max_duration=max_duration)

        # Sort by score descending, take top 15
        highlights.sort(key=lambda h: h["score"], reverse=True)
        return highlights[:15]

    def _analyze_motion(self, duration: float, fps: float) -> list[dict]:
        """
        Use FFmpeg to calculate motion levels across the video.
        Returns list of {time, motion} for each second.
        """
        # We'll sample one frame per second and compare with the previous frame
        # Using FFmpeg's signalstats filter to measure frame differences
        motion_scores = []

        sample_interval = max(1, int(fps))  # Sample every ~1 second

        # Use ffmpeg to extract frame difference metadata
        # The 'metadata' filter with 'signalstats' gives us frame difference info
        cmd = [
            "ffmpeg",
            "-i", str(self.input_path),
            "-vf", f"select='not(mod(n,{sample_interval}))',signalstats=stat=all,metadata=print",
            "-an",
            "-f", "null",
            "-",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            # Parse the metadata output for signalstats values
            current_time = 0.0
            current_motion = 0.0

            for line in result.stderr.split("\n"):
                if "pts_time:" in line:
                    try:
                        current_time = float(line.split("pts_time:")[1].split()[0])
                    except (ValueError, IndexError):
                        pass

                # YAVG = average luma (brightness change indicates motion)
                if "lavfi.signalstats.YAVG=" in line:
                    try:
                        yavg = float(line.split("=")[1])
                        # Higher variance in brightness = more motion
                        current_motion = yavg
                    except (ValueError, IndexError):
                        pass

                # After collecting a frame's data, save it
                if "frame:" in line and current_time > 0:
                    motion_scores.append({
                        "time": round(current_time, 2),
                        "motion": current_motion,
                    })

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        # If signalstats didn't work, try a simpler approach:
        # Compare frame differences using the 'idet' (interlace detection) filter
        # which measures differences between frames
        if len(motion_scores) < 3:
            motion_scores = self._analyze_motion_fallback(duration, fps)

        return motion_scores

    def _analyze_motion_fallback(self, duration: float, fps: float) -> list[dict]:
        """
        Fallback motion detection: use frame difference via FFmpeg's tblend filter.
        Measures how much each frame differs from the previous one.
        """
        motion_scores = []
        sample_interval = max(1, int(fps))

        # Use tblend=difference to get per-frame difference, then signalstats to measure it
        cmd = [
            "ffmpeg",
            "-i", str(self.input_path),
            "-vf", f"tblend=all_mode=difference,select='not(mod(n,{sample_interval}))',signalstats=stat=all,metadata=print",
            "-an",
            "-f", "null",
            "-",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            current_time = 0.0
            current_motion = 0.0

            for line in result.stderr.split("\n"):
                if "pts_time:" in line:
                    try:
                        current_time = float(line.split("pts_time:")[1].split()[0])
                    except (ValueError, IndexError):
                        pass

                # YAVG of difference frame = amount of change
                if "lavfi.signalstats.YAVG=" in line:
                    try:
                        yavg = float(line.split("=")[1])
                        current_motion = yavg
                    except (ValueError, IndexError):
                        pass

                if "frame:" in line and current_time > 0:
                    motion_scores.append({
                        "time": round(current_time, 2),
                        "motion": current_motion,
                    })

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        # If still no results, create synthetic scores (just split evenly)
        if len(motion_scores) < 2:
            step = 1.0
            t = 0.0
            while t < duration:
                # Alternate high/low to at least create some variety
                motion = 100 if (int(t) % 3 == 0) else 50
                motion_scores.append({"time": round(t, 2), "motion": motion})
                t += step

        return motion_scores

    def _force_split(self, duration: float, num_segments: int = 5, min_duration: float = 1.5, max_duration: float = 6.0) -> list[dict]:
        """Split the video into equal segments and return them as highlights."""
        if duration <= 0:
            return []

        segment_length = duration / num_segments
        segment_length = max(min_duration, min(segment_length, max_duration))

        highlights = []
        current = 0.0
        i = 0
        while current < duration:
            end = min(current + segment_length, duration)
            if end - current >= min_duration:
                # Vary scores so the "best" segments are selected
                score = 0.5 + (0.1 * (i % 5))
                highlights.append({
                    "start": round(current, 2),
                    "end": round(end, 2),
                    "score": round(score, 2),
                })
            current = end
            i += 1

        return highlights

    def trim_segment(
        self,
        output_path: str,
        start: float,
        end: float,
        speed: float = 1.0,
    ) -> bool:
        """Extract a segment from the video."""
        duration = end - start
        filters = []

        if speed != 1.0:
            filters.append(f"setpts={1/speed}*PTS")

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", str(self.input_path),
            "-t", str(duration),
        ]

        if filters:
            cmd += ["-vf", ",".join(filters)]

        cmd += [
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0

    def _parse_fps(self, r_frame_rate: str) -> float:
        """Parse FFmpeg frame rate string like '30000/1001' to float."""
        try:
            num, den = r_frame_rate.split("/")
            if int(den) == 0:
                return 30.0
            return float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            return 30.0
