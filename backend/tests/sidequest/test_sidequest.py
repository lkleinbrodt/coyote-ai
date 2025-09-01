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
    QuestStatus,
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
        assert "userId" in user_dict
        assert "categories" in user_dict
        assert "difficulty" in user_dict
        assert "maxTime" in user_dict
        assert "notificationsEnabled" in user_dict
        assert "onboardingCompleted" in user_dict
        assert "createdAt" in user_dict
        assert "updatedAt" in user_dict

    def test_quest_creation(self, test_quest):
        """Test SideQuest creation and properties."""
        assert test_quest.user_id is not None
        assert test_quest.text == "Take a 10-minute walk"
        assert test_quest.category == QuestCategory.FITNESS
        assert test_quest.estimated_time == "10 minutes"
        assert test_quest.difficulty == QuestDifficulty.EASY
        assert test_quest.tags == ["walking", "exercise", "outdoors"]
        assert test_quest.status == QuestStatus.POTENTIAL
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
        assert "status" in quest_dict
        assert "createdAt" in quest_dict
        assert "expiresAt" in quest_dict

    def test_quest_expiration(self, test_quest):
        """Test quest expiration logic."""
        # Quest should not be expired when just created
        assert not test_quest.is_expired()

        # Set expiration to past
        test_quest.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert test_quest.is_expired()


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
        """Test UserService update_user_profile."""
        with app.app_context():
            from backend.extensions import db

            user_service = UserService(db.session)

            new_preferences = {
                "categories": ["social", "learning"],
                "difficulty": "hard",
                "max_time": 30,
                "notifications_enabled": False,
            }

            updated_profile = user_service.update_user_profile(
                test_sidequest_user.user_id, new_preferences
            )

            assert updated_profile.categories == ["social", "learning"]
            assert updated_profile.difficulty == QuestDifficulty.HARD
            assert updated_profile.max_time == 30
            assert updated_profile.notifications_enabled is False

    def test_quest_update_status(self, sample_quest, app):
        """Test QuestService update_quest_status."""
        with app.app_context():
            from backend.extensions import db

            quest_service = QuestService(db.session)
            assert sample_quest.status == QuestStatus.POTENTIAL
            quest = db.session.query(SideQuest).filter_by(id=sample_quest.id).first()
            quest_service.update_quest_status(sample_quest.id, QuestStatus.ABANDONED)
            assert quest.status == QuestStatus.ABANDONED
            quest_service.update_quest_status(sample_quest.id, QuestStatus.ACCEPTED)
            assert quest.status == QuestStatus.ACCEPTED
            quest_service.update_quest_status(
                sample_quest.id,
                QuestStatus.COMPLETED,
                {
                    "feedback": {
                        "rating": QuestRating.THUMBS_UP,
                        "comment": "Great quest!",
                        "timeSpent": 10,
                    }
                },
            )
            assert quest.status == QuestStatus.COMPLETED
            quest_service.update_quest_status(sample_quest.id, QuestStatus.FAILED)
            assert quest.status == QuestStatus.FAILED
            quest_service.update_quest_status(sample_quest.id, QuestStatus.DECLINED)
            assert quest.status == QuestStatus.DECLINED


class TestSideQuestAPI:
    """Test SideQuest API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/sidequest/health")
        assert response.status_code == 200

        data = response.get_json()

        assert data["data"]["service"] == "SideQuest"
        assert data["data"]["status"] == "healthy"

    def test_get_user_preferences_unauthorized(self, client):
        """Test getting preferences without authentication."""
        response = client.get("/api/sidequest/me")
        assert response.status_code == 401

        data = response.get_json()
        print(data)
        assert "error" in data
        assert data["error"]["message"] == "Authentication required"
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_get_user_preferences_authorized(
        self, client, test_sidequest_user, auth_headers
    ):
        """Test getting preferences with authentication."""
        response = client.get("/api/sidequest/me", headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert all(
            key in data["data"]
            for key in [
                "categories",
                "difficulty",
                "maxTime",
                "includeCompleted",
                "includeSkipped",
                "notificationsEnabled",
                "notificationTime",
                "timezone",
                "onboardingCompleted",
            ]
        )
        assert "userId" in data["data"]

    def test_update_user_profile_unauthorized(self, client):
        """Test updating preferences without authentication."""
        response = client.put("/api/sidequest/me", json={})
        assert response.status_code == 401

    def test_update_user_profile_authorized(
        self, client, test_sidequest_user, auth_headers, quest_preferences
    ):
        """Test updating preferences with authentication."""
        response = client.put(
            "/api/sidequest/me", json=quest_preferences, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert "message" in data["data"]
        assert "preferences" in data["data"]
        assert "userId" in data["data"]["preferences"]

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
        assert "message" in data["data"]
        assert "Onboarding completed successfully" in data["data"]["message"]
        assert data["data"]["preferences"]["onboardingCompleted"] is True
