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


class UserQuest(db.Model):
    """Individual quest instances"""

    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_user_quests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quest_board_id = db.Column(
        db.Integer, db.ForeignKey("sidequest.sidequest_quest_boards.id"), nullable=True
    )
    quest_template_id = db.Column(
        db.Integer,
        db.ForeignKey("sidequest.sidequest_quest_templates.id"),
        nullable=True,
    )

    # Quest content
    resolved_text = db.Column(db.Text, nullable=True)

    # Quest state
    status = db.Column(
        db.Enum(QuestStatus), nullable=False, default=QuestStatus.POTENTIAL
    )

    # Completion details
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    failed_at = db.Column(db.DateTime, nullable=True)
    abandoned_at = db.Column(db.DateTime, nullable=True)
    declined_at = db.Column(db.DateTime, nullable=True)

    feedback_rating = db.Column(db.Enum(QuestRating), nullable=True)
    feedback_comment = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, nullable=True)  # in minutes

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
    user = db.relationship("User", backref="user_quests")
    quest_template = db.relationship("QuestTemplate", backref="user_quests")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure resolved_text is set if not provided
        if self.resolved_text is None and self.quest_template_id:
            # This will be set when the quest_template relationship is loaded
            pass

    def to_dict(self):
        template_info = self.quest_template.to_dict() if self.quest_template else None

        quest_dict = {
            "id": str(self.id),  # Convert to string for frontend compatibility
            "user_id": self.user_id,
            "text": self.resolved_text
            or (self.quest_template.text if self.quest_template else None),
            "quest_board_id": self.quest_board_id,
            "quest_template_id": self.quest_template_id,
            "accepted_at": (self.accepted_at.isoformat() if self.accepted_at else None),
            "failed_at": (self.failed_at.isoformat() if self.failed_at else None),
            "abandoned_at": (
                self.abandoned_at.isoformat() if self.abandoned_at else None
            ),
            "declined_at": (self.declined_at.isoformat() if self.declined_at else None),
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
            "updated_at": self.updated_at.isoformat(),
        }
        if template_info:
            quest_dict["category"] = template_info["category"]
            quest_dict["difficulty"] = template_info["difficulty"]
            quest_dict["tags"] = template_info["tags"]
            quest_dict["estimated_time"] = template_info["estimatedTime"]
            quest_dict["owner_user_id"] = template_info["ownerUserId"]
            quest_dict["parent_template_id"] = template_info["parentTemplateId"]
        # Convert all keys to camelCase for the API response
        return humps.camelize(quest_dict)

    def is_completed(self):
        """Check if quest is completed"""
        return self.status == QuestStatus.COMPLETED

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
        return f"<UserQuest {self.id}: {self.to_dict()}>"


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
    quests = db.relationship("UserQuest", backref="quest_board", lazy="dynamic")

    def cleanup(self):
        """
        Cleanup old quests.
        """
        quests = self.quests.all()
        for quest in quests:
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


class QuestTemplate(db.Model):
    """Template for a quest"""

    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quest_templates"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum(QuestCategory), nullable=False)
    difficulty = db.Column(db.Enum(QuestDifficulty), nullable=False)
    tags = db.Column(JSON, nullable=False, default=[])
    estimated_time = db.Column(db.String(50), nullable=False)

    owner_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    parent_template_id = db.Column(
        db.Integer,
        db.ForeignKey("sidequest.sidequest_quest_templates.id"),
        nullable=True,
    )

    model_used = db.Column(db.String(100), nullable=True)  # LLM model used
    fallback_used = db.Column(db.Boolean, nullable=False, default=False)

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

    def to_dict(self):
        template_dict = {
            "id": self.id,
            "text": self.text,
            "category": self.category.value if self.category else None,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "tags": self.tags or [],
            "estimated_time": self.estimated_time,
            "owner_user_id": self.owner_user_id,
            "parent_template_id": self.parent_template_id,
            "model_used": self.model_used,
            "fallback_used": self.fallback_used,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return humps.camelize(template_dict)


class QuestTemplateVote(db.Model):
    """Vote on a quest template"""

    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quest_template_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quest_template_id = db.Column(
        db.Integer,
        db.ForeignKey("sidequest.sidequest_quest_templates.id"),
        nullable=False,
    )
    vote = db.Column(db.Enum(QuestRating), nullable=False)  # thumbs_up or thumbs_down

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Relationships
    user = db.relationship("User", backref="quest_template_votes")
    quest_template = db.relationship("QuestTemplate", backref="votes")

    def to_dict(self):
        vote_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "quest_template_id": self.quest_template_id,
            "vote": self.vote.value if self.vote else None,
            "created_at": self.created_at.isoformat(),
        }
        return humps.camelize(vote_dict)
