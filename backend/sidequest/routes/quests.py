"""
Quest routes
"""

from flask import request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
import humps

from backend.extensions import create_logger, db
from backend.sidequest.services import QuestService
from backend.sidequest.routes import sidequest_bp
from backend.sidequest.utils.response import success_response, error_response
from backend.sidequest.models import SideQuest

logger = create_logger(__name__)

"""
We need routes to:
1) check if your quest board needs a refresh
2) refresh the quest board
3) get the quest board
4) Update a quest with each of the possible statuses (consolidated)
5) pull user's quest history

"""


# Check if quest board needs a refresh
@sidequest_bp.route("/quests/needs-refresh", methods=["GET"])
@jwt_required()
def needs_refresh():
    try:
        user_id = get_jwt_identity()
        quest_service = QuestService(db.session)
        needs_refresh = quest_service.board_needs_refresh(user_id)
        return success_response({"needs_refresh": needs_refresh})
    except Exception as e:
        logger.error(f"Error checking if board needs refresh: {str(e)}")
        return error_response(
            "Failed to check board refresh status", "INTERNAL_ERROR", 500
        )


# Get the quest board
@sidequest_bp.route("/quests/board", methods=["GET"])
@jwt_required()
def get_board():
    try:
        user_id = get_jwt_identity()
        # user can skip a refresh if desired
        skip_refresh = request.args.get("skipRefresh", "false").lower() == "true"
        service = QuestService(db.session)
        if skip_refresh:
            board = service.get_or_create_board(user_id)
        else:
            board = service.get_refreshed_board(user_id)
        return success_response(board.to_dict())
    except Exception as e:
        logger.error(f"Error retrieving quest board: {str(e)}")
        return error_response("Failed to retrieve quest board", "INTERNAL_ERROR", 500)


# Consolidated route for all quest status updates
@sidequest_bp.route("/quests/<int:quest_id>/status", methods=["PUT"])
@jwt_required()
def update_quest_status(quest_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        new_status = data.get("status")

        if not new_status:
            return error_response("New status is required", "MISSING_PARAMETER", 400)

        quest_service = QuestService(db.session)
        print(f"Validating ownership for quest {quest_id} and user {user_id}")
        if not quest_service.validate_ownership(quest_id, user_id):
            return error_response("Permission denied", "PERMISSION_DENIED", 403)

        # Convert incoming camelCase keys to snake_case for the service layer
        snake_case_data = humps.decamelize(data)

        # A new generic method will be needed in the service
        updated_quest = quest_service.update_quest_status(
            quest_id, new_status, snake_case_data
        )

        if not updated_quest:
            return error_response(f"Quest {quest_id} not found", "NOT_FOUND", 404)

        return success_response(updated_quest.to_dict())

    except ValueError as e:
        return error_response(str(e), "VALIDATION_ERROR", 400)
    except Exception as e:
        logger.error(f"Error updating quest {quest_id} status: {str(e)}")
        return error_response("Failed to update quest status", "INTERNAL_ERROR", 500)


# Get user's quest history
@sidequest_bp.route("/quests/history", methods=["GET"])
@jwt_required()
def get_quest_history():
    try:
        user_id = get_jwt_identity()
        quest_service = QuestService(db.session)

        # Get query parameters for filtering
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        status = request.args.get("status")
        category = request.args.get("category")

        # Get quests from the database
        query = quest_service.db.query(SideQuest).filter_by(user_id=user_id)

        if status:
            query = query.filter(SideQuest.status == status)
        if category:
            query = query.filter(SideQuest.category == category)

        # Order by creation date (newest first) and apply pagination
        quests = (
            query.order_by(SideQuest.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Convert to dict format
        quest_data = [quest.to_dict() for quest in quests]

        return success_response(
            {
                "quests": quest_data,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(quest_data),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving quest history: {str(e)}")
        return error_response("Failed to retrieve quest history", "INTERNAL_ERROR", 500)
