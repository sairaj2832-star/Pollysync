from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response as FastAPIResponse

from app.api.router import api_router
from app.core.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate_security()
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API foundation for PolliSync.",
    lifespan=lifespan,
)

# Handle CORS dynamically so allowed_origins is read after env vars are fully loaded
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")
    allowed = settings.allowed_origins

    # Handle preflight
    if request.method == "OPTIONS":
        response = FastAPIResponse(status_code=200)
    else:
        response = await call_next(request)

    if origin and (origin in allowed or "*" in allowed):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-XSRF-TOKEN"
        response.headers["Vary"] = "Origin"

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
    }
