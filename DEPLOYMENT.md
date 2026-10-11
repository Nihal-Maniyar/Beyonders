# LearnLoop AI — Production Deployment Guide

This guide details the exact procedures to deploy LearnLoop AI for production accessibility. It covers unified single-service deployment, separated frontend/backend deployment, and the Streamlit backup deployment.

---

## 1. Detected Project Architecture

| Layer | Technology | Primary Directory | Entry Point / Configuration |
|---|---|---|---|
| **Frontend** | React 18, TypeScript, Vite | `frontend/` | `npm run build` &rarr; `frontend/dist/` |
| **Backend API** | FastAPI, Uvicorn, SQLAlchemy 2 | `src/learnloop/` | `learnloop.api.main:app` |
| **Educational Engine** | Deterministic Python Domain | `src/learnloop/domain/` | M1–M4 diagnosis & Rubric R1–R5 |
| **Voice AI Proxy** | ElevenLabs TTS (`eleven_flash_v2_5`) & STT (`scribe_v2`) | `src/learnloop/services/voice_service.py` | `/api/v1/voice/synthesize`, `/api/v1/voice/transcribe` |
| **Persistence** | SQLite (local) / PostgreSQL (production) | `src/learnloop/db/` | Auto-initialized & seeded on startup |
| **Streamlit Backup** | Streamlit 1.30+ | `./` | `app.py` |

---

## 2. Recommended Hosting Options

### Option A: Unified Single-Service Deployment (Fastest & Simplest)
- **Platforms:** Render, Railway, Fly.io, Heroku, or Docker.
- **How it works:** The multi-stage `Dockerfile` (or build script) compiles the React frontend into `frontend/dist/`, and FastAPI serves both the REST API (`/api/v1`) and the static Learning Studio (`/studio`) on a single port (`$PORT`).
- **Advantages:** Zero CORS configuration required, one environment, single subscription/tier.

### Option B: Split Frontend / Backend Deployment
- **Frontend Host:** Vercel, Netlify, or Cloudflare Pages (`frontend/`).
- **Backend Host:** Render, Railway, or Fly.io (`src/learnloop/`).
- **How it works:** Frontend makes HTTPS requests to backend using `VITE_API_BASE_URL`.

### Option C: Streamlit Backup Deployment
- **Platforms:** Streamlit Community Cloud or Render Web Service.
- **Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

---

## 3. Environment Variables Reference

### Backend Environment Variables (Render / Railway / Fly.io / Docker)

| Variable Name | Required? | Default / Example Value | Description |
|---|---|---|---|
| `APP_ENV` | Optional | `production` | Application runtime environment. |
| `LOG_LEVEL` | Optional | `INFO` | Logging verbosity (`INFO`, `DEBUG`, `WARNING`). |
| `PORT` | Auto-set | `8000` | Port assigned by hosting provider (Render/Railway/Heroku auto-inject this). |
| `HOST` | Optional | `0.0.0.0` | Host IP address to bind to. |
| `DATABASE_URL` | Optional | `sqlite:///./learnloop.db` | Database connection string. Supports `postgresql://...` or SQLite. |
| `CORS_ORIGINS` | Recommended | `https://your-frontend.vercel.app,*` | Comma-separated list of allowed origins or `*`. |
| `SESSION_TOKEN_PEPPER`| Recommended | High-entropy random secret | Pepper string for HMAC-SHA256 session token hashing. |
| `SESSION_EXPIRY_HOURS`| Optional | `24` | Session lifetime before automatic expiration. |
| `ELEVENLABS_API_KEY` | Recommended | `sk_...` | ElevenLabs API key for spoken tutor guidance and speech-to-text. |
| `ELEVENLABS_VOICE_ID`| Optional | `21m00Tcm4TlvDq8ikWAM` | ElevenLabs voice ID (default: Rachel). |
| `ELEVENLABS_MODEL_ID`| Optional | `eleven_flash_v2_5` | ElevenLabs TTS model. |
| `ELEVENLABS_STT_MODEL_ID` | Optional | `scribe_v2` | ElevenLabs Speech-to-Text model. |

> **Security Note:** Provider secrets (`ELEVENLABS_API_KEY`, `SESSION_TOKEN_PEPPER`) must NEVER be prefixed with `VITE_` or placed in frontend bundles.

### Frontend Environment Variables (Vercel / Netlify)

| Variable Name | Required? | Example Value | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | If split host | `https://learnloop-backend.onrender.com` | Full HTTPS URL of deployed FastAPI backend. (Leave empty if using unified deployment). |

---

## 4. Step-by-Step Deployment Procedures

### Procedure 1: Unified Docker Deployment (Render / Railway / Fly.io)

1. Connect your GitHub repository to your PaaS provider.
2. Select **Docker** environment.
3. Configure Environment Variables in the provider dashboard:
   - `APP_ENV=production`
   - `SESSION_TOKEN_PEPPER=<generate-random-secret>`
   - `ELEVENLABS_API_KEY=<your-elevenlabs-key>`
4. The provided `Dockerfile` will automatically:
   - Install Node.js dependencies and build `frontend/dist/`.
   - Install Python dependencies from `requirements.txt`.
   - Initialize the database and seed verified fraction concepts.
   - Run `uvicorn learnloop.api.main:app --host 0.0.0.0 --port $PORT`.
5. Access your deployment:
   - Learning Studio: `https://<your-app-domain>/studio`
   - API Docs: `https://<your-app-domain>/docs`
   - Health Probe: `https://<your-app-domain>/health`

---

### Procedure 2: Split Deployment (Vercel Frontend + Render Backend)

#### Part A: Deploy Backend (Render)
1. In Render, click **New + &rarr; Web Service**.
2. Connect your GitHub repository.
3. Settings:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn learnloop.api.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `APP_ENV=production`
   - `CORS_ORIGINS=https://<your-vercel-app>.vercel.app,*`
   - `SESSION_TOKEN_PEPPER=<random-string>`
   - `ELEVENLABS_API_KEY=<your-key>`
5. Click **Deploy**. Note the backend URL (e.g., `https://learnloop-api.onrender.com`).

#### Part B: Deploy Frontend (Vercel)
1. In Vercel, click **Add New &rarr; Project**.
2. Import the GitHub repository.
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add Environment Variable:
   - `VITE_API_BASE_URL=https://learnloop-api.onrender.com`
5. Click **Deploy**. `vercel.json` will automatically route client-side SPA navigation.

---

### Procedure 3: Streamlit Community Cloud (Backup Demo)

1. Navigate to [share.streamlit.io](https://share.streamlit.io).
2. Connect GitHub repository.
3. Settings:
   - **Main file path:** `app.py`
4. In Advanced Settings &rarr; Secrets, paste:
   ```toml
   ELEVENLABS_API_KEY = "sk_..."
   ```
5. Click **Deploy**.

---

## 5. Local Build & Run Commands

To verify locally before deployment:

### Backend:
```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn learnloop.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend:
```bash
# Install dependencies
cd frontend
npm install

# Build for production
npm run build

# Run local preview
npm run preview
```

### Full Test Suite:
```bash
# Run all unit, API, integration, and rule tests
pytest -v
```

---

## 6. Health Checks & Verification

After deployment, verify that all core endpoints return expected responses:

1. **Root Health Check:**
   ```bash
   curl -i https://<your-domain>/health
   # Expected: HTTP 200 {"status": "healthy", "version": "1.0.0", "app": "LearnLoop AI"}
   ```
2. **API v1 Health Check:**
   ```bash
   curl -i https://<your-domain>/api/v1/health
   # Expected: HTTP 200 {"status": "healthy", "version": "1.0.0", "api_prefix": "/api/v1"}
   ```
3. **Assessment Integrity Check (no answers leaked):**
   ```bash
   curl -i https://<your-domain>/api/v1/assessments/FRACTIONS_PRE
   # Expected: HTTP 200 with question prompts and options (no is_correct flags)
   ```
4. **Voice Service Health Check:**
   - Navigate to the Teach-Back Studio in the browser.
   - Click **`🎙️ Speak Explanation`** and allow microphone access.
   - Speak your answer and confirm audio transcription populates the textbox.
   - If audio/microphone is unavailable, confirm the text fallback operates without crashing.

---

## 7. Troubleshooting Common Deployment Failures

| Symptom | Root Cause | Fix |
|---|---|---|
| **CORS error in browser console** | Backend `CORS_ORIGINS` does not include frontend domain. | Set `CORS_ORIGINS=https://<frontend-domain>,*` on backend service. |
| **API requests 404 in frontend** | `VITE_API_BASE_URL` is missing or wrong in split deployment. | In Vercel/Netlify, set `VITE_API_BASE_URL=https://<backend-domain>` and redeploy. |
| **Port binding failure on Render/Heroku** | Hardcoded port `8000` instead of reading `$PORT`. | Use `uvicorn learnloop.api.main:app --host 0.0.0.0 --port $PORT` (already handled in `Procfile` and `main.py`). |
| **Voice synthesis shows fallback notice** | `ELEVENLABS_API_KEY` not configured or quota exceeded. | Check that `ELEVENLABS_API_KEY` is added to host environment variables. Fallback text tutoring continues to function normally. |
| **Database write errors on ephemeral host** | Default SQLite path resets on container restarts. | For persistent multi-session history in production, supply a hosted PostgreSQL `DATABASE_URL=postgresql://...`. SQLite works for live demos. |

---

## 8. Redeployment After GitHub Updates

To deploy changes made to the repository:
1. Push commits to your deployed GitHub branch (`main` or `feature/learnloop-v1-foundation`).
2. If your PaaS provider has **Auto-Deploy** enabled, it will automatically rebuild and deploy within 1–2 minutes.
3. If auto-deploy is disabled, click **Manual Deploy &rarr; Deploy Latest Commit** in your provider dashboard.

