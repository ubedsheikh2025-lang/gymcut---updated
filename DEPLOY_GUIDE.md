# 🚀 Deploy GymCut to Render (Free — No Coding Required)

This guide will get your app live at a public URL like `https://gymcut.onrender.com`.

**Time required:** ~15 minutes
**Cost:** Free
**Skills needed:** None — just follow each step

---

## Step 1: Create a GitHub Account

1. Go to **https://github.com**
2. Click **"Sign up"**
3. Enter your email, create a password, choose a username
4. Verify your email
5. You now have a GitHub account!

---

## Step 2: Upload the Code to GitHub

### Option A: Drag & Drop (Easiest)

1. Go to **https://github.com/new**
2. Repository name: `gymcut`
3. Keep it **Public**
4. Click **"Create repository"**
5. On the next page, click **"uploading an existing file"**
6. Drag the ENTIRE `gym-video-editor` folder into the browser
7. Scroll down and click **"Commit changes"**

### Option B: Using GitHub Desktop (If you prefer an app)

1. Download GitHub Desktop from **https://desktop.github.com**
2. Install and sign in with your GitHub account
3. Click **"Add" > "Add Existing Repository"**
4. Select the `gym-video-editor` folder
5. Click **"Publish repository"**

---

## Step 3: Deploy to Render

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with your **GitHub account** (this connects Render to your code)
4. After signing in, click **"New +"** > **"Web Service"**
5. Find `gymcut` in the list and click **"Connect"**
6. Configure the service:

   | Setting | Value |
   |---------|-------|
   | Name | `gymcut` |
   | Region | `Oregon (US West)` |
   | Branch | `main` |
   | Runtime | **Docker** |
   | Dockerfile Path | `./Dockerfile` |
   | Instance Type | **Free** |

7. Scroll down and click **"Create Web Service"**

---

## Step 4: Wait for Deployment

Render will now:
1. Build the Docker image (3-5 minutes)
2. Install Python + FFmpeg + Node.js
3. Build the frontend
4. Start the server

You'll see a log output. When it says **"Your service is live"**, you're done!

---

## Step 5: Open Your App

1. Click the URL Render gives you (looks like `https://gymcut.onrender.com`)
2. You should see the GymCut website!
3. Upload a gym video and test it

---

## Important Notes

### ⚠️ Free Tier Limitations

- **Cold starts:** If no one visits for 15 minutes, the server sleeps. First visit takes ~30 seconds to wake up.
- **Storage:** Uploaded videos are temporary. They get deleted when the server restarts.
- **Processing time:** Free tier has limited CPU. Long videos may take 3-5 minutes.

### 🔧 If Something Goes Wrong

1. Go to your Render dashboard
2. Click on `gymcut`
3. Click the **"Logs"** tab
4. Look for red error messages
5. Copy the error and send it to me — I'll help fix it

---

## That's It!

Your AI gym video editor is now live on the internet. Share the URL with friends, use it on your phone, or embed it anywhere.

**Need help?** Tell me which step you're stuck on and what error you see.
