import pytest
from backend.sidequest.models import (
    SideQuestUser,
    SideQuest,
    QuestGenerationLog,
    QuestDifficulty,
    QuestCategory,
)
from backend.extensions import db, jwt
from backend.models import User
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token


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
        user_id=test_sidequest_user.id,
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
def sample_quest(test_quest):
    """Alias for test_quest to match test expectations."""
    return test_quest


@pytest.fixture
def test_generation_log(app, test_sidequest_user):
    """Create a test generation log for testing."""
    log = QuestGenerationLog(
        user_id=test_sidequest_user.id,
        request_preferences={
            "categories": ["fitness"],
            "difficulty": "medium",
            "max_time": 15,
        },
        quests_generated=3,
        model_used="gpt-4",
        generation_time_ms=1500,
    )
    db.session.add(log)
    db.session.commit()

    return log


@pytest.fixture
def auth_headers(test_user, app):
    """Create real authentication headers with JWT token for testing."""
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
