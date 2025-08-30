import pytest
from backend.sidequest.models import SideQuestUser, SideQuest, QuestGenerationLog
from backend.extensions import db
from datetime import datetime, timedelta


@pytest.fixture
def test_sidequest_user(app, test_user):
    """Create a test SideQuest user with preferences."""
    sidequest_user = SideQuestUser(
        user_id=test_user.id,
        categories=["fitness", "mindfulness"],
        difficulty="medium",
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
        text="Test quest: Do 10 push-ups",
        category="fitness",
        estimated_time="5-10 minutes",
        difficulty="easy",
        tags=["exercise", "strength"],
        expires_at=datetime.now() + timedelta(days=1),
    )
    db.session.add(quest)
    db.session.commit()

    return quest


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
