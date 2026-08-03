"""
AI-powered video analysis using Google Cloud Video Intelligence API.
Only works if Google Cloud credentials are configured.
"""

import os
from pathlib import Path


class AIAnalyzer:
    """
    Analyzes gym videos using Google Cloud Video Intelligence.
    Returns empty list if credentials are not configured.
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
                print("[AI] No Google Cloud credentials found. AI features disabled.")
        except ImportError:
            print("[AI] google-cloud-videointelligence not installed.")
        except Exception as e:
            print(f"[AI] Failed to initialize client: {e}")

    async def detect_highlights(self, video_path: str) -> list[dict]:
        """
        Detect highlight moments in a gym video.
        Returns empty list if AI is not available.
        """
        if self.client:
            return await self._ai_detect(video_path)
        else:
            print("[AI] AI not available — returning empty highlights.")
            return []

    async def _ai_detect(self, video_path: str) -> list[dict]:
        """Use Google Cloud Video Intelligence for person/label detection."""
        from google.cloud import videointelligence_v1 as vi

        with open(video_path, "rb") as f:
            input_content = f.read()

        features = [
            vi.Feature.LABEL_DETECTION,
            vi.Feature.PERSON_DETECTION,
        ]

        operation = self.client.annotate_video(
            request={
                "features": features,
                "input_content": input_content,
            }
        )

        print("[AI] Processing video... (this may take a minute)")
        result = operation.result(timeout=300)

        highlights = []

        for annotation in result.person_detection_annotations:
            for track in annotation.tracks:
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

        exercise_keywords = [
            "exercise", "weightlifting", "running", "fitness",
            "gym", "workout", "training", "sport", "bodybuilding",
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

        highlights = self._deduplicate(highlights)
        highlights.sort(key=lambda h: h["score"], reverse=True)
        return highlights[:15]

    def _deduplicate(self, highlights: list[dict]) -> list[dict]:
        """Merge overlapping highlight segments."""
        if not highlights:
            return []

        highlights.sort(key=lambda h: h["start"])
        merged = []
        current = highlights[0].copy()

        for next_h in highlights[1:]:
            if next_h["start"] <= current["end"]:
                current["end"] = max(current["end"], next_h["end"])
                current["score"] = max(current["score"], next_h["score"])
            else:
                merged.append(current)
                current = next_h.copy()

        merged.append(current)
        return merged
