import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.models import User
from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestRating,
    SideQuest,
)
from backend.sidequest.services import QuestGenerationService, UserService, QuestService
from backend.extensions import db


class TestSideQuestModels:
    """Test SideQuest database models."""

    def test_quest_category_enum(self):
        """Test QuestCategory enum values."""
        assert QuestCategory.FITNESS == "fitness"
        assert QuestCategory.SOCIAL == "social"
        assert QuestCategory.MINDFULNESS == "mindfulness"
        assert QuestCategory.CHORES == "chores"
        assert QuestCategory.HOBBIES == "hobbies"
        assert QuestCategory.OUTDOORS == "outdoors"
        assert QuestCategory.LEARNING == "learning"
        assert QuestCategory.CREATIVITY == "creativity"

    def test_quest_difficulty_enum(self):
        """Test QuestDifficulty enum values."""
        assert QuestDifficulty.EASY == "easy"
        assert QuestDifficulty.MEDIUM == "medium"
        assert QuestDifficulty.HARD == "hard"

    def test_quest_rating_enum(self):
        """Test QuestRating enum values."""
        assert QuestRating.THUMBS_UP == "thumbs_up"
        assert QuestRating.THUMBS_DOWN == "thumbs_down"

    def test_sidequest_user_creation(self, test_sidequest_user):
        """Test SideQuestUser creation and properties."""
        assert test_sidequest_user.user_id is not None
        assert test_sidequest_user.categories == ["fitness", "mindfulness"]
        assert test_sidequest_user.difficulty == QuestDifficulty.MEDIUM
        assert test_sidequest_user.max_time == 15
        assert test_sidequest_user.notifications_enabled is True
        assert test_sidequest_user.onboarding_completed is True
        assert test_sidequest_user.created_at is not None
        assert test_sidequest_user.updated_at is not None

    def test_sidequest_user_to_dict(self, test_sidequest_user):
        """Test SideQuestUser to_dict method."""
        user_dict = test_sidequest_user.to_dict()
        assert "id" in user_dict
        assert "user_id" in user_dict
        assert "categories" in user_dict
        assert "difficulty" in user_dict
        assert "max_time" in user_dict
        assert "notifications_enabled" in user_dict
        assert "onboarding_completed" in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict

    def test_quest_creation(self, test_quest):
        """Test SideQuest creation and properties."""
        assert test_quest.user_id is not None
        assert test_quest.text == "Take a 10-minute walk"
        assert test_quest.category == QuestCategory.FITNESS
        assert test_quest.estimated_time == "10 minutes"
        assert test_quest.difficulty == QuestDifficulty.EASY
        assert test_quest.tags == ["walking", "exercise", "outdoors"]
        assert test_quest.selected is False
        assert test_quest.completed is False
        assert test_quest.skipped is False
        assert test_quest.created_at is not None
        assert test_quest.expires_at is not None

    def test_quest_to_dict(self, test_quest):
        """Test SideQuest to_dict method."""
        quest_dict = test_quest.to_dict()
        assert "id" in quest_dict
        assert "text" in quest_dict
        assert "category" in quest_dict
        assert "estimatedTime" in quest_dict
        assert "difficulty" in quest_dict
        assert "tags" in quest_dict
        assert "selected" in quest_dict
        assert "completed" in quest_dict
        assert "skipped" in quest_dict
        assert "createdAt" in quest_dict
        assert "expiresAt" in quest_dict

    def test_quest_expiration(self, test_quest):
        """Test quest expiration logic."""
        # Quest should not be expired when just created
        assert not test_quest.is_expired()

        # Set expiration to past
        test_quest.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert test_quest.is_expired()

    def test_quest_mark_completed(self, test_quest):
        """Test marking quest as completed."""
        # Refresh the quest to get current timestamp
        from backend.extensions import db

        db.session.refresh(test_quest)
        original_updated = test_quest.updated_at

        test_quest.mark_completed(
            feedback_rating=QuestRating.THUMBS_UP,
            feedback_comment="Great exercise!",
            time_spent=12,
        )

        # Commit the changes to trigger the onupdate
        db.session.commit()
        db.session.refresh(test_quest)

        assert test_quest.completed is True
        assert test_quest.completed_at is not None
        assert test_quest.feedback_rating == QuestRating.THUMBS_UP
        assert test_quest.feedback_comment == "Great exercise!"
        assert test_quest.time_spent == 12
        assert test_quest.updated_at > original_updated

    def test_quest_mark_skipped(self, test_quest):
        """Test marking quest as skipped."""
        # Refresh the quest to get current timestamp
        from backend.extensions import db

        db.session.refresh(test_quest)
        original_updated = test_quest.updated_at

        test_quest.mark_skipped()

        # Commit the changes to trigger the onupdate
        db.session.commit()

        assert test_quest.skipped is True
        assert test_quest.updated_at > original_updated

    def test_quest_mark_selected(self, test_quest):
        """Test marking quest as selected."""
        # Refresh the quest to get current timestamp
        from backend.extensions import db

        db.session.refresh(test_quest)
        original_updated = test_quest.updated_at

        test_quest.mark_selected()

        # Commit the changes to trigger the onupdate
        db.session.commit()
        db.session.refresh(test_quest)

        assert test_quest.selected is True
        assert test_quest.updated_at > original_updated


class TestSideQuestServices:
    """Test SideQuest service classes."""

    def test_user_service_get_or_create_profile(self, app):
        """Test UserService get_or_create_user_profile."""
        with app.app_context():
            from backend.models import User
            from backend.sidequest.services import UserService
            from backend.extensions import db

            # Create a base user
            user = User(apple_id="test_user", email="test@test.com")
            db.session.add(user)
            db.session.commit()

            user_service = UserService(db.session)
            profile = user_service.get_or_create_user_profile(user.id)

            assert profile is not None
            assert profile.user_id == user.id
            assert profile.categories == []  # Default empty list
            assert profile.difficulty == QuestDifficulty.MEDIUM  # Default
            assert profile.max_time == 15  # Default
            assert profile.onboarding_completed is False  # Default

    def test_user_service_update_preferences(self, test_sidequest_user, app):
        """Test UserService update_user_preferences."""
        with app.app_context():
            from backend.extensions import db

            user_service = UserService(db.session)

            new_preferences = {
                "categories": ["social", "learning"],
                "difficulty": "hard",
                "max_time": 30,
                "notifications_enabled": False,
            }

            updated_profile = user_service.update_user_preferences(
                test_sidequest_user.user_id, new_preferences
            )

            assert updated_profile.categories == ["social", "learning"]
            assert updated_profile.difficulty == QuestDifficulty.HARD
            assert updated_profile.max_time == 30
            assert updated_profile.notifications_enabled is False

    def test_quest_service_get_user_quests(self, sample_quest, app):
        """Test QuestService get_user_quests."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)

            quests = quest_service.get_user_quests(sample_quest.user_id)

            assert len(quests) == 1
            assert quests[0].id == sample_quest.id
            assert quests[0].text == sample_quest.text

    def test_quest_service_mark_quest_selected(self, sample_quest, app):
        """Test QuestService mark_quest_selected."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)

            success = quest_service.mark_quest_selected(
                sample_quest.id, sample_quest.user_id
            )

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, sample_quest.id)
            assert updated_quest.selected is True

    def test_quest_service_mark_quest_completed(self, sample_quest, app):
        """Test QuestService mark_quest_completed."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)

            feedback = {
                "rating": "thumbs_up",
                "comment": "Great quest!",
                "timeSpent": 15,
            }

            success = quest_service.mark_quest_completed(
                sample_quest.id, sample_quest.user_id, feedback
            )

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, sample_quest.id)
            assert updated_quest.completed is True
            assert updated_quest.feedback_rating == QuestRating.THUMBS_UP
            assert updated_quest.feedback_comment == "Great quest!"
            assert updated_quest.time_spent == 15

    def test_quest_service_mark_quest_skipped(self, sample_quest, app):
        """Test QuestService mark_quest_skipped."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)

            success = quest_service.mark_quest_skipped(
                sample_quest.id, sample_quest.user_id
            )

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, sample_quest.id)
            assert updated_quest.skipped is True

    def test_quest_service_get_quest_history(self, sample_quest, app):
        """Test QuestService get_quest_history."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)

            history = quest_service.get_quest_history(sample_quest.user_id, days=7)

            assert "period" in history
            assert "start_date" in history
            assert "end_date" in history
            assert "stats" in history
            assert "quests" in history

            stats = history["stats"]
            assert "total" in stats
            assert "selected" in stats
            assert "completed" in stats
            assert "skipped" in stats
            assert "total_time" in stats


class TestSideQuestAPI:
    """Test SideQuest API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/sidequest/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["service"] == "SideQuest"
        assert data["data"]["status"] == "healthy"

    def test_get_user_preferences_unauthorized(self, client):
        """Test getting preferences without authentication."""
        response = client.get("/api/sidequest/preferences")
        assert response.status_code == 401

        data = response.get_json()
        print(data)
        assert data["success"] is False
        assert "error" in data
        assert data["error"]["message"] == "Authentication required"
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_get_user_preferences_authorized(
        self, client, test_sidequest_user, auth_headers
    ):
        """Test getting preferences with authentication."""
        response = client.get("/api/sidequest/preferences", headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "preferences" in data["data"]
        assert "user_id" in data["data"]

    def test_update_user_preferences_unauthorized(self, client):
        """Test updating preferences without authentication."""
        response = client.put("/api/sidequest/preferences", json={})
        assert response.status_code == 401

    def test_update_user_preferences_authorized(
        self, client, test_sidequest_user, auth_headers, quest_preferences
    ):
        """Test updating preferences with authentication."""
        response = client.put(
            "/api/sidequest/preferences", json=quest_preferences, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert "preferences" in data["data"]

    def test_generate_daily_quests_unauthorized(self, client):
        """Test quest generation without authentication."""
        response = client.post("/api/sidequest/generate", json={})
        assert response.status_code == 401

    def test_generate_daily_quests_missing_preferences(self, client, auth_headers):
        """Test quest generation with missing preferences."""
        response = client.post("/api/sidequest/generate", json={}, headers=auth_headers)
        assert response.status_code == 400

        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "data" in data["error"]["message"]

    def test_generate_daily_quests_invalid_preferences(self, client, auth_headers):
        """Test quest generation with invalid preferences."""
        invalid_preferences = {
            "categories": [],  # Empty categories
            "difficulty": "invalid",  # Invalid difficulty
            "max_time": -5,  # Invalid time
        }

        response = client.post(
            "/api/sidequest/generate",
            json={"preferences": invalid_preferences},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_get_user_quests_unauthorized(self, client):
        """Test getting quests without authentication."""
        response = client.get("/api/sidequest/quests")
        assert response.status_code == 401

    def test_get_user_quests_authorized(self, client, sample_quest, auth_headers):
        """Test getting quests with authentication."""
        response = client.get("/api/sidequest/quests", headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "quests" in data["data"]
        assert "count" in data["data"]
        assert data["data"]["count"] == 1

    def test_select_quest_unauthorized(self, client):
        """Test selecting quest without authentication."""
        response = client.post("/api/sidequest/quests/1/select")
        assert response.status_code == 401

    def test_select_quest_authorized(self, client, sample_quest, auth_headers):
        """Test selecting quest with authentication."""

        response = client.post(
            f"/api/sidequest/quests/{sample_quest.id}/select", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert "Quest selected successfully" in data["data"]["message"]

    def test_complete_quest_unauthorized(self, client):
        """Test completing quest without authentication."""
        response = client.post("/api/sidequest/quests/1/complete", json={})
        assert response.status_code == 401

    def test_complete_quest_authorized(self, client, sample_quest, auth_headers):
        """Test completing quest with authentication."""
        feedback = {
            "feedback": {
                "rating": "thumbs_up",
                "comment": "Great quest!",
                "timeSpent": 12,
            }
        }

        response = client.post(
            f"/api/sidequest/quests/{sample_quest.id}/complete",
            json=feedback,
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert "Quest completed successfully" in data["data"]["message"]

    def test_skip_quest_unauthorized(self, client):
        """Test skipping quest without authentication."""
        response = client.post("/api/sidequest/quests/1/skip")
        assert response.status_code == 401

    def test_skip_quest_authorized(self, client, sample_quest, auth_headers):
        """Test skipping quest with authentication."""
        response = client.post(
            f"/api/sidequest/quests/{sample_quest.id}/skip", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert "Quest skipped successfully" in data["data"]["message"]

    def test_get_quest_history_unauthorized(self, client):
        """Test getting quest history without authentication."""
        response = client.get("/api/sidequest/history")
        assert response.status_code == 401

    def test_get_quest_history_authorized(self, client, sample_quest, auth_headers):
        """Test getting quest history with authentication."""
        response = client.get("/api/sidequest/history", headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "history" in data["data"]
        assert "user_id" in data["data"]

    def test_complete_onboarding_unauthorized(self, client):
        """Test completing onboarding without authentication."""
        response = client.post("/api/sidequest/onboarding/complete")
        assert response.status_code == 401

    def test_complete_onboarding_authorized(
        self, client, test_sidequest_user, auth_headers
    ):
        """Test completing onboarding with authentication."""
        response = client.post(
            "/api/sidequest/onboarding/complete", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert "Onboarding completed successfully" in data["data"]["message"]
        assert data["data"]["onboarding_completed"] is True

    @patch("backend.src.apple_auth_service.validate_apple_token")
    def test_mobile_apple_login_existing_user(
        self,
        mock_validate,
        client,
        test_sidequest_user,
    ):
        """Test Apple Sign-In with existing user"""
        # get the example test apple user from the db
        test_user = User.query.filter_by(apple_id="test_apple_id").first()
        # Mock the Apple validator to return valid claims
        mock_validate.return_value = {
            "sub": "test_apple_id",
            "email": test_user.email,
            "email_verified": True,
        }

        # Update the test user to have an apple_id
        test_sidequest_user.user.apple_id = "test_apple_id"
        db.session.commit()

        apple_credential = {
            "appleIdToken": {
                "identityToken": "mock_jwt_token",
                "fullName": {"givenName": "Updated", "familyName": "Name"},
            }
        }

        response = client.post(
            "/api/auth/mobile/login-with-apple",
            json=apple_credential,
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["id"] == test_user.id

    @patch("backend.src.apple_auth_service.validate_apple_token")
    def test_mobile_apple_login_new_user(self, mock_validate, client):
        """Test Apple Sign-In with new user registration"""
        # Mock the Apple validator to return valid claims for a new user
        mock_validate.return_value = {
            "sub": "new_apple_id",
            "email": "newuser@example.com",
            "email_verified": True,
        }

        apple_credential = {
            "appleIdToken": {
                "identityToken": "mock_jwt_token_new",
                "fullName": {"givenName": "New", "familyName": "User"},
            }
        }

        response = client.post(
            "/api/auth/mobile/login-with-apple",
            json=apple_credential,
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]

        # Verify new user was created
        from backend.models import User

        user = User.query.filter_by(apple_id="new_apple_id").first()
        assert user is not None
        assert user.email == "newuser@example.com"
        assert "New User" in user.name

    def test_mobile_apple_login_missing_credential(self, client):
        """Test Apple Sign-In with missing credential"""
        response = client.post(
            "/api/auth/mobile/login-with-apple",
            json={},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "No data provided" in data["error"]["message"]

    def test_mobile_apple_login_missing_identity_token(self, client):
        """Test Apple Sign-In with missing identity token"""
        response = client.post(
            "/api/auth/mobile/login-with-apple",
            json={"appleIdToken": {"fullName": {"givenName": "Test"}}},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "identityToken" in data["error"]["message"]
