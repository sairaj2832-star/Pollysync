# PolliSync Engineering Playbook

> **AI-Based Crop Pollination Suitability System**
> **Team:** 4 SY CSE-AI Students
> **Version:** Student Edition

---

## Table of Contents

1. [Philosophy & Principles](#1-philosophy--principles)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Team Roles](#4-team-roles)
5. [Phase 1: Hackathon MVP](#5-phase-1-hackathon-mvp)
6. [Phase 2: Main Project Polish](#6-phase-2-main-project-polish)
7. [Module A: Infrastructure & DevOps](#7-module-a-infrastructure--devops)
8. [Module B: Frontend](#8-module-b-frontend)
9. [Module C: Backend](#9-module-c-backend)
10. [Module D: ML & AI](#10-module-d-ml--ai)
11. [Database Schema](#11-database-schema)
12. [API Contract](#12-api-contract)
13. [AI/ML Architecture](#13-aiml-architecture)
14. [Workflow & Tools](#14-workflow--tools)
15. [Roadmap](#15-roadmap)
16. [Risk Register](#16-risk-register)
17. [Deployment Checklists](#17-deployment-checklists)

---

## 1. Philosophy & Principles

We are 4 Second-Year CSE-AI students building a working hackathon MVP in 2 weeks, then polishing it for the main project deadline.

### Core Principles

1. **Ship what works.** A working SQLite app beats a broken PostgreSQL microservices architecture.
2. **Free tools only.** No paid APIs, no paid hosting tiers for MVP.
3. **Copy-paste is okay.** Use templates, use boilerplate. Hackathons reward working demos, not handwritten code.
4. **One person, one domain.** Own your module. Cross-train only enough to unblock each other.
5. **Demo-first thinking.** Every week's output must be demo-able to a non-technical judge.

### What We Are NOT Building (For Now)

- Docker, Kubernetes, microservices
- Redis, Celery, RabbitMQ
- MLflow, Kubeflow, complex MLOps
- LangChain, LangGraph, ChromaDB
- PostgreSQL with PostGIS (SQLite for MVP, upgrade later)
- Google Maps API (costs money — use Leaflet + OpenStreetMap)
- Google Pollen API (hard to get access — use seasonal mock data)
- Real-time satellite NDVI from Sentinel-2 (use NASA POWER or mock)

### What We ARE Building

- React + Tailwind frontend on Netlify
- FastAPI + Supabase PostgreSQL backend on Render
- Scikit-learn / XGBoost models (train locally, deploy as .pkl files)
- Open-Meteo weather API (free, no key)
- Direct LLM API calls (Gemini) for recommendations
- Firebase Authentication (email/password + Google OAuth)
- Leaflet maps (free)
- A dashboard that looks professional and demo-ready

---

## 2. System Architecture

See [docs/images/architecture.png](images/architecture.png) for the full diagram. For detailed component breakdowns, see [ARCHITECTURE.md](ARCHITECTURE.md).

```
User → React Frontend (Vite) → FastAPI Backend → External APIs + ML Models + SQLite
```

### Data Flow (simplified)

```
User selects Crop + Location
    → Backend fetches Weather from Open-Meteo (cached 1h)
    → Backend fetches Bee data from GBIF (cached 1 week)
    → Feature Engineering (24-dim vector)
    → Flowering Model (XGBoost) → predicted window
    → PSI Model (XGBoost) → score 0-100 + risk level
    → LLM API Call (Gemini) → natural language recommendation
    → Dashboard displays everything
```

---

## 3. Tech Stack

### Frontend

| Tech | Purpose |
|------|---------|
| React 18 | UI framework |
| Vite | Build tool with instant HMR |
| Tailwind CSS | Utility-first styling |
| Chart.js | Data visualization |
| React-Leaflet | Interactive maps |
| Axios | HTTP client with interceptors |
| React Router v6 | Client-side routing |
| React Context | Global state (no Redux needed) |

### Backend

| Tech | Purpose |
|------|---------|
| FastAPI | Async Python API framework |
| SQLAlchemy 2.0 | ORM for database operations |
| SQLite | Zero-config database |
| Pydantic | Data validation |
| python-jose | JWT authentication |
| bcrypt | Password hashing |
| Uvicorn | ASGI server |

### ML & AI

| Tech | Purpose |
|------|---------|
| XGBoost | Gradient boosting (best on tabular data) |
| Scikit-learn | Model evaluation, preprocessing |
| Pandas / NumPy | Data manipulation |
| Joblib | Model serialization (.pkl) |
| Google Gemini | LLM-powered recommendations |
| Open-Meteo | Free weather API |
| GBIF | Free bee occurrence data |

### Deployment (All Free)

| Platform | What |
|----------|------|
| Netlify | Frontend hosting (free tier) |
| Render | Backend hosting (free tier) |
| Supabase | PostgreSQL database (free tier) |
| GitHub | Code + CI + project board |

---

## 4. Team Roles

| Member | Role | Responsibilities |
|--------|------|-----------------|
| **Member 1** | Team Lead + DevOps | GitHub setup, Vercel/Render deploy, integration testing, documentation |
| **Member 2** | Frontend Developer | All React pages, dashboard, charts, maps, API wiring, responsive design |
| **Member 3** | Backend Developer | FastAPI, SQLite, auth, weather API, bee API, feature engineering, prediction endpoints |
| **Member 4** | ML + AI Engineer | Dataset creation, model training, model packaging, LLM prompt engineering |

### Cross-Training Expectations

- Everyone can run the full app locally by Week 1.
- If someone is sick, another person can deploy.
- Member 1 helps everyone with Git issues.
- Member 3 and Member 4 work closely on model serving.
- Member 2 and Member 3 agree on API contracts before coding.

---

## 5. Phase 1: Hackathon MVP

### Goal

A working web app where a user selects a crop and location, the system fetches real data, runs ML models, and shows a dashboard with predictions and AI recommendations.

### What Judges Will See

Landing page → Login/Register → Add Farm → Predict → Dashboard with PSI gauge, weather cards, flowering calendar, bee map, and AI recommendation. Clean, professional UI with real weather data for any location in India.

### What We Skip for Hackathon

- Real-time satellite NDVI (use seasonal average)
- Google Pollen API (use estimated seasonal data)
- Complex caching (simple SQLite cache table)
- Background jobs (fetch on-demand)
- Advanced auth (email/password only)
- Mobile app, admin dashboard

---

## 6. Phase 2: Main Project Polish

If selected, we add:

1. PostgreSQL migration (NeonDB free tier) + Alembic migrations
2. Redis caching (Upstash free tier) for API responses
3. Celery for background data fetching
4. Google Pollen API (if access granted)
5. Real NDVI from Sentinel-2 via Google Earth Engine
6. ChromaDB + RAG for better recommendations
7. More crops (15+ instead of 5)
8. Yield prediction as stretch goal
9. PWA for mobile-like experience
10. IoT integration (stretch goal)

---

## 7. Module A: Infrastructure & DevOps

**Owner:** Member 1

### A.1 GitHub Setup (Day 1)

- Create repo with `main` + `test` branches
- Protect main: require PR reviews, dismiss stale approvals
- Create `.gitignore` (Node + Python templates)
- Add all team members as collaborators
- Create initial README with project name and tech stack

**Success:** Everyone can clone, push, and create PRs.

### A.2 Deployment Setup (Day 2-3)

**Frontend (Netlify):**
- Connect repo to Netlify, base dir: `frontend`, build: `npm run build`, publish: `dist`
- Set env vars: `VITE_API_URL`, `VITE_FIREBASE_*`
- Add `netlify.toml` for SPA routing redirect
- Auto-deploys on push to main

**Backend (Render):**
- Connect repo to Render, service type: Web Service, root dir: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set env vars: `SECRET_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`, `FIREBASE_*`, `SUPABASE_*`, `CORS_ORIGINS`, `FRONTEND_ORIGIN`
- Auto-deploy on push to main

**Success:** Frontend shows landing page. Backend Swagger UI at `/docs`.

### A.3 CI/CD (Day 4)

GitHub Actions workflow runs on every push/PR:
- Frontend: `npm run build`
- Backend: `pytest`

See `.github/workflows/ci.yml`.

**Success:** Every PR shows green checkmark.

### A.4 Documentation (Ongoing)

- `README.md` — project overview, quick start
- `docs/ARCHITECTURE.md` — system design
- `docs/SETUP.md` — local dev setup
- `docs/PLAYBOOK.md` — this document

**Success:** A new person can set up the project in 10 minutes using only the docs.

### A.5 Integration Testing (Week 2)

- Test full flow on deployed app: Register → Login → Add Farm → Predict → Dashboard
- Check all API endpoints via Swagger UI
- Verify frontend-backend CORS works
- Test on mobile browser
- Prepare 3 demo scenarios: happy path, medium risk, map demo

**Success:** Demo runs smoothly without errors.

---

## 8. Module B: Frontend

**Owner:** Member 2

### B.1 Project Setup & Design System (Day 1-2)

- Confirm structure: `src/pages/`, `src/components/`, `src/context/`, `src/lib/`
- Tech stack: React + Vite + Tailwind + Axios + React Router + Chart.js + Leaflet
- Use design assets in `frontend/stitch_pollisync_saas_design_system/`
- Validate with `npm install && npm run dev`

**Success:** Frontend starts, design folder is referenced.

### B.2 Authentication Pages (Day 3)

- `AuthContext.jsx` — login/register/logout, JWT in localStorage
- `LoginPage.jsx` — email + password form → `POST /auth/login`
- `RegisterPage.jsx` — email, password, name → `POST /auth/register` → auto-login
- `ProtectedRoute.jsx` — redirects to /login if no token
- Axios interceptor in `lib/api.js` — attaches `Authorization: Bearer <token>`

**Success:** Can register, login, and see token in localStorage.

### B.3 Landing Page (Day 4)

- Hero section: headline, subheadline, CTA → `/register`
- Features section: 3 cards (Flowering Forecasts, Pollination Score, AI Advice)
- Supported crops grid: Mustard, Wheat, Sunflower, Rice, Cotton
- Footer with team name and GitHub link

**Success:** Looks good on mobile and desktop. CTA routes correctly.

### B.4 Prediction Input Page (Day 5-6)

- Crop selection dropdown (5 options)
- Location selection (text input or dropdown of 20 major districts)
- Submit → `POST /predictions` with `{ crop, lat, lng }`
- Loading spinner with messages: "Fetching weather...", "Analyzing crop health...", "Consulting the AI..."
- On success: redirect to `/dashboard?farm_id={id}`

**Success:** Can select crop + location, submit, see loading state.

### B.5 Dashboard Page (Day 7-10)

This is the most important page. Make it beautiful.

Widgets:
- **PSI Gauge** — Circular progress, color: red <40, yellow 40-70, green >70
- **Weather Cards** — 4 small cards: Temperature, Humidity, Rainfall, Wind
- **Flowering Calendar** — Date range + confidence badge + progress bar
- **Pollen Bars** — Horizontal bar chart (Chart.js)
- **Recommendation Card** — Markdown rendering, "Generated by AI" badge
- **NDVI Card** — Big number + health label
- **Bee Map** — Leaflet map with red markers, 10km radius circle

Data source: `GET /api/dashboard/summary?farm_id={id}`

**Success:** Dashboard looks like a professional SaaS product with real data.

### B.6 Charts & Visualization (Day 11)

- `WeatherTrendChart.jsx` — 7-day temperature line chart
- `PSIHistoryChart.jsx` — PSI over time (multiple predictions)
- Custom Chart.js colors matching Tailwind theme

**Success:** Charts are responsive and styled.

### B.7 Responsive & Polish (Day 12-13)

- Mobile: sidebar → hamburger menu, single column grid
- Loading: skeleton components for all widgets
- Error: "Failed to load data. Retry?" button
- Empty: "No predictions yet. Create one!" with CTA
- Toast notifications for success/error

**Success:** App works on phone browser. No broken layouts.

---

## 9. Module C: Backend

**Owner:** Member 3

### C.1 FastAPI Project Setup (Day 1)

Create modular structure:

```
backend/app/
├── main.py          Entry point, CORS, router mounting
├── database.py      SQLAlchemy engine, Base, init_db
├── auth.py          JWT utilities, password hashing
├── core/config.py   Settings from environment
├── api/routes/      11 route groups
├── models/          8 SQLAlchemy ORM models
├── schemas/         Pydantic validation schemas
├── services/        Business logic layer
└── agent/           Gemini LLM integration
```

See `backend/requirements.txt` for the 17 dependencies.

**Success:** `uvicorn app.main:app --reload` starts. Swagger UI at `/docs`.

### C.2 Database & Models (Day 2)

8 tables via SQLAlchemy ORM:
- `users` — email, hashed_password, full_name
- `farms` — user_id, name, crop_type, location_lat, location_lng
- `predictions` — farm_id, flowering dates, PSI score, risk level, weather/bees/recommendation (JSON)
- `weather_cache` — farm_id, temperature, humidity, rainfall, wind_speed, timestamp
- `bee_occurrences` — farm_id, species_name, lat, lng, observation_date
- `team_members` — farm_id, name, role
- `notifications` — user_id, title, message, read status
- `notification_preferences` — user_id, notification settings

Tables auto-create on startup via `Base.metadata.create_all()`.

**Success:** `pollisync.db` created. Inspectable with DB Browser for SQLite.

### C.3 Authentication (Day 3)

- `POST /auth/register` — hash password, create user, return JWT
- `POST /auth/login` — verify password, return JWT
- `GET /auth/me` — decode JWT, return user profile
- JWT tokens: access (short-lived) + refresh (long-lived)
- Password hashing: bcrypt via passlib

**Success:** Can register and login via Swagger UI.

### C.4 Weather API Integration (Day 4)

- Service: `weather_service.py` — fetches from Open-Meteo API
- Router: `GET /weather/current?farm_id=1` — returns temperature, humidity, rainfall, wind
- Router: `GET /weather/forecast?farm_id=1&days=7` — returns daily forecast array
- Cache: SQLite `weather_cache` table, 1-hour TTL
- Free tier: no API key required

**Success:** Returns real weather data for Nashik.

### C.5 GBIF Bee Data Integration (Day 5)

- Service: `bee_service.py` — queries GBIF occurrence API
- Router: `GET /maps/bees?farm_id=1&radius=10` — returns species with coordinates
- Mock fallback: if GBIF is slow or empty, returns crop-specific bee species
- Cache: SQLite `bee_occurrences` table, 1-week TTL

**Success:** Bee endpoint returns species list. Map markers display correctly.

### C.6 Feature Engineering (Day 6)

- Service: `feature_engineering.py`
- Builds 24-dim feature vector: weather + crop one-hots + ecological + interaction terms
- Seasonal pollen lookup table (no Google Pollen API for MVP)

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full feature list.

**Success:** Feature dict has consistent keys. Convertible to DataFrame row.

### C.7 Prediction Endpoints (Day 7-8)

- Service: `prediction_service.py` — loads .pkl models, runs inference
- Router: `POST /predictions` — full pipeline: fetch data → features → models → LLM → store → return
- Router: `GET /predictions?farm_id=1` — return prediction history
- Scaler transform applied before model inference

**Success:** `POST /predictions` returns flowering window, PSI, risk, and recommendation in <3 seconds.

### C.8 AI Recommendation (Day 9)

- Service: Uses Google Gemini via `google-genai` library
- Router: `POST /recommendations/generate` — structured data → natural language advice
- Prompt template in `backend/app/agent/assistant_template.txt`
- Local fallback when API key is not configured

**Success:** Recommendation generated in <2 seconds. Specific to crop and conditions.

### C.9 Dashboard Aggregation (Day 10)

- Router: `GET /dashboard/summary?farm_id=1` — returns single JSON with farm, weather, prediction, bee species
- Router: `GET /dashboard/trends?farm_id=1` — returns array of past predictions for charts

**Success:** Single endpoint returns everything frontend needs.

### C.10 NDVI & Mock Data (Day 11)

- Service: `environment_service.py`
- Primary: NASA POWER API for vegetation index
- Fallback: crop + month lookup table for typical NDVI values
- NDVI value displayed as "Healthy" (>0.6), "Moderate" (0.4-0.6), or "Poor" (<0.4)

**Success:** NDVI value returned. Frontend displays correctly.

---

## 10. Module D: ML & AI

**Owner:** Member 4

### D.1 Dataset Creation (Day 1-3)

**Flowering dataset** (`ml/data/flowering_data.csv`):
- 4000 synthetic records using GDD phenology model
- Crops: Mustard, Wheat, Sunflower, Rice, Cotton
- Regions: Nashik, Punjab, Haryana, Gujarat, Madhya Pradesh
- Features: temperature, humidity, rainfall, NDVI, day-of-year, month
- Target: flowering start day-of-year

**PSI dataset** (`ml/data/psi_data.csv`):
- 4000 synthetic records with scoring rubric
- Wind penalties, abundance scaling, interaction effects
- Target: PSI score (0-100) and risk level (Low/Medium/High)

**Success:** 2 CSV files with 4000 rows each. Realistic distributions.

### D.2 Model 1 — Flowering Prediction (Day 4-5)

- Algorithm: XGBoost Regressor (tuned via GridSearchCV)
- Features: 24-dim feature vector
- Target: day-of-year for flowering start
- Performance: R²=0.9997 on test, MAE=0.6 days
- Saved as: `ml/models/flowering_model.pkl`

See `ml/src/train_improved_models.py` for training code.

**Success:** Model saved. R² > 0.99.

### D.3 Model 2 — PSI Prediction (Day 6-7)

- Algorithm: XGBoost Regresser (tuned)
- Target: PSI score (0-100)
- Performance: R²=0.988 on test, MAE=2.4
- Saved as: `ml/models/psi_model.pkl`

**Success:** Model saved. PSI RMSE < 5 points.

### D.4 Risk Model (Day 7)

- Algorithm: XGBoost Classifier
- Target: Risk level (Low/Medium/High)
- Performance: 98.4% accuracy
- Saved as: `ml/models/risk_model.pkl`

**Success:** Model saved. Accuracy > 95%.

### D.5 Model Packaging (Day 8)

- `ml/predict.py` — standalone prediction interface
- Loads all 3 models, applies scaler transform, returns structured output
- Baseline fallback: if models fail to load, returns default values

See `backend/app/services/prediction_service.py` for backend integration.

**Success:** Backend can call `predict()` with a feature dict.

### D.6 Feature Engineering v2 (Day 8)

- 17 base features + 7 interaction terms
- Interaction terms: temp_humidity, temp_ndvi, humidity_rainfall, bee_pollen, ndvi_bee, wind_humidity, crop_temp
- V2 models saved separately as `*_v2.pkl`

**Success:** V2 models outperform V1 on all targets.

### D.7 Hyperparameter Tuning (Day 8)

- GridSearchCV for RandomForest and XGBoost
- Best RF params: `max_depth=None, min_samples_leaf=2, n_estimators=300`
- XGBoost selected over RandomForest on all 3 targets

**Success:** Tuning complete. Best params documented.

### D.8 Ensemble Models (Day 9)

- Stacking ensemble: XGBoost + RandomForest + GradientBoosting
- R²=0.9997 on synthetic data
- Quantile regression for 80% prediction intervals
- Interval width: 11 days, coverage: 78%

See `ml/src/train_ensemble.py`.

**Success:** Ensemble saved. Uncertainty intervals available.

### D.9 LLM Prompt Engineering (Day 9)

- Template saved in `backend/app/agent/assistant_template.txt`
- Tested with 5 scenarios: high/medium/low PSI, different crops, edge cases
- Outputs: specific to crop, actionable, under 200 words

**Success:** 5 test cases produce good recommendations.

### D.10 Regression Tests (Day 10)

52 automated tests in `ml/src/test_regression.py`:
- Model loading and inference
- Feature alignment (correct dimensions)
- Prediction bounds (PSI 0-100, flowering in valid range)
- Physical sanity (warmer = earlier flowering, NDVI affects PSI)
- Sensitivity analysis (matches GDD expectations)

**Success:** All 52 tests pass.

### D.11 Validation Report (Day 10)

- Real data validation: R²=0.924, MAE=15.2 days
- 93.6% MAE improvement over naive baseline
- All physical sanity checks pass
- Cross-validation R²=0.9977 on synthetic data

See `ml/src/comprehensive_validation.py`.

**Success:** Report is honest about limitations but shows solid methodology.

---

## 11. Database Schema

8 SQLite tables managed by SQLAlchemy ORM. See `backend/app/models/` for column definitions.

**Key relationships:**
- User → Farms (one-to-many)
- Farm → Predictions (one-to-many)
- Farm → WeatherCache (one-to-many)
- Farm → BeeOccurrences (one-to-many)

**Predictions table** stores the full result snapshot: flowering dates, PSI score, risk level, weather summary (JSON), pollen summary (JSON), NDVI value, bee species (JSON), and recommendation text.

See `backend/app/models/` for the full SQLAlchemy model definitions. The backend runs schema reconciliation on startup to handle table evolution.

---

## 12. API Contract

All endpoints are under `/api`. See the auto-generated Swagger UI at `/api/docs` for interactive testing.

### Auth

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/auth/register` | `{email, password, full_name}` | `{user, access_token}` |
| POST | `/api/auth/login` | `{email, password}` | `{access_token, user}` |
| GET | `/api/auth/me` | — | `{id, email, full_name}` |

### Farms

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/farms` | `{name, crop_type, location_lat, location_lng}` | `{id, name, ...}` |
| GET | `/api/farms` | — | `{farms: [...]}` |

### Weather

| Method | Endpoint | Query Params | Response |
|--------|----------|-------------|----------|
| GET | `/api/weather/current` | `farm_id` | `{temperature, humidity, rainfall, wind_speed}` |
| GET | `/api/weather/forecast` | `farm_id, days` | `{forecast: [{date, temp_max, temp_min, rainfall}]}` |

### Predictions

| Method | Endpoint | Body/Query | Response |
|--------|----------|-----------|----------|
| POST | `/api/predictions` | `{farm_id}` | Full prediction object |
| GET | `/api/predictions` | `farm_id` | `{predictions: [...]}` |

### Dashboard

| Method | Endpoint | Query | Response |
|--------|----------|-------|----------|
| GET | `/api/dashboard/summary` | `farm_id` | `{farm, weather, prediction, bees}` |

### Maps

| Method | Endpoint | Query | Response |
|--------|----------|-------|----------|
| GET | `/api/maps/bees` | `farm_id, radius` | `{center, occurrences: [{species, lat, lng}]}` |

### Recommendations

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/recommendations/generate` | `{farm_id, prediction_id}` | `{recommendation: "markdown text"}` |

### Agent

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/agent/chat` | `{message}` | `{response: "markdown text"}` |

---

## 13. AI/ML Architecture

### For Hackathon (MVP)

```
User Input → Feature Engineering → XGBoost Models → Structured JSON
                                              │
                                              ▼
                                    Direct Gemini API Call
                                    (Good prompt + structured data)
                                              │
                                              ▼
                                    Natural Language Recommendation
```

**Why this works:** No vector database, no document ingestion, no retrieval logic. Just a good prompt and an API call. Takes 1 day to implement vs. 1 week for RAG.

### For Main Project (if selected)

```
User Input → Feature Engineering → ML Models → Structured JSON
                                              │
                                              ▼
                                    ChromaDB RAG Retrieval
                                    (Crop guides, best practices)
                                              │
                                              ▼
                                    Better Recommendation
```

---

## 14. Workflow & Tools

### Daily Workflow

```
09:00  Discord standup (15 min): What did you do? What will you do? Blockers?
09:15  Work on your module
13:00  Lunch break
14:00  Work on your module
17:00  Push code, create PR if ready
18:00  Optional pair programming / debugging
20:00  Update GitHub Project board
```

### GitHub Project Board (Kanban)

Columns: Backlog → To Do → In Progress → In Review → Done

### Free Resources

| Resource | What | Link |
|----------|------|------|
| Netlify | Frontend hosting | netlify.com |
| Render | Backend hosting | render.com |
| Open-Meteo | Weather API | open-meteo.com |
| Gemini | LLM API | ai.google.dev |
| Supabase | PostgreSQL + vector store | supabase.com |
| Firebase | Authentication | firebase.google.com |
| shadcn/ui | UI components | ui.shadcn.com |
| Figma | UI design (free student) | figma.com |
| Notion | Documentation | notion.so |

---

## 15. Roadmap

### Phase 1: Hackathon MVP

| Day | Member 1 | Member 2 | Member 3 | Member 4 |
|-----|----------|----------|----------|----------|
| 1 | GitHub setup, invite team | React + Vite + Tailwind setup | FastAPI scaffold | Dataset research |
| 2 | Vercel + Render accounts | Design system init, folder structure | SQLite models | Start flowering dataset |
| 3 | CI/CD setup | Auth pages (login/register) | Auth endpoints (JWT) | Complete flowering dataset |
| 4 | Help debug | Landing page design | Weather API (Open-Meteo) | Start PSI dataset |
| 5 | Integration testing plan | Prediction form | GBIF bee API | Complete PSI dataset |
| 6 | Help debug | Dashboard layout + sidebar | Feature engineering function | Train flowering model |
| 7 | Deploy check | PSI Gauge component | Prediction endpoint skeleton | Train PSI model |
| 8 | Help debug | Weather cards + Pollen bars | Prediction endpoint (full) | Model evaluation |
| 9 | Help debug | Flowering calendar + Bee map | AI recommendation endpoint | LLM prompt engineering |
| 10 | Integration test | NDVI card + Recommendation card | Dashboard aggregation | Model packaging |
| 11 | Integration test | Charts (weather trend, PSI history) | NDVI integration / mock | ML evaluation report |
| 12 | Integration test | Responsive design + loading states | CORS fix, API polish | Help with prompt refinement |
| 13 | Full end-to-end test | Polish UI, animations | Backend deploy to Render | Copy models to backend |
| 14 | Bug fixes, performance | Bug fixes, mobile testing | Bug fixes, API optimization | Demo script preparation |
| 15 | **SUBMISSION** | **SUBMISSION** | **SUBMISSION** | **SUBMISSION** |

### Phase 2: Main Project

| Week | Focus | Deliverables |
|------|-------|-------------|
| 4 | PostgreSQL migration, Redis, Celery | Production database, background jobs |
| 5 | Real NDVI, Google Pollen API, more crops | Satellite integration, 10+ crops |
| 6 | ChromaDB + RAG, advanced agent | Knowledge base, better recommendations |
| 7 | Testing, PWA, mobile optimization | Full test suite, PWA manifest |
| 8 | Final polish, presentation | Demo video, final submission |

---

## 16. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenAI API costs / no free tier | Medium | High | Use Gemini free tier. Have fallback prompt template. |
| Render free tier sleeps | High | Medium | Ping every 10 min to keep warm. Wake up 2min before demo. |
| Model performs poorly | Medium | High | Frame as "prototype needing real data." Use synthetic data smartly. |
| Team member busy with exams | High | High | Cross-train early. Member 1 knows deploy. Member 3 knows models. |
| CORS errors | High | Low | Test frontend-backend connection on Day 3. Fix immediately. |
| GBIF API slow/empty for India | Medium | Medium | Have mock bee data ready. Show real API call in code. |
| Feature creep | High | High | Stick to this document. No new features after Day 10. |
| SQLite file lost on Render | Medium | High | Seed database on startup. Migrate to PostgreSQL for main project. |

---

## 17. Deployment Checklists

### Render (Backend)

- [ ] GitHub repo connected to Render Web Service, root dir: `backend`
- [ ] Build: `pip install -r requirements.txt`
- [ ] Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Env vars: `SECRET_KEY`, `GEMINI_API_KEY`, `LLM_API_KEY`, `DATABASE_URL`, `FIREBASE_PROJECT_ID`, `FIREBASE_SERVICE_ACCOUNT_JSON`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`, `CORS_ORIGINS`, `FRONTEND_ORIGIN`, `APP_ENV=production`
- [ ] Auto-deploy on push to `main`

### Netlify (Frontend)

- [ ] GitHub repo connected to Netlify
- [ ] Base directory: `frontend`
- [ ] Build: `npm run build`
- [ ] Publish: `dist`
- [ ] `netlify.toml` present with SPA redirect rule
- [ ] Env vars: `VITE_API_URL`, `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`
- [ ] Auto-deploy on push to `main`

---

*Document Version: Student Edition 2.0*
*Last Updated: 20 July 2026*
*Target Audience: 4 SY CSE-AI Students*
