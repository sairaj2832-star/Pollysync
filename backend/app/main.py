from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

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


def _cors_headers(origin: str) -> dict:
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type, X-XSRF-TOKEN",
        "Vary": "Origin",
    }


@app.middleware("http")
async def cors_and_security(request: Request, call_next):
    origin = request.headers.get("origin", "").rstrip("/")
    allowed = settings.allowed_origins
    origin_allowed = origin and origin in allowed

    # Short-circuit OPTIONS preflight — return before FastAPI routing touches it
    if request.method == "OPTIONS":
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
        if origin_allowed:
            headers.update(_cors_headers(origin))
        return Response(status_code=200, headers=headers)

    response = await call_next(request)

    if origin_allowed:
        for k, v in _cors_headers(origin).items():
            response.headers[k] = v

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
