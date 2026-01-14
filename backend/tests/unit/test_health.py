"""
Health Check Endpoint Tests

Tests for the root and health check endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test that the root endpoint returns healthy status."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "todo-api"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test that the health check endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "todo-api"
