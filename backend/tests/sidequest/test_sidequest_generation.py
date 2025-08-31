import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from backend.extensions import db
from backend.sidequest.models import QuestCategory, QuestDifficulty
from backend.sidequest.services import QuestGenerationService


class TestQuestGenerationService:
    """Test the QuestGenerationService class."""

    def test_fallback_quests_initialization(self, app):
        """Test that fallback quests are properly initialized."""
        with app.app_context():
            from backend.extensions import db

            service = QuestGenerationService(db.session, "test_key")

            # Check that all categories have fallback quests
            assert "fitness" in service.fallback_quests
            assert "social" in service.fallback_quests
            assert "mindfulness" in service.fallback_quests
            assert "chores" in service.fallback_quests
            assert "hobbies" in service.fallback_quests
            assert "outdoors" in service.fallback_quests
            assert "learning" in service.fallback_quests
            assert "creativity" in service.fallback_quests

            # Check that each category has quests
            for category, quests in service.fallback_quests.items():
                assert len(quests) > 0
                for quest in quests:
                    assert "text" in quest
                    assert "category" in quest
                    assert "estimated_time" in quest
                    assert "difficulty" in quest
                    assert "tags" in quest

    def test_parse_time_estimate(self, app):
        """Test time estimate parsing."""
        with app.app_context():
            from backend.extensions import db

            service = QuestGenerationService(db.session, "test_key")

            # Test various time formats
            assert service._parse_time_estimate("5 minutes") == 5
            assert service._parse_time_estimate("10 min") == 10
            assert service._parse_time_estimate("5-10 minutes") == 10
            assert service._parse_time_estimate("3-7 min") == 7

            # Test invalid formats (should return default)
            assert service._parse_time_estimate("invalid") == 15
            assert service._parse_time_estimate("") == 15

    def test_validate_quest_data(self, app):
        """Test quest data validation."""
        with app.app_context():
            from backend.extensions import db

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

            # Missing required field
            invalid_quest = {
                "text": "Take a walk",
                "category": "fitness",
                "estimated_time": "10 minutes",
                "difficulty": "easy",
                # Missing tags
            }
            assert service._validate_quest_data(invalid_quest) is False

            # Invalid category
            invalid_category_quest = {
                "text": "Take a walk",
                "category": "invalid_category",
                "estimated_time": "10 minutes",
                "difficulty": "easy",
                "tags": ["walking"],
            }
            assert service._validate_quest_data(invalid_category_quest) is False

            # Invalid difficulty
            invalid_difficulty_quest = {
                "text": "Take a walk",
                "category": "fitness",
                "estimated_time": "10 minutes",
                "difficulty": "invalid_difficulty",
                "tags": ["walking"],
            }
            assert service._validate_quest_data(invalid_difficulty_quest) is False

            # Text too short
            short_text_quest = {
                "text": "Walk",  # Too short
                "category": "fitness",
                "estimated_time": "10 minutes",
                "difficulty": "easy",
                "tags": ["walking"],
            }
            assert service._validate_quest_data(short_text_quest) is False

    def test_build_quest_generation_prompt(self, app):
        """Test prompt building for quest generation."""
        with app.app_context():
            from backend.extensions import db

            service = QuestGenerationService(db.session, "test_key")

            preferences = {
                "categories": ["fitness", "mindfulness"],
                "difficulty": "easy",
                "max_time": 15,
                "include_completed": True,
                "include_skipped": True,
            }

            context = {"weather": "sunny", "mood": "energetic"}

            prompt = service._build_quest_generation_prompt(preferences, context)

            # Check that preferences are included
            assert "fitness, mindfulness" in prompt
            assert "easy" in prompt
            assert "15" in prompt

            # Check that context is included
            assert "sunny" in prompt
            assert "energetic" in prompt

            # Check that requirements are included
            assert "achievable within 15 minutes" in prompt
            assert "fun, creative, and engaging" in prompt

    def test_generate_fallback_quests(self, app):
        """Test fallback quest generation."""
        with app.app_context():
            service = QuestGenerationService(db.session, "test_key")

            preferences = {
                "categories": ["fitness", "mindfulness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            quests = service._generate_fallback_quests(preferences)

            # Should return 3 quests
            assert len(quests) == 3

            # All quests should match preferences
            for quest in quests:
                assert quest["category"] in preferences["categories"]
                assert quest["difficulty"] == preferences["difficulty"]
                # Time should be within limit
                time_minutes = service._parse_time_estimate(quest["estimated_time"])
                assert time_minutes <= preferences["max_time"]

    def test_generate_with_llm_success(self, app):
        """Test successful LLM quest generation."""
        with app.app_context():
            from backend.extensions import db

            service = QuestGenerationService(db.session, "test_key")

            # Mock the OpenAI client at the instance level
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

            quests = service._generate_with_llm(preferences)

            # Should return the generated quest
            assert len(quests) == 1
            assert quests[0]["text"] == "Do 10 jumping jacks"
            assert quests[0]["category"] == "fitness"
            assert quests[0]["difficulty"] == "easy"

    def test_generate_with_llm_failure(self, app):
        """Test LLM quest generation failure."""
        with app.app_context():
            from backend.extensions import db

            service = QuestGenerationService(db.session, "test_key")

            # Mock OpenAI failure
            mock_client = Mock()
            mock_client.chat.side_effect = Exception("API Error")
            service.client = mock_client

            preferences = {
                "categories": ["fitness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            # Should raise exception
            with pytest.raises(Exception):
                service._generate_with_llm(preferences)

    def test_generate_daily_quests_llm_success(self, app):
        """Test successful daily quest generation with LLM."""
        with app.app_context():
            from backend.extensions import db
            from backend.models import User

            service = QuestGenerationService(db.session, "test_key")

            # Mock the OpenAI client at the instance level
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
                        },
                        {
                            "text": "Take 5 deep breaths",
                            "category": "mindfulness",
                            "estimated_time": "2 minutes",
                            "difficulty": "easy",
                            "tags": ["breathing", "calm"],
                        },
                        {
                            "text": "Organize one drawer",
                            "category": "chores",
                            "estimated_time": "10 minutes",
                            "difficulty": "easy",
                            "tags": ["organization", "tidiness"],
                        },
                    ]
                }
            )
            mock_client.chat.return_value = mock_response
            service.client = mock_client

            preferences = {
                "categories": ["fitness", "mindfulness", "chores"],
                "difficulty": "easy",
                "max_time": 15,
            }

            # Create User record first (required for foreign key constraint)
            user = User(id=1001)
            db.session.add(user)
            db.session.commit()

            # Mock user profile with unique user ID
            from backend.sidequest.models import SideQuestUser

            user_profile = SideQuestUser(user_id=1001)
            db.session.add(user_profile)
            db.session.commit()

            quests = service.generate_daily_quests(1001, preferences)

            # Should return 3 quests
            assert len(quests) == 3

            # All quests should be saved to database
            for quest in quests:
                assert quest.id is not None
                assert quest.user_id == 1001
                assert quest.fallback_used is False
                assert quest.model_used == "meta-llama/llama-3.3-70b-instruct"

    def test_generate_daily_quests_fallback(self, app):
        """Test daily quest generation falling back to curated quests."""
        with app.app_context():
            from backend.extensions import db
            from backend.models import User

            service = QuestGenerationService(db.session, "test_key")

            # Mock OpenAI failure
            mock_client = Mock()
            mock_client.chat.side_effect = Exception("API Error")
            service.client = mock_client

            preferences = {
                "categories": ["fitness", "mindfulness"],
                "difficulty": "easy",
                "max_time": 15,
            }

            # Create User record first (required for foreign key constraint)
            user = User(id=1002)
            db.session.add(user)
            db.session.commit()

            # Mock user profile with unique user ID
            from backend.sidequest.models import SideQuestUser

            user_profile = SideQuestUser(user_id=1002)
            db.session.add(user_profile)
            db.session.commit()

            quests = service.generate_daily_quests(1002, preferences)

            # Should return 3 fallback quests
            assert len(quests) == 3

            # All quests should be marked as fallback
            for quest in quests:
                assert quest.id is not None
                assert quest.user_id == 1002
                assert quest.fallback_used is True
                assert quest.model_used is None
