import httpx
from fastapi import APIRouter, Depends, HTTPException, status
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
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User, db: Session) -> AuthResponse:
    refresh_token = create_refresh_token(user, db)
    return AuthResponse(
        access_token=create_access_token(user),
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
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
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
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
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
    return _auth_response(user, db)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    user = _authenticate(str(payload.email), payload.password, db)
    return _auth_response(user, db)


@router.post("/token", response_model=Token)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = _authenticate(form_data.username, form_data.password, db)
    return Token(access_token=create_access_token(user))


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user, refresh_token = rotate_refresh_token(payload.refresh_token, db)
    return AuthResponse(
        access_token=create_access_token(user),
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> None:
    revoke_refresh_token(payload.refresh_token, db)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/firebase", response_model=AuthResponse)
def firebase_auth(payload: FirebaseAuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        decoded = verify_firebase_token(payload.id_token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token validation failed",
        ) from exc

    email = (decoded.get("email") or "").lower()
    uid = decoded.get("uid") or decoded.get("sub")
    if not email or not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase token is missing email or uid",
        )

    user = _get_user_by_subject(uid, db) or _get_user_by_email(email, db)
    if user is None:
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
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        user.email = email
        user.full_name = decoded.get("name") or user.full_name
        user.oauth_provider = "firebase"
        user.oauth_subject = uid
        db.commit()
        db.refresh(user)

    return _auth_response(user, db)


@router.post("/oauth/google", response_model=AuthResponse)
async def google_oauth(payload: OAuthCallback, db: Session = Depends(get_db)) -> AuthResponse:
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
    return _auth_response(user, db)
