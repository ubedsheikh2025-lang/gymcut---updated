# Gym Video AI Editor

An AI-powered web app that automatically edits your gym workout videos. Upload raw footage, and the app detects the best moments, stitches them together with music and transitions, and exports a polished reel — no editing skills required.

## Features

- **Drag & Drop Upload** — supports MP4, MOV, AVI
- **AI Highlight Detection** — finds peak action moments using Google Cloud Video Intelligence
- **Auto-Edit** — trims, merges, adds transitions, and syncs to music
- **One-Click Export** — download the final edited video
- **Fallback Mode** — works without AI using scene detection (FFmpeg)

## Tech Stack

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Python FastAPI, FFmpeg, Google Cloud Video Intelligence API
- **Storage:** Local temporary files (can be extended to S3)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- FFmpeg installed on your system
- Google Cloud account (for AI features) — optional for basic mode

### Installation

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```
4. Set environment variables:
   - `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON) — optional
   - `UPLOAD_DIR` (temporary upload directory)

### Running

1. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open http://localhost:3000

## Project Structure

```
gym-video-editor/
├── frontend/           # Next.js frontend
│   ├── src/
│   │   ├── app/        # App router pages
│   │   ├── components/ # Reusable UI components
│   │   └── lib/        # Utilities & API client
│   └── ...
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py     # API routes
│   │   ├── services/   # Video processing & AI
│   │   └── models/     # Pydantic models
│   └── requirements.txt
└── README.md
```

## License

MIT