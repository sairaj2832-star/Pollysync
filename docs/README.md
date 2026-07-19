# PolliSync Documentation

AI-Based Crop Pollination Suitability System — built by 4 SY CSE-AI students.

## Quick Start

| Doc | What It Covers |
|-----|---------------|
| [Architecture](ARCHITECTURE.md) | System design, data flow, component breakdown, deployment topology |
| [Setup Guide](SETUP.md) | Local development environment, backend + frontend setup, troubleshooting |
| [Progress Tracker](progress.md) | Module-by-module task completion status |
| [Engineering Playbook](PLAYBOOK.md) | Full project plan, team roles, task breakdowns, roadmap, risk register |

## Project Overview

PolliSync combines farm details, real-time weather data, vegetation health indices, and pollinator observations to predict flowering windows, calculate a Pollination Suitability Index (0-100), and generate AI-powered farming recommendations.

## Repository Layout

```
.
├── frontend/          React 18 + Vite + Tailwind web app
├── backend/           FastAPI + SQLite API server
├── ml/                Training data, notebooks, model artifacts
├── docs/              This documentation
├── .github/workflows/ CI/CD (GitHub Actions)
└── README.md          Project overview
```

## Where to Start

- **New team member** — Read [Setup Guide](SETUP.md) first, then [Architecture](ARCHITECTURE.md).
- **Contributor** — Read [Playbook](PLAYBOOK.md) for task ownership and module breakdown.
