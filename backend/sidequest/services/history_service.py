from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from collections import Counter

from backend.sidequest.models import (
    QuestStatus,
    QuestCategory,
    SideQuestUser,
    UserQuest,
)
from backend.extensions import create_logger

logger = create_logger(__name__)


class HistoryService:
    """Service for calculating user history statistics and retrieving historical quest data"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics including streak, success rate, etc."""
        logger.debug(f"Getting user stats for user {user_id}")

        # Get all completed quests for the user
        completed_quests = (
            self.db.query(UserQuest)
            .filter_by(user_id=user_id, status=QuestStatus.COMPLETED)
            .all()
        )

        # Get all accepted quests (completed + failed/abandoned)
        accepted_quests = (
            self.db.query(UserQuest)
            .filter(
                UserQuest.user_id == user_id,
                UserQuest.status.in_(
                    [QuestStatus.COMPLETED, QuestStatus.FAILED, QuestStatus.ABANDONED]
                ),
            )
            .all()
        )

        # Calculate streak
        streak = self._calculate_streak(user_id)

        # Calculate success rate
        success_rate = self._calculate_success_rate(completed_quests, accepted_quests)

        # Get most completed category
        most_completed_category = self._get_most_completed_category(completed_quests)

        # Get top tags
        top_tags = self._get_top_tags(completed_quests)

        return {
            "streak": streak,
            "success_rate": success_rate,
            "most_completed_category": most_completed_category,
            "top_tags": top_tags,
            "total_completed": len(completed_quests),
            "total_accepted": len(accepted_quests),
        }

    def get_7_day_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get the last 7 days of quest history (excluding today)"""
        logger.debug(f"Getting 7-day history for user {user_id}")

        # Get user's timezone
        user_profile = self.db.query(SideQuestUser).filter_by(user_id=user_id).first()
        if not user_profile:
            logger.warning(f"No user profile found for user {user_id}")
            return []

        # Calculate date range (last 7 days, excluding today)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)

        # Get all quests from the last 7 days
        quests = (
            self.db.query(UserQuest)
            .filter(
                UserQuest.user_id == user_id,
                func.date(UserQuest.created_at) >= start_date,
                func.date(UserQuest.created_at) < end_date,
            )
            .order_by(desc(UserQuest.created_at))
            .all()
        )

        # Group quests by date
        quests_by_date = {}
        for quest in quests:
            quest_date = quest.created_at.date()
            if quest_date not in quests_by_date:
                quests_by_date[quest_date] = []
            quests_by_date[quest_date].append(quest)

        # Build history data
        history = []
        for i in range(7):
            date = end_date - timedelta(days=i + 1)  # Exclude today
            day_quests = quests_by_date.get(date, [])

            # Calculate day stats
            completed_count = len(
                [q for q in day_quests if q.status == QuestStatus.COMPLETED]
            )
            total_count = len(day_quests)

            # Create concise quest summaries
            quest_summaries = []
            for quest in day_quests:
                quest_summaries.append(
                    {
                        "id": str(quest.id),
                        "text": quest.text,
                        "category": quest.category.value if quest.category else None,
                        "completed": quest.status == QuestStatus.COMPLETED,
                        "skipped": quest.status
                        in [QuestStatus.DECLINED, QuestStatus.ABANDONED],
                    }
                )

            history.append(
                {
                    "date": date.isoformat(),
                    "quests": quest_summaries,
                    "completed_count": completed_count,
                    "total_count": total_count,
                }
            )

        return history

    def _calculate_streak(self, user_id: int) -> int:
        """Calculate the current streak of consecutive days with completed quests"""
        logger.debug(f"Calculating streak for user {user_id}")

        # Get all completed quests ordered by completion date
        completed_quests = (
            self.db.query(UserQuest)
            .filter_by(user_id=user_id, status=QuestStatus.COMPLETED)
            .filter(UserQuest.completed_at.isnot(None))
            .order_by(desc(UserQuest.completed_at))
            .all()
        )

        if not completed_quests:
            return 0

        # Get unique completion dates
        completion_dates = set()
        for quest in completed_quests:
            if quest.completed_at:
                completion_dates.add(quest.completed_at.date())

        # Sort dates in descending order
        sorted_dates = sorted(completion_dates, reverse=True)

        # Calculate streak
        streak = 0
        current_date = datetime.utcnow().date()

        for i, completion_date in enumerate(sorted_dates):
            if i == 0:
                # Check if the most recent completion was today or yesterday
                if (
                    completion_date == current_date
                    or completion_date == current_date - timedelta(days=1)
                ):
                    streak = 1
                    current_date = completion_date
                else:
                    break
            else:
                # Check if this completion was the day after the previous one
                if completion_date == current_date - timedelta(days=1):
                    streak += 1
                    current_date = completion_date
                else:
                    break

        return streak

    def _calculate_success_rate(
        self, completed_quests: List[UserQuest], accepted_quests: List[UserQuest]
    ) -> float:
        """Calculate the success rate (percentage of accepted quests that were completed)"""
        if not accepted_quests:
            return 0.0

        return round((len(completed_quests) / len(accepted_quests)) * 100, 1)

    def _get_most_completed_category(
        self, completed_quests: List[UserQuest]
    ) -> Optional[str]:
        """Get the category with the most completed quests"""
        if not completed_quests:
            return None

        category_counts = Counter()
        for quest in completed_quests:
            if quest.category:
                category_counts[quest.category.value] += 1

        if category_counts:
            return category_counts.most_common(1)[0][0]
        return None

    def _get_top_tags(
        self, completed_quests: List[UserQuest], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get the top tags from completed quests"""
        if not completed_quests:
            return []

        tag_counts = Counter()
        for quest in completed_quests:
            if quest.tags:
                for tag in quest.tags:
                    tag_counts[tag] += 1

        # Return top tags with counts
        top_tags = []
        for tag, count in tag_counts.most_common(limit):
            top_tags.append({"tag": tag, "count": count})

        return top_tags
