from datetime import datetime
import random
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, not_

from backend.sidequest.models import (
    QuestTemplate,
    QuestTemplateVote,
    QuestRating,
    QuestCategory,
    QuestDifficulty,
)
from backend.sidequest.services.quest_generation_service import QuestGenerationService
from backend.extensions import create_logger


logger = create_logger(__name__)


class VotingService:
    """Service for managing quest template voting"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.quest_generation_service = QuestGenerationService(db_session)

    def get_quests_to_vote_on(
        self, user_id: int, limit: int = 5
    ) -> List[QuestTemplate]:
        """Get quest templates for the user to vote on

        Returns quest templates that the user hasn't voted on yet.
        If there aren't enough, generates new ones.
        """
        logger.debug(f"Getting {limit} quest templates to vote on for user {user_id}")

        # Get quest templates the user hasn't voted on
        voted_template_ids = (
            self.db.query(QuestTemplateVote.quest_template_id)
            .filter_by(user_id=user_id)
            .subquery()
        )

        available_templates = (
            self.db.query(QuestTemplate)
            .filter(not_(QuestTemplate.id.in_(voted_template_ids)))
            .limit(limit)
            .all()
        )

        logger.debug(f"Found {len(available_templates)} available templates")

        # If we don't have enough templates, generate new ones
        if len(available_templates) < limit:
            n_needed = limit - len(available_templates)
            logger.info(f"Generating {n_needed} new quest templates for voting")

            new_templates = self._generate_voting_templates(n_needed)
            available_templates.extend(new_templates)

        return available_templates[:limit]

    def _generate_voting_templates(self, n_quests: int) -> List[QuestTemplate]:
        """Generate new quest templates specifically for voting

        These templates are NOT tied to any specific user (no owner_user_id)
        """
        logger.debug(f"Generating {n_quests} new quest templates for voting")

        def generate_random_context():
            """
            generate a random context of
            {
                "date+time": (random datetime object)
                "day of week": day of week corresponding to that datetime
            }

            """
            now = datetime.now()
            random_time = now.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=random.randint(0, 999999),
            )
            return {
                "date+time": random_time,
                "dayOfWeek": random_time.strftime("%A"),
            }

        # Generate quest templates with diverse categories and difficulties
        quests_data = self.quest_generation_service.generate_quest_template_data(
            user_id=None,  # No specific user TODO: this will mean we dont generate a questgeneration log
            preferences={
                "categories": [cat.value for cat in QuestCategory],
            },
            context=generate_random_context(),
            n_quests=n_quests,
        )

        templates = []
        for quest_data in quests_data:
            template = QuestTemplate(
                text=quest_data.get("text"),
                category=quest_data.get("category"),
                estimated_time=quest_data.get("estimated_time"),
                difficulty=quest_data.get("difficulty"),
                tags=quest_data.get("tags"),
                model_used=quest_data.get("model_used"),
                fallback_used=quest_data.get("fallback_used"),
                owner_user_id=None,  # No owner for voting templates
            )
            self.db.add(template)
            templates.append(template)

        self.db.commit()
        logger.info(f"Generated {len(templates)} new quest templates for voting")
        return templates

    def submit_vote(
        self, user_id: int, quest_template_id: int, vote: str
    ) -> QuestTemplateVote:
        """Submit a vote on a quest template"""
        logger.debug(
            f"Submitting vote for user {user_id} on template {quest_template_id}: {vote}"
        )

        # Validate vote value
        try:
            vote_enum = QuestRating(vote)
        except ValueError:
            raise ValueError(
                f"Invalid vote value: {vote}. Must be 'thumbs_up' or 'thumbs_down'"
            )

        # Check if user already voted on this template
        existing_vote = (
            self.db.query(QuestTemplateVote)
            .filter(
                and_(
                    QuestTemplateVote.user_id == user_id,
                    QuestTemplateVote.quest_template_id == quest_template_id,
                )
            )
            .first()
        )

        if existing_vote:
            # Update existing vote
            existing_vote.vote = vote_enum
            self.db.commit()
            logger.info(
                f"Updated existing vote for user {user_id} on template {quest_template_id}"
            )
            return existing_vote

        # Create new vote
        vote_obj = QuestTemplateVote(
            user_id=user_id,
            quest_template_id=quest_template_id,
            vote=vote_enum,
        )
        self.db.add(vote_obj)
        self.db.commit()

        logger.info(
            f"Created new vote for user {user_id} on template {quest_template_id}"
        )
        return vote_obj

    def get_user_votes(self, user_id: int, limit: int = 50) -> List[QuestTemplateVote]:
        """Get all votes by a user"""
        return (
            self.db.query(QuestTemplateVote)
            .filter_by(user_id=user_id)
            .order_by(QuestTemplateVote.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_template_vote_stats(self, quest_template_id: int) -> Dict[str, Any]:
        """Get voting statistics for a quest template"""
        votes = (
            self.db.query(QuestTemplateVote)
            .filter_by(quest_template_id=quest_template_id)
            .all()
        )

        thumbs_up = sum(1 for vote in votes if vote.vote == QuestRating.THUMBS_UP)
        thumbs_down = sum(1 for vote in votes if vote.vote == QuestRating.THUMBS_DOWN)
        total = len(votes)

        return {
            "quest_template_id": quest_template_id,
            "total_votes": total,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "approval_rate": (thumbs_up / total * 100) if total > 0 else 0,
        }

    def get_highly_rated_templates(
        self, min_approval_rate: float = 0.7, min_votes: int = 5
    ) -> List[QuestTemplate]:
        """Get quest templates with high approval rates"""
        # This is a more complex query that would need to be implemented
        # For now, return empty list - can be implemented later if needed
        logger.debug(
            f"Getting highly rated templates (min approval: {min_approval_rate}, min votes: {min_votes})"
        )
        return []
