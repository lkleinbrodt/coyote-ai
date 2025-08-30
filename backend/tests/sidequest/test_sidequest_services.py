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
from backend.sidequest.services import QuestGenerationService, QuestService, UserService


class TestUserService:
    """Test UserService functionality."""

    def test_get_user_preferences(self, test_sidequest_user):
        """Test getting user preferences."""
        service = UserService()
        preferences = service.get_user_preferences(test_sidequest_user.user_id)

        assert preferences is not None
        assert preferences.user_id == test_sidequest_user.user_id
        assert preferences.categories == test_sidequest_user.categories
        assert preferences.difficulty == test_sidequest_user.difficulty
        assert preferences.max_time == test_sidequest_user.max_time

    def test_update_user_preferences(self, test_sidequest_user):
        """Test updating user preferences."""
        service = UserService()
        new_categories = ["outdoors", "learning"]
        new_difficulty = "hard"
        new_max_time = 30

        updated_preferences = service.update_user_preferences(
            test_sidequest_user.user_id,
            categories=new_categories,
            difficulty=new_difficulty,
            max_time=new_max_time,
        )

        assert updated_preferences.categories == new_categories
        assert updated_preferences.difficulty == QuestDifficulty.HARD
        assert updated_preferences.max_time == new_max_time
        assert updated_preferences.updated_at is not None

    def test_complete_onboarding(self, test_sidequest_user):
        """Test completing user onboarding."""
        service = UserService()

        # Initially should be False
        assert test_sidequest_user.onboarding_completed is False

        # Complete onboarding
        service.complete_onboarding(test_sidequest_user.user_id)

        # Refresh from database
        from backend.extensions import db

        db.session.refresh(test_sidequest_user)

        assert test_sidequest_user.onboarding_completed is True


class TestQuestService:
    """Test QuestService functionality."""

    def test_get_user_quests(self, test_sidequest_user, test_quest):
        """Test getting user quests."""
        service = QuestService()
        quests = service.get_user_quests(test_sidequest_user.user_id)

        assert len(quests) >= 1
        assert any(q.id == test_quest.id for q in quests)

    def test_get_quest_by_id(self, test_quest):
        """Test getting a specific quest by ID."""
        service = QuestService()
        quest = service.get_quest_by_id(test_quest.id)

        assert quest is not None
        assert quest.id == test_quest.id
        assert quest.text == test_quest.text

    def test_mark_quest_completed(self, test_quest):
        """Test marking a quest as completed."""
        service = QuestService()
        feedback_rating = QuestRating.THUMBS_UP
        feedback_comment = "Great workout!"
        time_spent = 20

        updated_quest = service.mark_quest_completed(
            test_quest.id,
            feedback_rating=feedback_rating,
            feedback_comment=feedback_comment,
            time_spent=time_spent,
        )

        assert updated_quest.completed is True
        assert updated_quest.completed_at is not None
        assert updated_quest.feedback_rating == feedback_rating
        assert updated_quest.feedback_comment == feedback_comment
        assert updated_quest.time_spent == time_spent

    def test_mark_quest_skipped(self, test_quest):
        """Test marking a quest as skipped."""
        service = QuestService()

        updated_quest = service.mark_quest_skipped(test_quest.id)

        assert updated_quest.skipped is True
        assert updated_quest.updated_at is not None

    def test_mark_quest_selected(self, test_quest):
        """Test marking a quest as selected."""
        service = QuestService()

        updated_quest = service.mark_quest_selected(test_quest.id)

        assert updated_quest.selected is True
        assert updated_quest.updated_at is not None

    def test_get_expired_quests(self, test_sidequest_user):
        """Test getting expired quests."""
        service = QuestService()

        # Create an expired quest
        expired_quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Expired quest",
            category="fitness",
            estimated_time="5 minutes",
            difficulty="easy",
            expires_at=datetime.now() - timedelta(hours=1),
        )
        from backend.extensions import db

        db.session.add(expired_quest)
        db.session.commit()

        expired_quests = service.get_expired_quests(test_sidequest_user.user_id)

        assert len(expired_quests) >= 1
        assert any(q.id == expired_quest.id for q in expired_quests)

    def test_get_quests_by_category(self, test_sidequest_user, test_quest):
        """Test getting quests by category."""
        service = QuestService()
        fitness_quests = service.get_quests_by_category(
            test_sidequest_user.user_id, "fitness"
        )

        assert len(fitness_quests) >= 1
        assert all(q.category == QuestCategory.FITNESS for q in fitness_quests)


class TestQuestGenerationService:
    """Test QuestGenerationService functionality."""

    @patch("backend.sidequest.services.openai.ChatCompletion.create")
    def test_generate_quests_success(self, mock_openai, test_sidequest_user):
        """Test successful quest generation."""
        service = QuestGenerationService()

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""[
                        {
                            "text": "Do 10 push-ups",
                            "category": "fitness",
                            "estimated_time": "5-10 minutes",
                            "difficulty": "easy",
                            "tags": ["exercise", "strength"]
                        }
                    ]"""
                )
            )
        ]
        mock_openai.return_value = mock_response

        preferences = {"categories": ["fitness"], "difficulty": "easy", "max_time": 15}

        quests = service.generate_quests(test_sidequest_user.user_id, preferences)

        assert len(quests) == 1
        assert quests[0].text == "Do 10 push-ups"
        assert quests[0].category == QuestCategory.FITNESS
        assert quests[0].difficulty == QuestDifficulty.EASY

    @patch("backend.sidequest.services.openai.ChatCompletion.create")
    def test_generate_quests_fallback(self, mock_openai, test_sidequest_user):
        """Test quest generation with fallback when OpenAI fails."""
        service = QuestGenerationService()

        # Mock OpenAI failure
        mock_openai.side_effect = Exception("OpenAI API error")

        preferences = {"categories": ["fitness"], "difficulty": "easy", "max_time": 15}

        quests = service.generate_quests(test_sidequest_user.user_id, preferences)

        # Should use fallback quests
        assert len(quests) > 0
        assert all(q.fallback_used for q in quests)

    def test_log_generation_request(self, test_sidequest_user):
        """Test logging a generation request."""
        service = QuestGenerationService()

        preferences = {
            "categories": ["fitness"],
            "difficulty": "medium",
            "max_time": 20,
        }

        context_data = {"weather": "sunny", "mood": "energetic"}

        log = service.log_generation_request(
            test_sidequest_user.user_id,
            preferences,
            context_data,
            quests_generated=3,
            model_used="gpt-4",
            generation_time_ms=2000,
        )

        assert log.user_id == test_sidequest_user.id
        assert log.request_preferences == preferences
        assert log.context_data == context_data
        assert log.quests_generated == 3
        assert log.model_used == "gpt-4"
        assert log.generation_time_ms == 2000
        assert log.fallback_used is False


class TestServiceIntegration:
    """Test integration between different services."""

    def test_full_quest_lifecycle(self, test_sidequest_user):
        """Test a complete quest lifecycle from generation to completion."""
        quest_service = QuestService()
        generation_service = QuestGenerationService()

        # Generate a quest
        with patch(
            "backend.sidequest.services.openai.ChatCompletion.create"
        ) as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content="""[
                            {
                                "text": "Take a 10-minute walk",
                                "category": "outdoors",
                                "estimated_time": "10 minutes",
                                "difficulty": "easy",
                                "tags": ["exercise", "fresh_air"]
                            }
                        ]"""
                    )
                )
            ]
            mock_openai.return_value = mock_response

            preferences = {
                "categories": ["outdoors"],
                "difficulty": "easy",
                "max_time": 15,
            }

            quests = generation_service.generate_quests(
                test_sidequest_user.user_id, preferences
            )

            assert len(quests) == 1
            quest = quests[0]

            # Mark as selected
            selected_quest = quest_service.mark_quest_selected(quest.id)
            assert selected_quest.selected is True

            # Mark as completed
            completed_quest = quest_service.mark_quest_completed(
                quest.id,
                feedback_rating=QuestRating.THUMBS_UP,
                feedback_comment="Great walk!",
                time_spent=12,
            )

            assert completed_quest.completed is True
            assert completed_quest.feedback_rating == QuestRating.THUMBS_UP
            assert completed_quest.time_spent == 12
