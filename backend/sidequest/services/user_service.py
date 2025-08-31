import json
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from backend.extensions import create_logger

from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestGenerationLog,
    QuestRating,
    SideQuest,
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

    def update_user_profile(
        self, user_id: int, preferences: Dict[str, Any]
    ) -> SideQuestUser:
        """Update user profile"""
        profile = self.get_or_create_user_profile(user_id)

        # Update preference fields
        if "categories" in preferences:
            profile.categories = preferences["categories"]
        if "difficulty" in preferences:
            profile.difficulty = QuestDifficulty(preferences["difficulty"])
        if "max_time" in preferences:
            profile.max_time = preferences["max_time"]
        if "include_completed" in preferences:
            profile.include_completed = preferences["include_completed"]
        if "include_skipped" in preferences:
            profile.include_skipped = preferences["include_skipped"]
        if "notifications_enabled" in preferences:
            profile.notifications_enabled = preferences["notifications_enabled"]
        if "notification_time" in preferences:
            profile.notification_time = preferences["notification_time"]
        if "timezone" in preferences:
            profile.timezone = preferences["timezone"]
        if "onboarding_completed" in preferences:
            profile.onboarding_completed = preferences["onboarding_completed"]

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
