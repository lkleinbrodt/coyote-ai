"""
Consolidated tests for SideQuest API endpoints.

Tests authentication, authorization, request/response handling, and error cases.
"""

import json
import uuid
import pytest
from flask.testing import FlaskClient

from backend.models import User
from backend.sidequest.models import SideQuestUser
from backend.extensions import db


class TestAuthentication:
    """Test authentication and authorization."""

    def test_anonymous_signin_creates_user_and_profile(self, client: FlaskClient):
        """Test that anonymous signin creates both user and SideQuest profile."""
        device_uuid = str(uuid.uuid4())

        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()

        # Verify response structure
        assert "access_token" in data["data"]
        assert "user" in data["data"]

        # Verify user was created
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user is not None
        assert user.auth_type == "anonymous"

        # Verify SideQuest profile was created
        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        assert sidequest_user is not None
        assert sidequest_user.onboarding_completed is False

    def test_anonymous_signin_existing_user(self, client: FlaskClient):
        """Test that existing anonymous users can sign in again."""
        device_uuid = str(uuid.uuid4())

        # Create existing user
        existing_user = User(anon_id=device_uuid)
        db.session.add(existing_user)
        db.session.commit()

        # Sign in again
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )

        assert response.status_code == 200
        user = User.query.filter_by(anon_id=device_uuid).first()
        assert user.id == existing_user.id

    def test_anonymous_signin_validation_errors(self, client: FlaskClient):
        """Test that anonymous signin validates input correctly."""
        test_cases = [
            # Missing device_uuid
            ({"x": "y"}, "No device UUID provided"),
            # No data
            (None, "No data provided"),
            # Invalid UUID format
            ({"device_uuid": "invalid-uuid"}, "Invalid device UUID format"),
            # UUID v1 (should fail)
            ({"device_uuid": str(uuid.uuid1())}, "Invalid device UUID format"),
        ]

        for data, expected_error in test_cases:
            response = client.post(
                "/api/sidequest/auth/anonymous/signin",
                json=data,
                content_type="application/json",
            )

            assert response.status_code == 400
            error_data = response.get_json()
            assert expected_error in error_data["error"]["message"]

    def test_protected_endpoints_require_auth(self, client: FlaskClient):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("GET", "/api/sidequest/me"),
            ("PUT", "/api/sidequest/me"),
            ("POST", "/api/sidequest/onboarding/complete"),
        ]

        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "POST":
                response = client.post(endpoint)

            assert response.status_code == 401
            data = response.get_json()
            assert data["error"]["message"] == "Authentication required"
            assert data["error"]["code"] == "UNAUTHORIZED"


class TestUserPreferencesAPI:
    """Test user preferences API endpoints."""

    def test_get_user_preferences_authorized(
        self, client: FlaskClient, test_sidequest_user, auth_headers
    ):
        """Test getting user preferences with valid authentication."""
        response = client.get("/api/sidequest/me", headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        required_fields = [
            "categories",
            "difficulty",
            "maxTime",
            "includeCompleted",
            "includeSkipped",
            "notificationsEnabled",
            "notificationTime",
            "timezone",
            "onboardingCompleted",
            "userId",
        ]

        for field in required_fields:
            assert field in data["data"]

    def test_update_user_preferences_authorized(
        self, client: FlaskClient, test_sidequest_user, auth_headers
    ):
        """Test updating user preferences with valid authentication."""
        new_preferences = {
            "categories": ["fitness", "mindfulness"],
            "difficulty": "medium",
            "max_time": 15,
            "notifications_enabled": True,
        }

        response = client.put(
            "/api/sidequest/me", json=new_preferences, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert "message" in data["data"]
        assert "preferences" in data["data"]
        assert "userId" in data["data"]["preferences"]

    def test_complete_onboarding_authorized(
        self, client: FlaskClient, test_sidequest_user, auth_headers
    ):
        """Test completing onboarding with valid authentication."""
        response = client.post(
            "/api/sidequest/onboarding/complete", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert "Onboarding completed successfully" in data["data"]["message"]
        assert data["data"]["preferences"]["onboardingCompleted"] is True


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client: FlaskClient):
        """Test that health check endpoint returns correct status."""
        response = client.get("/api/sidequest/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["data"]["service"] == "SideQuest"
        assert data["data"]["status"] == "healthy"


class TestAnonymousUserIntegration:
    """Test that anonymous users can access core functionality."""

    def test_anonymous_user_can_access_protected_endpoints(self, client: FlaskClient):
        """Test that anonymous users can access protected endpoints."""
        device_uuid = str(uuid.uuid4())

        # Sign in anonymously
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )
        assert response.status_code == 200

        data = response.get_json()
        access_token = data["data"]["access_token"]

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/sidequest/me", headers=headers)

        # Should not get 401 (unauthorized)
        assert response.status_code != 401

    def test_anonymous_user_quest_generation_access(self, client: FlaskClient):
        """Test that anonymous users can access quest generation."""
        device_uuid = str(uuid.uuid4())

        # Sign in anonymously
        response = client.post(
            "/api/sidequest/auth/anonymous/signin",
            json={"device_uuid": device_uuid},
            content_type="application/json",
        )
        assert response.status_code == 200

        data = response.get_json()
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

        # Should not be blocked from core functionality
        assert response.status_code != 401
