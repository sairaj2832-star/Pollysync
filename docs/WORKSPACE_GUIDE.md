# PolliSync Repository Workspace & Integration Guide

This guide provides a comprehensive, file-by-file blueprint of the four main folders of the PolliSync workspace: **Frontend**, **Backend**, **Machine Learning**, and **Documentation**. 

---

## Workspace Directory Tree Overview

```
PolliSync Repository
├── backend/                  # FastAPI web server and database configurations
│   ├── app/
│   │   ├── agent/            # LLM Agricultural Advisory Agent & prompts
│   │   ├── api/routes/       # Core REST API endpoints (auth, farms, team, recs)
│   │   ├── core/             # Application config and settings
│   │   ├── models/           # SQLAlchemy DB models (Users, Farms, Rate Limits)
│   │   ├── schemas/          # Pydantic schemas for data serialization
│   │   ├── services/         # ML prediction and weather environment services
│   │   ├── auth.py           # Password hashing, JWT creation & blacklisting, CSRF check
│   │   ├── database.py       # SQLAlchemy engine & SQLite schema migration logic
│   │   └── main.py           # FastAPI server initializer & security header middlewares
│   └── tests/                # Pytest suite
│       └── test_api.py       # API authentication, IDOR, CSRF, and lockout tests
│
├── frontend/                 # React client built with Vite & Tailwind CSS
│   ├── src/
│   │   ├── components/       # Custom visual components (ProtectedRoutes)
│   │   ├── context/          # React Auth Context (session management)
│   │   ├── lib/              # API interfaces (api.js) & Geocoding Nominatim APIs
│   │   └── pages/            # Page layouts (HomePage, ChatPage, Login, Register)
│   ├── tailwind.config.js    # Tailwind color, spacing, and typography configuration
│   └── vite.config.js        # Vite bundling configurations
│
├── ml/                       # Machine Learning models, training pipelines, & notebooks
│   ├── data/                 # Raw and processed datasets (GBIF, weather, NDVIs)
│   ├── models/               # Serialized classifier model binaries (.pkl)
│   └── src/                  # Pipelines for feature engineering and model training
│
└── docs/                     # Guides and submission references for developers
    ├── ARCHITECTURE.md       # High-level data flows and interaction diagrams
    ├── DEMO_SCRIPT.md        # Scenario walkthrough guide for recording demos
    ├── SETUP.md              # Installation details for local setup
    └── WORKSPACE_GUIDE.md    # This integration guide file
```

---

## 1. Backend Core Architecture (`/backend`)

The backend functions as the centralized controller. It acts as the interface between the relational database, local machine learning models, external weather data, and the LLM agent.

| File Path | Description | Key Security / Design Role |
| :--- | :--- | :--- |
| [main.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/main.py) | Entry point for FastAPI application. | Configures CORS, mounts endpoints, and registers the **Security Headers Middleware** (`X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`). |
| [auth.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/auth.py) | Cryptography and session validation engine. | Generates JWT credentials containing a unique token ID (`jti`), enforces stateless access token database revocation checks upon user logouts, and implements **Double-Submit Cookie CSRF validation** checks. |
| [database.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/database.py) | SQLite engine configuration. | Instantiates SQLAlchemy sessions. Contains compile-time DDL parameters in `reconcile_sqlite_schema()` to dynamically apply missing database columns (avoiding raw SQL parsing injections). |

### Backend Subdirectory Breakdown

#### A. DB Models (`app/models/`)
*   [user.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/models/user.py): Defines the `User` model with additional safety columns: `failed_login_attempts` and `lockout_until` for lockout protections.
*   [revoked_token.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/models/revoked_token.py): Relational table storing blacklisted token unique identifiers (`jti`) after logouts.
*   [agent_rate_limit.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/models/agent_rate_limit.py): Enforces database-backed rate-limiting counters for LLM prompts to prevent server exploitation.
*   `farm.py`, `team_member.py`, `bee_occurrence.py`, `prediction.py`, `notification.py`: Map core entity relationship graphs for farm details, coordinates, crop indicators, and alerts.

#### B. API Endpoints (`app/api/routes/`)
*   [auth.py (routes)](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/api/routes/auth.py): Implements sign-ups, log-ins, session fetching, and logouts. Enforces account lockouts (15 minutes lockout if login fails 5 consecutive times) and token invalidations.
*   [team.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/api/routes/team.py): Manages team invitations. Secured against IDOR (Insecure Direct Object Reference) hazards by restricting action parameters using farm-ownership authorization checks.
*   [recommendations.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/api/routes/recommendations.py): Proxies prompt routing using secure headers to pass keys instead of vulnerable URL strings.

#### C. Predictions & Environment (`app/services/`)
*   [prediction_service.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/services/prediction_service.py): Lazy-loads model binaries (`.pkl`) on demand. Hardened against path traversal LFI/RCE by verifying that resolved path prefixes reside within the local `ml/models` directory.
*   `environment_service.py`: Interfaces with the Open-Meteo and Sentinel-2 APIs to fetch localized weather coordinates and NDVI greenness ratios.

#### D. Conversational Agent (`app/agent/`)
*   [router.py](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/agent/router.py): Handles `/api/agent/chat` queries. Filters out common prompt-injection/jailbreak override strings (e.g. `"ignore previous instructions"`), wraps user messages inside `<user_question>` tags, and enforces rate limit rules.
*   [system_prompt.txt](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/backend/app/agent/system_prompt.txt): Instructions guiding the LLM's personality constraints (formatting, bullet responses, risk levels, and ignore rules for text inside `<user_question>` bounds).

---

## 2. Frontend SPA Framework (`/frontend`)

The frontend React application is structured to deliver responsive, secure, and visually interactive client-side interfaces.

```
frontend/src/
├── components/
│   └── ProtectedRoute.jsx   # Redirects unauthenticated sessions to /login
├── context/
│   └── AuthContext.jsx      # Manages user state, login tokens, and cookie lifecycle
├── lib/
│   ├── api.js               # Global Axios config (enables cookies and credentials)
│   └── location.js          # nominatim geocode lookup with custom application User-Agent
└── pages/
    ├── HomePage.jsx         # User dashboard displaying weather, NDVI, and risk indices
    ├── ChatPage.jsx         # Chat interface for chatting with the AI advisor
    ├── LoginPage.jsx        # Login layout
    └── RegisterPage.jsx     # Registration layout
```

### Essential Implementations
*   **Nominatim Geocoding Compliance** ([location.js](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/frontend/src/lib/location.js)): Configures geolocation search fetch calls to pass the custom identity header `"User-Agent": "PolliSync-App/1.0"` to comply with OpenStreetMap access conditions.
*   **Protected Authentication Routes** ([ProtectedRoute.jsx](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/frontend/src/components/ProtectedRoute.jsx)): Wraps private pages to prevent access from unauthorized users, redirecting them back to `/login`.

---

## 3. Machine Learning Framework (`/ml`)

The Machine Learning environment contains data collection, pipelines, training scripts, and output serialized binaries.

### Pipeline Subdirectories
*   **`data/`**: Datasets tracking pollinator occurrences and district histories:
    *   [ml/data/README.md](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/ml/data/README.md) - Guides source logs and licensing rules.
    *   `raw/` & `processed/` - Raw coordinates, weather factors, and GBIF pollinator observations.
*   **`models/`**: Serialized Random Forest model binaries (`.pkl`) representing the application's intelligence layer:
    *   `flowering_model.pkl` & `flowering_scaler.pkl` - Predicts flowering windows from planting dates.
    *   `flowering_model_mh.pkl` & `flowering_scaler_mh.pkl` - Specialized model optimized for Maharashtra, trained on localized climate and crop dynamics.
    *   `psi_model.pkl` & `risk_model.pkl` - Evaluates current crop growth, coordinates, and weather indexes to output Suitability scores and risk levels.
*   **`src/`**: Feature preparation and model training scripts:
    *   `train_improved_models.py` - Prepares features and exports general model artifacts.
    *   `train_maharashtra_model.py` - Localized training workflow optimized for Maharashtra datasets.

---

## 4. Documentation & References (`/docs`)

Documentation guides are located in the `/docs` directory:

*   [SETUP.md](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/docs/SETUP.md): Getting started guide for new developers, explaining virtual env setups, npm dependencies, environment keys configuration, and running unit tests.
*   [ARCHITECTURE.md](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/docs/ARCHITECTURE.md): Diagram showing client browser interactions with backend routers, SQLAlchemy, SQLite, and the machine learning model prediction files.
*   [DEMO_SCRIPT.md](file:///c:/Users/kusha/OneDrive/Documents/Pollysync/docs/DEMO_SCRIPT.md): Step-by-step test scenario script (signing up, creating farm records, reviewing weather forecasts, running risk indices, and asking the AI chatbot advice).
