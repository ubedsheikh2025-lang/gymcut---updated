"""
Production entry point — serves both API and built frontend.
Use this instead of main.py when deploying to Render.
"""

import os
import sys

# Add parent directory to path so 'app' imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.main import app
from fastapi.staticfiles import StaticFiles

# Mount frontend static files (must happen AFTER all API routes are defined)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend-out")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
