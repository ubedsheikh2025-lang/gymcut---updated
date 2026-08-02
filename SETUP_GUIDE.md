# 🏋️ GymCut — Setup Guide for Complete Beginners

This guide assumes you know **nothing** about coding. Follow each step exactly.

---

## What We're Building

A website that:
1. You open in your browser
2. You drag & drop a gym video
3. AI finds the best moments
4. It gives you an edited video to download

---

## Step 1: Install Node.js (Makes the website run)

1. Open your browser and go to: **https://nodejs.org**
2. Click the big green button that says **"LTS"** (not "Current")
3. Download the file (it's a `.msi` installer)
4. Double-click the downloaded file
5. Click **Next > Next > Next > Install** (accept all defaults)
6. Click **Finish**
7. **Restart your computer** (this is important!)

**How to check it worked:**
- Press `Windows Key` on your keyboard
- Type `cmd` and press Enter (a black window opens)
- Type: `node --version` and press Enter
- You should see something like `v18.17.0`
- Type: `npm --version` and press Enter
- You should see something like `9.6.0`

---

## Step 2: Install Python (Makes the video processing work)

1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Double-click the downloaded file
4. ⚠️ **IMPORTANT:** At the bottom of the installer window, check the box that says:
   **"Add Python to PATH"**
5. Click **Install Now**
6. Wait for it to finish, then click **Close**
7. **Restart your computer again**

**How to check it worked:**
- Open Command Prompt again (`Windows Key` > type `cmd` > Enter)
- Type: `python --version` and press Enter
- You should see something like `Python 3.11.5`

---

## Step 3: Install FFmpeg (Handles the actual video editing)

This is the trickiest part. Follow carefully.

### Option A: Using Winget (Easiest)
1. Open Command Prompt as **Administrator**:
   - Press `Windows Key`
   - Type `cmd`
   - Right-click "Command Prompt" and select **"Run as administrator"**
2. Type this and press Enter:
   ```
   winget install ffmpeg
   ```
3. If it asks for confirmation, type `Y` and press Enter
4. Wait for it to finish
5. **Restart your computer**

### Option B: Manual Download (If Option A didn't work)
1. Go to: **https://www.gyan.dev/ffmpeg/builds/**
2. Scroll down to **"release builds"**
3. Find **"ffmpeg-release-essentials.zip"** and click it
4. Extract the ZIP file to `C:\ffmpeg`
5. Now you need to add it to PATH:
   - Press `Windows Key`, type "environment variables"
   - Click **"Edit the system environment variables"**
   - Click **"Environment Variables..."** button
   - In the bottom section (System variables), find **"Path"** and double-click it
   - Click **"New"** and type: `C:\ffmpeg\bin`
   - Click **OK > OK > OK**
6. **Restart your computer**

**How to check it worked:**
- Open Command Prompt
- Type: `ffmpeg -version` and press Enter
- You should see a bunch of text starting with "ffmpeg version"

---

## Step 4: Open the Project Folder

1. Press `Windows Key + E` to open File Explorer
2. Navigate to where the project is saved:
   ```
   C:\Users\ubeds\OneDrive\Documents\Easytoolkit - AI Agent\wp-content\gym-video-editor
   ```
3. You should see folders: `backend`, `frontend`, and a `README.md` file
4. **Click on the address bar** at the top of File Explorer
5. Type `cmd` and press Enter
6. A black Command Prompt window opens — **this is your control center**

---

## Step 5: Set Up the Backend (Video Processing Engine)

In the Command Prompt window you just opened, type these commands **one at a time**, pressing Enter after each:

### 5.1 Go into the backend folder
```
cd backend
```

### 5.2 Install Python packages
```
pip install -r requirements.txt
```
This will download a bunch of files. Wait for it to finish (1-2 minutes).
You should see "Successfully installed..." at the end.

### 5.3 Create folders for uploads and outputs
```
mkdir uploads
mkdir outputs
```

### 5.4 Start the backend server
```
python -m uvicorn app.main:app --reload --port 8000
```

If it works, you'll see something like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ **Leave this window open!** The backend is now running.

---

## Step 6: Set Up the Frontend (The Website You See)

Open a **NEW** Command Prompt window:
- Press `Windows Key`, type `cmd`, press Enter

### 6.1 Go to the project folder again
```
cd "C:\Users\ubeds\OneDrive\Documents\Easytoolkit - AI Agent\wp-content\gym-video-editor"
```

### 6.2 Go into the frontend folder
```
cd frontend
```

### 6.3 Install website packages
```
npm install
```
This will download a LOT of files. Wait patiently (2-5 minutes).
You'll see a progress bar. When it's done, you'll get a new prompt.

### 6.4 Start the website
```
npm run dev
```

If it works, you'll see something like:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
```

✅ **Leave this window open too!**

---

## Step 7: Open the App!

1. Open your web browser (Chrome, Edge, or Firefox)
2. In the address bar, type: **http://localhost:3000**
3. Press Enter

You should see the **GymCut** website with:
- A dark background
- "Your Gym Videos, Edited by AI" in big text
- A drag-and-drop upload box

---

## Step 8: Test It!

1. Find a short gym video on your computer (MP4 format works best)
2. Drag it onto the upload box, or click to browse
3. Set your options:
   - **AI Detection:** Leave OFF for now (it works without it)
   - **Target Duration:** Pick how long you want the final video (e.g., 30 seconds)
   - **Music Style:** Pick one
4. Click **"Start Auto-Edit"**
5. Wait 1-3 minutes while it processes
6. You'll see a **"Your Video is Ready!"** screen
7. Click **"Download Video"** to save it

---

## Troubleshooting

### "'node' is not recognized"
→ Node.js didn't install correctly. Restart your computer and try again.

### "'python' is not recognized"
→ You forgot to check "Add Python to PATH" during install. Reinstall Python.

### "'ffmpeg' is not recognized"
→ FFmpeg isn't in your PATH. Try Option A (winget) again, or follow Option B carefully.

### "pip is not recognized"
→ Python didn't install pip. Reinstall Python and make sure "Add Python to PATH" is checked.

### Backend shows errors when starting
→ Make sure you're in the `backend` folder when running the command.

### Frontend shows "Module not found" errors
→ Run `npm install` again inside the `frontend` folder.

### Upload fails
→ Make sure the backend is running (the first Command Prompt window is still open).

### Processing takes forever
→ Large videos take longer. Try a short 10-20 second clip first.

---

## How to Stop Everything

1. In each Command Prompt window, press `Ctrl + C`
2. Type `Y` if it asks to confirm
3. Close the windows

---

## How to Start Again Later

You only need to do Steps 5.4 and 6.4 next time:

**Window 1 — Backend:**
```
cd "C:\Users\ubeds\OneDrive\Documents\Easytoolkit - AI Agent\wp-content\gym-video-editor\backend"
python -m uvicorn app.main:app --reload --port 8000
```

**Window 2 — Frontend:**
```
cd "C:\Users\ubeds\OneDrive\Documents\Easytoolkit - AI Agent\wp-content\gym-video-editor\frontend"
npm run dev
```

Then open http://localhost:3000

---

## Need Help?

If you get stuck at any step, tell me:
1. Which step number you're on
2. The exact error message you see (copy and paste it)

I'll help you fix it.
