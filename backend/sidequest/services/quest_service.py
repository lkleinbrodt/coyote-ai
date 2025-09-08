from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import or_
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from backend.sidequest.models import (
    UserQuest,
    QuestStatus,
    QuestBoard,
    QuestTemplate,
    SideQuestUser,
)
from backend.sidequest.services.quest_generation_service import QuestGenerationService
from backend.sidequest.services.user_service import UserService
from backend.extensions import create_logger


logger = create_logger(__name__)


class QuestService:
    """Service for managing quest interactions and quest board operations

    Note on quest board refresh:

    We want your quest board to refresh every day at midnight in the user's timezone
    When we do a refresh, we first clean up all the quests on the board (potential are marked as declined, accepted are marked as failed, and completed are kept, etc)
    THen we populate the board with new potential quests

    but we also want the option to just simply top up the user's potential quests
    Say the user didnt like their first 3 recommendations, they want to request new ones
    THis is different from a "refresh", because we arent clearing their other board data (like their accepted quests, completed quests, etc)

    I'm not fully happy with our current approach, but it's doing the job for now

    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.quest_generation_service = QuestGenerationService(db_session)
        self.user_service = UserService(db_session)

    def board_needs_refresh(self, user_id: int) -> bool:
        """Check if the quest board needs to be refreshed

        A board needs refreshing if it has not been refreshed during the user's current calendar day
        """
        logger.debug(f"Checking if board needs refresh for user {user_id}")
        sidequest_user = self.db.query(SideQuestUser).filter_by(user_id=user_id).first()
        if not sidequest_user:
            raise ValueError(f"SideQuestUser not found for user {user_id}")

        # Convert timezone string to tzinfo object
        try:
            logger.debug(f"User timezone: {sidequest_user.timezone}")
            user_tz = ZoneInfo(sidequest_user.timezone)
        except Exception as e:
            # Fallback to UTC if timezone is invalid
            logger.warning(
                f"Invalid timezone '{sidequest_user.timezone}' for user {user_id}, falling back to UTC"
            )
            user_tz = ZoneInfo("UTC")

        quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not quest_board:
            logger.debug("Quest board not found, returning True")
            return True

        # if the quest board is empty, return True
        if not quest_board.quests.all():
            logger.debug("Quest board is empty, returning True")
            return True

        # Ensure last_refreshed has timezone info for comparison
        if quest_board.last_refreshed and quest_board.last_refreshed.tzinfo is None:
            # If last_refreshed is timezone-naive, assume it's in UTC
            last_refreshed_tz = quest_board.last_refreshed.replace(
                tzinfo=ZoneInfo("UTC")
            )
        else:
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
        last_refreshed_day = last_refreshed_day.replace(tzinfo=user_tz)

        needs_refresh = last_refreshed_day < current_day
        logger.debug(
            f"Board refresh check: current_day={current_day}, last_refreshed_day={last_refreshed_day}, needs_refresh={needs_refresh}"
        )
        return needs_refresh

    def cleanup_board(self, user_id: int):
        """Cleanup the quest board for a user"""
        quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
        if not quest_board:
            return

        quest_board.cleanup()

    def populate_board(self, user_id: int):
        """Populate the quest board for a user with new quests"""
        logger.info(f"Populating quest board with new quests for user {user_id}")

        quest_board = self.get_or_create_board(user_id)

        if not quest_board:
            logger.info(f"Quest board not found for user {user_id}, creating...")
            quest_board = QuestBoard(user_id=user_id)
            self.db.add(quest_board)
            self.db.commit()
            self.db.refresh(quest_board)

        profile = self.user_service.get_or_create_user_profile(user_id)
        # Convert to dict to ensure datetime objects are serialized
        preferences = profile.to_dict()

        quest_board_quests = quest_board.quests.all()
        potential_quests = [
            quest
            for quest in quest_board_quests
            if quest.status == QuestStatus.POTENTIAL
        ]

        n_quests_needed = 3 - len(potential_quests)

        if n_quests_needed <= 0:
            logger.info(f"No quests needed for user {user_id}, returning")
            return
        logger.info(f"User {user_id} needs {n_quests_needed} quests")

        """
        We have 2 sources of quests:
        - Creating a new quest template for the user and assigning it to them
        - grabbing an existing quest template from the db and assigning it to the user
        
        If user only needs 1 quest:
            We generate 1 new quest template and 0 existing quest templates
        If user needs 2 or more quests:
            We generate 1 new quest template for sure
        And then half of all remaining templates are split between new and existing (if existing are available)
        """

        if n_quests_needed == 1:
            n_new_quests_needed = 1
            n_existing_quests_needed = 0
        else:
            n_new_quests_needed = n_quests_needed // 2
            n_existing_quests_needed = n_quests_needed - n_new_quests_needed

        templates_for_user = []
        if n_new_quests_needed > 0:
            new_quest_data = self.quest_generation_service.generate_quest_template_data(
                user_id=user_id,
                preferences=preferences,
                n_quests=n_new_quests_needed,
            )
            for quest_data in new_quest_data:
                logger.info(f"Generating new quest for user {user_id}")
                template = QuestTemplate(
                    text=quest_data.get("text"),
                    category=quest_data.get("category"),
                    estimated_time=quest_data.get("estimated_time"),
                    difficulty=quest_data.get("difficulty"),
                    tags=quest_data.get("tags"),
                    model_used=quest_data.get("model_used"),
                    fallback_used=quest_data.get("fallback_used"),
                    owner_user_id=user_id,
                )
                self.db.add(template)
                self.db.flush()  # Get the template ID

                templates_for_user.append(template)

        if n_existing_quests_needed > 0:
            potential_templates = self.get_potential_templates(
                user_id, n_existing_quests_needed
            )
            templates_for_user.extend(potential_templates)

        for template in templates_for_user:
            logger.info(f"Adding new quest to user {user_id}")
            quest = UserQuest(
                user_id=user_id,
                quest_template_id=template.id,
                quest_board_id=quest_board.id,
                resolved_text=template.text,
            )

            self.db.add(quest)

        user_profile = self.user_service.get_or_create_user_profile(user_id)
        user_profile.last_quest_generation = datetime.utcnow()

        self.db.commit()

        return True

    def refresh_board(self, user_id: int):
        """Refresh the quest board for a user"""
        logger.info(f"Refreshing quest board for user {user_id}")
        self.cleanup_board(user_id)
        self.populate_board(user_id)
        quest_board = self.get_board(user_id)
        quest_board.last_refreshed = datetime.utcnow()
        self.db.commit()
        return quest_board

    def top_up_or_refresh_board(self, user_id: int):
        """Top up the quest board for a user or refresh it if it needs to be refreshed"""
        if self.board_needs_refresh(user_id):
            logger.info(f"Board needs refresh for user {user_id}, refreshing...")
            self.refresh_board(user_id)
        else:
            logger.info(
                f"Board does not need refresh for user {user_id}, checking if board needs top up"
            )
            self.populate_board(user_id)

        return self.get_board(user_id)

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
            logger.info(f"Board needs refresh for user {user_id}, refreshing...")
            self.refresh_board(user_id)
        return self.db.query(QuestBoard).filter_by(user_id=user_id).first()

    def cleanup_quest(self, quest_id: int) -> UserQuest:
        quest = self.db.query(UserQuest).filter_by(id=quest_id).first()
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        quest.cleanup()
        self.db.commit()
        return quest

    def get_quest(self, quest_id: int) -> Optional[UserQuest]:
        """Helper to get a single quest."""
        return self.db.query(UserQuest).filter_by(id=quest_id).first()

    def update_quest_status(
        self,
        quest_id: int,
        status: str,
        data: Dict[str, Any] = {},
    ) -> Optional[UserQuest]:
        """Generic method to update a quest's status."""
        quest = self.get_quest(quest_id)
        if not quest:
            return None

        status_map = {
            "accepted": quest.accept,
            "abandoned": quest.abandon,
            "declined": quest.decline,
            "failed": quest.fail,
        }

        if status == "completed":
            # Assumes camelCase from request was converted to snake_case in route
            feedback = data.get("feedback", {})
            quest.complete(
                feedback_rating=feedback.get("rating"),
                feedback_comment=feedback.get("comment"),
                time_spent=feedback.get("time_spent"),
            )
        elif status in status_map:
            status_map[status]()
        else:
            raise ValueError(f"Invalid status '{status}' provided.")

        self.db.commit()
        return quest

    def validate_ownership(self, quest_id: int, user_id: int) -> bool:
        """Validate that a quest belongs to the specified user"""
        quest = self.db.query(UserQuest).filter_by(id=quest_id).first()
        if not quest:
            return False
        if str(quest.user_id) != str(user_id):
            print(
                f"Quest does not belong to user {user_id}, the quest belongs to {quest.user_id}"
            )
            return False
        return True

    def get_potential_templates(
        self, user_id: int, n_templates: int = 3
    ) -> List[QuestTemplate]:
        """Get the potential templates for a user.
        To be potential we shouuld grab all quest tempaltes that are:
        1) have never been shown to the user before (they have no user quests associated with them)
        2) are either owned by the user or have no owner

        """
        valid_templates = self.db.query(QuestTemplate).filter(
            or_(
                QuestTemplate.owner_user_id == user_id,
                QuestTemplate.owner_user_id.is_(None),
            )
        )
        logger.info(
            f"Found {valid_templates.count()} valid templates for user {user_id}"
        )

        valid_templates = valid_templates.filter(
            QuestTemplate.id.notin_(
                self.db.query(UserQuest.quest_template_id).filter_by(user_id=user_id)
            )
        )
        logger.info(
            f"Found {valid_templates.count()} valid templates for user {user_id} after filtering"
        )

        return valid_templates.limit(n_templates).all()
