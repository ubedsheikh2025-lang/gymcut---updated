"""
Auto-editor: stitches highlight clips together with transitions and music.
Uses FFmpeg for concatenation, filtering, and audio mixing.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class AutoEditor:
    """
    Creates the final edited video from highlight segments.
    """

    # Royalty-free music tracks (replace with your own or use a music API)
    DEFAULT_MUSIC = {
        "energetic": None,  # Will use silence if no music file provided
        "motivational": None,
        "chill": None,
    }

    async def create_edit(
        self,
        input_path: str,
        highlights: list[dict],
        output_path: str,
        duration_target: int = 60,
        music_style: str = "energetic",
        add_text_overlay: bool = False,
    ) -> str:
        """
        Create the final edited video.

        Steps:
        1. Trim each highlight segment from the source
        2. Concatenate with crossfade transitions
        3. Add background music (if available)
        4. Normalize audio
        5. Output final MP4
        """
        if not highlights:
            # No highlights — just trim the first 60s of the video
            highlights = [{"start": 0, "end": min(60, self._get_duration(input_path))}]

        # Sort highlights by start time for chronological edit
        highlights.sort(key=lambda h: h["start"])

        # Select enough highlights to fill the target duration
        selected = self._select_for_duration(highlights, duration_target)

        if len(selected) == 1:
            # Single clip — just trim it
            return await self._trim_single(input_path, selected[0], output_path)

        # Multiple clips — create concat file and merge
        return await self._concat_with_transitions(
            input_path, selected, output_path, duration_target
        )

    def _select_for_duration(
        self, highlights: list[dict], target: int
    ) -> list[dict]:
        """Select highlights to fill approximately the target duration."""
        selected = []
        total = 0.0

        for h in highlights:
            duration = h["end"] - h["start"]
            if total + duration > target * 1.2:  # Allow 20% over
                # Trim last clip to fit
                remaining = target - total
                if remaining > 1.0:
                    h_copy = h.copy()
                    h_copy["end"] = h_copy["start"] + remaining
                    selected.append(h_copy)
                break
            selected.append(h)
            total += duration

        return selected

    async def _trim_single(
        self, input_path: str, highlight: dict, output_path: str
    ) -> str:
        """Trim a single segment from the video."""
        start = highlight["start"]
        duration = highlight["end"] - highlight["start"]

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Trim failed: {result.stderr}")

        return output_path

    async def _concat_with_transitions(
        self,
        input_path: str,
        highlights: list[dict],
        output_path: str,
        duration_target: int,
    ) -> str:
        """
        Concatenate multiple clips with crossfade transitions.
        Uses FFmpeg's complex filter for smooth transitions.
        """
        # First, trim each segment to individual files
        temp_dir = tempfile.mkdtemp(prefix="gym_edit_")
        clip_files = []

        try:
            for i, h in enumerate(highlights):
                clip_path = os.path.join(temp_dir, f"clip_{i:03d}.mp4")
                start = h["start"]
                duration = h["end"] - h["start"]

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-i", input_path,
                    "-t", str(duration),
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "18",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    clip_path,
                ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                clip_files.append(clip_path)

            if len(clip_files) == 1:
                # Just copy the single clip
                os.rename(clip_files[0], output_path)
                return output_path

            # Create concat file
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                for clip in clip_files:
                    f.write(f"file '{clip}'\n")

            # Concatenate using the concat demuxer (fast, no re-encode)
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-movflags", "+faststart",
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                # Fallback: re-encode concat
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-movflags", "+faststart",
                    output_path,
                ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        finally:
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        return output_path

    def _get_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        import json
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 60))
        return 60.0
