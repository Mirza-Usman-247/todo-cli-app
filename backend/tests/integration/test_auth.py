"""
Authentication Integration Tests

Tests for user signup, signin, signout, and session management.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user signup."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert "message" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    """Test signup with already registered email."""
    # First signup
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "TestPass123",
        },
    )

    # Second signup with same email
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "TestPass456",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    """Test signup with weak password."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "weak@example.com",
            "password": "weak",
        },
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_signup_password_no_uppercase(client: AsyncClient):
    """Test signup with password missing uppercase."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "noupper@example.com",
            "password": "lowercase123",
        },
    )
    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient):
    """Test successful user signin."""
    # First create user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "signin@example.com",
            "password": "TestPass123",
        },
    )

    # Then sign in
    response = await client.post(
        "/api/v1/auth/signin",
        json={
            "email": "signin@example.com",
            "password": "TestPass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "signin@example.com"


@pytest.mark.asyncio
async def test_signin_invalid_credentials(client: AsyncClient):
    """Test signin with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass123",
        },
    )
    assert response.status_code == 401
    # Should not reveal if email exists
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signin_wrong_password(client: AsyncClient):
    """Test signin with wrong password."""
    # Create user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "wrongpass@example.com",
            "password": "TestPass123",
        },
    )

    # Try to sign in with wrong password
    response = await client.post(
        "/api/v1/auth/signin",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPass456",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_signout(client: AsyncClient):
    """Test user signout."""
    response = await client.post("/api/v1/auth/signout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_session_unauthenticated(client: AsyncClient):
    """Test session endpoint without authentication."""
    response = await client.get("/api/v1/auth/session")
    assert response.status_code == 401
