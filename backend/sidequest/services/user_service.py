import json
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openai import OpenAI
import pytz
from sqlalchemy.orm import Session

from backend.extensions import create_logger

from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    SideQuestUser,
)
from backend.models import User


logger = create_logger(__name__)


class UserService:
    """Service for managing SideQuest user profiles and preferences"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_or_create_user_profile(self, user_id: int) -> SideQuestUser:
        """Get existing user profile or create a new one"""
        profile = self.db.query(SideQuestUser).filter_by(user_id=user_id).first()

        if not profile:
            profile = SideQuestUser(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            logger.info(f"Created new SideQuest profile for user {user_id}")

        return profile

    def update_user_profile(self, user_id: int, data: Dict[str, Any]) -> SideQuestUser:
        """Update user profile"""
        profile = self.get_or_create_user_profile(user_id)

        # Update preference fields
        if "categories" in data:
            quest_categories = [
                QuestCategory(category) for category in data["categories"]
            ]
            profile.set_categories(quest_categories)
        if "difficulty" in data:
            difficulty = QuestDifficulty(data["difficulty"])
            profile.set_difficulty(difficulty)
        if "max_time" in data:
            profile.max_time = data["max_time"]
        if "include_completed" in data:
            profile.include_completed = data["include_completed"]
        if "include_skipped" in data:
            profile.include_skipped = data["include_skipped"]
        if "additional_notes" in data:
            profile.additional_notes = data["additional_notes"]
        if "notifications_enabled" in data:
            profile.notifications_enabled = data["notifications_enabled"]
        if "notification_time" in data:
            profile.notification_time = data["notification_time"]
        if "timezone" in data:
            profile.timezone = data["timezone"]
        if "onboarding_completed" in data:
            profile.onboarding_completed = data["onboarding_completed"]

        profile.updated_at = datetime.now()
        self.db.commit()

        logger.info(f"Updated preferences for user {user_id}")
        return profile

    def mark_onboarding_completed(self, user_id: int) -> SideQuestUser:
        """Mark user's onboarding as completed"""
        profile = self.get_or_create_user_profile(user_id)
        profile.onboarding_completed = True
        profile.updated_at = datetime.now()
        self.db.commit()

        logger.info(f"Marked onboarding completed for user {user_id}")
        return profile

    def get_user_time(self, user_id: int) -> str:
        """Get the time of day for a user"""
        profile = self.get_or_create_user_profile(user_id)
        tz = profile.timezone
        return datetime.now(pytz.timezone(tz))

    def create_user(self, user_id: int, data: Dict[str, Any] = {}) -> SideQuestUser:
        """Create a new user"""
        exiting_user = SideQuestUser.query.filter_by(user_id=user_id).first()
        if exiting_user:
            raise ValueError(f"User {user_id} already exists")
        user = SideQuestUser(user_id=user_id, **data)
        self.db.add(user)
        self.db.commit()
        return user

    def reset_user_profile(self, user_id: int) -> SideQuestUser:
        """Reset user profile"""
        profile = self.get_or_create_user_profile(user_id)
        profile.reset()
        profile.updated_at = datetime.now()
        self.db.commit()
        return profile
