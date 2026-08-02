"""
AI-powered video analysis using Google Cloud Video Intelligence API.
Detects exercise movements, people, and action moments in gym videos.
"""

import os
import json
from pathlib import Path
from typing import Optional


class AIAnalyzer:
    """
    Analyzes gym videos using Google Cloud Video Intelligence.
    Falls back gracefully if credentials are not configured.
    """

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Google Cloud client if credentials are available."""
        try:
            from google.cloud import videointelligence_v1 as vi
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.client = vi.VideoIntelligenceServiceClient()
                print("[AI] Google Cloud Video Intelligence initialized.")
            else:
                print("[AI] No Google Cloud credentials found. Using fallback mode.")
        except ImportError:
            print("[AI] google-cloud-videointelligence not installed. Using fallback mode.")
        except Exception as e:
            print(f"[AI] Failed to initialize client: {e}")

    async def detect_highlights(self, video_path: str) -> list[dict]:
        """
        Detect highlight moments in a gym video.
        Uses AI if available, otherwise falls back to basic motion detection.

        Returns list of {start, end, score, label} dicts.
        """
        if self.client:
            return await self._ai_detect(video_path)
        else:
            return await self._fallback_detect(video_path)

    async def _ai_detect(self, video_path: str) -> list[dict]:
        """
        Use Google Cloud Video Intelligence to:
        1. Detect person/body parts
        2. Detect action moments (high motion)
        3. Label segments (e.g., 'weightlifting', 'running')
        """
        from google.cloud import videointelligence_v1 as vi

        # Read video file
        with open(video_path, "rb") as f:
            input_content = f.read()

        # Configure features
        features = [
            vi.Feature.LABEL_DETECTION,
            vi.Feature.PERSON_DETECTION,
        ]

        # For videos > 1 minute, use async (would need GCS upload)
        # For simplicity, we use sync for videos < 1 min
        operation = self.client.annotate_video(
            request={
                "features": features,
                "input_content": input_content,
            }
        )

        print("[AI] Processing video... (this may take a minute)")
        result = operation.result(timeout=300)

        highlights = []

        # Extract person detection segments (high-confidence person presence = action)
        for annotation in result.person_detection_annotations:
            for track in annotation.tracks:
                # High confidence person detection = likely exercise moment
                confidence = track.confidence
                if confidence > 0.6:
                    start = track.segment.start_time_offset.total_seconds()
                    end = track.segment.end_time_offset.total_seconds()
                    highlights.append({
                        "start": round(start, 2),
                        "end": round(end, 2),
                        "score": round(confidence, 2),
                        "label": "exercise",
                    })

        # Also extract label annotations for exercise-related labels
        exercise_keywords = [
            "exercise", "weightlifting", "running", "fitness",
            "gym", "workout", "training", "sport", "bodybuilding",
            "push-up", "pull-up", "squat", "deadlift", "bench press",
        ]

        for annotation in result.label_annotations:
            entity = annotation.entity.description.lower()
            if any(kw in entity for kw in exercise_keywords):
                for segment in annotation.segments:
                    confidence = segment.confidence
                    if confidence > 0.5:
                        start = segment.segment.start_time_offset.total_seconds()
                        end = segment.segment.end_time_offset.total_seconds()
                        highlights.append({
                            "start": round(start, 2),
                            "end": round(end, 2),
                            "score": round(confidence, 2),
                            "label": entity,
                        })

        # Deduplicate and sort by score
        highlights = self._deduplicate(highlights)
        highlights.sort(key=lambda h: h["score"], reverse=True)

        return highlights[:15]

    async def _fallback_detect(self, video_path: str) -> list[dict]:
        """
        Fallback: use OpenCV to detect motion intensity as a proxy for highlights.
        Segments with high motion = likely exercise moments.
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            # If OpenCV is also not available, return empty
            print("[AI] OpenCV not available. Returning empty highlights.")
            return []

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        # Sample every N frames for motion analysis
        sample_interval = int(fps)  # 1 sample per second
        motion_scores = []

        prev_frame = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (320, 240))

                if prev_frame is not None:
                    # Calculate motion as frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    motion = np.mean(diff)
                    timestamp = frame_idx / fps
                    motion_scores.append({
                        "time": timestamp,
                        "motion": float(motion),
                    })

                prev_frame = gray

            frame_idx += 1

        cap.release()

        if not motion_scores:
            return []

        # Find peaks in motion (top 20% = highlights)
        motions = [m["motion"] for m in motion_scores]
        threshold = sorted(motions, reverse=True)[max(1, int(len(motions) * 0.2))]

        highlights = []
        for m in motion_scores:
            if m["motion"] >= threshold:
                highlights.append({
                    "start": round(max(0, m["time"] - 1.5), 2),
                    "end": round(min(duration, m["time"] + 3.0), 2),
                    "score": round(min(1.0, m["motion"] / (threshold * 2)), 2),
                    "label": "high-motion",
                })

        highlights = self._deduplicate(highlights)
        highlights.sort(key=lambda h: h["score"], reverse=True)

        return highlights[:15]

    def _deduplicate(self, highlights: list[dict]) -> list[dict]:
        """Merge overlapping highlight segments."""
        if not highlights:
            return []

        # Sort by start time
        highlights.sort(key=lambda h: h["start"])

        merged = []
        current = highlights[0].copy()

        for next_h in highlights[1:]:
            if next_h["start"] <= current["end"]:
                # Overlapping — merge
                current["end"] = max(current["end"], next_h["end"])
                current["score"] = max(current["score"], next_h["score"])
                if "label" in next_h and "label" in current:
                    if next_h["label"] != current["label"]:
                        current["label"] = f"{current['label']}+{next_h['label']}"
            else:
                merged.append(current)
                current = next_h.copy()

        merged.append(current)
        return merged
