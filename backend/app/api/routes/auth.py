import logging
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

logger = logging.getLogger(__name__)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    rotate_refresh_token,
    revoke_refresh_token,
    set_auth_cookies,
    clear_auth_cookies,
    verify_password,
)
from app.core.config import settings
from app.database import get_db
from app.firebase_auth import verify_firebase_token
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    FirebaseAuthRequest,
    OAuthCallback,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User, db: Session, response: Response) -> AuthResponse:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user, db)
    set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
        user=UserRead.model_validate(user),
    )


def _get_user_by_email(email: str, db: Session) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def _get_user_by_subject(subject: str, db: Session) -> User | None:
    return db.scalar(
        select(User).where(
            User.oauth_provider == "firebase",
            User.oauth_subject == subject,
        )
    )


def _authenticate(email: str, password: str, db: Session) -> User:
    user = _get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.lockout_until:
        lockout_time = user.lockout_until
        if lockout_time.tzinfo is None:
            lockout_time = lockout_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < lockout_time:
            remaining_mins = int((lockout_time - datetime.now(timezone.utc)).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is temporarily locked due to multiple failed login attempts. Try again in {remaining_mins} minutes.",
            )

    if not user.hashed_password or not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    if user.failed_login_attempts > 0 or user.lockout_until:
        user.failed_login_attempts = 0
        user.lockout_until = None
        db.commit()

    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    email = str(payload.email).lower()
    existing = _get_user_by_email(email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user, db, response)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = _authenticate(str(payload.email), payload.password, db)
    return _auth_response(user, db, response)


@router.post("/token", response_model=Token)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = _authenticate(form_data.username, form_data.password, db)
    return Token(access_token=create_access_token(user))


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshTokenRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    refresh_token_str = payload.refresh_token
    user, new_refresh_token = rotate_refresh_token(refresh_token_str, db)
    access_token = create_access_token(user)
    set_auth_cookies(response, access_token, new_refresh_token)
    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: dict | None = None,
    request: Request = None,
    response: Response = None,
    db: Session = Depends(get_db),
) -> None:
    refresh_token_str = (payload or {}).get("refresh_token", "") or request.cookies.get("refresh_token", "")
    if refresh_token_str:
        revoke_refresh_token(refresh_token_str, db)

    access_token_str = None
    if request:
        access_token_str = request.cookies.get("access_token")
        if not access_token_str:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token_str = auth_header.split(" ")[1]

    if access_token_str:
        try:
            from app.auth import decode_access_token
            from app.models.revoked_token import RevokedToken
            payload_data = decode_access_token(access_token_str)
            jti = payload_data.get("jti")
            exp = payload_data.get("exp")
            if jti and exp:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                db.add(RevokedToken(jti=jti, expires_at=expires_at))
                db.commit()
        except Exception:
            pass

    clear_auth_cookies(response)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/firebase", response_model=AuthResponse)
def firebase_auth(payload: FirebaseAuthRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        decoded = verify_firebase_token(payload.id_token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Firebase token validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase token validation failed: {exc}",
        ) from exc

    email = (decoded.get("email") or "").lower()
    uid = decoded.get("uid") or decoded.get("sub")
    if not email or not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase token is missing email or uid",
        )

    user = _get_user_by_subject(uid, db)
    if user is None:
        existing_user = _get_user_by_email(email, db)
        if existing_user is None:
            user = User(
                email=email,
                full_name=decoded.get("name") or email.split("@")[0],
                oauth_provider="firebase",
                oauth_subject=uid,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if not existing_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is disabled",
                )
            if not decoded.get("email_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Firebase email is not verified. Account linking rejected.",
                )
            if existing_user.oauth_provider and existing_user.oauth_provider != "firebase":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"An account with this email already exists using {existing_user.oauth_provider.capitalize()}.",
                )
            user = existing_user
            user.oauth_provider = "firebase"
            user.oauth_subject = uid
            db.commit()
            db.refresh(user)
    else:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        user.email = email
        user.full_name = decoded.get("name") or user.full_name
        db.commit()
        db.refresh(user)

    return _auth_response(user, db, response)


@router.post("/oauth/google", response_model=AuthResponse)
async def google_oauth(payload: OAuthCallback, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    if not all(
        [
            settings.oauth_google_client_id,
            settings.oauth_google_client_secret,
            settings.oauth_google_redirect_uri,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": payload.code,
                "client_id": settings.oauth_google_client_id,
                "client_secret": settings.oauth_google_client_secret,
                "redirect_uri": settings.oauth_google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google OAuth code exchange failed",
            )
        id_token = token_response.json().get("id_token")
        profile_response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )

    profile = profile_response.json()
    if (
        profile_response.status_code >= 400
        or profile.get("aud") != settings.oauth_google_client_id
        or profile.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}
        or profile.get("email_verified") != "true"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google OAuth token validation failed",
        )

    email = profile["email"].lower()
    user = _get_user_by_email(email, db)
    if user is None:
        user = User(
            email=email,
            full_name=profile.get("name") or email.split("@")[0],
            oauth_provider="google",
            oauth_subject=profile["sub"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    return _auth_response(user, db, response)
