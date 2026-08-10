# Deployment Guide — Supabase + Render + Vercel

This is the part I can't do for you — I don't have accounts, credentials, or the ability to click buttons on Supabase/GitHub/Render/Vercel's websites. Everything below is copy-paste-able. Total time: ~30-45 minutes, all on free tiers.

**Note:** third-party dashboards change their UI occasionally. If a button/label below doesn't match exactly what you see, look for the nearest equivalent — the underlying steps (create project → get connection string → set env vars → deploy) don't change.

---

## Step 1 — Create your Supabase database

1. Go to [supabase.com](https://supabase.com) → sign up (GitHub login is fastest) → **New Project**.
2. Pick an organization, name the project (e.g. `nexatel-churn`), generate/save a strong database password, pick the region closest to you, and click **Create new project**. Wait ~2 minutes for it to provision.
3. Once it's ready, go to **Project Settings → Database**. Under **Connection string**, copy the **URI** value (choose the "Session pooler" connection string — it looks like `postgresql://postgres.xxxx:[YOUR-PASSWORD]@aws-x-xx-xxxx-x.pooler.supabase.com:5432/postgres`). Replace `[YOUR-PASSWORD]` with the password you set in step 2.
4. In the project's **SQL Editor** (left sidebar), click **New query**, paste the entire contents of `database/schema.sql`, and click **Run**. You should see "Success. No rows returned" — this creates all 4 tables + the `v_customer_360` view.
5. On your own machine, in the project folder:
   ```bash
   cd database
   cp ../backend/.env.example .env    # or create a new .env here
   ```
   Edit `.env` and set:
   ```
   DATABASE_URL=postgresql://postgres.xxxx:[YOUR-PASSWORD]@aws-x-xx-xxxx-x.pooler.supabase.com:5432/postgres
   ```
6. Install dependencies and load the data:
   ```bash
   pip install pandas sqlalchemy psycopg2-binary python-dotenv
   python load_data.py
   ```
   You should see `Loaded 7043 rows -> customers` (and 3 more tables), then `Verification: v_customer_360 view returns 7043 joined rows.`
7. Sanity check in Supabase's **Table Editor**: open `customers` — you should see 7,043 rows.

You now have a live, cloud-hosted Postgres database. (Note: the deployed backend does **not** need to connect to this database — it loads `model.pkl` directly from disk. This step is for having a real, live version of the Phase 1 database deliverable, and for anyone re-running `database/queries.sql` against real cloud infrastructure.)

---

## Step 2 — Push the project to GitHub

1. Go to [github.com/new](https://github.com/new), create a new **public** repository (e.g. `nexatel-churn-prediction`), don't initialize it with a README (you already have one).
2. From the project's root folder:
   ```bash
   cd nexatel-churn-prediction
   git init
   git add .
   git commit -m "Initial commit: NexaTel churn prediction system"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/nexatel-churn-prediction.git
   git push -u origin main
   ```
3. Double check on GitHub that `frontend/node_modules/`, `.env`, and `__pycache__/` were **not** pushed (the included `.gitignore` should already prevent this — if you see them, remove and re-push).

---

## Step 3 — Deploy the backend to Render

1. Go to [render.com](https://render.com) → sign up (GitHub login recommended, since it lets Render see your repos directly).
2. Click **New +** → **Web Service**. Connect your GitHub account if prompted, then select the `nexatel-churn-prediction` repo.
3. Configure it:
   | Field | Value |
   |---|---|
   | Name | `nexatel-churn-api` (or anything) |
   | Root Directory | `backend` |
   | Environment | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | `Free` |
4. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `ALLOWED_ORIGINS` | `http://localhost:5173` (you'll update this in Step 5) |
5. Click **Create Web Service**. Render will build and deploy — takes 3-5 minutes the first time. Watch the logs; you're looking for `Application startup complete.`
6. Once live, copy your backend's URL from the top of the Render dashboard — it looks like `https://nexatel-churn-api.onrender.com`.
7. Test it directly in your browser: visit `https://nexatel-churn-api.onrender.com/health` — you should see `{"status":"ok"}`. Visit `/docs` for the interactive Swagger UI and try the `/predict` endpoint right there.

**Free tier note:** Render's free web services spin down after ~15 minutes of no traffic and take 30-50 seconds to "wake up" on the next request. This is normal — if your first test after a while feels slow, that's why, not a bug.

---

## Step 4 — Deploy the frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → sign up (GitHub login recommended).
2. Click **Add New...** → **Project**, import the same `nexatel-churn-prediction` repo.
3. Configure it:
   | Field | Value |
   |---|---|
   | Root Directory | `frontend` (click "Edit" next to Root Directory to set this) |
   | Framework Preset | `Vite` (should auto-detect) |
   | Build Command | `npm run build` (default, from `vercel.json`) |
   | Output Directory | `dist` (default, from `vercel.json`) |
4. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://nexatel-churn-api.onrender.com` (your actual Render URL from Step 3.6, **no trailing slash**) |
5. Click **Deploy**. Takes ~1-2 minutes.
6. Once live, copy your frontend's URL — it looks like `https://nexatel-churn-prediction.vercel.app`.

---

## Step 5 — Connect the two (update CORS)

Right now the backend only allows requests from `localhost`. Point it at your real frontend URL:

1. Back in the Render dashboard, go to your `nexatel-churn-api` service → **Environment**.
2. Edit `ALLOWED_ORIGINS` to: `https://nexatel-churn-prediction.vercel.app` (your actual Vercel URL from Step 4.6 — if you want to keep local dev working too, use a comma-separated list: `http://localhost:5173,https://nexatel-churn-prediction.vercel.app`).
3. Save — Render will automatically redeploy the backend with the new setting (~1-2 minutes).

---

## Step 6 — Test the live app end-to-end

1. Open your Vercel URL in a normal browser tab (not logged into anything, incognito is a good test).
2. On the **Score a customer** tab, fill out the form (or leave the defaults) and click **Score customer**. You should see the signal-meter gauge populate with a real prediction within a few seconds (or up to ~50 seconds if the Render backend was asleep — see the free-tier note above).
3. Click the **Portfolio insights** tab and confirm the stat cards and bar charts load.
4. Open your browser's dev tools → Network tab and confirm the `/predict` and `/dashboard-stats` requests are going to your Render URL, not `localhost`.
5. Try it on your phone too, to confirm the responsive layout holds up.

If `/predict` fails with a CORS error in the browser console, double check Step 5 — the `ALLOWED_ORIGINS` value must **exactly** match your Vercel URL (including `https://`, no trailing slash).

---

## Step 7 — Finish the documentation

Once both URLs are live, go back and fill in the placeholders:

- `README.md` — replace both `<add your ... URL here>` lines at the top
- `docs/case_study.md` — replace the `[GitHub repository link] · [Live app link]` line at the bottom
- Your resume / LinkedIn — use the bullets in `docs/resume_bullets.md`, and add the live link

**Optional but recommended (Phase 9 bonus):** record a 2-3 minute screen recording walking through the live app — fill out a couple of different customer profiles (a clear high-risk one and a clear low-risk one), show the Portfolio Insights tab, and briefly explain the architecture. This is one of the highest-leverage things you can add to a portfolio project; a live link is good, a link plus a video where you talk through it confidently is much better in an interview context.
