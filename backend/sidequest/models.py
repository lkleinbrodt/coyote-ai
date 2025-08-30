from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.dialects.postgresql import JSON

from backend.extensions import db


class QuestCategory(str, Enum):
    """Quest categories"""

    FITNESS = "fitness"
    SOCIAL = "social"
    MINDFULNESS = "mindfulness"
    CHORES = "chores"
    HOBBIES = "hobbies"
    OUTDOORS = "outdoors"
    LEARNING = "learning"
    CREATIVITY = "creativity"


class QuestDifficulty(str, Enum):
    """Quest difficulty levels"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestRating(str, Enum):
    """Quest feedback ratings"""

    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


class SideQuestUser(db.Model):
    """SideQuest user preferences and settings"""

    __tablename__ = "sidequest_users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True
    )

    # Preferences
    categories = db.Column(JSON, nullable=False, default=[])
    difficulty = db.Column(
        db.Enum(QuestDifficulty), nullable=False, default=QuestDifficulty.MEDIUM
    )
    max_time = db.Column(db.Integer, nullable=False, default=15)  # in minutes
    include_completed = db.Column(db.Boolean, nullable=False, default=True)
    include_skipped = db.Column(db.Boolean, nullable=False, default=True)

    # Notification settings
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=True)
    notification_time = db.Column(
        db.Time, nullable=False, default=datetime.strptime("07:00", "%H:%M").time()
    )
    timezone = db.Column(db.String(50), nullable=False, default="UTC")

    # App state
    onboarding_completed = db.Column(db.Boolean, nullable=False, default=False)
    last_quest_generation = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
    user = db.relationship(
        "User", backref=db.backref("sidequest_profile", uselist=False)
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure mutable defaults are properly initialized
        if self.categories is None:
            self.categories = []
        # Ensure enum defaults are properly initialized
        if self.difficulty is None:
            self.difficulty = QuestDifficulty.MEDIUM
        # Ensure other defaults are properly initialized
        if self.max_time is None:
            self.max_time = 15
        if self.include_completed is None:
            self.include_completed = True
        if self.include_skipped is None:
            self.include_skipped = True
        if self.notifications_enabled is None:
            self.notifications_enabled = True
        if self.timezone is None:
            self.timezone = "UTC"
        if self.onboarding_completed is None:
            self.onboarding_completed = False

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "categories": self.categories,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "max_time": self.max_time,
            "include_completed": self.include_completed,
            "include_skipped": self.include_skipped,
            "notifications_enabled": self.notifications_enabled,
            "notification_time": (
                self.notification_time.strftime("%H:%M")
                if self.notification_time
                else None
            ),
            "timezone": self.timezone,
            "onboarding_completed": self.onboarding_completed,
            "last_quest_generation": (
                self.last_quest_generation.isoformat()
                if self.last_quest_generation
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class SideQuest(db.Model):
    """Individual quest instances"""

    __tablename__ = "sidequest_quests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Quest content
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum(QuestCategory), nullable=False)
    estimated_time = db.Column(db.String(50), nullable=False)  # e.g., "5-10 minutes"
    difficulty = db.Column(db.Enum(QuestDifficulty), nullable=False)
    tags = db.Column(JSON, nullable=False, default=[])

    # Quest state
    selected = db.Column(db.Boolean, nullable=False, default=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    skipped = db.Column(db.Boolean, nullable=False, default=False)

    # Completion details
    completed_at = db.Column(db.DateTime, nullable=True)
    feedback_rating = db.Column(db.Enum(QuestRating), nullable=True)
    feedback_comment = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, nullable=True)  # in minutes

    # Generation metadata
    generated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    model_used = db.Column(db.String(100), nullable=True)  # LLM model used
    fallback_used = db.Column(db.Boolean, nullable=False, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure mutable defaults are properly initialized
        if self.tags is None:
            self.tags = []
        # Ensure boolean defaults are properly initialized
        if self.selected is None:
            self.selected = False
        if self.completed is None:
            self.completed = False
        if self.skipped is None:
            self.skipped = False
        if self.fallback_used is None:
            self.fallback_used = False
        # Set expiration to end of day if not specified
        if not self.expires_at:
            tomorrow = datetime.utcnow() + timedelta(days=1)
            self.expires_at = tomorrow.replace(
                hour=23, minute=59, second=59, microsecond=0
            )

    def to_dict(self):
        return {
            "id": str(self.id),  # Convert to string for frontend compatibility
            "text": self.text,
            "category": self.category.value if self.category else None,
            "estimatedTime": self.estimated_time,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "tags": self.tags or [],
            "selected": self.selected,
            "completed": self.completed,
            "skipped": self.skipped,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "feedback": (
                {
                    "rating": (
                        self.feedback_rating.value if self.feedback_rating else None
                    ),
                    "comment": self.feedback_comment,
                    "completed": self.completed,
                    "timeSpent": self.time_spent,
                }
                if self.feedback_rating or self.feedback_comment or self.completed
                else None
            ),
            "createdAt": self.created_at.isoformat(),
            "expiresAt": self.expires_at.isoformat(),
        }

    def is_expired(self):
        """Check if quest has expired"""
        return datetime.utcnow() > self.expires_at

    def mark_completed(
        self, feedback_rating=None, feedback_comment=None, time_spent=None
    ):
        """Mark quest as completed with feedback"""
        self.completed = True
        self.completed_at = datetime.utcnow()
        self.feedback_rating = feedback_rating
        self.feedback_comment = feedback_comment
        self.time_spent = time_spent

    def mark_skipped(self):
        """Mark quest as skipped"""
        self.skipped = True

    def mark_selected(self):
        """Mark quest as selected"""
        self.selected = True


class QuestGenerationLog(db.Model):
    """Log of quest generation requests for analytics"""

    __tablename__ = "sidequest_generation_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Generation details
    request_preferences = db.Column(JSON, nullable=False)  # QuestPreferences
    context_data = db.Column(JSON, nullable=True)  # Optional context like weather, mood

    # Response details
    quests_generated = db.Column(db.Integer, nullable=False)
    model_used = db.Column(db.String(100), nullable=True)
    fallback_used = db.Column(db.Boolean, nullable=False, default=False)

    # Performance metrics
    generation_time_ms = db.Column(
        db.Integer, nullable=True
    )  # Time taken in milliseconds
    tokens_used = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    user = db.relationship("User", backref="sidequest_generation_logs")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure boolean defaults are properly initialized
        if self.fallback_used is None:
            self.fallback_used = False

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "request_preferences": self.request_preferences,
            "context_data": self.context_data,
            "quests_generated": self.quests_generated,
            "model_used": self.model_used,
            "fallback_used": self.fallback_used,
            "generation_time_ms": self.generation_time_ms,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat(),
        }
