import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend import db
from backend.speech.models import SpeechProfile


def test_apple_signin_success(client: FlaskClient, mock_apple_user: dict):
    """Test successful Apple Sign In."""
    response = client.post("/api/speech/auth/apple/signin", json=mock_apple_user)
    assert response.status_code == 200

    data = response.get_json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == mock_apple_user["email"]

    # Verify user was created in database
    user = SpeechProfile.query.filter_by(apple_user_id=mock_apple_user["user"]).first()
    assert user is not None
    assert user.email == mock_apple_user["email"]


def test_apple_signin_missing_data(client: FlaskClient):
    """Test Apple Sign In with missing data."""
    response = client.post("/api/speech/auth/apple/signin", json={})
    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data
    assert "message" in data


def test_get_current_user(
    client: FlaskClient, test_user: SpeechProfile, auth_headers: dict
):
    """Test getting current user profile."""
    response = client.get("/api/speech/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert "totalRecordings" in data
    assert "totalPracticeTime" in data


def test_get_current_user_unauthorized(client: FlaskClient):
    """Test getting current user without auth token."""
    response = client.get("/api/speech/me")
    assert response.status_code == 401


def test_signout(client: FlaskClient, auth_headers: dict):
    """Test user sign out."""
    response = client.post("/api/speech/signout", headers=auth_headers)
    assert response.status_code == 200


def test_signout_unauthorized(client: FlaskClient):
    """Test sign out without auth token."""
    response = client.post("/api/speech/signout")
    assert response.status_code == 401


def test_apple_signin_existing_user(
    client: FlaskClient, mock_apple_user: dict, test_user: SpeechProfile
):
    """Test Apple Sign In with existing user."""
    response = client.post("/api/speech/auth/apple/signin", json=mock_apple_user)
    assert response.status_code == 200

    data = response.get_json()
    assert data["user"]["id"] == test_user.id
    assert data["user"]["email"] == test_user.email

    # Verify no duplicate user was created
    user_count = SpeechProfile.query.filter_by(
        apple_user_id=mock_apple_user["user"]
    ).count()
    assert user_count == 1
