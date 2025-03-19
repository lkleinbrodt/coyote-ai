import os

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend import create_app, db
from backend.speech_coach.models import SpeechProfile


@pytest.fixture
def app() -> Flask:
    """Create and configure a test Flask application instance."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SPEECH_DEVELOPMENT_MODE": True,
            "SPEECH_APPLE_BUNDLE_ID": "com.test.speechcoach",
            "SECRET_KEY": "test_key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_headers() -> dict:
    """Create mock Apple authentication headers."""
    return {
        "Authorization": "Bearer mock_token",
        "X-Device-Platform": "ios",
        "X-Device-Version": "17.0",
    }


@pytest.fixture
def mock_apple_user() -> dict:
    """Create mock Apple user data."""
    return {
        "identityToken": "mock_identity_token",
        "user": "mock_user_id",
        "email": "test@example.com",
        "fullName": {"givenName": "Test", "familyName": "User"},
    }


@pytest.fixture
def test_user(app: Flask) -> SpeechProfile:
    """Create a test user in the database."""
    user = SpeechProfile(
        apple_user_id="mock_user_id", email="test@example.com", name="Test User"
    )
    db.session.add(user)
    db.session.commit()
    return user
