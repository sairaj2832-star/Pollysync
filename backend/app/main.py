from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

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


def _add_cors(response: Response, origin: str) -> Response:
    """Attach CORS headers to any response when origin is allowed."""
    allowed = settings.allowed_origins
    if origin and origin.rstrip("/") in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin.rstrip("/")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
    return response


# Override exception handlers so CORS headers are present even on errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    origin = request.headers.get("origin", "")
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    return _add_cors(response, origin)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    origin = request.headers.get("origin", "")
    response = JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
    return _add_cors(response, origin)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    return _add_cors(response, origin)


@app.middleware("http")
async def cors_and_security(request: Request, call_next):
    origin = request.headers.get("origin", "").rstrip("/")
    allowed = settings.allowed_origins
    origin_allowed = bool(origin and origin in allowed)

    # Short-circuit OPTIONS preflight before FastAPI routing
    if request.method == "OPTIONS":
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
        if origin_allowed:
            headers.update({
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-XSRF-TOKEN",
                "Vary": "Origin",
            })
        return Response(status_code=200, headers=headers)

    response = await call_next(request)

    if origin_allowed:
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
