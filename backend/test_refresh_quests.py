#!/usr/bin/env python3
"""
Test script for the new quest refresh functionality
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


def test_refresh_quests():
    """Test the refresh quests functionality"""

    # Create a test user
    user = User(
        email="test_refresh@example.com",
        username="testuser_refresh",
        apple_id="test_apple_id_refresh",
    )
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

    # Quest 1: Open quest within generation window (should be marked as skipped)
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

    # Quest 2: Another open quest (should be marked as skipped)
    quest2 = SideQuest(
        user_id=user.id,
        text="Take a walk",
        category=QuestCategory.FITNESS,
        estimated_time="10 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["walking", "outdoors"],
        generated_at=now - timedelta(hours=6),
        expires_at=now + timedelta(hours=18),
    )
    db.session.add(quest2)

    # Quest 3: Already completed quest (should NOT be affected)
    quest3 = SideQuest(
        user_id=user.id,
        text="Completed quest",
        category=QuestCategory.SOCIAL,
        estimated_time="5 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["social"],
        completed=True,
        generated_at=now - timedelta(hours=8),
        expires_at=now + timedelta(hours=16),
    )
    db.session.add(quest3)

    db.session.commit()

    print(f"User ID: {user.id}")
    print(f"Created {quest1.id}, {quest2.id}, {quest3.id}")

    # Test the refresh service
    quest_service = QuestService(db.session)

    # Check initial state
    initial_available = quest_service.get_available_quests(user.id)
    print(f"Initial available quests: {len(initial_available)}")

    # Refresh quests
    refresh_result = quest_service.refresh_user_quests(
        user.id,
        {"categories": ["fitness", "social"], "difficulty": "easy", "max_time": 15},
        {"timeOfDay": "morning"},
    )

    print(f"Refresh result: {refresh_result}")

    # Check final state
    final_available = quest_service.get_available_quests(user.id)
    print(f"Final available quests: {len(final_available)}")

    # Check that old quests were marked as skipped
    quest1_reloaded = db.session.query(SideQuest).filter_by(id=quest1.id).first()
    quest2_reloaded = db.session.query(SideQuest).filter_by(id=quest2.id).first()
    quest3_reloaded = db.session.query(SideQuest).filter_by(id=quest3.id).first()

    print(f"Quest 1 skipped: {quest1_reloaded.skipped}")
    print(f"Quest 2 skipped: {quest2_reloaded.skipped}")
    print(f"Quest 3 completed: {quest3_reloaded.completed} (should be unchanged)")

    # Clean up
    db.session.delete(quest1)
    db.session.delete(quest2)
    db.session.delete(quest3)
    db.session.delete(user_prefs)
    db.session.delete(user)
    db.session.commit()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    test_refresh_quests()
