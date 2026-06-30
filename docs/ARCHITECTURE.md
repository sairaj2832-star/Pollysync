# Architecture

PolliSync begins as a modular monorepo and a single deployable backend.

    Browser
       |
       v
    React + Vite frontend
       |
       v
    FastAPI REST API
       |----------- SQLite
       |----------- Open-Meteo
       |----------- GBIF
       |----------- Local ML artifacts and optional LLM provider

The MVP deliberately avoids microservices, background queues, containers, and a vector database. Module boundaries inside the backend preserve a path to later growth without creating deployment overhead during the hackathon.

Frontend code owns presentation and browser state. Backend code owns validation, persistence, external API integration, and model orchestration. ML notebooks are for experiments; reusable feature and inference code belongs in ml/src and is promoted into the backend only after validation.
