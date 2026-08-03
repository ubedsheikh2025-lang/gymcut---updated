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
        "file_size": 0,
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
        # Get file size if possible
        file.file.seek(0, 2)  # seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # seek back to start
        job["file_size"] = file_size if file_size > 0 else None
    except Exception:
        job["file_size"] = None

    try:
        with open(input_path
