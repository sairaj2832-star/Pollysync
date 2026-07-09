# PolliSync — Hackathon & Main Project Engineering Playbook

> **AI-Based Crop Pollination Suitability System**  
> **Team:** 4 SY CSE-AI Students  
> **Hackathon MVP Deadline:** 15 July 2026  
> **Main Project Deadline:** 8 August 2026  
> **Version:** Student Edition (Realistic & Achievable)

---

## Table of Contents

1. [Reality Check & Philosophy](#1-reality-check--philosophy)
2. [Simplified System Architecture](#2-simplified-system-architecture)
3. [Tech Stack (Student-Friendly & Free)](#3-tech-stack-student-friendly--free)
4. [Team Roles for 4 SY Students](#4-team-roles-for-4-sy-students)
5. [Phase 1: Hackathon MVP (Now -> 15 July)](#5-phase-1-hackathon-mvp-now--15-july)
6. [Phase 2: Main Project Polish (16 July -> 8 August)](#6-phase-2-main-project-polish-16-july--8-august)
7. [Module A: Infrastructure & DevOps](#7-module-a-infrastructure--devops)
8. [Module B: Frontend](#8-module-b-frontend)
9. [Module C: Backend](#9-module-c-backend)
9.1 [AI Agent Work Plan: Backend + ML Setup](#ai-agent-work-plan-backend--ml-setup)
10. [Module D: ML & AI](#10-module-d-ml--ai)
11. [Database Schema (SQLite -> PostgreSQL)](#11-database-schema-sqlite--postgresql)
12. [API Contract (MVP Version)](#12-api-contract-mvp-version)
13. [AI/ML Simplified Architecture](#13-aiml-simplified-architecture)
14. [Student Workflow & Free Tools](#14-student-workflow--free-tools)
15. [Roadmap & Day-by-Day Plan](#15-roadmap--day-by-day-plan)
16. [Risk Register (Student Edition)](#16-risk-register-student-edition)
17. [Appendices](#17-appendices)

---

## 1. Reality Check & Philosophy

### What This Document Is
This is a **battle-tested, student-realistic** engineering plan. We are 4 Second-Year CSE-AI students. We do not have 2 years of DevOps experience. We do not have corporate cloud budgets. We have **2 weeks for a hackathon MVP** and **3 more weeks for the main project**.

### Core Principles
1. **Ship what works.** A working SQLite app beats a broken PostgreSQL microservices architecture.
2. **Free tools only.** No paid APIs, no paid hosting tiers for MVP.
3. **Copy-paste is okay.** Use shadcn/ui, use templates, use boilerplate. Hackathons reward working demos, not handwritten CSS.
4. **One person, one domain.** Do not make everyone learn everything. Own your module.
5. **Demo-first thinking.** Every week's output must be demo-able to a non-technical judge.

### What We Are NOT Building (For Now)
- X Docker, Kubernetes, microservices
- X Redis, Celery, RabbitMQ
- X MLflow, Kubeflow, complex MLOps
- X LangChain, LangGraph, ChromaDB (for hackathon -- we use direct LLM API calls)
- X PostgreSQL with PostGIS (SQLite for MVP, upgrade later)
- X Google Maps API (costs money -- use Leaflet + OpenStreetMap)
- X Google Pollen API (hard to get access -- use seasonal mock/estimated data for MVP)
- X Real-time satellite NDVI from Sentinel-2 (complex auth -- use NASA POWER vegetation index or mock for MVP)

### What We ARE Building
- [x] React + Tailwind frontend on Vercel
- [x] FastAPI + SQLite backend on Render
- [x] Scikit-learn / XGBoost models (train locally, deploy as pickle files)
- [x] Open-Meteo weather API (free, no key)
- [x] GBIF bee data API (free, no key)
- [x] Direct LLM API calls (OpenAI/Claude/Groq) for recommendations
- [x] Leaflet maps (free)
- [x] A dashboard that looks professional and demo-ready

---

## 2. Simplified System Architecture

```
+-------------------------------------------------------------+
|                        USER LAYER                            |
|  +--------------+  +--------------+  +--------------------+  |
|  |   Landing    |  |   Predict    |  |     Dashboard      |  |
|  |   Page       |  |   Page       |  |  (Weather/PSI/Map) |  |
|  +--------------+  +--------------+  +--------------------+  |
|                      React + Vite                            |
+------------------------------+------------------------------+
                               | HTTPS
                               v
+-------------------------------------------------------------+
|                     FASTAPI BACKEND                          |
|  +-------------+  +-------------+  +---------------------+ |
|  |   Auth      |  |  Weather    |  |   Predictions       | |
|  |  (JWT)      |  |  Router     |  |  (Flowering + PSI)  | |
|  +-------------+  +-------------+  +---------------------+ |
|  +-------------+  +-------------+  +---------------------+ |
|  |   Maps      |  |  Bees       |  |  AI Recommendations | |
|  |  Router     |  |  Router     |  |  (Direct LLM Call) | |
|  +-------------+  +-------------+  +---------------------+ |
+------------------------------+------------------------------+
                               |
           +-------------------+-------------------+
           |                   |                   |
           v                   v                   v
+-----------------+  +-----------------+  +---------------------+
|   SQLite DB     |  |  EXTERNAL APIs  |  |    ML MODELS      |
|  (Single File)  |  |  (Free Tier)    |  |  (Pickle Files)   |
|                 |  |                 |  |                   |
|  - users        |  |  Open-Meteo     |  |  flowering_model  |
|  - farms        |  |  (Weather)      |  |  psi_model        |
|  - predictions  |  |                 |  |                   |
|  - weather_cache|  |  GBIF           |  |  OpenAI/Groq      |
|  - bees         |  |  (Bee Data)     |  |  (LLM API)        |
+-----------------+  +-----------------+  +---------------------+
```

### Data Flow (Simplified)
```
User selects Crop + Location
    |
    v
Backend fetches Weather from Open-Meteo (cached 1 hour)
Backend fetches Bee data from GBIF (cached 1 week)
Backend loads NDVI from NASA POWER or uses mock/seasonal data
    |
    v
Feature Engineering (Python function, 15 features)
    |
    v
Model 1 (Flowering): Predicts date range
Model 2 (PSI): Predicts 0-100 score + Risk Level
    |
    v
LLM API Call: Structured data -> Natural language recommendation
    |
    v
Dashboard displays everything
```

---

## 3. Tech Stack (Student-Friendly & Free)

### Frontend

| Tech | Why | Learning Curve |
|------|-----|----------------|
| **React 18** | You probably already know it | Low |
| **Vite** | Faster than CRA, instant HMR | Low |
| **Tailwind CSS** | Write styles fast without leaving HTML | Low |
| **shadcn/ui** | Copy-paste beautiful components (no npm install needed) | Low |
| **Chart.js** | Simple, well-documented charts | Low |
| **React-Leaflet** | Free maps, easy to use | Low |
| **Axios** | HTTP requests with interceptors | Low |
| **React Context** | Global state (no Redux/Zustand needed for MVP) | Low |

### Backend

| Tech | Why | Learning Curve |
|------|-----|----------------|
| **FastAPI** | Python, auto-docs, async support, easy to learn | Medium |
| **SQLite** | Zero setup, single file, perfect for student projects | None |
| **SQLAlchemy** | ORM -- write Python, not SQL | Medium |
| **Pydantic** | Data validation built into FastAPI | Low |
| **python-jose** | JWT tokens for auth | Low |
| **bcrypt** | Password hashing | Low |
| **Uvicorn** | Run FastAPI server | None |

### ML & AI

| Tech | Why | Learning Curve |
|------|-----|----------------|
| **Scikit-learn** | You learned this in class -- Random Forest, metrics | Low |
| **XGBoost** | Better performance, still easy to use | Medium |
| **Pandas / NumPy** | Standard data tools | Low |
| **Joblib** | Save/load models as .pkl files | None |
| **OpenAI API** | Direct API call for recommendations (no LangChain needed) | Low |
| **Open-Meteo** | Free weather data, no API key, generous limits | None |
| **GBIF API** | Free bee occurrence data | Low |

### Deployment (All Free)

| Platform | What | Why |
|----------|------|-----|
| **Vercel** | Frontend hosting | Zero config for React, free, custom domain support |
| **Render** | Backend hosting | Free tier for FastAPI, auto-deploy from GitHub |
| **SQLite** | Database | File-based, deploy alongside backend on Render |
| **GitHub** | Code + CI + Project Board | Free, built-in Projects board (simpler than Jira) |

### Project Management (Free & Simple)

| Tool | Use |
|------|-----|
| **GitHub Projects** | Kanban board (simpler than Jira, integrated with repo) |
| **Notion** | Documentation, notes, meeting minutes |
| **Discord / WhatsApp** | Daily communication |
| **Figma** | UI design (free student plan) |
| **Google Sheets** | Dataset tracking, task checklist |

---

## 4. Team Roles for 4 SY Students

| Member | Role | What You Actually Do | What You Need to Know |
|--------|------|---------------------|----------------------|
| **Member 1** | **Team Lead + DevOps** | GitHub setup, Vercel/Render deploy, integration testing, README, documentation, helps everyone debug | Git, GitHub Actions basics, how to read logs |
| **Member 2** | **Frontend Developer** | All React pages, dashboard, charts, maps, API wiring, making it look beautiful | React, Tailwind, Chart.js, Axios |
| **Member 3** | **Backend Developer** | FastAPI, SQLite database, auth, weather API, bee API, feature engineering, prediction endpoints | Python, FastAPI basics, SQLAlchemy, REST APIs |
| **Member 4** | **ML + AI Engineer** | Dataset creation, model training (2 models), saving models, LLM prompt engineering, recommendation generation | Scikit-learn, XGBoost, Pandas, how to call an API |

### Important: Cross-Training
- Everyone should be able to run the full app locally by Week 1.
- If someone is sick, another person can deploy.
- Member 1 helps everyone with Git issues.
- Member 3 and Member 4 work closely on model serving.
- Member 2 and Member 3 agree on API contracts before coding.

---

## 5. Phase 1: Hackathon MVP (Now -> 15 July)

### Goal
A working web app that:
1. User selects **Crop** and **Location**
2. Backend fetches **weather** and **bee data**
3. ML models predict **flowering window** and **PSI score**
4. LLM generates a **recommendation**
5. Dashboard displays everything with **charts and maps**
6. Deployed and demo-ready

### What Judges Will See
- Landing page -> Login/Register -> Add Farm -> Predict -> Dashboard with PSI gauge, weather cards, flowering calendar, bee map, and AI recommendation
- Clean UI that looks professional
- Real weather data for any location in India
- A recommendation that actually mentions the crop and weather

### What We Skip for Hackathon
- Real-time satellite NDVI (use seasonal average or NASA POWER API)
- Google Pollen API (use estimated seasonal pollen data by region)
- Complex caching (simple in-memory dict or SQLite cache table)
- Background jobs (fetch data on-demand when user clicks Predict)
- Advanced auth (email/password is enough, skip OAuth)
- Mobile app
- Admin dashboard

---

## 6. Phase 2: Main Project Polish (16 July -> 8 August)

### If Selected, We Add:
1. **PostgreSQL migration** (NeonDB free tier) + proper migrations (Alembic)
2. **Redis caching** (Upstash free tier) for API responses
3. **Celery** for background data fetching (keep data fresh)
4. **Google Pollen API** (if we get access by then)
5. **Real NDVI** from Sentinel-2 via Google Earth Engine
6. **ChromaDB + RAG** for better recommendations (replace direct LLM with knowledge base)
7. **More crops** (train on 15+ crops instead of 5)
8. **More models** (add yield prediction as stretch goal)
9. **PWA** (Progressive Web App) for mobile-like experience
10. **IoT integration** (stretch -- if hardware available)

---

## 7. Module A: Infrastructure & DevOps (Member 1)

### Task A.1: GitHub Setup (Day 1)
**Steps:**
1. Create GitHub organization or use one person's account.
2. Create 2 repositories:
   - `polli-sync-web` (Frontend)
   - `polli-sync-api` (Backend + ML models)
3. Add all 4 members as collaborators (Settings -> Manage Access).
4. Create `main` branch and protect it (Settings -> Branches -> Add rule):
   - Require pull request reviews before merging
   - Dismiss stale PR approvals
5. Create `.gitignore` for both repos (use GitHub templates for Node and Python).
6. Create a simple `README.md` in each repo with project name and tech stack.

**Success:** Everyone can clone, push, and create PRs.

---

### Task A.2: Deployment Setup (Day 2-3)
**Steps:**
1. **Frontend (Vercel):**
   - Connect `polli-sync-web` repo to Vercel (vercel.com, login with GitHub).
   - Framework preset: Vite.
   - Environment variable: `VITE_API_URL=https://polli-sync-api.onrender.com` (we will update this after backend deploy).
   - Every push to `main` auto-deploys.
2. **Backend (Render):**
   - Connect `polli-sync-api` repo to Render (render.com).
   - Service type: Web Service.
   - Runtime: Python 3.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables: Add `SECRET_KEY`, `OPENAI_API_KEY` (if using).
   - Free tier: Web Service sleeps after 15 min inactivity (cold start ~30s -- acceptable for demo).
3. **SQLite on Render:**
   - SQLite file lives in repo or is created on first run.
   - Warning: Render free tier has ephemeral filesystem -- data may reset on redeploy.
   - **Hackathon fix:** Seed database on startup if empty. For main project, migrate to PostgreSQL.
4. **Custom domain (optional):**
   - Vercel gives free `.vercel.app` domain.
   - Render gives free `.onrender.com` domain.

**Success:** `https://polli-sync-web.vercel.app` shows landing page. `https://polli-sync-api.onrender.com/docs` shows FastAPI Swagger UI.

---

### Task A.3: CI/CD (Optional but Impressive) (Day 4)
**Steps:**
1. Add GitHub Actions workflow for backend:
   ```yaml
   # .github/workflows/test.yml
   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with: { python-version: '3.11' }
         - run: pip install -r requirements.txt
         - run: pytest
   ```
2. Add frontend lint check (optional).

**Success:** Every PR shows green checkmark.

---

### Task A.4: Documentation & README (Ongoing)
**Steps:**
1. Write `README.md` for backend with:
   - How to run locally: `pip install -r requirements.txt && uvicorn app.main:app --reload`
   - API endpoints list
   - Environment variables needed
2. Write `README.md` for frontend with:
   - How to run: `npm install && npm run dev`
   - Tech stack
3. Create `SETUP.md` with:
   - How to get OpenAI API key (if using)
   - How to add env vars in Render/Vercel
4. Create a demo script (`DEMO_SCRIPT.md`) for hackathon presentation:
   - Step-by-step what to click
   - What to say for each screen
   - Expected outputs

**Success:** A new person can set up the project in 10 minutes using only the README.

---

### Task A.5: Integration Testing (Week 2)
**Steps:**
1. Test full flow on deployed app:
   - Register -> Login -> Add Farm (Nashik, Mustard) -> Predict -> View Dashboard
2. Check all API endpoints via Swagger UI (`/docs`).
3. Verify frontend-backend connection (CORS must work).
4. Test on mobile browser.
5. Prepare 3 demo scenarios:
   - **Happy path:** Nashik + Mustard -> High PSI -> Good recommendation
   - **Medium risk:** Location with moderate weather -> Medium PSI -> Cautionary recommendation
   - **Map demo:** Show bee occurrences around farm

**Success:** Demo runs smoothly without errors. No "let me refresh and try again."

---

## 8. Module B: Frontend Engineering (Member 2)

### Task B.1: Project Setup & Design System (Day 1-2)
**Steps:**
1. Confirm the existing frontend repo structure in `frontend/src`:
   - `App.jsx`
   - `pages/HomePage.jsx`, `pages/LoginPage.jsx`, `pages/RegisterPage.jsx`, `pages/PredictPage.jsx`, `pages/DashboardPage.jsx`
   - `components/PSIgauge.jsx`, `components/WeatherCard.jsx`, `components/PollenBar.jsx`, `components/FloweringCalendar.jsx`, `components/RecommendationCard.jsx`, `components/NDVICard.jsx`, `components/BeeMap.jsx`, `components/Layout.jsx`, `components/ProtectedRoute.jsx`, `components/LoadingSkeleton.jsx`
   - `context/AuthContext.jsx`
   - `hooks/useApi.js`
   - `lib/api.js`
2. Keep the tech stack as decided:
   - React + Vite
   - Tailwind CSS
   - Axios
   - React Router DOM
   - Chart.js / react-chartjs-2
   - Leaflet + React-Leaflet
   - Optional shadcn/ui for shared UI components
3. Use the existing design assets in `frontend/stitch_pollisync_saas_design_system/` for landing page, login, registration, dashboard, and prediction flows.
4. Confirm `tailwind.config.js` and `postcss.config.js` are set up for Vite and that Tailwind content paths include `./src/**/*.{js,ts,jsx,tsx}`.
5. Validate the project with the real frontend files:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
   - Open `http://localhost:5173`

**Success:** The frontend project starts using the actual repo files, the design folder is referenced, and the agreed tech stack is preserved.

---

### Task B.2: Authentication Pages (Day 3)
**Steps:**
1. Create `AuthContext.jsx`:
   ```jsx
   // Simple context, no Redux needed
   const AuthContext = createContext();
   export const AuthProvider = ({ children }) => {
     const [user, setUser] = useState(null);
     const [token, setToken] = useState(localStorage.getItem('token'));
     // login, logout, register functions
     return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>;
   };
   ```
2. Create `LoginPage.jsx`:
   - Email + password form
   - On submit: `POST /auth/login` -> save token -> redirect to `/dashboard`
3. Create `RegisterPage.jsx`:
   - Email, password, full name, farm name, location
   - On submit: `POST /auth/register` -> auto-login -> redirect
4. Create `ProtectedRoute` wrapper:
   - If no token, redirect to `/login`
5. Add Axios interceptor in `lib/api.js`:
   ```js
   const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });
   api.interceptors.request.use((config) => {
     const token = localStorage.getItem('token');
     if (token) config.headers.Authorization = `Bearer ${token}`;
     return config;
   });
   ```

**Success:** Can register, login, and see token in localStorage. Protected routes work.

---

### Task B.3: Landing Page (Day 4)
**Steps:**
1. Hero section:
   - Big headline: "Know Before Your Crops Flower"
   - Subheadline: "AI-powered pollination forecasts for Indian farmers"
   - CTA button: "Get Started" -> `/register`
   - Background: Use a free Unsplash image of mustard field or gradient
2. Features section (3 cards with icons):
   - "Flowering Forecasts" -- Calendar icon
   - "Pollination Score" -- Shield/check icon
   - "AI Advice" -- Sparkles icon
3. Supported crops grid: Mustard, Wheat, Sunflower, Rice, Cotton (use emojis or free icons)
4. Simple footer with team name and GitHub link.

**Success:** Page looks good on mobile and desktop. CTA buttons route correctly.

---

### Task B.4: Prediction Input Page (Day 5-6)
**Steps:**
1. Create `/predict` route.
2. Step 1: Crop selection dropdown.
   - Options: Mustard, Wheat, Sunflower, Rice, Cotton
   - Use shadcn Select component
3. Step 2: Location selection.
   - Text input with autocomplete (hardcode 50 Indian cities for MVP)
   - OR: Lat/Lng input with "Use Map" button
   - For hackathon: simple dropdown of 20 major agricultural districts
4. Step 3: Submit button.
   - On click: `POST /predictions` with `{ crop, lat, lng }`
   - Show loading spinner with fun messages:
     - "Fetching weather data..."
     - "Analyzing crop health..."
     - "Consulting the AI..."
5. On success: redirect to `/dashboard?farm_id=123`

**Success:** Can select crop + location, submit, and see loading state.

---

### Task B.5: Dashboard Page (Day 7-10)
**This is the most important page. Make it beautiful.**

**Layout:**
```
+---------------------------------------------+
|  Sidebar: Logo, Dashboard, Predict, Logout   |
+---------------------------------------------+
|  Top: Farm Name + Crop Badge                 |
+---------------------------------------------+
|  +-------------+  +-------------+  +------+ |
|  |  PSI Gauge  |  |  Weather    |  | Risk | |
|  |   (big)     |  |  (4 cards)  |  |Badge | |
|  +-------------+  +-------------+  +------+ |
|  +-----------------+  +-----------------+   |
|  | Flowering Window|  |   Pollen Bars   |   |
|  |  (Date range)   |  |  (Chart.js)     |   |
|  +-----------------+  +-----------------+   |
|  +-----------------------------------------+ |
|  |  AI Recommendation Card (Markdown)       |
|  +-----------------------------------------+ |
|  +-----------------+  +-----------------+   |
|  |   NDVI Value    |  |   Bee Map       |   |
|  |  (Number +      |  |  (Leaflet)      |   |
|  |   health text)  |  |                 |   |
|  +-----------------+  +-----------------+   |
+---------------------------------------------+
```

**Implementation:**
1. `PSIGauge.jsx`:
   - Circular progress using CSS or a simple Chart.js doughnut
   - Color: red <40, yellow 40-70, green >70
   - Big number in center
2. `WeatherCard.jsx`:
   - 4 small cards: Temperature, Humidity, Rainfall, Wind
   - Show current values + small trend arrow (up/down from yesterday)
3. `FloweringCalendar.jsx`:
   - Simple card showing: "Predicted Window: 18 Jan - 25 Jan"
   - Confidence badge: "87% confident"
   - Progress bar showing days until flowering
4. `PollenBar.jsx`:
   - Horizontal bar chart (Chart.js) showing tree/grass/weed pollen indices
5. `RecommendationCard.jsx`:
   - White card with left border colored by risk level
   - Render Markdown text (use `react-markdown` or simple formatting)
   - Show "Generated by AI" badge with sparkle icon
6. `NDVICard.jsx`:
   - Big number: "0.82"
   - Label: "Crop Health: Healthy"
   - Small text: "Based on satellite imagery"
7. `BeeMap.jsx`:
   - Leaflet map centered on farm
   - Red markers for bee observations
   - Popup shows species name
   - 10km radius circle
8. `DashboardPage.jsx`:
   - Fetch data on mount: `GET /dashboard/summary?farm_id={id}`
   - Pass data to all child components
   - Loading skeletons while fetching

**Success:** Dashboard looks like a professional SaaS product. All widgets display real data from backend.

---

### Task B.6: Charts & Visualization (Day 11)
**Steps:**
1. `WeatherTrendChart.jsx`:
   - Line chart: 7-day temperature forecast
   - Data from `GET /weather/forecast?days=7`
2. `PSIHistoryChart.jsx`:
   - Line chart showing PSI over time (if user has multiple predictions)
3. Configure Chart.js with custom colors matching Tailwind theme.

**Success:** Charts are responsive and look good.

---

### Task B.7: Responsive & Polish (Day 12-13)
**Steps:**
1. Mobile responsive:
   - Sidebar becomes top navbar or hamburger menu
   - Grid becomes single column on mobile
   - Charts resize correctly
2. Loading states:
   - Use shadcn Skeleton components for all widgets
3. Error states:
   - "Failed to load data. Retry?" button
4. Empty states:
   - "No predictions yet. Create one!" with CTA
5. Add toast notifications for success/error (use shadcn Toast or simple library).

**Success:** App works on phone browser. No broken layouts.

---

## 9. Module C: Backend Engineering (Member 3)

### Task C.1: FastAPI Project Setup (Day 1)
**Steps:**
1. Create project structure:
   ```
   polli-sync-api/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── config.py
   │   ├── database.py
   │   ├── models.py
   │   ├── schemas.py
   │   ├── routers/
   │   │   ├── auth.py
   │   │   ├── farms.py
   │   │   ├── weather.py
   │   │   ├── predictions.py
   │   │   ├── recommendations.py
   │   │   └── maps.py
   │   └── services/
   │       ├── weather_service.py
   │       ├── feature_engineering.py
   │       └── prediction_service.py
   ├── models/              # ML pickle files
   │   ├── flowering_model.pkl
   │   └── psi_model.pkl
   ├── data/                # CSV datasets
   ├── requirements.txt
   └── README.md
   ```
2. `requirements.txt`:
   ```
   fastapi==0.111.0
   uvicorn[standard]==0.30.0
   sqlalchemy==2.0.31
   pydantic==2.7.4
   pydantic-settings==2.3.4
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   python-multipart==0.0.9
   httpx==0.27.0
   pandas==2.2.2
   scikit-learn==1.5.0
   xgboost==2.1.0
   joblib==1.4.2
   openai==1.35.0
   ```
3. `main.py`:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from app.routers import auth, farms, weather, predictions, recommendations, maps

   app = FastAPI(title="PolliSync API", version="1.0.0")

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://polli-sync-web.vercel.app", "http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   app.include_router(auth.router, prefix="/auth", tags=["auth"])
   app.include_router(farms.router, prefix="/farms", tags=["farms"])
   app.include_router(weather.router, prefix="/weather", tags=["weather"])
   app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
   app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
   app.include_router(maps.router, prefix="/maps", tags=["maps"])

   @app.get("/health")
   def health():
       return {"status": "ok"}
   ```

**Success:** `uvicorn app.main:app --reload` starts server. `http://localhost:8000/docs` shows Swagger UI.

---

### Task C.2: Database & Models (Day 2)
**Use SQLite. Zero setup.**

**Steps:**
1. `database.py`:
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker

   SQLALCHEMY_DATABASE_URL = "sqlite:///./pollisync.db"
   engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   Base = declarative_base()
   ```
2. `models.py` (simplified for MVP):
   ```python
   from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
   from sqlalchemy.sql import func
   from app.database import Base

   class User(Base):
       __tablename__ = "users"
       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True)
       hashed_password = Column(String)
       full_name = Column(String)
       created_at = Column(DateTime(timezone=True), server_default=func.now())

   class Farm(Base):
       __tablename__ = "farms"
       id = Column(Integer, primary_key=True, index=True)
       user_id = Column(Integer, index=True)
       name = Column(String)
       crop_type = Column(String)
       location_lat = Column(Float)
       location_lng = Column(Float)
       created_at = Column(DateTime(timezone=True), server_default=func.now())

   class WeatherCache(Base):
       __tablename__ = "weather_cache"
       id = Column(Integer, primary_key=True, index=True)
       farm_id = Column(Integer, index=True)
       temperature = Column(Float)
       humidity = Column(Float)
       rainfall = Column(Float)
       wind_speed = Column(Float)
       timestamp = Column(DateTime(timezone=True), server_default=func.now())

   class Prediction(Base):
       __tablename__ = "predictions"
       id = Column(Integer, primary_key=True, index=True)
       farm_id = Column(Integer, index=True)
       flowering_start = Column(String)  # "2026-01-18"
       flowering_end = Column(String)
       flowering_confidence = Column(Float)
       psi_score = Column(Integer)
       risk_level = Column(String)
       weather_summary = Column(JSON)
       pollen_summary = Column(JSON)
       ndvi_value = Column(Float)
       bee_species = Column(JSON)
       recommendation = Column(Text)
       created_at = Column(DateTime(timezone=True), server_default=func.now())

   class BeeOccurrence(Base):
       __tablename__ = "bee_occurrences"
       id = Column(Integer, primary_key=True, index=True)
       species_name = Column(String)
       lat = Column(Float)
       lng = Column(Float)
       observation_date = Column(String)
       farm_id = Column(Integer, index=True)
   ```
3. Create tables on startup:
   ```python
   # In main.py or database.py
   Base.metadata.create_all(bind=engine)
   ```

**Success:** `pollisync.db` file created. Can inspect with DB Browser for SQLite.

---

### Task C.3: Authentication (Day 3)
**Steps:**
1. `schemas.py`:
   ```python
   from pydantic import BaseModel, EmailStr

   class UserCreate(BaseModel):
       email: EmailStr
       password: str
       full_name: str

   class UserLogin(BaseModel):
       email: EmailStr
       password: str

   class UserOut(BaseModel):
       id: int
       email: str
       full_name: str

   class Token(BaseModel):
       access_token: str
       token_type: str = "bearer"
   ```
2. `auth.py` router:
   - `POST /auth/register` -- hash password with bcrypt, create user, return token
   - `POST /auth/login` -- verify password, return JWT token
   - `GET /auth/me` -- decode JWT, return user
3. JWT utility:
   ```python
   from jose import jwt
   SECRET_KEY = "your-secret-key-change-in-production"
   ALGORITHM = "HS256"

   def create_token(data: dict):
       return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

   def decode_token(token: str):
       return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   ```
4. Dependency for protected routes:
   ```python
   def get_current_user(token: str = Header(...)):
       payload = decode_token(token)
       return payload.get("sub")
   ```

**Success:** Can register and login via Swagger UI. Token works on protected endpoints.

---

### Task C.4: Weather API Integration (Day 4)
**Use Open-Meteo (FREE, no API key).**

**Steps:**
1. `weather_service.py`:
   ```python
   import httpx

   async def fetch_weather(lat: float, lng: float):
       url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
       async with httpx.AsyncClient() as client:
           resp = await client.get(url)
           return resp.json()
   ```
2. `weather.py` router:
   - `GET /weather/current?farm_id=1`
     - Check SQLite cache (if <1 hour old, return cached)
     - Else fetch from Open-Meteo, store in DB, return
   - `GET /weather/forecast?farm_id=1&days=7`
     - Return daily forecast array
3. Cache logic (simple):
   ```python
   # Check if we have recent data
   recent = db.query(WeatherCache).filter(
       WeatherCache.farm_id == farm_id,
       WeatherCache.timestamp > datetime.now() - timedelta(hours=1)
   ).first()
   if recent:
       return recent
   ```

**Success:** `GET /weather/current?farm_id=1` returns real weather data for Nashik.

---

### Task C.5: GBIF Bee Data Integration (Day 5)
**Steps:**
1. `maps.py` router:
   - `GET /maps/bees?farm_id=1&radius=10`
2. Fetch from GBIF:
   ```python
   url = f"https://api.gbif.org/v1/occurrence/search?taxonKey=4334&decimalLatitude={lat}&decimalLongitude={lng}&distance={radius/111}&limit=100&basisOfRecord=HUMAN_OBSERVATION"
   # Note: GBIF uses degrees for distance, not km. 1 degree ~ 111km.
   ```
3. Parse response:
   - Extract `species`, `decimalLatitude`, `decimalLongitude`, `eventDate`
   - Store in `bee_occurrences` table (deduplicate by species + location)
   - Return grouped by species with counts
4. For hackathon: If GBIF is slow or empty for a location, return mock bee data:
   ```python
   MOCK_BEES = {
       "Mustard": ["Apis cerana", "Apis dorsata", "Apis florea"],
       "Sunflower": ["Apis mellifera", "Bombus taschenbergi"],
   }
   ```

**Success:** Bee endpoint returns species list with counts. Map markers display correctly.

---

### Task C.6: Feature Engineering (Day 6)
**Steps:**
1. `feature_engineering.py`:
   ```python
   def build_features(farm, weather_data, pollen_data, ndvi_value, bee_count):
       features = {
           'temp_7d_mean': weather_data['temperature'],
           'humidity': weather_data['humidity'],
           'rainfall_7d': weather_data['rainfall'],
           'wind_speed': weather_data['wind_speed'],
           'ndvi': ndvi_value,
           'day_of_year': datetime.now().timetuple().tm_yday,
           'month': datetime.now().month,
           'crop_mustard': 1 if farm.crop_type == 'Mustard' else 0,
           'crop_wheat': 1 if farm.crop_type == 'Wheat' else 0,
           'crop_sunflower': 1 if farm.crop_type == 'Sunflower' else 0,
           'crop_rice': 1 if farm.crop_type == 'Rice' else 0,
           'crop_cotton': 1 if farm.crop_type == 'Cotton' else 0,
           'bee_richness': bee_count,
           'pollen_tree': pollen_data.get('tree', 2),
           'pollen_grass': pollen_data.get('grass', 2),
           'pollen_weed': pollen_data.get('weed', 2),
       }
       return features
   ```
2. For pollen data (since we do not have Google Pollen API for hackathon):
   - Use seasonal lookup table by region and month:
   ```python
   SEASONAL_POLLEN = {
       "January": {"tree": 3, "grass": 1, "weed": 2},
       "February": {"tree": 4, "grass": 2, "weed": 3},
       # ... etc
   }
   ```

**Success:** Feature dict has 15 consistent keys. Can be converted to DataFrame row.

---

### Task C.7: Prediction Endpoints (Day 7-8)
**Steps:**
1. `prediction_service.py`:
   ```python
   import joblib
   import pandas as pd

   flowering_model = joblib.load("models/flowering_model.pkl")
   psi_model = joblib.load("models/psi_model.pkl")

   def predict_flowering(features):
       df = pd.DataFrame([features])
       start_doy = flowering_model.predict(df)[0]
       # Add 7 days for end date
       end_doy = start_doy + 7
       return start_doy, end_doy

   def predict_psi(features):
       df = pd.DataFrame([features])
       score = int(psi_model.predict(df)[0])
       score = max(0, min(100, score))
       if score >= 70: risk = "Low"
       elif score >= 40: risk = "Medium"
       else: risk = "High"
       return score, risk
   ```
2. `predictions.py` router:
   - `POST /predictions` -> Body: `{ farm_id }`
     - Fetch farm, weather, bees
     - Build features
     - Call both models
     - Call recommendation generation
     - Store everything in `predictions` table
     - Return full result
   - `GET /predictions?farm_id=1` -> Return latest prediction

**Success:** `POST /predictions` returns flowering window, PSI, risk, and recommendation in <3 seconds.

---

### Task C.8: AI Recommendation (Day 9)
**Direct LLM API call. No LangChain. No RAG. Just a good prompt.**

**Steps:**
1. `recommendations.py` router:
   - `POST /recommendations/generate` -> Body: `{ farm_id, prediction_id }`
2. Build prompt:
   ```python
   import openai

   def generate_recommendation(farm, weather, psi_score, risk_level, flowering_window, bee_species):
       prompt = f"""You are an expert agronomist advising Indian farmers.

   Farm Details:
   - Crop: {farm.crop_type}
   - Location: {farm.location_lat}, {farm.location_lng}

   Current Conditions:
   - Temperature: {weather['temperature']} C
   - Humidity: {weather['humidity']}%
   - Rainfall: {weather['rainfall']}mm
   - Wind: {weather['wind_speed']}km/h

   Predictions:
   - Flowering Window: {flowering_window['start']} to {flowering_window['end']}
   - Pollination Suitability Index: {psi_score}/100
   - Risk Level: {risk_level}
   - Nearby Bee Species: {', '.join(bee_species)}

   Write a concise, actionable recommendation (max 200 words) in markdown format with:
   1. A brief assessment
   2. 2-3 specific actions the farmer should take
   3. Any warnings if risk is Medium or High
   4. End with a confidence statement

   Be practical. Mention the crop by name."""

       client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",  # Cheaper than GPT-4, good enough
           messages=[
               {"role": "system", "content": "You are a helpful agronomist."},
               {"role": "user", "content": prompt}
           ],
           temperature=0.7,
           max_tokens=300
       )
       return response.choices[0].message.content
   ```
3. **Free alternative if no OpenAI budget:**
   - Use **Groq API** (free tier, fast, uses Llama 3): https://console.groq.com/
   - Or use **Google Gemini API** (free tier available)
   - Or use **Ollama** locally with a small model (but needs GPU/compute)

**Success:** Recommendation is generated in <2 seconds. Text is specific to the crop and conditions.

---

### Task C.9: Dashboard Aggregation (Day 10)
**Steps:**
1. `GET /dashboard/summary?farm_id=1`
   - Query latest prediction from DB
   - Query latest weather from DB
   - Query bee species from DB
   - Return single JSON object
2. `GET /dashboard/trends?farm_id=1`
   - Return array of past predictions for charts

**Success:** Single endpoint returns everything frontend needs.

---

### Task C.10: NDVI & Mock Data Handling (Day 11)
**For hackathon, use NASA POWER API or simple NDVI estimation:**

**Steps:**
1. Try NASA POWER API:
   ```python
   url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=EVLAND&community=AG&longitude={lng}&latitude={lat}&start=20260101&end=20260115&format=JSON"
   ```
   - `EVLAND` is vegetation index. Scale to 0-1.
2. If API is complex or unreliable for hackathon:
   - Use crop + month lookup table for typical NDVI:
   ```python
   TYPICAL_NDVI = {
       "Mustard": {"January": 0.75, "February": 0.82},
       "Wheat": {"January": 0.65, "February": 0.70},
   }
   ```
   - Add note: "Using regional average NDVI. Real-time satellite integration coming in main project."

**Success:** NDVI value returned. Frontend shows "Healthy" or "Moderate" based on value.

---

## AI Agent Work Plan: Backend + ML Setup

This section is written as a practical step-by-step agent workflow for a new teammate or AI assistant who is setting up the backend and ML model stack from the repository.

### Goal
- Get the backend running locally.
- Confirm backend API contracts work.
- Build or load ML models and connect them to the prediction endpoints.
- Validate the full backend + model prediction workflow.

### Step 1: Prepare the environment
1. Clone or pull the latest repo:
   - `git pull origin main`
2. Open the workspace at `d:\Pollysync`.
3. Create and activate a Python virtual environment:
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
4. Install backend dependencies:
   - `cd backend`
   - `pip install -r requirements.txt`

### Step 2: Verify backend file structure
The agent should confirm these files exist:
- `backend/app/main.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routers/auth.py`
- `backend/app/routers/weather.py`
- `backend/app/routers/predictions.py`
- `backend/app/routers/maps.py`
- `backend/app/routers/recommendations.py`
- `backend/app/services/feature_engineering.py`
- `backend/app/services/prediction_service.py`
- `backend/models/flowering_model.pkl`
- `backend/models/psi_model.pkl`

If any file is missing, the agent should create it from the project template or restore it from the repository.

### Step 3: Confirm model artifacts or train them
1. Check whether `backend/models/flowering_model.pkl` and `backend/models/psi_model.pkl` exist.
2. If models are missing, run the training scripts or notebook helper scripts in `backend/ml` or `ml/src`.
   - Example training commands:
     - `python backend/ml/train_flowering.py`
     - `python backend/ml/train_psi.py`
3. Ensure the agent saves outputs to:
   - `backend/models/flowering_model.pkl`
   - `backend/models/psi_model.pkl`
4. Run a quick local model test in Python:
   ```python
   from joblib import load
   import pandas as pd

   flowering = load('backend/models/flowering_model.pkl')
   psi = load('backend/models/psi_model.pkl')
   sample = pd.DataFrame([{
       'temp_7d_mean': 28,
       'humidity': 65,
       'rainfall_7d': 12,
       'ndvi': 0.72,
       'day_of_year': 15,
       'month': 1,
       'crop_mustard': 1,
       'crop_wheat': 0,
       'crop_sunflower': 0,
       'crop_rice': 0,
       'crop_cotton': 0,
       'bee_richness': 4,
       'pollen_tree': 3,
       'pollen_grass': 2,
       'pollen_weed': 2,
   }])
   print('flowering start', flowering.predict(sample))
   print('psi score', psi.predict(sample))
   ```
5. If this test works, the model setup is valid.

### Step 4: Configure backend secrets and CORS
1. Create or update a `.env` file or use environment variables:
   - `SECRET_KEY=your-secret-key`
   - `OPENAI_API_KEY=your-openai-api-key` (optional)
2. Confirm `backend/app/main.py` has CORS origins for local frontend and production:
   - `http://localhost:5173`
   - `https://polli-sync-web.vercel.app`
   - Add the deployed backend origin if needed.
3. Confirm `backend/app/database.py` uses SQLite path:
   - `sqlite:///./pollisync.db`
   - This allows `pollisync.db` to be created automatically on first run.

### Step 5: Run the backend locally and verify endpoints
1. Start the server:
   - `cd backend`
   - `uvicorn app.main:app --reload`
2. Open `http://localhost:8000/docs`.
3. Verify the following endpoints exist and respond:
   - `GET /health`
   - `POST /auth/register`
   - `POST /auth/login`
   - `GET /weather/current?farm_id=1`
   - `GET /weather/forecast?farm_id=1&days=7`
   - `POST /predictions`
   - `GET /dashboard/summary?farm_id=1`
   - `GET /maps/bees?farm_id=1&radius=10`
4. If the API fails, inspect the server logs and fix the import or dependency issue.

### Step 6: Validate prediction flow end to end
1. Create a user via `/auth/register`.
2. Create a farm via `/farms` or the appropriate farm endpoint.
3. Call `POST /predictions` with the new `farm_id`.
4. Confirm the response contains:
   - `flowering_start`
   - `flowering_end`
   - `psi_score`
   - `risk_level`
   - `weather_summary`
   - `pollen_summary`
   - `ndvi_value`
   - `bee_species`
   - `recommendation`
5. If recommendation generation is disabled because of missing API keys, verify the fallback text or mock output path.

### Step 7: Document exact setup commands
Add a short setup checklist to `backend/README.md` so any teammate can follow it verbatim:
- `cd backend`
- `python -m venv .venv`
- `.\.venv\Scripts\Activate.ps1`
- `pip install -r requirements.txt`
- `uvicorn app.main:app --reload`
- open `http://localhost:8000/docs`

### Success Criteria for AI Agent
- Backend starts cleanly with `uvicorn`.
- SQLite database file is created automatically.
- ML models load from `backend/models` and return valid predictions.
- Core backend APIs respond correctly.
- A full prediction call returns structured forecast + recommendation.

---

## 10. Module D: ML & AI (Member 4)

### Task D.1: Dataset Creation (Day 1-3)
**Goal: Create synthetic but realistic training data. We do not have 500 real records, so we generate them based on agricultural knowledge.**

**Steps:**
1. **Flowering Dataset** (`data/flowering_data.csv`):
   - Create 300 synthetic records using agricultural calendars:
   ```python
   import pandas as pd
   import numpy as np

   crops = ['Mustard', 'Wheat', 'Sunflower', 'Rice', 'Cotton']
   regions = ['Nashik', 'Punjab', 'Haryana', 'Gujarat', 'Madhya Pradesh']

   data = []
   for _ in range(300):
       crop = np.random.choice(crops)
       region = np.random.choice(regions)
       # Base flowering dates by crop
       base_start = {'Mustard': 15, 'Wheat': 45, 'Sunflower': 60, 'Rice': 90, 'Cotton': 120}[crop]
       # Add noise
       start = base_start + np.random.randint(-7, 8)
       end = start + np.random.randint(5, 10)
       temp = np.random.normal(25, 5)
       humidity = np.random.normal(60, 10)
       rainfall = np.random.exponential(10)
       ndvi = np.random.normal(0.7, 0.1)

       data.append({
           'crop': crop, 'region': region, 'start_doy': start, 'end_doy': end,
           'temp_7d_mean': temp, 'humidity': humidity, 'rainfall_7d': rainfall,
           'ndvi': ndvi, 'month': 1, 'day_of_year': start - 5
       })

   df = pd.DataFrame(data)
   df.to_csv('data/flowering_data.csv', index=False)
   ```
   - **Important:** Add 20 real records from ICAR or agricultural university websites for credibility.

2. **PSI Dataset** (`data/psi_data.csv`):
   - Create 300 records with scoring rubric:
   ```python
   for _ in range(300):
       temp = np.random.normal(28, 6)
       humidity = np.random.normal(65, 15)
       rainfall = np.random.exponential(15)
       ndvi = np.random.normal(0.65, 0.15)
       bee_count = np.random.poisson(5)
       pollen = np.random.randint(1, 6)

       # Scoring rubric
       score = 0
       if 20 <= temp <= 32: score += 25
       elif 15 <= temp <= 35: score += 15
       if 50 <= humidity <= 80: score += 20
       elif 30 <= humidity <= 90: score += 10
       if ndvi > 0.6: score += 20
       elif ndvi > 0.4: score += 10
       if bee_count >= 3: score += 15
       elif bee_count >= 1: score += 8
       if pollen >= 3: score += 15
       elif pollen >= 2: score += 8

       score = min(100, score + np.random.randint(-5, 6))
       risk = 'Low' if score >= 70 else 'Medium' if score >= 40 else 'High'

       data.append({...})
   ```

**Success:** 2 CSV files with 300 rows each. Data looks realistic when plotted.

---

### Task D.2: Model 1 -- Flowering Prediction (Day 4-5)
**Steps:**
1. Load `flowering_data.csv`
2. Preprocess:
   - One-hot encode `crop` and `region`
   - Features: `temp_7d_mean`, `humidity`, `rainfall_7d`, `ndvi`, `day_of_year`, `month`, crop_onehots, region_onehots
   - Target: `start_doy` (day of year for flowering start)
3. Train models:
   ```python
   from sklearn.ensemble import RandomForestRegressor
   from xgboost import XGBRegressor
   from sklearn.model_selection import train_test_split
   from sklearn.metrics import mean_squared_error, r2_score

   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   # Random Forest
   rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
   rf.fit(X_train, y_train)

   # XGBoost
   xgb = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42)
   xgb.fit(X_train, y_train)

   # Evaluate
   for model, name in [(rf, 'RF'), (xgb, 'XGB')]:
       preds = model.predict(X_test)
       print(f"{name}: RMSE={mean_squared_error(y_test, preds, squared=False):.2f}, R2={r2_score(y_test, preds):.2f}")
   ```
4. Choose best model. Save with joblib:
   ```python
   import joblib
   joblib.dump(xgb, 'models/flowering_model.pkl')
   ```
5. Create `notebooks/01_flowering_model.ipynb` with:
   - Data exploration plots
   - Feature importance plot (XGBoost `plot_importance`)
   - Actual vs. predicted scatter plot

**Success:** Model saved as `.pkl`. RMSE < 8 days acceptable for hackathon. R2 > 0.60.

---

### Task D.3: Model 2 -- PSI Prediction (Day 6-7)
**Steps:**
1. Load `psi_data.csv`
2. Train regression model for `psi_score`:
   ```python
   # Same approach as Model 1
   xgb_psi = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05)
   xgb_psi.fit(X_train, y_train)
   ```
3. Train classifier for `risk_level`:
   ```python
   from sklearn.ensemble import RandomForestClassifier
   from sklearn.metrics import classification_report, confusion_matrix

   rf_risk = RandomForestClassifier(n_estimators=100, max_depth=8)
   rf_risk.fit(X_train, y_risk_train)
   print(classification_report(y_risk_test, rf_risk.predict(X_test)))
   ```
4. Save both models:
   ```python
   joblib.dump(xgb_psi, 'models/psi_model.pkl')
   joblib.dump(rf_risk, 'models/risk_model.pkl')
   ```
5. Create `notebooks/02_psi_model.ipynb` with evaluation plots.

**Success:** 2 models saved. PSI RMSE < 12 points. Risk accuracy > 75%.

---

### Task D.4: Model Packaging for Backend (Day 8)
**Steps:**
1. Create `ml/predict.py`:
   ```python
   import joblib
   import pandas as pd

   flowering_model = joblib.load('models/flowering_model.pkl')
   psi_model = joblib.load('models/psi_model.pkl')
   risk_model = joblib.load('models/risk_model.pkl')

   def predict(features_dict):
       df = pd.DataFrame([features_dict])
       start_doy = int(flowering_model.predict(df)[0])
       end_doy = start_doy + 7
       psi = int(psi_model.predict(df)[0])
       psi = max(0, min(100, psi))
       risk = risk_model.predict(df)[0]
       return {
           'flowering_start_doy': start_doy,
           'flowering_end_doy': end_doy,
           'psi_score': psi,
           'risk_level': risk
       }
   ```
2. Test with sample input:
   ```python
   test_features = {
       'temp_7d_mean': 29, 'humidity': 68, 'rainfall_7d': 5,
       'ndvi': 0.82, 'day_of_year': 15, 'month': 1,
       'crop_mustard': 1, 'crop_wheat': 0, ...,
       'bee_richness': 2, 'pollen_tree': 4, 'pollen_grass': 2, 'pollen_weed': 3
   }
   print(predict(test_features))
   ```
3. Copy `models/` folder into backend repo.

**Success:** Backend can import and call `predict()` with a feature dict.

---

### Task D.5: LLM Prompt Engineering (Day 9)
**Steps:**
1. Write 5 test prompts with different scenarios:
   - High PSI + Mustard + good weather
   - Medium PSI + Wheat + moderate weather
   - Low PSI + Cotton + poor weather
   - High pollen but low bees
   - Good NDVI but high winds
2. Test with OpenAI/Groq API.
3. Refine system prompt until outputs are:
   - Specific to crop
   - Actionable (has bullet points)
   - Under 200 words
   - Confident but honest
4. Save final prompt template in `ml/prompt_template.txt`.

**Success:** 5 test cases produce good recommendations. Prompt template finalized.

---

### Task D.6: Model Evaluation Report (Day 10)
**Steps:**
1. Create `docs/ML_REPORT.md`:
   - Dataset description (size, sources, synthetic vs. real)
   - Model 1: Algorithm, features, RMSE, R2, feature importance
   - Model 2: Algorithm, features, RMSE, accuracy, confusion matrix
   - Limitations: "Trained on synthetic data, needs real-world validation"
   - Future improvements: More crops, real satellite NDVI, IoT sensors
2. Include screenshots of plots from notebooks.

**Success:** Report is honest about limitations but shows solid methodology.

---

## 11. Database Schema (SQLite -> PostgreSQL)

### MVP Schema (SQLite)

```sql
-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farms
CREATE TABLE farms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    crop_type TEXT NOT NULL,
    location_lat REAL NOT NULL,
    location_lng REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather Cache
CREATE TABLE weather_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id INTEGER NOT NULL,
    temperature REAL,
    humidity REAL,
    rainfall REAL,
    wind_speed REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions (stores everything)
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id INTEGER NOT NULL,
    flowering_start TEXT,
    flowering_end TEXT,
    flowering_confidence REAL,
    psi_score INTEGER,
    risk_level TEXT,
    weather_summary TEXT,  -- JSON as text
    pollen_summary TEXT,   -- JSON as text
    ndvi_value REAL,
    bee_species TEXT,      -- JSON array as text
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bee Occurrences
CREATE TABLE bee_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id INTEGER,
    species_name TEXT,
    lat REAL,
    lng REAL,
    observation_date TEXT
);
```

### Main Project Upgrade (PostgreSQL)
- Add proper foreign keys
- Add indexes
- Split `predictions` into `flowering_predictions`, `psi_predictions`, `recommendations`
- Add `historical_flowering` table
- Add `feature_snapshots` table
- Use PostGIS for geospatial queries

---

## 12. API Contract (MVP Version)

### Auth
```
POST /auth/register
  Body: { email, password, full_name }
  Response: { user, access_token }

POST /auth/login
  Body: { email, password }
  Response: { access_token, user }

GET /auth/me
  Headers: Authorization: Bearer <token>
  Response: { id, email, full_name }
```

### Farms
```
POST /farms
  Body: { name, crop_type, location_lat, location_lng }
  Response: { id, name, crop_type, location_lat, location_lng }

GET /farms
  Response: { farms: [...] }
```

### Weather
```
GET /weather/current?farm_id=1
  Response: { temperature, humidity, rainfall, wind_speed, timestamp }

GET /weather/forecast?farm_id=1&days=7
  Response: { forecast: [{ date, temp_max, temp_min, rainfall }, ...] }
```

### Predictions
```
POST /predictions
  Body: { farm_id }
  Response: {
    farm_id,
    flowering_start: "2026-01-18",
    flowering_end: "2026-01-25",
    flowering_confidence: 0.87,
    psi_score: 91,
    risk_level: "Low",
    weather_summary: { temperature: 29, humidity: 68, ... },
    pollen_summary: { tree: 4, grass: 2, weed: 3 },
    ndvi_value: 0.82,
    bee_species: ["Apis cerana", "Apis dorsata"],
    recommendation: "## Assessment\n..."
  }

GET /predictions?farm_id=1
  Response: { predictions: [...] }
```

### Dashboard
```
GET /dashboard/summary?farm_id=1
  Response: { farm, current_weather, latest_prediction, bee_species }
```

### Maps
```
GET /maps/bees?farm_id=1&radius=10
  Response: { center: { lat, lng }, occurrences: [{ species, lat, lng }, ...] }
```

---

## 13. AI/ML Simplified Architecture

### For Hackathon (15 July)
```
User Input -> Feature Engineering -> Scikit-learn/XGBoost Models -> Structured JSON
                                                    |
                                                    v
                                          Direct OpenAI/Groq API Call
                                          (Good prompt + structured data)
                                                    |
                                                    v
                                          Natural Language Recommendation
```

**Why this works:**
- No vector database to set up
- No document ingestion pipeline
- No retrieval logic to debug
- Just a good prompt and an API call
- Takes 1 day to implement vs. 1 week for RAG

### For Main Project (8 August) -- If Selected
```
User Input -> Feature Engineering -> ML Models -> Structured JSON
                                                    |
                                                    v
                                          ChromaDB RAG Retrieval
                                          (Crop guides, best practices)
                                                    |
                                                    v
                                          LangChain Agent
                                          (Multi-step reasoning)
                                                    |
                                                    v
                                          Better Recommendation
```

---

## 14. Student Workflow & Free Tools

### Daily Workflow
```
09:00 - Discord standup (15 min): What did you do? What will you do? Any blockers?
09:15 - Work on your module
13:00 - Lunch break
14:00 - Work on your module
17:00 - Push your code, create PR if ready
18:00 - Optional pair programming / debugging session
20:00 - Update GitHub Project board
```

### GitHub Project Board (Free Kanban)
Create 5 columns:
1. **Backlog** -- All tasks from this document
2. **To Do** -- Tasks for this week
3. **In Progress** -- Currently working on
4. **In Review** -- PR created, needs review
5. **Done** -- Merged and deployed

### Free Resources
| Resource | What | Link |
|----------|------|------|
| **Vercel** | Frontend hosting | vercel.com |
| **Render** | Backend hosting | render.com |
| **Open-Meteo** | Free weather API | open-meteo.com |
| **GBIF** | Free bee data | gbif.org |
| **Groq** | Free LLM API (Llama 3) | console.groq.com |
| **Google Gemini** | Free LLM API | ai.google.dev |
| **shadcn/ui** | Free UI components | ui.shadcn.com |
| **Unsplash** | Free stock photos | unsplash.com |
| **Flaticon** | Free icons | flaticon.com |
| **Figma** | UI design (free for students) | figma.com |
| **Notion** | Documentation (free) | notion.so |
| **DB Browser** | SQLite GUI | sqlitebrowser.org |

---

## 15. Roadmap & Day-by-Day Plan

### Phase 1: Hackathon MVP (Now -> 15 July)

| Day | Member 1 | Member 2 | Member 3 | Member 4 |
|-----|----------|----------|----------|----------|
| **1** | GitHub setup, invite team | React + Vite + Tailwind setup | FastAPI project scaffold | Dataset research, collect agricultural calendars |
| **2** | Vercel + Render accounts, connect repos | shadcn/ui init, folder structure | SQLite models, database setup | Start synthetic flowering dataset |
| **3** | CI/CD setup (optional) | Auth pages (login/register) | Auth endpoints (JWT) | Complete flowering dataset (300 rows) |
| **4** | Help debug | Landing page design | Weather API (Open-Meteo) | Start PSI dataset |
| **5** | Integration testing plan | Prediction form (crop + location) | GBIF bee API integration | Complete PSI dataset (300 rows) |
| **6** | Help debug | Dashboard layout + sidebar | Feature engineering function | Train Model 1 (Flowering) |
| **7** | Deploy check | PSI Gauge component | Prediction endpoint skeleton | Train Model 2 (PSI) |
| **8** | Help debug | Weather cards + Pollen bars | Prediction endpoint (call models) | Model evaluation, save .pkl files |
| **9** | Help debug | Flowering calendar + Bee map | AI recommendation endpoint (LLM API) | LLM prompt engineering, test 5 scenarios |
| **10** | Integration test | NDVI card + Recommendation card | Dashboard aggregation endpoint | Model packaging for backend |
| **11** | Integration test | Charts (weather trend, PSI history) | NDVI integration / mock data | ML evaluation report |
| **12** | Integration test | Responsive design + loading states | CORS fix, API polish | Help with prompt refinement |
| **13** | Full end-to-end test | Polish UI, animations | Backend deploy to Render | Copy models to backend repo |
| **14** | Bug fixes, performance | Bug fixes, mobile testing | Bug fixes, API optimization | Demo script preparation |
| **15** | **SUBMISSION** | **SUBMISSION** | **SUBMISSION** | **SUBMISSION** |

### Phase 2: Main Project (16 July -> 8 August)

| Week | Focus | Deliverables |
|------|-------|--------------|
| **Week 4** | PostgreSQL migration, Redis caching, Celery | Production database, background jobs |
| **Week 5** | Real NDVI (Sentinel-2), Google Pollen API, more crops | Satellite integration, 10+ crops |
| **Week 6** | ChromaDB + RAG, advanced agent, more models | Knowledge base, better recommendations |
| **Week 7** | Testing, PWA, mobile optimization, docs | Full test suite, PWA manifest |
| **Week 8** | Final polish, presentation, buffer | Demo video, final submission |

---

## 16. Risk Register (Student Edition)

| Risk | Likelihood | Impact | What To Do |
|------|------------|--------|------------|
| **OpenAI API costs / no free tier** | Medium | High | Use Groq (free, fast) or Google Gemini free tier. Have fallback prompt template ready. |
| **Render free tier sleeps** | High | Medium | Keep Render URL warm by pinging every 10 min. For demo, wake it up 2 min before showing. |
| **Model performs poorly** | Medium | High | Use synthetic data smartly. If real accuracy is low, frame it as "prototype needing real data." |
| **Team member busy with exams** | High | High | Cross-train early. Member 1 knows enough to deploy frontend. Member 3 knows enough to run models. |
| **CORS errors** | High | Low | Test frontend-backend connection on Day 3. Fix immediately. |
| **GBIF API slow/empty for Indian locations** | Medium | Medium | Have mock bee data ready. Show real API call in code, mock data in demo if needed. |
| **Feature creep** | High | High | Stick to this document. No new features after Day 10. |
| **SQLite file lost on Render redeploy** | Medium | High | Seed database on startup. For main project, migrate to PostgreSQL. |

---

## 17. Appendices

### Appendix A: Hackathon Demo Script (5 Minutes)

**Slide 1: Problem (30 sec)**
- "Climate change is shifting flowering times. Farmers don't know if pollination conditions will be good."
- "Existing weather apps don't tell you about POLLINATION."

**Slide 2: Solution (30 sec)**
- "PolliSync predicts flowering windows and gives a Pollination Suitability Index."
- "Plus AI-generated advice specific to your crop."

**Demo 1: Register & Add Farm (1 min)**
- "Let me register as a farmer in Nashik growing Mustard."
- [Show registration, add farm with map pin]

**Demo 2: Get Prediction (1.5 min)**
- "I click Predict. The system fetches live weather, analyzes satellite data, and runs our ML models."
- [Show loading screen, then results]
- "Flowering predicted for January 18-25. PSI is 91 -- Low Risk."

**Demo 3: Dashboard (1.5 min)**
- "Here's my dashboard. I can see weather, pollen levels, NDVI crop health, nearby bee species on the map, and the AI recommendation."
- [Scroll through dashboard, highlight map and recommendation]
- "The AI tells me exactly what to do: monitor bee activity, avoid irrigation during peak hours."

**Closing (30 sec)**
- "We built this in 2 weeks. With more time, we'll add real satellite NDVI, IoT sensors, and 15+ crops."
- "Thank you!"

### Appendix B: Free LLM Options (No Credit Card Needed)

| Provider | Free Tier | Model | Speed | Notes |
|----------|-----------|-------|-------|-------|
| **Groq** | $5/month credit | Llama 3, Mixtral | Very fast | Best free option for hackathons |
| **Google Gemini** | 60 requests/min | Gemini 1.5 Flash | Fast | Good quality, easy setup |
| **OpenRouter** | Some free models | Various | Medium | Aggregator, try multiple models |
| **Ollama (local)** | Unlimited | Llama 3, Mistral | Slow (CPU) | Needs 8GB+ RAM, no internet needed |

### Appendix C: Quick SQLite Commands

```bash
# Open database
sqlite3 pollisync.db

# List tables
.tables

# Describe table
.schema predictions

# Query
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 5;

# Exit
.quit
```

### Appendix D: Render Deployment Checklist

- [ ] GitHub repo connected to Render Web Service
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables added: `SECRET_KEY`, `OPENAI_API_KEY` (or `GROQ_API_KEY`)
- [ ] CORS origins include Vercel URL
- [ ] SQLite file path is relative (`./pollisync.db`)
- [ ] Auto-deploy enabled on push to `main`

### Appendix E: Vercel Deployment Checklist

- [ ] GitHub repo connected to Vercel
- [ ] Framework preset: Vite
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Environment variable: `VITE_API_URL=https://your-backend.onrender.com`
- [ ] Auto-deploy on push to `main`

---

*Document Version: Student Edition 1.0*  
*Last Updated: 28 June 2026*  
*Next Review: 5 July 2026*  
*Target Audience: 4 SY CSE-AI Students*  
*Motto: "Ship it. Demo it. Win it."*
