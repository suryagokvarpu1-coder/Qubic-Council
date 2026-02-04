# Vercel Deployment Guide

You have two versions of the frontend available given the codebase structure.

## Option A: Deploy "Quantum Consensus" (3D Interface) - RECOMMENDED
This uses the animated 3D loading page and the main HTML interface you have been working on.

**1. Deploy Backend (Render/Railway)**
   - Deploy the `backend` folder to Render.com (or similar).
   - Get your Backend URL (e.g., `https://qubic-council.onrender.com`).
   - **Update your code**: Open `mainpage.html` (line ~432) and replace `https://replace-with-your-backend-url.com` with your actual Backend URL.
   - Commit and push changes.

**2. Deploy Frontend (Vercel)**
   - **Root Directory**: `.` (Project Root) -- Leave it as the default `./`
   - **Framework Preset**: Other (or None) -- It's a static site
   - **Build Command**: (Leave empty)
   - **Output Directory**: (Leave empty)
   - **Env Variables**: None needed (config is in `mainpage.html`)

   *Note: Vercel might try to detect the backend python files. If it asks, ensure you are deploying as a Static Site or just "Web".*

---

## Option B: Deploy React Dashboard
This uses the modern React application located in the `frontend` folder.

**1. Deploy Backend** (Same as above)

**2. Deploy Frontend (Vercel)**
   - **Root Directory**: `frontend` (You must select this folder)
   - **Framework Preset**: Vite
   - **Env Variables**: `VITE_API_BASE_URL` = Your Backend URL

---

## ⚠️ Important Note regarding Backend
The "Consensus Engine" backend performs heavy AI tasks (querying 4 models, peer review).
**DO NOT deploy the backend to Vercel Serverless Functions.**
They will timeout after 10 seconds. Use **Render**, **Railway**, or **Heroku**.
