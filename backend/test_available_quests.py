#!/usr/bin/env python3
"""
Test script for the new available quests functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from backend.extensions import db
from backend.sidequest.models import (
    SideQuest,
    SideQuestUser,
    QuestCategory,
    QuestDifficulty,
)
from backend.sidequest.services import QuestService
from backend.models import User


def test_available_quests():
    """Test the get_available_quests functionality"""

    # Create a test user
    user = User(email="test@example.com", username="testuser", apple_id="test_apple_id")
    db.session.add(user)
    db.session.commit()

    # Create user preferences
    user_prefs = SideQuestUser(
        user_id=user.id,
        categories=["fitness", "social"],
        difficulty=QuestDifficulty.EASY,
        max_time=15,
    )
    db.session.add(user_prefs)
    db.session.commit()

    # Create some test quests
    now = datetime.utcnow()

    # Quest 1: Open quest within generation window (should be available)
    quest1 = SideQuest(
        user_id=user.id,
        text="Do 10 jumping jacks",
        category=QuestCategory.FITNESS,
        estimated_time="5 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["exercise", "quick"],
        generated_at=now - timedelta(hours=12),  # 12 hours ago
        expires_at=now + timedelta(hours=12),
    )
    db.session.add(quest1)

    # Quest 2: Completed quest (should not be available)
    quest2 = SideQuest(
        user_id=user.id,
        text="Take a walk",
        category=QuestCategory.FITNESS,
        estimated_time="10 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["walking", "outdoors"],
        completed=True,
        generated_at=now - timedelta(hours=6),
        expires_at=now + timedelta(hours=18),
    )
    db.session.add(quest2)

    # Quest 3: Quest outside generation window (should not be available)
    quest3 = SideQuest(
        user_id=user.id,
        text="Old quest",
        category=QuestCategory.SOCIAL,
        estimated_time="5 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["social"],
        generated_at=now - timedelta(hours=30),  # 30 hours ago
        expires_at=now + timedelta(hours=6),
    )
    db.session.add(quest3)

    db.session.commit()

    # Test the service
    quest_service = QuestService(db.session)
    available_quests = quest_service.get_available_quests(user.id)

    print(f"User ID: {user.id}")
    print(f"Available quests: {len(available_quests)}")

    for quest in available_quests:
        print(f"  - {quest.text} (generated: {quest.generated_at})")

    # Clean up
    db.session.delete(quest1)
    db.session.delete(quest2)
    db.session.delete(quest3)
    db.session.delete(user_prefs)
    db.session.delete(user)
    db.session.commit()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    test_available_quests()
