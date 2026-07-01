# PolliSync setup

## Prerequisites

- Git 2.40 or newer
- Node.js 20 or newer
- Python 3.11 or newer
- GitHub CLI for publishing and repository administration

## Clone and configure

    git clone https://github.com/sairaj2832-star/Pollysync.git
    cd Pollysync

Create local environment files only when defaults need to change:

    Copy-Item frontend\.env.example frontend\.env
    Copy-Item backend\.env.example backend\.env

Never commit real API keys or deployment secrets.

## Backend

    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
    Set-Location backend
    ..\.venv\Scripts\python.exe -m pytest
    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

## Frontend

    Set-Location frontend
    npm install
    npm run build
    npm run dev

## Team branch workflow

1. Start work from the current test branch.
2. Use a short feature branch for substantial changes when collaboration begins.
3. Integrate and validate changes on test.
4. Update main from test only after CI and manual smoke checks pass.
5. Deploy production from main.

Never force-push main or test. If main and test diverge, stop and resolve the history intentionally rather than overwriting either branch.

## Secrets expected later

- SECRET_KEY for backend authentication
- GEMINI_API_KEY for recommendations
- VITE_API_URL for the deployed backend URL

Weather from Open-Meteo and occurrence data from GBIF do not require API keys for the planned MVP.
