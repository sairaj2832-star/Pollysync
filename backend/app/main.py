from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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

# Use a wildcard-safe explicit origin list.
# CORSMiddleware is initialized with allow_origins=["*"] so it always responds
# to preflight, then the http middleware below restricts to the actual allowed origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-XSRF-TOKEN"],
)


@app.middleware("http")
async def restrict_cors_and_add_security_headers(request: Request, call_next):
    origin = request.headers.get("origin", "").rstrip("/")
    allowed = settings.allowed_origins
    response = await call_next(request)

    # Replace the wildcard CORS header with the exact origin when it's allowed
    if origin and origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
    elif "Access-Control-Allow-Origin" in response.headers:
        # Remove wildcard for origins not in our allowlist
        del response.headers["Access-Control-Allow-Origin"]

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
