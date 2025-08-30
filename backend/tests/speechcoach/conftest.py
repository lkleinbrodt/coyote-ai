import pytest
from flask import Flask

from backend import db
from backend.speech.models import SpeechProfile


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
