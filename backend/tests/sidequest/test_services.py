"""
Consolidated tests for SideQuest services.

Tests business logic, error handling, and integration between services.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.sidequest.models import (
    QuestDifficulty,
    QuestRating,
    QuestStatus,
)
from backend.extensions import db
from backend.sidequest.services import QuestGenerationService, QuestService, UserService


class TestUserService:
    """Test UserService business logic."""

    def test_get_or_create_user_profile_creates_new(self, app, test_user):
        """Test that service creates new profile when none exists."""
        with app.app_context():
            service = UserService(db.session)
            profile = service.get_or_create_user_profile(test_user.id)

            assert profile is not None
            assert profile.user_id == test_user.id
            assert profile.categories == []
            assert profile.difficulty == QuestDifficulty.MEDIUM
            assert profile.max_time == 15
            assert profile.onboarding_completed is False

    def test_get_or_create_user_profile_returns_existing(
        self, test_sidequest_user, app
    ):
        """Test that service returns existing profile when it exists."""
        with app.app_context():
            service = UserService(db.session)
            profile = service.get_or_create_user_profile(test_sidequest_user.user_id)

            assert profile.id == test_sidequest_user.id
            assert profile.categories == test_sidequest_user.categories

    def test_update_user_profile_validates_data(self, test_sidequest_user, app):
        """Test that profile updates validate and transform data correctly."""
        with app.app_context():
            service = UserService(db.session)

            new_preferences = {
                "categories": ["social", "learning"],
                "difficulty": "hard",
                "max_time": 30,
                "notifications_enabled": False,
            }

            updated_profile = service.update_user_profile(
                test_sidequest_user.user_id, new_preferences
            )

            assert updated_profile.categories == ["social", "learning"]
            assert updated_profile.difficulty == QuestDifficulty.HARD
            assert updated_profile.max_time == 30
            assert updated_profile.notifications_enabled is False

    def test_mark_onboarding_completed(self, test_sidequest_user, app):
        """Test that onboarding completion is properly tracked."""
        with app.app_context():
            service = UserService(db.session)

            # Initially not completed
            assert test_sidequest_user.onboarding_completed is True  # From fixture

            # Mark as completed (should be idempotent)
            updated_profile = service.mark_onboarding_completed(
                test_sidequest_user.user_id
            )
            assert updated_profile.onboarding_completed is True


class TestQuestService:
    """Test QuestService business logic."""

    def test_update_quest_status_with_feedback(self, test_quest, app):
        """Test that quest status updates handle feedback correctly."""
        with app.app_context():
            service = QuestService(db.session)

            feedback = {
                "rating": "thumbs_up",
                "comment": "Great workout!",
                "time_spent": 20,
            }

            quest = service.update_quest_status(
                test_quest.id,
                QuestStatus.COMPLETED,
                {"feedback": feedback},
            )

            assert quest is not None
            assert quest.status == QuestStatus.COMPLETED
            assert quest.completed_at is not None
            assert quest.feedback_rating == QuestRating.THUMBS_UP
            assert quest.feedback_comment == "Great workout!"
            assert quest.time_spent == 20

    def test_quest_status_transitions(self, test_quest, app):
        """Test that quest status transitions work correctly."""
        with app.app_context():
            service = QuestService(db.session)

            # Test multiple status changes
            quest = service.update_quest_status(test_quest.id, QuestStatus.ACCEPTED)
            assert quest.status == QuestStatus.ACCEPTED

            quest = service.update_quest_status(test_quest.id, QuestStatus.COMPLETED)
            assert quest.status == QuestStatus.COMPLETED

    def test_get_or_create_board(self, test_sidequest_user, app):
        """Test that quest board creation works correctly."""
        with app.app_context():
            service = QuestService(db.session)
            board = service.get_or_create_board(test_sidequest_user.user_id)

            assert board is not None
            assert board.user_id == test_sidequest_user.user_id
            assert board.is_active is True
            assert board.last_refreshed is not None

    def test_board_refresh_logic(self, test_sidequest_user_with_board, app):
        """Test that board refresh logic works correctly."""
        with app.app_context():
            service = QuestService(db.session)
            user = test_sidequest_user_with_board

            # Board should not need refresh initially
            assert service.board_needs_refresh(user.user_id) is False

            # Force board to need refresh
            board = service.get_board(user.user_id)
            board.last_refreshed = datetime.utcnow() - timedelta(days=1)
            db.session.commit()

            assert service.board_needs_refresh(user.user_id) is True


class TestQuestGenerationService:
    """Test QuestGenerationService business logic."""

    def test_fallback_quests_initialization(self, app):
        """Test that fallback quests are properly loaded."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            # Check that all categories have fallback quests
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
                assert category in service.fallback_quests
                assert len(service.fallback_quests[category]) > 0

                # Check quest structure
                for quest in service.fallback_quests[category]:
                    assert "text" in quest
                    assert "category" in quest
                    assert "estimated_time" in quest
                    assert "difficulty" in quest
                    assert "tags" in quest

    def test_time_estimate_parsing(self, app):
        """Test that time estimates are parsed correctly."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            # Test various formats
            assert service._parse_time_estimate("5 minutes") == 5
            assert service._parse_time_estimate("10 min") == 10
            assert service._parse_time_estimate("5-10 minutes") == 10
            assert service._parse_time_estimate("3-7 min") == 7

            # Test invalid formats return default
            assert service._parse_time_estimate("invalid") == 15
            assert service._parse_time_estimate("") == 15

    def test_quest_data_validation(self, app):
        """Test that quest data validation works correctly."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            # Valid quest data
            valid_quest = {
                "text": "Take a 10-minute walk",
                "category": "fitness",
                "estimated_time": "10 minutes",
                "difficulty": "easy",
                "tags": ["walking", "exercise"],
            }
            assert service._validate_quest_data(valid_quest) is True

            # Invalid quest data
            invalid_quests = [
                {"text": "Walk", "category": "fitness"},  # Missing fields
                {
                    "text": "Walk",
                    "category": "invalid",
                    "difficulty": "easy",
                    "tags": [],
                },  # Invalid category
                {
                    "text": "Walk",
                    "category": "fitness",
                    "difficulty": "invalid",
                    "tags": [],
                },  # Invalid difficulty
                {
                    "text": "W",
                    "category": "fitness",
                    "difficulty": "easy",
                    "tags": [],
                },  # Text too short
            ]

            for invalid_quest in invalid_quests:
                assert service._validate_quest_data(invalid_quest) is False

    def test_llm_generation_success(self, app):
        """Test successful LLM quest generation."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            # Mock successful LLM response
            mock_client = Mock()
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

            quests = service._generate_with_llm(preferences)

            assert len(quests) == 1
            assert quests[0]["text"] == "Do 10 jumping jacks"
            assert quests[0]["category"] == "fitness"

    def test_llm_generation_failure_fallback(self, app):
        """Test that LLM failures fall back to curated quests."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            # Mock LLM failure
            mock_client = Mock()
            mock_client.chat.side_effect = Exception("API Error")
            service.client = mock_client

            preferences = {
                "categories": ["fitness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            # Should raise exception for LLM failure
            with pytest.raises(Exception):
                service._generate_with_llm(preferences)

    def test_fallback_quest_generation(self, app):
        """Test fallback quest generation logic."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            preferences = {
                "categories": ["fitness", "mindfulness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            quests = service._generate_fallback_quests(preferences)

            assert len(quests) == 3
            for quest in quests:
                assert quest["category"] in preferences["categories"]
                assert quest["difficulty"] == preferences["difficulty"]
                time_minutes = service._parse_time_estimate(quest["estimated_time"])
                assert time_minutes <= preferences["max_time"]


class TestServiceIntegration:
    """Test integration between services."""

    def test_full_quest_lifecycle(self, test_sidequest_user, app):
        """Test complete quest lifecycle from generation to completion."""
        with app.app_context():
            quest_service = QuestService(db.session)

            # Mock quest generation
            mock_client = Mock()
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
            quest_service.quest_generation_service.client = mock_client

            # Generate quest
            quest_service.refresh_board(test_sidequest_user.user_id)
            quest = quest_service.get_board(test_sidequest_user.user_id).quests.first()
            assert quest is not None

            # Accept quest
            quest = quest_service.update_quest_status(quest.id, QuestStatus.ACCEPTED)
            assert quest.status == QuestStatus.ACCEPTED

            # Complete quest with feedback
            quest = quest_service.update_quest_status(
                quest.id,
                QuestStatus.COMPLETED,
                {
                    "feedback": {
                        "rating": QuestRating.THUMBS_UP,
                        "comment": "Great walk!",
                        "time_spent": 12,
                    }
                },
            )
            assert quest.status == QuestStatus.COMPLETED
            assert quest.completed_at is not None
            assert quest.feedback_rating == QuestRating.THUMBS_UP
            assert quest.time_spent == 12
