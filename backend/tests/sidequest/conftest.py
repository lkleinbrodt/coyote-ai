"""
Consolidated fixtures for SideQuest tests.

Only essential fixtures, no duplicates or unnecessary complexity.
"""

import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from backend.sidequest.models import (
    SideQuestUser,
    SideQuest,
    QuestDifficulty,
    QuestCategory,
    QuestStatus,
)
from backend.extensions import db
from backend.models import User
from backend.sidequest.services import QuestService


@pytest.fixture
def test_sidequest_user(app, test_user):
    """Create a test SideQuest user with preferences."""
    sidequest_user = SideQuestUser(
        user_id=test_user.id,
        categories=["fitness", "mindfulness"],
        difficulty=QuestDifficulty.MEDIUM,
        max_time=15,
        notifications_enabled=True,
        onboarding_completed=True,
    )
    db.session.add(sidequest_user)
    db.session.commit()
    return sidequest_user


@pytest.fixture
def test_quest(app, test_sidequest_user):
    """Create a test quest for testing."""
    quest = SideQuest(
        user_id=test_sidequest_user.user_id,
        text="Take a 10-minute walk",
        category=QuestCategory.FITNESS,
        estimated_time="10 minutes",
        difficulty=QuestDifficulty.EASY,
        tags=["walking", "exercise", "outdoors"],
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    db.session.add(quest)
    db.session.commit()
    return quest


@pytest.fixture
def test_sidequest_user_with_board(app, test_user):
    """Create a test SideQuest user with a quest board and some quests."""
    sidequest_user = SideQuestUser(
        user_id=test_user.id,
        categories=["fitness", "mindfulness"],
        difficulty=QuestDifficulty.MEDIUM,
        max_time=15,
        notifications_enabled=True,
        onboarding_completed=True,
    )
    db.session.add(sidequest_user)
    db.session.commit()

    # Create quest board with some quests
    service = QuestService(db.session)
    quest_board = service.get_or_create_board(sidequest_user.user_id)

    quest_texts = [
        "Do 10 push-ups",
        "Take a 5-minute meditation break",
        "Call a friend you haven't talked to in a while",
    ]

    for i, text in enumerate(quest_texts):
        quest = SideQuest(
            user_id=sidequest_user.user_id,
            text=text,
            category=QuestCategory.FITNESS if i == 0 else QuestCategory.MINDFULNESS,
            estimated_time=f"{5 + i * 5} minutes",
            difficulty=QuestDifficulty.EASY,
            tags=["test"],
            expires_at=datetime.utcnow() + timedelta(days=1),
            status=QuestStatus.POTENTIAL,
            quest_board_id=quest_board.id,
        )
        db.session.add(quest)

    db.session.commit()
    return sidequest_user


@pytest.fixture
def auth_headers(test_user, app):
    """Create authentication headers with JWT token for testing."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user.id))
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def quest_preferences():
    """Sample quest preferences for testing."""
    return {
        "categories": ["fitness", "mindfulness"],
        "difficulty": "medium",
        "max_time": 15,
        "notifications_enabled": True,
    }
