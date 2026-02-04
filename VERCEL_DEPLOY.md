# Vercel Deployment Guide

Since your application has a separate Backend (Python) and Frontend (React), the deployment strategy involves two parts.

## ⚠️ Important Warning
**The Backend (Consensus Engine) may timeout on Vercel.**
Vercel's Hobby plan has a **10-second timeout** for serverless functions. Your consensus engine (querying 4 models, peer review, etc.) typically takes 15-40 seconds.
**Recommendation:** Deploy the Backend on **Render** or **Railway** (which allow longer execution times) and the Frontend on **Vercel**.

---

## Part 1: Deploy Backend (Render/Railway)

We recommend **Render** for the backend.

1. Push your code to GitHub.
2. Sign up at [render.com](https://render.com).
3. Create a **New Web Service**.
4. Connect your GitHub repo.
5. **Root Directory**: `backend`
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. **Environment Variables**:
   - `PYTHON_VERSION`: `3.11` (optional but recommended)
   - `OPENROUTER_API_KEY`: (Your key)
   - `GROQ_API_KEY`: (Your key)
9. Deploy! Copy the **Service URL** (e.g., `https://qubic-council.onrender.com`).

---

## Part 2: Deploy Frontend (Vercel)

Now deploy the UI and connect it to the backend.

1. Go to [vercel.com](https://vercel.com) and "Add New Project".
2. Import your GitHub repository (`Qubic-Council`).
3. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`  <-- **IMPORTANT** (Click "Edit" next to Root Directory)
   - **Build Command**: `npm run build` (Default)
   - **Output Directory**: `dist` (Default)
4. **Environment Variables**:
   Add the following variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: Your Backend URL from Part 1 (e.g., `https://qubic-council.onrender.com`)
     *(Do not include a trailing slash)*
5. Click **Deploy**.

## Part 3: Deploying "Whole App" on Vercel (Advanced/Not Recommended)

If you strictly want to deploy **everything** on Vercel (knowing it might timeout):

1. **Root Directory**: `.` (Project Root)
2. You must create a `vercel.json` in the root (created by AI, see below).
3. You must restructure the backend to match Vercel's Serverless Function expectations (requires creating an `api/` folder).

**We strongly suggest the Render + Vercel approach.**
