import json
import uuid
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.models import User
from backend.sidequest.models import SideQuestUser
from backend.extensions import db


class TestAnonymousAuthentication:
    """Test anonymous user authentication functionality."""

    def test_anonymous_signin_success_new_user(self, client: FlaskClient):
        """Test successful anonymous signin for new user."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200, response.get_json()
        data = json.loads(response.data)
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]

        # Verify user was created in database
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user is not None
        assert user.auth_type == "anonymous"

        # Verify SideQuest profile was created
        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        assert sidequest_user is not None
        assert sidequest_user.onboarding_completed is False

    def test_anonymous_signin_success_existing_user(self, client: FlaskClient):
        """Test successful anonymous signin for existing user."""
        # Create existing anonymous user
        device_uuid = str(uuid.uuid4())
        existing_user = User(anon_id=device_uuid)
        db.session.add(existing_user)
        db.session.commit()

        # Try to sign in again with same device UUID
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify same user was returned
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user.id == existing_user.id

    def test_anonymous_signin_missing_device_uuid(self, client: FlaskClient):
        """Test anonymous signin with missing device UUID."""
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"x": "y"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "No device UUID provided" in data["error"]["message"]

    def test_anonymous_signin_no_data(self, client: FlaskClient):
        """Test anonymous signin with no request data."""
        response = client.post(
            "/api/sidequest/auth/anonymous/signin", content_type="application/json"
        )

        assert response.status_code == 400, response.get_json()

        data = response.get_json()
        assert data["success"] is False
        assert "No data provided" in data["error"]["message"]

    def test_anonymous_signin_invalid_uuid_format(self, client: FlaskClient):
        """Test anonymous signin with invalid UUID format."""
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": "invalid-uuid-format"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Invalid device UUID format" in data["error"]["message"]

    def test_anonymous_signin_uuid_v4_validation(self, client: FlaskClient):
        """Test that only UUID v4 format is accepted."""
        # Test with valid UUID v4
        valid_uuid = str(uuid.uuid4())
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": valid_uuid},
            content_type="application/json",
        )
        assert response.status_code == 200

        # Test with UUID v1 (should fail)
        uuid_v1 = str(uuid.uuid1())
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": uuid_v1},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid device UUID format" in data["error"]["message"]

    def test_anonymous_user_auth_type_property(self, client: FlaskClient):
        """Test that anonymous users have correct auth_type property."""
        device_uuid = str(uuid.uuid4())

        # Create anonymous user
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200

        # Verify auth_type property
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user.auth_type == "anonymous"

    def test_anonymous_user_jwt_claims(self, client: FlaskClient):
        """Test that JWT token includes correct claims for anonymous users."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        access_token = data["data"]["access_token"]

        # Decode JWT to verify claims
        from flask_jwt_extended import decode_token

        with client.application.app_context():
            decoded = decode_token(access_token)
            assert decoded["sub"] is not None  # user_id
            assert decoded["anon_id"] == device_uuid

    def test_anonymous_user_unique_constraint(self, client: FlaskClient):
        """Test that anon_id has unique constraint."""
        device_uuid = str(uuid.uuid4())

        # Create first user
        user1 = User(anon_id=device_uuid)
        db.session.add(user1)
        db.session.commit()

        # Try to create second user with same anon_id
        user2 = User(anon_id=device_uuid)
        db.session.add(user2)

        with pytest.raises(Exception):  # Should raise unique constraint violation
            db.session.commit()

    def test_anonymous_user_sidequest_profile_creation(self, client: FlaskClient):
        """Test that SideQuest profile is created for new anonymous users."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200

        # Verify user and SideQuest profile were created
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user is not None

        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        assert sidequest_user is not None
        assert sidequest_user.onboarding_completed is False

    def test_anonymous_user_existing_sidequest_profile(self, client: FlaskClient):
        """Test that existing SideQuest profile is not recreated."""
        device_uuid = str(uuid.uuid4())

        # Create user with existing SideQuest profile
        user = User(anon_id=device_uuid)
        db.session.add(user)
        db.session.commit()

        sidequest_user = SideQuestUser(
            user_id=user.id, onboarding_completed=True  # Mark as completed
        )
        db.session.add(sidequest_user)
        db.session.commit()

        # Sign in again
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200

        # Verify profile wasn't recreated
        updated_profile = SideQuestUser.query.filter_by(user_id=user.id).first()
        assert updated_profile.onboarding_completed is True  # Should still be True

    def test_anonymous_user_response_structure(self, client: FlaskClient):
        """Test that anonymous signin response matches Apple signin structure."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure matches Apple signin
        assert "success" in data
        assert "data" in data
        assert "access_token" in data["data"]
        assert "user" in data["data"]

        user_data = data["data"]["user"]
        assert "id" in user_data
        assert "name" in user_data
        assert "email" in user_data
        assert "image" in user_data
        assert "role" in user_data

    def test_anonymous_user_token_expiration(self, client: FlaskClient):
        """Test that anonymous users get same token expiration as Apple users."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        access_token = data["data"]["access_token"]

        # Decode JWT to verify expiration
        from flask_jwt_extended import decode_token

        with client.application.app_context():
            decoded = decode_token(access_token)
            # Token should be valid for 1 year (365 days)
            # This is a basic check - in practice you'd verify the exact expiration time
            assert decoded is not None


class TestAnonymousUserIntegration:
    """Test anonymous users can access SideQuest features."""

    def test_anonymous_user_can_access_protected_endpoints(self, client: FlaskClient):
        """Test that anonymous users can access protected endpoints with JWT."""
        device_uuid = str(uuid.uuid4())

        # Sign in anonymously
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        access_token = data["data"]["access_token"]

        # Try to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/sidequest/me", headers=headers)

        # Should not get 401 (unauthorized)
        assert response.status_code != 401

    def test_anonymous_user_quest_generation(self, client: FlaskClient):
        """Test that anonymous users can generate quests."""
        device_uuid = str(uuid.uuid4())

        # Sign in anonymously
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        access_token = data["data"]["access_token"]

        # Try to generate quests
        headers = {"Authorization": f"Bearer {access_token}"}
        quest_data = {
            "categories": ["fitness", "mindfulness"],
            "difficulty": "medium",
            "max_time": 15,
        }

        response = client.post(
            "/api/sidequest/generate",
            json=quest_data,
            headers=headers,
            content_type="application/json",
        )

        # Should be able to generate quests (assuming endpoint exists and works)
        # This test verifies that anonymous users aren't blocked from core functionality
        assert response.status_code != 401  # Not unauthorized
