import pytest
from datetime import datetime, timedelta
from backend.sidequest.models import (
    SideQuestUser, SideQuest, QuestGenerationLog,
    QuestCategory, QuestDifficulty, QuestRating
)
from backend.models import User, UserBalance


class TestSideQuestUser:
    """Test SideQuestUser model functionality."""
    
    def test_create_sidequest_user(self, test_user):
        """Test creating a new SideQuest user."""
        sidequest_user = SideQuestUser(
            user_id=test_user.id,
            categories=["fitness", "mindfulness"],
            difficulty="medium",
            max_time=15,
            notifications_enabled=True,
            onboarding_completed=False
        )
        
        assert sidequest_user.user_id == test_user.id
        assert sidequest_user.categories == ["fitness", "mindfulness"]
        assert sidequest_user.difficulty == QuestDifficulty.MEDIUM
        assert sidequest_user.max_time == 15
        assert sidequest_user.notifications_enabled is True
        assert sidequest_user.onboarding_completed is False
    
    def test_sidequest_user_defaults(self, test_user):
        """Test SideQuest user default values."""
        sidequest_user = SideQuestUser(user_id=test_user.id)
        
        assert sidequest_user.categories == []
        assert sidequest_user.difficulty == QuestDifficulty.MEDIUM
        assert sidequest_user.max_time == 15
        assert sidequest_user.include_completed is True
        assert sidequest_user.include_skipped is True
        assert sidequest_user.notifications_enabled is True
        assert sidequest_user.timezone == "UTC"
        assert sidequest_user.onboarding_completed is False
    
    def test_sidequest_user_to_dict(self, test_sidequest_user):
        """Test SideQuest user serialization."""
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


class TestSideQuest:
    """Test SideQuest model functionality."""
    
    def test_create_quest(self, test_sidequest_user):
        """Test creating a new quest."""
        quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Test quest: Do 10 push-ups",
            category="fitness",
            estimated_time="5-10 minutes",
            difficulty="easy",
            tags=["exercise", "strength"]
        )
        
        assert quest.user_id == test_sidequest_user.id
        assert quest.text == "Test quest: Do 10 push-ups"
        assert quest.category == QuestCategory.FITNESS
        assert quest.estimated_time == "5-10 minutes"
        assert quest.difficulty == QuestDifficulty.EASY
        assert quest.tags == ["exercise", "strength"]
        assert quest.selected is False
        assert quest.completed is False
        assert quest.skipped is False
    
    def test_quest_expiration_default(self, test_sidequest_user):
        """Test quest expiration is set to end of day by default."""
        quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Test quest",
            category="fitness",
            estimated_time="5 minutes",
            difficulty="easy"
        )
        
        # Should expire at end of day
        tomorrow = datetime.utcnow() + timedelta(days=1)
        expected_expiry = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)
        
        assert quest.expires_at.date() == expected_expiry.date()
        assert quest.expires_at.hour == 23
        assert quest.expires_at.minute == 59
    
    def test_quest_custom_expiration(self, test_sidequest_user):
        """Test quest with custom expiration."""
        custom_expiry = datetime.now() + timedelta(hours=2)
        quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Test quest",
            category="fitness",
            estimated_time="5 minutes",
            difficulty="easy",
            expires_at=custom_expiry
        )
        
        assert quest.expires_at == custom_expiry
    
    def test_quest_mark_completed(self, test_quest):
        """Test marking a quest as completed."""
        feedback_rating = QuestRating.THUMBS_UP
        feedback_comment = "Great workout!"
        time_spent = 15
        
        test_quest.mark_completed(feedback_rating, feedback_comment, time_spent)
        
        assert test_quest.completed is True
        assert test_quest.completed_at is not None
        assert test_quest.feedback_rating == feedback_rating
        assert test_quest.feedback_comment == feedback_comment
        assert test_quest.time_spent == time_spent
        assert test_quest.updated_at is not None
    
    def test_quest_mark_skipped(self, test_quest):
        """Test marking a quest as skipped."""
        test_quest.mark_skipped()
        
        assert test_quest.skipped is True
        assert test_quest.updated_at is not None
    
    def test_quest_mark_selected(self, test_quest):
        """Test marking a quest as selected."""
        test_quest.mark_selected()
        
        assert test_quest.selected is True
        assert test_quest.updated_at is not None
    
    def test_quest_is_expired(self, test_sidequest_user):
        """Test quest expiration check."""
        # Create expired quest
        expired_quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Expired quest",
            category="fitness",
            estimated_time="5 minutes",
            difficulty="easy",
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        assert expired_quest.is_expired() is True
        
        # Create future quest
        future_quest = SideQuest(
            user_id=test_sidequest_user.id,
            text="Future quest",
            category="fitness",
            estimated_time="5 minutes",
            difficulty="easy",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert future_quest.is_expired() is False
    
    def test_quest_to_dict(self, test_quest):
        """Test quest serialization."""
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


class TestQuestGenerationLog:
    """Test QuestGenerationLog model functionality."""
    
    def test_create_generation_log(self, test_sidequest_user):
        """Test creating a new generation log."""
        log = QuestGenerationLog(
            user_id=test_sidequest_user.id,
            request_preferences={
                "categories": ["fitness"],
                "difficulty": "medium",
                "max_time": 15
            },
            quests_generated=3,
            model_used="gpt-4",
            generation_time_ms=1500
        )
        
        assert log.user_id == test_sidequest_user.id
        assert log.request_preferences["categories"] == ["fitness"]
        assert log.request_preferences["difficulty"] == "medium"
        assert log.quests_generated == 3
        assert log.model_used == "gpt-4"
        assert log.generation_time_ms == 1500
        assert log.fallback_used is False
    
    def test_generation_log_to_dict(self, test_generation_log):
        """Test generation log serialization."""
        log_dict = test_generation_log.to_dict()
        
        assert "id" in log_dict
        assert "user_id" in log_dict
        assert "request_preferences" in log_dict
        assert "quests_generated" in log_dict
        assert "model_used" in log_dict
        assert "fallback_used" in log_dict
        assert "generation_time_ms" in log_dict
        assert "created_at" in log_dict


class TestModelRelationships:
    """Test relationships between models."""
    
    def test_user_sidequest_relationship(self, test_user, test_sidequest_user):
        """Test relationship between User and SideQuestUser."""
        assert test_user.sidequest_profile == test_sidequest_user
        assert test_sidequest_user.user == test_user
    
    def test_sidequest_user_quests_relationship(self, test_user, test_sidequest_user, test_quest):
        """Test relationship between User and SideQuest through SideQuestUser."""
        # The quest should be linked to the main user
        assert test_quest.user_id == test_user.id
        # The quest should be accessible through the user's sidequest_quests relationship
        assert test_quest in test_user.sidequest_quests
    
    def test_sidequest_user_generation_logs_relationship(self, test_user, test_sidequest_user, test_generation_log):
        """Test relationship between User and QuestGenerationLog through SideQuestUser."""
        # The generation log should be linked to the main user
        assert test_generation_log.user_id == test_user.id
        # The generation log should be accessible through the user's sidequest_generation_logs relationship
        assert test_generation_log in test_user.sidequest_generation_logs
