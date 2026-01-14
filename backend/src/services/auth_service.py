"""
Authentication Service

Business logic for user authentication, password hashing, and session management.
"""

import os
import re
from datetime import datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User

# JWT configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service with database session."""
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password.

        Returns:
            Bcrypt hashed password.
        """
        # bcrypt has a 72-byte limit; truncate if necessary
        password_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify.
            hashed_password: Bcrypt hashed password.

        Returns:
            True if password matches, False otherwise.
        """
        # bcrypt has a 72-byte limit; truncate if necessary
        password_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password meets strength requirements.

        Requirements:
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains number

        Args:
            password: Password to validate.

        Returns:
            True if password meets requirements.
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email to lowercase for case-insensitive comparison.

        Args:
            email: Email address to normalize.

        Returns:
            Lowercase email address.
        """
        return email.lower().strip()

    @staticmethod
    def create_session_token(user_id: UUID) -> str:
        """
        Create a JWT session token for a user.

        Args:
            user_id: User's UUID.

        Returns:
            JWT token string.
        """
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_session_token(token: str) -> UUID | None:
        """
        Decode and validate a JWT session token.

        Args:
            token: JWT token string.

        Returns:
            User UUID if valid, None otherwise.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return UUID(user_id)
        except (JWTError, ValueError):
            return None

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email address.

        Args:
            email: Email address to search for.

        Returns:
            User if found, None otherwise.
        """
        normalized_email = self.normalize_email(email)
        result = await self.db.execute(
            select(User).where(User.email == normalized_email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Get a user by ID.

        Args:
            user_id: User's UUID.

        Returns:
            User if found, None otherwise.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password: str) -> User:
        """
        Create a new user with hashed password.

        Args:
            email: User's email address.
            password: Plain text password.

        Returns:
            Created User instance.
        """
        normalized_email = self.normalize_email(email)
        password_hash = self.hash_password(password)

        user = User(
            email=normalized_email,
            password_hash=password_hash,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email address.
            password: Plain text password.

        Returns:
            User if credentials are valid, None otherwise.
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    async def soft_delete_user(self, user_id: UUID) -> bool:
        """
        Soft delete a user by setting deleted_at timestamp.

        Args:
            user_id: User's UUID.

        Returns:
            True if user was deleted, False if not found.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.deleted_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await self.db.commit()

        return True
