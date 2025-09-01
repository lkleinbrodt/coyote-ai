"""
Test the new quest management system with QuestBoard and unified status

These tests will fail until the new system is implemented.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.extensions import db
from backend.sidequest.models import (
    QuestBoard,
    SideQuest,
    QuestStatus,
    QuestCategory,
    QuestDifficulty,
)
from backend.sidequest.services import QuestService
from backend.sidequest.routes import sidequest_bp


class TestModels:
    """Test the new QuestBoard model"""

    def test_quest_board_creation(self):
        """Test creating a new quest board"""
        # This will fail until QuestBoard model is implemented
        board = QuestBoard(user_id=1, last_refreshed=datetime.utcnow(), is_active=True)
        db.session.add(board)
        db.session.commit()
        db.session.refresh(board)

        assert board.user_id == 1
        assert board.is_active is True
        assert board.last_refreshed is not None
        assert board.created_at is not None
        assert board.updated_at is not None

    def test_quest_board_relationships(self, test_sidequest_user):
        """Test quest board relationships with quests"""
        service = QuestService(db.session)
        board = service.get_or_create_board(test_sidequest_user.user_id)

        quest = SideQuest(
            user_id=test_sidequest_user.user_id,
            text="Test quest",
            category=QuestCategory.FITNESS,
            estimated_time="5 minutes",
            difficulty=QuestDifficulty.EASY,
            status=QuestStatus.POTENTIAL,
            quest_board_id=board.id,
        )
        db.session.add(quest)
        db.session.commit()

        board = service.get_board(test_sidequest_user.user_id)
        quests = board.quests.all()

        assert len(quests) == 1
        assert quests[0].text == "Test quest"
        assert quest.quest_board_id == board.id

    def test_quest_status_transitions(self):
        """Test valid quest status transitions"""
        # This will fail until status validation is implemented
        quest = SideQuest(
            user_id=1,
            text="Test quest",
            category=QuestCategory.FITNESS,
            estimated_time="5 minutes",
            difficulty=QuestDifficulty.EASY,
            status=QuestStatus.POTENTIAL,
        )

        # Test valid transitions
        quest.accept()
        assert quest.status == QuestStatus.ACCEPTED

        quest.complete()
        assert quest.status == QuestStatus.COMPLETED


class TestServices:
    """Test the new QuestBoardService"""

    def test_get_board(self, test_sidequest_user):
        """Test getting the quest board"""
        service = QuestService(db.session)
        board = service.get_or_create_board(test_sidequest_user.user_id)
        assert board is not None
        assert board.user_id == test_sidequest_user.user_id
        assert board.is_active is True
        assert board.last_refreshed is not None
        assert board.created_at is not None
        assert board.updated_at is not None

    def test_board_refresh(self, test_sidequest_user_with_board):
        """Test refreshing the quest board"""
        user = test_sidequest_user_with_board
        service = QuestService(db.session)
        board = service.get_or_create_board(user.user_id)

        # the board will not need a refresh
        assert service.board_needs_refresh(user.user_id) is False, board.last_refreshed

        # get all the existing quest ids to make sure they get cleaned up
        quest_board = service.get_board(user.user_id)
        existing_quest_ids = [quest.id for quest in quest_board.quests]
        # now adjust the last refreshed time to make the board need a refresh

        quest_board.last_refreshed = datetime.utcnow() - timedelta(days=1)
        db.session.commit()

        assert service.board_needs_refresh(user.user_id) is True

        # mock the LLM call to generate new quests
        from unittest.mock import Mock
        import json

        mock_client = Mock()
        mock_response = Mock()
        mock_response = json.dumps(
            {
                "quests": [
                    {
                        "text": "Do 10 jumping jacks",
                        "category": "fitness",
                        "estimated_time": "5 minutes",
                        "difficulty": "easy",
                        "tags": ["exercise", "quick"],
                    }
                ]
            }
        )
        mock_client.chat.return_value = mock_response
        service.quest_generation_service.client = mock_client

        service.refresh_board(user.user_id)

        # make sure the new quests are on the board
        board = service.get_board(user.user_id)
        quests = board.quests.all()
        assert len(quests) == 1
        assert quests[0].text == "Do 10 jumping jacks"
        assert quests[0].category == QuestCategory.FITNESS
        assert quests[0].difficulty == QuestDifficulty.EASY
        # old quests should no longer have a board
        for quest_id in existing_quest_ids:
            quest = db.session.query(SideQuest).filter_by(id=quest_id).first()
            assert quest.quest_board_id is None
