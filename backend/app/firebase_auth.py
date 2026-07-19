import json
import logging
from pathlib import Path
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings

logger = logging.getLogger(__name__)

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
    elif settings.firebase_private_key and settings.firebase_client_email:
        private_key = settings.firebase_private_key.replace("\\n", "\n")
        cert_dict = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key": private_key,
            "client_email": settings.firebase_client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        certificate = credentials.Certificate(cert_dict)
    elif settings.firebase_service_account_path:
        resolved_path = Path(_resolve_service_account_path(settings.firebase_service_account_path))
        if not resolved_path.exists():
            raise RuntimeError(
                f"Firebase Admin service account file not found: {resolved_path}"
            )
        certificate = credentials.Certificate(str(resolved_path))
    else:
        raise RuntimeError("Firebase Admin is not configured")

    options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None
    return firebase_admin.initialize_app(certificate, options=options)


def verify_firebase_token(id_token: str) -> dict:
    try:
        try:
            app = get_firebase_app()
            return auth.verify_id_token(id_token, app=app, check_revoked=True)
        except RuntimeError:
            if not settings.firebase_project_id:
                raise
            request = google_requests.Request()
            decoded = google_id_token.verify_firebase_token(
                id_token,
                request,
                audience=settings.firebase_project_id,
            )
            if not decoded:
                raise RuntimeError("Firebase token verification returned no payload")
            return decoded
    except Exception as exc:
        if settings.app_env.lower() == "development":
            import base64
            logger.warning(
                f"Firebase token verification failed ({exc}). "
                "Falling back to unverified decode for development mode."
            )
            try:
                segments = id_token.split('.')
                if len(segments) == 3:
                    payload = segments[1]
                    rem = len(payload) % 4
                    if rem > 0:
                        payload += "=" * (4 - rem)
                    data = base64.urlsafe_b64decode(payload)
                    return json.loads(data)
            except Exception as decode_exc:
                logger.error(f"Failed to decode unverified token: {decode_exc}")
        raise
