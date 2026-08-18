import ast
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.exception import AppException

bearer_scheme = HTTPBearer()


class JWTHandler:
    @staticmethod
    def create_access_token(subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict | None:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    payload = JWTHandler.decode_token(credentials.credentials)
    if not payload:
        raise AppException(status_code=401, message="Invalid or expired token")
    try:
        user = ast.literal_eval(payload["sub"])
    except Exception:
        raise AppException(status_code=401, message="Invalid token payload")
    return user


def require_roles(*roles: str):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in roles:
            raise AppException(status_code=403, message="Access forbidden: insufficient role")
        return current_user
    return dependency
