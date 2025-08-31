from datetime import datetime, timedelta
import random
from backend.models import User, UserBalance
from backend.sidequest.models import (
    SideQuestUser,
    SideQuest,
    QuestGenerationLog,
    QuestStatus,
)
from backend.sidequest.models import QuestCategory, QuestDifficulty, QuestRating


def init_test_db(db):
    """Initialize the test database with sample data."""
    db.create_all()

    # Create test users
    users = []
    for i in range(3):
        user = User(
            email=f"test{i+1}@example.com",
            name=f"Test User {i+1}",
            google_id=f"test_google_id_{i+1}",
        )
        db.session.add(user)
        users.append(user)

    # Create apple user
    apple_user = User(
        apple_id="test_apple_id",
        name="Apple Test User",
        email="apple@example.com",
    )
    db.session.add(apple_user)
    users.append(apple_user)

    db.session.flush()

    # Create user balances
    for user in users:
        balance = UserBalance(user_id=user.id)
        db.session.add(balance)

    # Create SideQuest users with different preferences
    sidequest_users = []
    for i, user in enumerate(users):
        categories = random.sample(list(QuestCategory), random.randint(2, 4))
        difficulty = random.choice(list(QuestDifficulty))

        sidequest_user = SideQuestUser(
            user_id=user.id,
            categories=[cat.value for cat in categories],
            difficulty=difficulty,
            max_time=random.choice([5, 10, 15, 20, 30]),
            notifications_enabled=random.choice([True, False]),
            onboarding_completed=random.choice([True, False]),
            timezone="UTC",
        )
        db.session.add(sidequest_user)
        sidequest_users.append(sidequest_user)

    db.session.flush()

    # Create sample quests
    quest_texts = [
        "Do 10 push-ups",
        "Take a 5-minute meditation break",
        "Call a friend you haven't talked to in a while",
        "Clean your desk for 10 minutes",
        "Learn a new word and use it in conversation",
        "Take a 15-minute walk outside",
        "Write down 3 things you're grateful for",
        "Try a new recipe for dinner",
        "Read a book for 20 minutes",
        "Practice deep breathing for 5 minutes",
    ]

    quests = []
    for i in range(20):
        user = random.choice(sidequest_users)
        category = random.choice(list(QuestCategory))
        difficulty = random.choice(list(QuestDifficulty))

        quest = SideQuest(
            user_id=user.id,
            text=random.choice(quest_texts),
            category=category,
            estimated_time=f"{random.randint(5, 30)} minutes",
            difficulty=difficulty,
            tags=[category.value, difficulty.value],
            expires_at=datetime.now() + timedelta(days=random.randint(1, 7)),
            status=random.choice(list(QuestStatus)),
        )

        # Add completion details for completed quests
        if quest.is_completed():
            quest.completed_at = datetime.now() - timedelta(hours=random.randint(1, 24))
            quest.feedback_rating = random.choice(list(QuestRating))
            quest.feedback_comment = random.choice(
                [
                    "Great workout!",
                    "Felt good",
                    "Challenging but rewarding",
                    "Easy peasy",
                    "Will do again",
                ]
            )
            quest.time_spent = random.randint(5, 45)

        db.session.add(quest)
        quests.append(quest)

    db.session.flush()

    # Create generation logs
    for i in range(10):
        user = random.choice(sidequest_users)
        categories = random.sample(list(QuestCategory), random.randint(1, 3))

        log = QuestGenerationLog(
            user_id=user.id,
            request_preferences={
                "categories": [cat.value for cat in categories],
                "difficulty": random.choice(list(QuestDifficulty)).value,
                "max_time": random.choice([5, 10, 15, 20, 30]),
            },
            context_data={
                "weather": random.choice(["sunny", "rainy", "cloudy"]),
                "mood": random.choice(["energetic", "tired", "focused", "relaxed"]),
            },
            quests_generated=random.randint(3, 8),
            model_used=random.choice(["gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]),
            fallback_used=random.choice([True, False]),
            generation_time_ms=random.randint(500, 3000),
            tokens_used=random.randint(100, 500),
        )
        db.session.add(log)

    db.session.commit()
