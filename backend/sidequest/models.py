from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.dialects.postgresql import JSON
import humps

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


class QuestStatus(str, Enum):
    """Quest status states"""

    POTENTIAL = "potential"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    DECLINED = "declined"


class SideQuestUser(db.Model):
    """SideQuest user preferences and settings"""

    __table_args__ = {"schema": "sidequest"}

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
    additional_notes = db.Column(db.Text, nullable=True)

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
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    from sqlalchemy import func

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=func.now(),
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
        quest_dict = {
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
            "additional_notes": self.additional_notes,
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
        # Convert all keys to camelCase for the API response
        return humps.camelize(quest_dict)

    def set_categories(self, categories: list[QuestCategory]):
        assert isinstance(categories, list)
        assert all(isinstance(category, QuestCategory) for category in categories)
        self.categories = categories
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def set_difficulty(self, difficulty: QuestDifficulty):
        assert isinstance(difficulty, QuestDifficulty)
        self.difficulty = difficulty
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def reset(self):
        """Reset user profile"""
        self.categories = []
        self.difficulty = QuestDifficulty.MEDIUM
        self.max_time = 15
        self.include_completed = True
        self.include_skipped = True
        self.notifications_enabled = True
        self.notification_time = datetime.strptime("07:00", "%H:%M").time()
        self.timezone = "UTC"
        self.onboarding_completed = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self


class SideQuest(db.Model):
    """Individual quest instances"""

    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quest_board_id = db.Column(
        db.Integer, db.ForeignKey("sidequest.sidequest_quest_boards.id"), nullable=True
    )

    # Quest content
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum(QuestCategory), nullable=False)
    estimated_time = db.Column(db.String(50), nullable=False)  # e.g., "5-10 minutes"
    difficulty = db.Column(db.Enum(QuestDifficulty), nullable=False)
    tags = db.Column(JSON, nullable=False, default=[])

    # Quest state
    status = db.Column(
        db.Enum(QuestStatus), nullable=False, default=QuestStatus.POTENTIAL
    )

    # Completion details
    completed_at = db.Column(db.DateTime, nullable=True)
    feedback_rating = db.Column(db.Enum(QuestRating), nullable=True)
    feedback_comment = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, nullable=True)  # in minutes

    # Generation metadata
    generated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    model_used = db.Column(db.String(100), nullable=True)  # LLM model used
    fallback_used = db.Column(db.Boolean, nullable=False, default=False)

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure mutable defaults are properly initialized
        if self.tags is None:
            self.tags = []
        if self.status is None:
            self.status = QuestStatus.POTENTIAL
        if self.fallback_used is None:
            self.fallback_used = False
        # Set expiration to end of day if not specified
        if not self.expires_at:
            tomorrow = datetime.utcnow() + timedelta(days=1)
            self.expires_at = tomorrow.replace(
                hour=23, minute=59, second=59, microsecond=0
            )

    def to_dict(self):
        quest_dict = {
            "id": str(self.id),  # Convert to string for frontend compatibility
            "user_id": self.user_id,
            "quest_board_id": self.quest_board_id,
            "text": self.text,
            "category": self.category.value if self.category else None,
            "estimated_time": self.estimated_time,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "tags": self.tags or [],
            "status": self.status.value if self.status else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "feedback": (
                {
                    "rating": (
                        self.feedback_rating.value if self.feedback_rating else None
                    ),
                    "comment": self.feedback_comment,
                    "time_spent": self.time_spent,
                }
                if self.feedback_rating or self.feedback_comment
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }
        # Convert all keys to camelCase for the API response
        return humps.camelize(quest_dict)

    def is_completed(self):
        """Check if quest is completed"""
        return self.status == QuestStatus.COMPLETED

    def is_expired(self):
        """Check if quest has expired"""
        return datetime.utcnow() > self.expires_at

    def is_open(self):
        """Check if quest is open (not yet acted upon)"""
        return not (self.status == QuestStatus.POTENTIAL)

    def is_within_generation_window(self, hours: int = 24):
        """Check if quest is within the generation window (default 24 hours)"""
        if not self.generated_at:
            return False
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.generated_at >= cutoff_time

    def complete(self, feedback_rating=None, feedback_comment=None, time_spent=None):
        """Mark quest as completed with feedback"""
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.feedback_rating = feedback_rating
        self.feedback_comment = feedback_comment
        self.time_spent = time_spent

    def accept(self):
        """Accept quest"""
        self.status = QuestStatus.ACCEPTED

    def abandon(self):
        """Abandon quest"""
        self.status = QuestStatus.ABANDONED

    def decline(self):
        """Decline quest"""
        self.status = QuestStatus.DECLINED

    def fail(self):
        """Mark quest as failed"""
        self.status = QuestStatus.FAILED

    def cleanup(self):
        """
        Cleanup old quests.
        If status is:
        Potential -> mark as declined
        Accepted -> mark as failed
        otherwise, do nothing
        """
        if self.status == QuestStatus.POTENTIAL:
            self.decline()
        elif self.status == QuestStatus.ACCEPTED:
            self.fail()

    def __repr__(self):
        return f"<SideQuest {self.id}: {self.to_dict()}>"


class QuestGenerationLog(db.Model):
    """Log of quest generation requests for analytics"""

    __table_args__ = {"schema": "sidequest"}
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
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Relationships
    user = db.relationship("User", backref="sidequest_generation_logs")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure boolean defaults are properly initialized
        if self.fallback_used is None:
            self.fallback_used = False

    def to_dict(self):
        log_dict = {
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
        # Convert all keys to camelCase for the API response
        return humps.camelize(log_dict)


class QuestBoard(db.Model):
    """Daily quest board for a user"""

    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quest_boards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Board metadata
    last_refreshed = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    user = db.relationship("User", backref=db.backref("quest_boards", uselist=False))
    quests = db.relationship("SideQuest", backref="quest_board", lazy="dynamic")

    def cleanup(self):
        """
        Cleanup old quests.
        """
        for quest in self.quests:
            quest.cleanup()
            # remove from the quest board
            self.quests.remove(quest)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        board_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "last_refreshed": self.last_refreshed.isoformat(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "quests": [quest.to_dict() for quest in self.quests],
        }
        # Convert all keys to camelCase for the API response
        return humps.camelize(board_dict)
