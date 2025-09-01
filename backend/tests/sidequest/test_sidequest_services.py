import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.models import User
from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestGenerationLog,
    QuestRating,
    QuestStatus,
    SideQuest,
    SideQuestUser,
)
from backend.extensions import db
from backend.sidequest.services import QuestGenerationService, QuestService, UserService


class TestUserService:
    """Test UserService functionality."""

    def test_get_user_preferences(self, test_sidequest_user, app):
        """Test getting user preferences."""
        with app.app_context():
            from backend.extensions import db

            service = UserService(db.session)
            preferences = service.get_or_create_user_profile(
                test_sidequest_user.user_id
            )

        assert preferences is not None
        assert preferences.user_id == test_sidequest_user.user_id
        assert preferences.categories == test_sidequest_user.categories
        assert preferences.difficulty == test_sidequest_user.difficulty
        assert preferences.max_time == test_sidequest_user.max_time

    def test_update_user_profile(self, test_sidequest_user, app):
        """Test updating user preferences."""
        with app.app_context():
            from backend.extensions import db

            service = UserService(db.session)
            new_categories = ["outdoors", "learning"]
            new_difficulty = "hard"
            new_max_time = 30

            updated_preferences = service.update_user_profile(
                test_sidequest_user.user_id,
                {
                    "categories": new_categories,
                    "difficulty": new_difficulty,
                    "max_time": new_max_time,
                },
            )

            assert updated_preferences.categories == new_categories
            assert updated_preferences.difficulty == QuestDifficulty.HARD
            assert updated_preferences.max_time == new_max_time
            assert updated_preferences.updated_at is not None

    def test_complete_onboarding(self, test_sidequest_user, app):
        """Test completing user onboarding."""
        with app.app_context():
            from backend.extensions import db

            service = UserService(db.session)

            # Create a fresh profile to test onboarding completion
            fresh_profile = service.mark_onboarding_completed(
                test_sidequest_user.user_id
            )

            # Verify onboarding was marked as completed
            assert fresh_profile.onboarding_completed is True

            # Verify the profile was updated in the database
            db_profile = db.session.get(SideQuestUser, fresh_profile.id)
            assert db_profile.onboarding_completed is True

    def test_sidequest_user_delete(self, test_user, test_sidequest_user):
        """Test deleting a SideQuestUser."""
        # Delete the SideQuestUser
        db.session.delete(test_sidequest_user)
        db.session.commit()
        # Verify the SideQuestUser is deleted
        assert db.session.get(SideQuestUser, test_sidequest_user.id) is None


class TestQuestService:
    """Test QuestService functionality."""

    def test_get_user_quests(self, test_sidequest_user, test_quest, app):
        """Test getting user quests."""
        with app.app_context():
            from backend.extensions import db

            service = QuestService(db.session)
            quests = service.get_user_quests(test_sidequest_user.user_id)

        assert len(quests) >= 1
        assert any(q.id == test_quest.id for q in quests)

    def test_complete_quest(self, test_quest, app):
        """Test marking a quest as completed."""
        with app.app_context():
            from backend.extensions import db

            service = QuestService(db.session)

            feedback = {
                "rating": "thumbs_up",
                "comment": "Great workout!",
                "timeSpent": 20,
            }

            quest = service.complete_quest(
                test_quest.id,
                feedback["rating"],
                feedback["comment"],
                feedback["timeSpent"],
            )

            assert quest is not None

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, test_quest.id)
            assert updated_quest.status == QuestStatus.COMPLETED
            assert updated_quest.completed_at is not None
            assert updated_quest.feedback_rating == QuestRating.THUMBS_UP
            assert updated_quest.feedback_comment == "Great workout!"
            assert updated_quest.time_spent == 20


class TestQuestGenerationService:
    """Test QuestGenerationService functionality."""

    def test_generate_quests_success(self, test_sidequest_user, app):
        """Test successful quest generation."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

        # Mock OpenAI response
        from unittest.mock import Mock

        mock_client = Mock()
        mock_response = Mock()
        mock_response = json.dumps(
            {
                "quests": [
                    {
                        "text": "Do 10 jumping jacks",
                        "category": "fitness",
                        "estimated_time": "5 minutes",
                        "difficulty": "easy",
                        "tags": ["exercise", "quick"],
                    }
                ]
            }
        )
        mock_client.chat.return_value = mock_response
        service.client = mock_client

        preferences = {
            "categories": ["fitness"],
            "difficulty": "easy",
            "max_time": 15,
        }

        quests = service.generate_daily_quests(test_sidequest_user.user_id, preferences)

        assert len(quests) == 1
        assert quests[0].text == "Do 10 jumping jacks"
        assert quests[0].category == QuestCategory.FITNESS
        assert quests[0].difficulty == QuestDifficulty.EASY

    def test_generate_quests_fallback(self, test_sidequest_user, app):
        """Test quest generation with fallback when OpenAI fails."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

        # Mock OpenAI failure
        with patch.object(
            service.client,
            "chat",
            side_effect=Exception("OpenAI API error"),
        ):
            preferences = {
                "categories": ["fitness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            quests = service.generate_daily_quests(
                test_sidequest_user.user_id, preferences
            )

            # Should use fallback quests
            assert len(quests) > 0
            assert all(q.fallback_used for q in quests)


class TestServiceIntegration:
    """Test integration between different services."""

    def test_full_quest_lifecycle(self, test_sidequest_user):
        """Test a complete quest lifecycle from generation to completion."""
        quest_service = QuestService(db.session)
        generation_service = QuestGenerationService(db.session, "test_key")

        from unittest.mock import Mock

        mock_client = Mock()
        mock_response = Mock()
        mock_response = json.dumps(
            {
                "quests": [
                    {
                        "text": "Take a 10-minute walk",
                        "category": "outdoors",
                        "estimated_time": "10 minutes",
                        "difficulty": "easy",
                        "tags": ["exercise", "fresh_air"],
                    }
                ]
            }
        )
        mock_client.chat.return_value = mock_response
        generation_service.client = mock_client

        preferences = {
            "categories": ["outdoors"],
            "difficulty": "easy",
            "max_time": 15,
        }

        quests = generation_service.generate_daily_quests(
            test_sidequest_user.user_id, preferences
        )

        assert len(quests) == 1
        quest = quests[0]

        # Mark as selected
        quest = quest_service.accept_quest(quest.id)
        assert quest is not None

        # Verify the quest was marked as accepted
        updated_quest = db.session.get(SideQuest, quest.id)
        assert updated_quest.status == QuestStatus.ACCEPTED

        # Mark as completed
        quest = quest_service.complete_quest(
            quest.id,
            QuestRating.THUMBS_UP,
            "Great walk!",
            12,
        )
        assert quest is not None

        # Verify the quest was marked as completed
        updated_quest = db.session.get(SideQuest, quest.id)
        assert updated_quest.status == QuestStatus.COMPLETED
        assert updated_quest.completed_at is not None
        assert updated_quest.feedback_rating == QuestRating.THUMBS_UP
        assert updated_quest.time_spent == 12
