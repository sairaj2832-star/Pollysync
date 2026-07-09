import json
from pathlib import Path
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings


BACKEND_DIR = Path(__file__).resolve().parents[1]


def _resolve_service_account_path(raw_path: str) -> str:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return str(candidate)

    repo_relative = (BACKEND_DIR.parent / candidate).resolve()
    if repo_relative.exists():
        return str(repo_relative)

    backend_relative = (BACKEND_DIR / candidate).resolve()
    return str(backend_relative)


@lru_cache(maxsize=1)
def get_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    if settings.firebase_service_account_json:
        certificate = credentials.Certificate(json.loads(settings.firebase_service_account_json))
    elif settings.firebase_service_account_path:
        certificate = credentials.Certificate(
            _resolve_service_account_path(settings.firebase_service_account_path)
        )
    else:
        raise RuntimeError("Firebase Admin is not configured")

    options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None
    return firebase_admin.initialize_app(certificate, options=options)


def verify_firebase_token(id_token: str) -> dict:
    app = get_firebase_app()
    return auth.verify_id_token(id_token, app=app, check_revoked=False)
