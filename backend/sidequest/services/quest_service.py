from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from backend.sidequest.models import (
    SideQuest,
    QuestStatus,
    QuestBoard,
    SideQuestUser,
    QuestRating,
)
from backend.sidequest.services.quest_generation_service import QuestGenerationService
from backend.sidequest.services.user_service import UserService
from backend.extensions import create_logger


logger = create_logger(__name__)


class QuestService:
    """Service for managing quest interactions and feedback"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.quest_generation_service = QuestGenerationService(db_session)
        self.user_service = UserService(db_session)

    def create_quest(self, user_id, **kwargs):
        quest = SideQuest(user_id=user_id, **kwargs)

        # Auto-associate with current active board
        active_board = self.get_active_quest_board(user_id)
        if active_board:
            quest.quest_board_id = active_board.id
        else:
            # Create new board if none exists
            active_board = QuestBoard(user_id=user_id)
            self.db.add(active_board)
            self.db.commit()
            self.db.refresh(active_board)
            quest.quest_board_id = active_board.id

        return quest

    def get_user_quests(
        self,
        user_id: int,
        date: Optional[datetime] = None,
        include_expired: bool = False,
    ) -> List[SideQuest]:
        """Get quests for a user, optionally filtered by date"""
        query = self.db.query(SideQuest).filter_by(user_id=user_id)

        if date:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.filter(
                SideQuest.created_at >= start_of_day, SideQuest.created_at < end_of_day
            )

        if not include_expired:
            query = query.filter(SideQuest.expires_at > datetime.now())

        return query.order_by(SideQuest.created_at.desc()).all()

    def get_quest_history(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get quest history and statistics for a user"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        quests = (
            self.db.query(SideQuest)
            .filter(
                SideQuest.user_id == user_id,
                SideQuest.created_at >= start_date,
                SideQuest.created_at <= end_date,
            )
            .all()
        )

        stats = {
            "total": len(quests),
            "selected": sum(1 for q in quests if q.selected),
            "completed": sum(1 for q in quests if q.completed),
            "skipped": sum(1 for q in quests if q.skipped),
            "total_time": sum(q.time_spent or 0 for q in quests if q.time_spent),
        }

        return {
            "period": f"Last {days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "stats": stats,
            "quests": [q.to_dict() for q in quests],
        }

    def board_needs_refresh(self, user_id: int) -> bool:
        """Check if the quest board needs to be refreshed

        A board needs refreshing if it has not been refreshed during the user's current calendar day

        """
        sidequest_user = self.db.query(SideQuestUser).filter_by(user_id=user_id).first()
        if not sidequest_user:
            raise ValueError(f"SideQuestUser not found for user {user_id}")

        # Convert timezone string to tzinfo object
        try:
            print(f"User timezone: {sidequest_user.timezone}")
            user_tz = ZoneInfo(sidequest_user.timezone)
        except Exception as e:
            # Fallback to UTC if timezone is invalid
            logger.warning(
                f"Invalid timezone '{sidequest_user.timezone}' for user {user_id}, falling back to UTC"
            )
            print("Falling back to UTC")
            user_tz = ZoneInfo("UTC")

        quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not quest_board:
            print("Quest board not found, returning True")
            return True

        # if the quest board is empty, return True
        if not quest_board.quests.all():
            print("Quest board is empty, returning True")
            return True

        # Ensure last_refreshed has timezone info for comparison
        if quest_board.last_refreshed and quest_board.last_refreshed.tzinfo is None:
            # If last_refreshed is timezone-naive, assume it's in UTC
            print("Last refreshed is timezone-naive, assuming UTC")
            last_refreshed_tz = quest_board.last_refreshed.replace(
                tzinfo=ZoneInfo("UTC")
            )
        else:
            print("Last refreshed has timezone info, using it")
            last_refreshed_tz = quest_board.last_refreshed

        """
        Quests refresh at midnight in the user's timezone.
        So we get the user's current day (local time)
        And we get the last refreshed day (local time)
        if last refreshed day is < current day, then the board needs a refresh
        otherwise, it does not need a refresh
        """
        current_day = datetime.now(user_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        last_refreshed_day = last_refreshed_tz.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if last_refreshed_day < current_day:
            return True
        else:
            return False

    def cleanup_board(self, user_id: int):
        """Cleanup the quest board for a user"""
        quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not quest_board:
            return

        quest_board.cleanup()

    def populate_board(self, user_id: int):
        """Populate the quest board for a user"""
        quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not quest_board:
            quest_board = QuestBoard(user_id=user_id)
            self.db.add(quest_board)
            self.db.commit()
            self.db.refresh(quest_board)

        profile = self.user_service.get_or_create_user_profile(user_id)
        preferences = profile.to_dict()

        self.quest_generation_service.generate_daily_quests(user_id, preferences)
        quest_board.last_refreshed = datetime.now()
        self.db.commit()
        self.db.refresh(quest_board)
        return quest_board

    def refresh_board(self, user_id: int):
        """Refresh the quest board for a user"""
        self.cleanup_board(user_id)
        self.populate_board(user_id)

    def get_board(self, user_id: int) -> QuestBoard:
        """Get the quest board for a user"""
        return self.db.query(QuestBoard).filter_by(user_id=user_id).first()

    def get_or_create_board(self, user_id: int) -> QuestBoard:
        """Get the quest board for a user, creating it if it doesn't exist"""
        board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not board:
            board = QuestBoard(user_id=user_id)
            self.db.add(board)
            self.db.commit()
            self.db.refresh(board)
        return board

    def get_refreshed_board(self, user_id: int) -> QuestBoard:
        """Get the quest board for a user, refreshing it if it needs to be refreshed"""
        if self.board_needs_refresh(user_id):
            self.refresh_board(user_id)
        return self.db.query(QuestBoard).filter_by(user_id=user_id).first()

    def complete_quest(
        self,
        quest_id: int,
        feedback_rating: QuestRating,
        feedback_comment: str,
        time_spent: int,
    ) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.complete(feedback_rating, feedback_comment, time_spent)
        self.db.commit()
        return quest

    def accept_quest(self, quest_id: int) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.accept()
        self.db.commit()
        return quest

    def abandon_quest(self, quest_id: int) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.abandon()
        self.db.commit()
        return quest

    def decline_quest(self, quest_id: int) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.decline()
        self.db.commit()
        return quest

    def fail_quest(self, quest_id: int) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.fail()
        self.db.commit()
        return quest

    def cleanup_quest(self, quest_id: int) -> SideQuest:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.cleanup()
        self.db.commit()
        return quest

    def validate_ownership(self, quest_id: int, user_id: int) -> bool:
        quest = self.db.query(SideQuest).filter_by(id=quest_id).first()
        if not quest:
            return False
        if quest.user_id != user_id:
            return False
        return True
