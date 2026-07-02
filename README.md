# PolliSync

PolliSync is an AI-assisted crop pollination suitability system. It combines farm details, weather, vegetation health, and pollinator observations to predict flowering windows, calculate a Pollination Suitability Index (PSI), and produce practical recommendations.

This repository is a student-friendly monorepo for the hackathon MVP described in PolliSync_Student_Hackathon_Playbook.md.

## Repository layout

    .
    |-- frontend/          React 18, Vite, and Tailwind web app
    |-- backend/           FastAPI and SQLite API
    |-- ml/                Data, notebooks, model artifacts, and ML code
    |-- docs/              Setup and architecture notes
    |-- .github/workflows/ Continuous integration
    |-- .claude/agents/    Reusable repository setup agent
    |-- PolliSync_Student_Hackathon_Playbook.md

## Branch model

- main is the production-ready branch.
- test is the shared integration branch and recovery point before production.
- Changes should reach test first. After validation passes, main is fast-forwarded from test.

Git history and remote hosting remain the actual backup. The test branch is best treated as staging/integration rather than as the only backup.

## Quick start

### Backend

From the repository root:

    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
    cd backend
    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

Open http://localhost:8000/docs. The health endpoint is http://localhost:8000/api/health.

### Frontend

In another terminal:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173.

Copy frontend/.env.example to frontend/.env only when you need to change the local API URL. Copy backend/.env.example to backend/.env before adding secrets.

## Validation

    cd frontend
    npm run build

    cd backend
    ..\.venv\Scripts\python.exe -m pytest

See docs/SETUP.md for the complete setup and team workflow.

## Current starter scope

The MVP code now provides:

- a responsive React landing page, auth flow, prediction form, dashboard, and map components;
- a central API client boundary for future frontend work;
- FastAPI auth, farms, weather, predictions, recommendations, maps, dashboard, and health endpoints;
- SQLite persistence with SQLAlchemy;
- backend API coverage for auth, farms, weather, predictions, and dashboard summary;
- ML data, training scripts, model loading hooks, and baseline prediction fallback;
- CI checks for frontend builds and backend tests.

Live weather and GBIF integrations have local fallbacks so the demo can still run when a free external API is slow or unavailable. Deployment to Vercel/Render still needs project-specific account setup and production environment variables.
