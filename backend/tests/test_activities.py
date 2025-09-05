"""
Tests for activity logging functionality.

Tests activity creation, retrieval, and processing.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_log_activity_text():
    """Test logging activity with text input."""
    # First get a token
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    token = verify_response.json()["access_token"]
    
    # Log activity
    response = client.post("/activities/log", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "farmer_id": "123e4567-e89b-12d3-a456-426614174000",
            "text": "നാളെ പാട്ട നടാം",
            "language": "ml-IN"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "farmer_id" in data
    assert "text_raw" in data
    assert "language" in data


def test_log_activity_audio():
    """Test logging activity with audio input."""
    # First get a token
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    token = verify_response.json()["access_token"]
    
    # Log activity with audio
    response = client.post("/activities/log",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "farmer_id": "123e4567-e89b-12d3-a456-426614174000",
            "audio_url": "https://example.com/audio.wav",
            "language": "ml-IN"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "farmer_id" in data


def test_list_activities():
    """Test listing activities."""
    # First get a token
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    token = verify_response.json()["access_token"]
    
    # List activities
    response = client.get("/activities/",
        headers={"Authorization": f"Bearer {token}"},
        params={"farmer_id": "123e4567-e89b-12d3-a456-426614174000"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data


def test_get_activity():
    """Test getting specific activity."""
    # First get a token
    start_response = client.post("/auth/otp/start", json={"phone": "+919876543210"})
    verify_response = client.post("/auth/otp/verify", json={
        "req_id": "test_req_id",
        "code": "000000"
    })
    token = verify_response.json()["access_token"]
    
    # Get activity
    response = client.get("/activities/123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": f"Bearer {token}"}
    )
    # This might return 404 if activity doesn't exist, which is expected
    assert response.status_code in [200, 404]
