# Setup Guide

Get PolliSync running locally for development.

---

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Git | 2.40+ | `git --version` |
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |

Optional: GitHub CLI (`gh`) for repository administration.

---

## Clone

```bash
git clone https://github.com/sairaj2832-star/Pollysync.git
cd Pollysync
```

---

## Environment Files

```bash
# Windows
Copy-Item frontend\.env.example frontend\.env
Copy-Item backend\.env.example backend\.env

# macOS/Linux
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

Never commit real API keys. Both `.env` files are gitignored.

---

## Backend

### 1. Create virtual environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
# From repo root
pip install -r backend\requirements-dev.txt    # Windows
pip install -r backend/requirements-dev.txt     # macOS/Linux
```

Use `requirements-dev.txt` (includes pytest + httpx for testing). Use `requirements.txt` for production only.

### 3. ML model setup

The backend requires serialized model files in `ml/models/`. These are committed to the repository.

```bash
# Verify models exist
dir ml\models\*.pkl      # Windows
ls ml/models/*.pkl        # macOS/Linux
```

You should see 24 `.pkl` files including `flowering_model.pkl`, `psi_model.pkl`, `risk_model.pkl`, and their v2/ensemble variants.

**If models are missing**, regenerate them:

```bash
cd ml/src
python train_improved_models.py
python train_ensemble.py
```

### 4. Run the backend

```bash
cd backend
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI. The health endpoint is http://localhost:8000/api/health.

### 5. Run backend tests

```bash
cd backend
pytest
```

---

## Frontend

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment

Edit `frontend/.env` if you need to change the API URL. The default points to `http://localhost:8000` for local development.

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_USE_MOCK` | Enable mock data mode | `false` |

### 3. Run the frontend

```bash
npm run dev
```

Opens at http://localhost:5173.

### 4. Build for production

```bash
npm run build
```

Output goes to `frontend/dist/`.

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No | SQLite connection string. Default: `sqlite:///./pollisync.db` |
| `SECRET_KEY` | Yes | JWT signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GEMINI_API_KEY` | No | Google Gemini API key for LLM recommendations. Without it, fallback recommendations are used. |
| `FIREBASE_PROJECT_ID` | No | Firebase project ID for Google OAuth |
| `FIREBASE_PRIVATE_KEY` | No | Firebase service account private key |
| `FIREBASE_CLIENT_EMAIL` | No | Firebase service account email |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API base URL |
| `VITE_USE_MOCK` | No | Set to `true` to use mock data instead of real API |
| `VITE_FIREBASE_*` | No | Firebase config for Google OAuth (apiKey, authDomain, projectId, etc.) |

---

## Team Branch Workflow

1. Start work from the current test branch.
2. Use a short feature branch for substantial changes: `git checkout -b feature/your-feature`
3. Push and create a PR when ready for review.
4. Integrate and validate changes on test.
5. Update main from test only after CI and manual smoke checks pass.
6. Deploy production from main.

**Never force-push main or test.** If main and test diverge, stop and resolve the history intentionally.

---

## Troubleshooting

### Backend won't start

- **ModuleNotFoundError**: Run `pip install -r backend/requirements-dev.txt` from the repo root with the venv activated.
- **Model file not found**: Ensure `ml/models/*.pkl` files exist. See [ML model setup](#3-ml-model-setup).
- **Port already in use**: Use `uvicorn app.main:app --reload --port 8001` or kill the process on port 8000.

### Frontend won't start

- **npm install fails**: Delete `node_modules` and `package-lock.json`, then run `npm install` again.
- **Blank page**: Check that `VITE_API_URL` in `frontend/.env` points to a running backend.
- **CORS errors**: Ensure the backend CORS origins include `http://localhost:5173`. Check `backend/app/main.py`.

### Database issues

- **SQLite locked**: Make sure only one backend instance is running. Stop other uvicorn processes.
- **Database reset**: Delete `pollisync.db` and restart the backend. Tables are recreated automatically.
- **Schema mismatch**: The backend runs schema reconciliation on startup. Check the server logs for ALTER TABLE statements.

### ML model issues

- **Model accuracy seems low**: The models are trained on synthetic data. This is expected for the hackathon MVP. See `docs/PLAYBOOK.md` Section 10 for model performance details.
- **Prediction errors**: Check that the feature vector has all 24 dimensions. Enable debug logging in `prediction_service.py`.
