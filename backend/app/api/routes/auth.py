from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import JWT_COOKIE_NAME, create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

# En producción, frontend (Netlify) y backend (Render) viven en dominios
# distintos -> el cookie de sesión necesita SameSite=None (y por lo tanto
# Secure=True, exigido por los navegadores para SameSite=None). En local,
# localhost:5173 -> localhost:8000 es "same-site" (mismo dominio, distinto
# puerto), así que Lax + sin Secure funciona sobre HTTP normal.
IS_PRODUCTION = settings.app_env != "development"
COOKIE_SAMESITE = "none" if IS_PRODUCTION else "lax"
COOKIE_SECURE = IS_PRODUCTION


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")

    token = create_access_token(user.id)
    max_age = settings.access_token_expire_minutes * 60 if payload.remember_me else None
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age,
    )
    return user


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(JWT_COOKIE_NAME, samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
