"""
History routes for SideQuest
"""

from flask import request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from backend.extensions import create_logger, db
from backend.sidequest.services import HistoryService
from backend.sidequest.routes import sidequest_bp
from backend.sidequest.utils.response import success_response, error_response

logger = create_logger(__name__)


@sidequest_bp.route("/history/stats", methods=["GET"])
@jwt_required()
def get_history_stats():
    """Get user's history statistics including streak, success rate, etc."""
    try:
        user_id = get_jwt_identity()
        history_service = HistoryService(db.session)

        stats = history_service.get_user_stats(user_id)
        return success_response(stats)

    except Exception as e:
        logger.error(f"Error retrieving history stats: {str(e)}")
        return error_response("Failed to retrieve history stats", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/history/7day", methods=["GET"])
@jwt_required()
def get_7_day_history():
    """Get the last 7 days of quest history (excluding today)"""
    try:
        user_id = get_jwt_identity()
        history_service = HistoryService(db.session)

        history = history_service.get_7_day_history(user_id)
        return success_response({"history": history})

    except Exception as e:
        logger.error(f"Error retrieving 7-day history: {str(e)}")
        return error_response("Failed to retrieve 7-day history", "INTERNAL_ERROR", 500)
