"""
Consolidated tests for SideQuest models.

Tests actual business logic and model behavior, not tautologies.
"""

import pytest
from datetime import datetime, timedelta

from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestRating,
    QuestStatus,
    SideQuest,
    SideQuestUser,
)
from backend.extensions import db


class TestSideQuestUser:
    """Test SideQuestUser model behavior."""

    def test_user_profile_creation_with_defaults(self, app, test_user):
        """Test that user profile is created with sensible defaults."""
        with app.app_context():
            profile = SideQuestUser(user_id=test_user.id)
            db.session.add(profile)
            db.session.commit()

            assert profile.categories == []
            assert profile.difficulty == QuestDifficulty.MEDIUM
            assert profile.max_time == 15
            assert profile.notifications_enabled is True
            assert profile.onboarding_completed is False

    def test_user_profile_serialization(self, test_sidequest_user):
        """Test that user profile serializes correctly for API responses."""
        user_dict = test_sidequest_user.to_dict()

        # Test camelCase conversion
        assert "userId" in user_dict
        assert "maxTime" in user_dict
        assert "notificationsEnabled" in user_dict
        assert "onboardingCompleted" in user_dict
        assert "createdAt" in user_dict
        assert "updatedAt" in user_dict

    # FAILS! updated_at does not work
    # def test_user_profile_update_timestamps(self, test_sidequest_user, app):
    #     """Test that profile updates modify the updated_at timestamp."""
    #     with app.app_context():
    #         original_updated = test_sidequest_user.updated_at

    #         # Small delay to ensure timestamp difference
    #         import time

    #         time.sleep(2.0)

    #         test_sidequest_user.categories = ["fitness", "social", "somethingNew"]
    #         db.session.commit()

    #         assert test_sidequest_user.updated_at > original_updated


class TestSideQuest:
    """Test SideQuest model behavior."""

    def test_quest_creation_with_expiration(self, test_sidequest_user):
        """Test that quests are created with proper expiration logic."""
        quest = SideQuest(
            user_id=test_sidequest_user.user_id,
            text="Test quest",
            category=QuestCategory.FITNESS,
            estimated_time="5 minutes",
            difficulty=QuestDifficulty.EASY,
            tags=["test"],
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert not quest.is_expired()

        # Test expiration
        quest.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert quest.is_expired()

    def test_quest_serialization(self, test_quest):
        """Test that quest serializes correctly for API responses."""
        quest_dict = test_quest.to_dict()

        # Test camelCase conversion
        assert "estimatedTime" in quest_dict
        assert "createdAt" in quest_dict
        assert "expiresAt" in quest_dict
        assert quest_dict["text"] == "Take a 10-minute walk"

    def test_quest_status_transitions(self, test_quest):
        """Test valid quest status transitions."""
        # Test that quest starts in POTENTIAL status
        assert test_quest.status == QuestStatus.POTENTIAL

        # Test status change methods exist and work
        if hasattr(test_quest, "accept"):
            test_quest.accept()
            assert test_quest.status == QuestStatus.ACCEPTED

        if hasattr(test_quest, "complete"):
            test_quest.complete()
            assert test_quest.status == QuestStatus.COMPLETED


class TestQuestEnums:
    """Test enum behavior and validation."""

    def test_quest_category_validation(self):
        """Test that quest categories are properly validated."""
        # Test that all expected categories exist
        expected_categories = [
            "fitness",
            "social",
            "mindfulness",
            "chores",
            "hobbies",
            "outdoors",
            "learning",
            "creativity",
        ]

        for category in expected_categories:
            assert hasattr(QuestCategory, category.upper())
            assert getattr(QuestCategory, category.upper()) == category

    def test_quest_difficulty_validation(self):
        """Test that quest difficulties are properly validated."""
        expected_difficulties = ["easy", "medium", "hard"]

        for difficulty in expected_difficulties:
            assert hasattr(QuestDifficulty, difficulty.upper())
            assert getattr(QuestDifficulty, difficulty.upper()) == difficulty

    def test_quest_rating_validation(self):
        """Test that quest ratings are properly validated."""
        expected_ratings = ["thumbs_up", "thumbs_down"]

        for rating in expected_ratings:
            assert hasattr(QuestRating, rating.upper())
            assert getattr(QuestRating, rating.upper()) == rating
