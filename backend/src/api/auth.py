"""
Authentication API and Middleware

Provides authentication endpoints and middleware for protected routes.
"""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# Request/Response Schemas
class SignUpRequest(BaseModel):
    """Sign up request schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignInRequest(BaseModel):
    """Sign in request schema."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response schema."""

    user: dict
    message: str


class SessionUser(BaseModel):
    """User data extracted from session."""

    id: UUID
    email: str


# Session cookie configuration
SESSION_COOKIE_NAME = "session_token"
SESSION_EXPIRY_HOURS = 24


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SessionUser | None:
    """
    Dependency to extract current user from session.

    Validates session token from cookie and returns user info.
    """
    # Extract session token from cookie
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None

    # Validate token and get user ID
    auth_service = AuthService(db)
    user_id = auth_service.decode_session_token(token)
    if not user_id:
        return None

    # Get user from database
    user = await auth_service.get_user_by_id(user_id)
    if not user or user.deleted_at is not None:
        return None

    return SessionUser(id=user.id, email=user.email)


async def require_auth(
    current_user: SessionUser | None = Depends(get_current_user),
) -> SessionUser:
    """
    Dependency that requires authentication.

    Raises 401 if user is not authenticated.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Type alias for authenticated user dependency
AuthenticatedUser = Annotated[SessionUser, Depends(require_auth)]


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user account.

    - Validates email format and uniqueness
    - Enforces password strength requirements
    - Creates user with hashed password
    - Returns session token in cookie
    """
    auth_service = AuthService(db)

    # Check if email already exists
    existing_user = await auth_service.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password strength
    if not auth_service.validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, and number",
        )

    # Create user
    user = await auth_service.create_user(request.email, request.password)

    # Create session token
    token = auth_service.create_session_token(user.id)

    # Set session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_EXPIRY_HOURS * 3600,
    )

    return AuthResponse(
        user={"id": str(user.id), "email": user.email},
        message="Account created successfully",
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SignInRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Sign in with email and password.

    - Validates credentials
    - Returns session token in cookie
    - Does not reveal if email exists (security)
    """
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is soft-deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create session token
    token = auth_service.create_session_token(user.id)

    # Set session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_EXPIRY_HOURS * 3600,
    )

    return AuthResponse(
        user={"id": str(user.id), "email": user.email},
        message="Signed in successfully",
    )


@router.post("/signout")
async def signout(response: Response):
    """
    Sign out the current user.

    - Clears session cookie
    """
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return {"success": True, "message": "Signed out successfully"}


@router.get("/session")
async def get_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current session information.

    Returns user info if authenticated, 401 otherwise.
    """
    # Extract session token from cookie
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Validate token and get user ID
    auth_service = AuthService(db)
    user_id = auth_service.decode_session_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Get user from database
    user = await auth_service.get_user_by_id(user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return {"user": {"id": str(user.id), "email": user.email}}
