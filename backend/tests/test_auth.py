"""
Tests for authentication functionality.

Tests OTP generation, verification, and JWT token management.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_otp_start():
    """Test OTP start endpoint."""
    response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    assert response.status_code == 200
    data = response.json()
    assert "req_id" in data
    assert "message" in data
    assert "expires_in" in data


def test_otp_verify():
    """Test OTP verification endpoint."""
    # Start OTP flow
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    assert start_response.status_code == 200
    
    # Verify OTP (using dev code)
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    assert verify_response.status_code == 200
    data = verify_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


def test_invalid_otp():
    """Test invalid OTP verification."""
    response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "123456"
    })
    assert response.status_code == 400


def test_get_current_user():
    """Test getting current user info."""
    # First get a token
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    token = verify_response.json()["access_token"]
    
    # Test protected endpoint
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "phone" in data
    assert "role" in data


def test_invalid_token():
    """Test access with invalid token."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
