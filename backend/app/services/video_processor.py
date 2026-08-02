"""
Video processing utilities using FFmpeg.
Handles video info extraction, scene-change detection, and basic transformations.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional


class VideoProcessor:
    """Wrapper around FFmpeg for video analysis and manipulation."""

    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Video not found: {input_path}")

    def get_info(self) -> dict:
        """
        Extract video metadata using ffprobe.
        Returns duration, resolution, codec, fps, bitrate.
        """
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

        # Extract video stream info
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
        min_duration: float = 2.0,
        max_duration: float = 8.0,
        threshold: float = 0.4,
    ) -> list[dict]:
        """
        Detect scene changes using FFmpeg's scene detection filter.
        Returns a list of highlight segments: [{start, end, score}, ...]
        """
        cmd = [
            "ffmpeg",
            "-i", str(self.input_path),
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null",
            "-",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )

        # Parse showinfo output for scene change timestamps
        scene_times = []
        for line in result.stderr.split("\n"):
            if "pts_time:" in line:
                try:
                    time_str = line.split("pts_time:")[1].split()[0]
                    t = float(time_str)
                    scene_times.append(t)
                except (ValueError, IndexError):
                    continue

        if not scene_times:
            # No scene changes detected — use the whole video as one highlight
            info = self.get_info()
            duration = info["duration"]
            return [{
                "start": 0,
                "end": min(duration, max_duration),
                "score": 0.5,
            }]

        # Build highlight segments from scene changes
        highlights = []
        for i, t in enumerate(scene_times):
            end = scene_times[i + 1] if i + 1 < len(scene_times) else t + max_duration
            segment_duration = end - t

            # Skip segments that are too short
            if segment_duration < min_duration:
                continue

            # Cap segment duration
            if segment_duration > max_duration:
                end = t + max_duration

            highlights.append({
                "start": round(t, 2),
                "end": round(end, 2),
                "score": round(0.5 + (0.5 * (i / max(len(scene_times), 1))), 2),
            })

        # Sort by score descending, take top segments
        highlights.sort(key=lambda h: h["score"], reverse=True)
        return highlights[:15]  # Max 15 highlights

    def trim_segment(
        self,
        output_path: str,
        start: float,
        end: float,
        speed: float = 1.0,
    ) -> bool:
        """
        Extract a segment from the video.
        Optionally apply speed change (1.0 = normal, 2.0 = 2x speed).
        """
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
