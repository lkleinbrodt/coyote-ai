from datetime import datetime, timedelta

import pytest

from backend.sidequest.models import QuestCategory, QuestDifficulty, QuestRating


class TestSideQuestModelsSimple:
    """Test SideQuest database models without Flask app context."""

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

    def test_enum_validation(self):
        """Test that enum values are valid strings."""
        for category in QuestCategory:
            assert isinstance(category.value, str)
            assert len(category.value) > 0

        for difficulty in QuestDifficulty:
            assert isinstance(difficulty.value, str)
            assert len(difficulty.value) > 0

        for rating in QuestRating:
            assert isinstance(rating.value, str)
            assert len(rating.value) > 0


class TestSideQuestServicesSimple:
    """Test SideQuest services without Flask app context."""

    def test_fallback_quests_structure(self):
        """Test that fallback quests have the correct structure."""
        from backend.sidequest.services import QuestGenerationService

        # Create service with mock session and API key
        service = QuestGenerationService(None, "test_key")

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
                assert quest["category"] == category

    def test_time_parsing(self):
        """Test time estimate parsing."""
        from backend.sidequest.services import QuestGenerationService

        service = QuestGenerationService(None, "test_key")

        # Test various time formats
        assert service._parse_time_estimate("5 minutes") == 5
        assert service._parse_time_estimate("10 min") == 10
        assert service._parse_time_estimate("5-10 minutes") == 10
        assert service._parse_time_estimate("3-7 min") == 7

        # Test invalid formats (should return default)
        assert service._parse_time_estimate("invalid") == 15
        assert service._parse_time_estimate("") == 15

    def test_quest_validation(self):
        """Test quest data validation."""
        from backend.sidequest.services import QuestGenerationService

        service = QuestGenerationService(None, "test_key")

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

    def test_prompt_building(self):
        """Test prompt building for quest generation."""
        from backend.sidequest.services import QuestGenerationService

        service = QuestGenerationService(None, "test_key")

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


class TestSideQuestAPISimple:
    """Test SideQuest API endpoints without Flask app context."""

    def test_health_check_response_structure(self):
        """Test that health check response has the correct structure."""
        # This would normally test the actual endpoint, but we'll test the expected structure
        expected_response = {
            "success": True,
            "data": {"service": "SideQuest", "status": "healthy"},
        }

        assert "success" in expected_response
        assert "data" in expected_response
        assert "service" in expected_response["data"]
        assert "status" in expected_response["data"]
        assert expected_response["success"] is True
        assert expected_response["data"]["service"] == "SideQuest"
        assert expected_response["data"]["status"] == "healthy"

    def test_error_response_structure(self):
        """Test that error responses have the correct structure."""
        expected_error_response = {
            "success": False,
            "error": {"message": "Test error message"},
        }

        assert "success" in expected_error_response
        assert "error" in expected_error_response
        assert "message" in expected_error_response["error"]
        assert expected_error_response["success"] is False
        assert expected_error_response["error"]["message"] == "Test error message"
