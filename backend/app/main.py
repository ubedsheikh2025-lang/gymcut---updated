"""
Gym Video AI Editor — Backend API (Memory-Optimized for Render Free Tier)
"""

import os
import uuid
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.video_processor import VideoProcessor
from app.services.auto_editor import AutoEditor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB limit

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Gym Video AI Editor",
    description="AI-powered automatic gym workout video editor",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output files
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------
jobs: dict = {}


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    message: str = ""
    output_url: Optional[str] = None
    highlights: list = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    ffmpeg_available = shutil.which("ffmpeg") is not None
    return {
        "status": "ok",
        "ffmpeg": ffmpeg_available,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_ai: bool = Form(False),
    music_style: str = Form("energetic"),
    duration_target: int = Form(60),
):
    """
    Upload a gym video for processing.
    Returns a job_id immediately, processes in background.
    """
    # Validate file type
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}",
        )

    # Create job immediately so we can report progress
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    input_path = job_dir / f"input{ext}"

    # Initialize job with upload progress
    jobs[job_id] = {
        "job_id": job_id,
        "status": "uploading",
        "progress": 0,
        "message": "Starting upload...",
        "output_url": None,
        "highlights": [],
        "input_path": str(input_path),
        "job_dir": str(job_dir),
        "use_ai": use_ai,
        "music_style": music_style,
        "duration_target": duration_target,
    }

    # Save file in background with progress updates
    background_tasks.add_task(save_and_process, job_id, file, input_path, job_dir)

    return {"job_id": job_id, "status": "uploading"}


async def save_and_process(job_id: str, file: UploadFile, input_path: Path, job_dir: Path):
    """Save uploaded file with progress tracking, then start processing."""
    job = jobs.get(job_id)
    if not job:
        return

    total_size = 0
    try:
        with open(input_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    buffer.close()
                    shutil.rmtree(job_dir, ignore_errors=True)
                    job["status"] = "failed"
                    job["message"] = f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB."
                    return
                buffer.write(chunk)
                # Update progress during upload (0-15%)
                if job.get("file_size"):
                    pct = int((total_size / job["file_size"]) * 15)
                    job["progress"] = min(pct, 15)
                    job["message"] = f"Uploading... {total_size // (1024*1024)}MB"
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        job["status"] = "failed"
        job["message"] = f"Upload failed: {str(e)}"
        return

    job["progress"] = 15
    job["message"] = "Upload complete. Starting analysis..."
    await process_video(job_id)


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "output_url": job.get("output_url"),
        "highlights": job.get("highlights", []),
    }


@app.get("/api/jobs/{job_id}/download")
async def download_video(job_id: str):
    """Download the edited video."""
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Video not ready")

    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"gym-edit-{job_id[:8]}.mp4",
    )


# ---------------------------------------------------------------------------
# Background Processing (Memory-Optimized)
# ---------------------------------------------------------------------------

async def process_video(job_id: str):
    """Main video processing pipeline — uses only FFmpeg, no OpenCV."""
    job = jobs.get(job_id)
    if not job:
        return

    try:
        input_path = job["input_path"]
        job_dir = job["job_dir"]
        output_path = str(OUTPUT_DIR / f"{job_id}.mp4")

        # Step 1: Analyze video using FFmpeg only
        job["status"] = "analyzing"
        job["progress"] = 20
        job["message"] = "Analyzing video for highlights..."

        processor = VideoProcessor(input_path)
        video_info = processor.get_info()

        # Always use FFmpeg scene detection (memory-efficient)
        job["message"] = "Detecting best moments using scene analysis..."
        highlights = processor.detect_scene_changes(
            min_duration=1.5,
            max_duration=6.0,
        )

        job["highlights"] = highlights
        job["progress"] = 50

        # Step 2: Auto-edit
        job["status"] = "editing"
        job["message"] = f"Editing {len(highlights)} highlight clips together..."

        editor = AutoEditor()
        await editor.create_edit(
            input_path=input_path,
            highlights=highlights,
            output_path=output_path,
            duration_target=job["duration_target"],
            music_style=job["music_style"],
        )

        job["progress"] = 80

        # Step 3: Render
        job["status"] = "rendering"
        job["message"] = "Rendering final video..."
        job["progress"] = 95

        # Step 4: Done
        job["status"] = "done"
        job["progress"] = 100
        job["message"] = "Your gym video is ready!"
        job["output_path"] = output_path
        job["output_url"] = f"/api/jobs/{job_id}/download"

        # Cleanup upload temp files (keep output)
        shutil.rmtree(job_dir, ignore_errors=True)

    except Exception as e:
        job["status"] = "failed"
        job["message"] = f"Processing failed: {str(e)}"
        job["progress"] = 0


# ---------------------------------------------------------------------------
# Serve frontend static files (MUST be last)
# ---------------------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend-out")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
