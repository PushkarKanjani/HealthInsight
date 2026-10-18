"""
Authentication module for HealthInsight v2 AI Portal.
Handles JWT creation, verification, and route protection.
"""
import os
import datetime
from typing import Optional
from dotenv import load_dotenv
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

JWT_SECRET = os.getenv("PORTAL_JWT_SECRET", "healthinsight_jwt_secret_change_me_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 8

# Default administrator credentials
DEFAULT_ADMIN_USER = os.getenv("PORTAL_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASS = os.getenv("PORTAL_ADMIN_PASS", "healthinsight2024")

security_bearer = HTTPBearer(auto_error=False)


def create_access_token(username: str) -> str:
    """Create a signed JWT token valid for 8 hours."""
    payload = {
        "sub": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "role": "clinical_admin"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> dict:
    """FastAPI dependency to protect endpoints with Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_user(username: str, password: str) -> bool:
    """Verify login credentials against environment or defaults."""
    return username == DEFAULT_ADMIN_USER and password == DEFAULT_ADMIN_PASS
