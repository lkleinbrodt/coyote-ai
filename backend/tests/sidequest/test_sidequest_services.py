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

    def test_update_user_preferences(self, test_sidequest_user, app):
        """Test updating user preferences."""
        with app.app_context():
            from backend.extensions import db

            service = UserService(db.session)
            new_categories = ["outdoors", "learning"]
            new_difficulty = "hard"
            new_max_time = 30

            updated_preferences = service.update_user_preferences(
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

    def test_mark_quest_completed(self, test_quest, app):
        """Test marking a quest as completed."""
        with app.app_context():
            from backend.extensions import db

            service = QuestService(db.session)

            feedback = {
                "rating": "thumbs_up",
                "comment": "Great workout!",
                "timeSpent": 20,
            }

            success = service.mark_quest_completed(
                test_quest.id, test_quest.user_id, feedback
            )

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, test_quest.id)
            assert updated_quest.completed is True
            assert updated_quest.completed_at is not None
            assert updated_quest.feedback_rating == QuestRating.THUMBS_UP
            assert updated_quest.feedback_comment == "Great workout!"
            assert updated_quest.time_spent == 20

    def test_mark_quest_skipped(self, test_quest, app):
        """Test marking a quest as skipped."""
        with app.app_context():
            from backend.extensions import db

            service = QuestService(db.session)

            success = service.mark_quest_skipped(test_quest.id, test_quest.user_id)

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, test_quest.id)
            assert updated_quest.skipped is True

    def test_mark_quest_selected(self, test_quest, app):
        """Test marking a quest as selected."""
        with app.app_context():
            from backend.extensions import db

            service = QuestService(db.session)

            success = service.mark_quest_selected(test_quest.id, test_quest.user_id)

            assert success is True

            # Verify quest was updated
            updated_quest = db.session.get(SideQuest, test_quest.id)
            assert updated_quest.selected is True


class TestQuestGenerationService:
    """Test QuestGenerationService functionality."""

    def test_generate_quests_success(self, test_sidequest_user, app):
        """Test successful quest generation."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "quests": [
                                {
                                    "text": "Do 10 push-ups",
                                    "category": "fitness",
                                    "estimated_time": "5-10 minutes",
                                    "difficulty": "easy",
                                    "tags": ["exercise", "strength"],
                                }
                            ]
                        }
                    )
                )
            )
        ]
        with patch.object(
            service.openai_client.chat.completions, "create", return_value=mock_response
        ):
            preferences = {
                "categories": ["fitness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            quests = service.generate_daily_quests(
                test_sidequest_user.user_id, preferences
            )

            assert len(quests) == 1
            assert quests[0].text == "Do 10 push-ups"
            assert quests[0].category == QuestCategory.FITNESS
            assert quests[0].difficulty == QuestDifficulty.EASY

    def test_generate_quests_fallback(self, test_sidequest_user, app):
        """Test quest generation with fallback when OpenAI fails."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

        # Mock OpenAI failure
        with patch.object(
            service.openai_client.chat.completions,
            "create",
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

        # Generate a quest
        with patch.object(
            generation_service.openai_client.chat.completions, "create"
        ) as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=json.dumps(
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
                    )
                )
            ]
            mock_openai.return_value = mock_response

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
            success = quest_service.mark_quest_selected(
                quest.id, test_sidequest_user.user_id
            )
            assert success is True

            # Verify the quest was marked as selected
            updated_quest = quest_service.db.query(SideQuest).get(quest.id)
            assert updated_quest.selected is True

            # Mark as completed
            success = quest_service.mark_quest_completed(
                quest.id,
                test_sidequest_user.user_id,
                {
                    "rating": QuestRating.THUMBS_UP.value,
                    "comment": "Great walk!",
                    "timeSpent": 12,
                },
            )
            assert success is True

            # Verify the quest was marked as completed
            updated_quest = quest_service.db.query(SideQuest).get(quest.id)
            assert updated_quest.completed is True
            assert updated_quest.feedback_rating == QuestRating.THUMBS_UP
            assert updated_quest.time_spent == 12
