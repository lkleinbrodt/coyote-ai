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
from backend.sidequest.services import QuestService
from backend.sidequest.models import QuestStatus


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


@pytest.fixture
def test_sidequest_user_with_board(app, test_user):
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

    service = QuestService(db.session)

    quest_texts = [
        "Do 10 push-ups",
        "Take a 5-minute meditation break",
        "Call a friend you haven't talked to in a while",
        "Clean your desk for 10 minutes",
    ]
    quests = []
    for i in range(3):
        import random

        category = random.choice(list(QuestCategory))
        difficulty = random.choice(list(QuestDifficulty))

        quest_board = service.get_or_create_board(sidequest_user.user_id)

        quest = SideQuest(
            user_id=sidequest_user.user_id,
            text=random.choice(quest_texts),
            category=category,
            estimated_time=f"{random.randint(5, 30)} minutes",
            difficulty=difficulty,
            tags=[category.value, difficulty.value],
            expires_at=datetime.now() + timedelta(days=random.randint(1, 7)),
            status=random.choice(list(QuestStatus)),
            quest_board_id=quest_board.id,
        )
        db.session.add(quest)
        quests.append(quest)

    db.session.commit()

    return sidequest_user
