# PolliSync

> **AI-assisted crop-pollination decision support for farmers.**

PolliSync turns farm context, weather, crop-health signals, seasonal pollen context, and pollinator observations into a clear **Pollination Suitability Index (PSI)**, flowering-window outlook, and practical next action. It is built for the Hack4Humanity **AI for Societal Good** track and begins with Maharashtra-focused crop scenarios.

**Tags:** `agritech` `pollination` `climate-resilience` `farmer-decision-support` `fastapi` `react` `machine-learning` `ai-for-good` `hackathon`

> PolliSync is decision support—not a yield guarantee or replacement for local agronomist advice. Data sources, missing-data fallbacks, and model confidence must always be communicated clearly.

## Table of contents

- [What PolliSync does](#what-pollisync-does)
- [Product features](#product-features)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Run and validate](#run-and-validate)
- [Data sources and model status](#data-sources-and-model-status)
- [API overview](#api-overview)
- [Development workflow](#development-workflow)
- [Documentation](#documentation)
- [Known limitations and next steps](#known-limitations-and-next-steps)
- [License](#license)

## What PolliSync does

A grower creates a farm profile, chooses a crop and location, and requests a prediction. PolliSync then:

1. retrieves or reuses recent weather data;
2. builds crop, weather, pollen, vegetation, and pollinator features;
3. calculates a PSI score and risk label, and estimates a flowering window;
4. saves the prediction so trends and history are available; and
5. generates a concise recommendation using Gemini when configured, or a deterministic local fallback when it is not.

The intended outcome is a simpler field decision: for example, prepare for an upcoming flowering window, monitor weather stress, or avoid disruptive activity during likely pollinator-active conditions.

## Product features

- Farm onboarding, profiles, multiple farms, districts, notifications, and team-management APIs
- JWT authentication, refresh-token flow, and optional Firebase token exchange
- Prediction dashboard with PSI, risk, weather, pollen, flowering, NDVI, charts, and field map
- Open-Meteo current weather and forecast with a one-hour database cache
- NASA POWER seven-day environmental features for prediction enrichment
- GBIF pollinator occurrence lookup and local occurrence persistence
- Optional Google Earth Engine / Sentinel-2 NDVI lookup
- Gemini-backed agronomy recommendations with a controlled local fallback
- AI-assistant and optional Supabase-vector-store retrieval endpoints
- React/Vite responsive interface with mock mode for deterministic UI demos
- FastAPI OpenAPI documentation and GitHub Actions CI for frontend build and backend tests

## Architecture

```text
Farmer
  │
  ▼
React + Vite frontend ── HTTPS / JWT ──► FastAPI API
                                            │
              ┌─────────────────────────────┼────────────────────────────┐
              ▼                             ▼                            ▼
       SQLite now /                    Prediction services           AI services
       PostgreSQL later                 + feature engineering        Gemini / RAG
              │                             │                            │
              └───────────────┬─────────────┼─────────────┬─────────────┘
                              ▼             ▼             ▼
                        Open-Meteo      GBIF / NASA    Earth Engine
                                       POWER / pollen     (optional)
```

The hackathon implementation is deliberately a modular monolith. The backend keeps data-ingestion, prediction, recommendation, and persistence boundaries separate so that queues, managed PostgreSQL, model serving, and observability can be added later without rebuilding the product.

For the full current-vs-planned architecture and data-flow diagrams, see [Project_Pollysync.md](Project_Pollysync.md).

## Repository structure

```text
Pollysync/
├── frontend/                  # React 18 + Vite + Tailwind interface
│   └── src/                   # Pages, components, contexts, API client
├── backend/                   # FastAPI application and SQLAlchemy models
│   ├── app/api/routes/        # Auth, farms, weather, predictions, maps, AI
│   ├── app/services/          # Weather, features, predictions, recommendations
│   ├── tests/                 # API tests
│   └── supabase/              # PostgreSQL/Supabase migration path
├── ml/                        # Data, ML utilities, training and validation scripts
│   ├── src/
│   ├── data/
│   └── models/                # Generated model artefacts (not committed)
├── docs/                      # Setup, architecture, progress, and demo notes
├── .github/workflows/         # CI workflow
├── Project_Pollysync.md       # Submission brief, audit, deck, and demo guide
└── PolliSync_Student_Hackathon_Playbook.md
```

## Quick start

### Prerequisites

- Node.js 20+
- Python **3.11** (the CI target; recommended for dependency compatibility)
- npm 10+
- Git

### 1. Clone and configure

```powershell
git clone https://github.com/sairaj2832-star/Pollysync.git
Set-Location Pollysync

Copy-Item frontend\.env.example frontend\.env
Copy-Item backend\.env.example backend\.env
```

On macOS/Linux, use `cp frontend/.env.example frontend/.env` and `cp backend/.env.example backend/.env`.

Do not commit `.env` files, API keys, Firebase service-account files, or local databases.

### 2. Start the backend

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt

Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation. The health endpoint is [http://localhost:8000/api/health](http://localhost:8000/api/health).

### 3. Start the frontend

Open a second terminal at the repository root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Configuration

### Frontend environment

`frontend/.env.example` contains the main frontend options:

```dotenv
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=true
```

- `VITE_USE_MOCK=true` uses deterministic mock data for UI development and a reliable prototype recording.
- Set `VITE_USE_MOCK=false` only after the backend is running and the real end-to-end flow has been verified.
- Firebase values are optional unless Firebase sign-in is being used.

### Backend environment

`backend/.env.example` supports local SQLite by default:

```dotenv
APP_ENV=development
DATABASE_URL=sqlite:///./pollisync.db
FRONTEND_ORIGIN=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=replace-this-before-deployment
```

Optional integrations:

| Variable group | Enables |
| --- | --- |
| `GEMINI_API_KEY` / `LLM_API_KEY` | Generated recommendations and AI assistant |
| `EE_SERVICE_ACCOUNT`, `EE_PRIVATE_KEY_FILE` | Google Earth Engine / Sentinel-2 NDVI |
| `SUPABASE_URL`, `SUPABASE_*_KEY` | Supabase database/vector-store path |
| `FIREBASE_*` | Firebase identity-token verification |

Use a long random `SECRET_KEY` and deployment secret manager in production. Never expose service credentials in source control or the browser.

## Run and validate

### Frontend

```powershell
Set-Location frontend
npm run build
npm run preview
```

### Backend

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest
```

The CI workflow runs `npm ci && npm run build` in `frontend/` and `python -m pytest` in `backend/` using Python 3.11. Run the same commands before opening a pull request.

## Data sources and model status

| Source / component | Purpose | Important limitation |
| --- | --- | --- |
| Open-Meteo | Current weather and forecast | Cached for one hour; a controlled fallback is used if unavailable. |
| NASA POWER | Seven-day environmental features | External availability and response freshness can vary. |
| GBIF | Recorded bee/pollinator occurrences | Indicates recorded observations, not a real-time count of pollinators on a farm. |
| Seasonal pollen lookup | Pollen context | Static monthly proxy, not a local live pollen sensor. |
| Earth Engine / Sentinel-2 | NDVI crop-health signal | Optional; credentials and suitable imagery are required. |
| Local ML artefacts | Flowering, PSI, and risk inference | Artefacts are generated and intentionally ignored by Git. A clean checkout without `.pkl` artefacts uses the rule-based baseline. |
| Gemini | Natural-language advisory / assistant | Optional and subject to API configuration, quotas, and output safety checks. |

Use visible source, timestamp, confidence, and fallback labels in any live demo. Do not present proxy data or a rule-based fallback as a verified live measurement or field-validated ML result.

## API overview

All routes are served below `/api`. Protected endpoints require `Authorization: Bearer <access_token>`.

| Area | Example endpoints |
| --- | --- |
| Health | `GET /api/health` |
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Farms | `GET/POST /api/farms`, `PATCH/DELETE /api/farms/{farm_id}` |
| Weather | `GET /api/weather/current`, `GET /api/weather/forecast` |
| Predictions | `POST /api/predictions`, `GET /api/predictions`, `GET /api/predictions/dashboard/summary` |
| Recommendations | `POST /api/recommendations/generate` |
| Maps | `GET /api/maps/bees` |
| AI agent | `POST /api/agent/chat`, `POST /api/agent/search` |

The authoritative request/response schemas are available from the running FastAPI documentation at `/docs`.

## Development workflow

1. Start from the shared integration branch (`test`) or your assigned feature branch.
2. Keep commits focused; do not mix generated databases, environment files, or unrelated refactors with product changes.
3. Run the frontend build and backend tests locally.
4. Open a pull request into `test`; merge to `main` only after CI and manual smoke testing.
5. Never force-push shared branches. Resolve divergent history intentionally.

### Submission/demo workflow

Before recording:

1. Choose and verify one scenario (farm, crop, and district).
2. Run the real flow with `VITE_USE_MOCK=false`, or clearly state that a mock-mode prototype is being shown.
3. Keep a pre-computed dashboard view ready in case an external provider is slow.
4. Explain one decision from PSI/risk to recommended action; avoid claiming unverified yield or accuracy numbers.

See [Project_Pollysync.md](Project_Pollysync.md) for the slide outline, demo run sheet, question bank, system flow, and full readiness audit.

## Documentation

- [Project_Pollysync.md](Project_Pollysync.md) — submission brief, architecture, redundancy audit, PPT outline, and demo guide
- [docs/SETUP.md](docs/SETUP.md) — local setup and team branch workflow
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — original architecture notes
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) — existing demo script
- [docs/progress.md](docs/progress.md) — implementation tracker
- [ml/README.md](ml/README.md) — ML workspace notes
- [PolliSync_Student_Hackathon_Playbook.md](PolliSync_Student_Hackathon_Playbook.md) — hackathon playbook

## Known limitations and next steps

- Package versioned model artefacts and model cards before claiming deployed ML inference.
- Validate on the supported Python 3.11 environment; do not rely on an untested Python 3.13 dependency combination.
- Move production data to managed PostgreSQL, use versioned migrations, and stop tracking SQLite WAL/SHM sidecars.
- Add API rate limits, dependency/secret scanning, structured logging, and monitoring before public deployment.
- Make provenance/fallback state prominent in the UI, then validate the product with farmers and agronomists.
- Add local-language, low-bandwidth/PWA, and accessible field-summary experiences based on user research.

## License

This project is released under the [MIT License](LICENSE).
