from datetime import datetime, timedelta
from typing import Dict, Any

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)
from sqlalchemy.orm import Session

from backend.extensions import create_logger, db
from backend.src.apple_auth_service import get_apple_auth_service
from backend.sidequest.services import QuestGenerationService, UserService, QuestService
from backend.sidequest.models import QuestCategory, QuestDifficulty, SideQuestUser
from backend.models import User
from backend.sidequest.routes import sidequest_bp

logger = create_logger(__name__)

"""
We need routes to:
1) check if your quest board needs a refresh
2) refresh the quest board
3) get the quest board
4) Update a quest with each of the possible statuses
5) pull user's quest history

"""


# first, check if your quest board needs a refresh
@sidequest_bp.route("/quests/needs-refresh", methods=["GET"])
@jwt_required()
def needs_refresh():
    user_id = get_jwt_identity()
    quest_service = QuestService(db.session)
    needs_refresh = quest_service.board_needs_refresh(user_id)
    return jsonify({"needs_refresh": needs_refresh})


# refresh the quest board
@sidequest_bp.route("/quests/refresh", methods=["POST"])
@jwt_required()
def refresh():
    user_id = get_jwt_identity()
    quest_service = QuestService(db.session)
    quest_service.get_refreshed_board(user_id)
    return jsonify({"success": True, "board": quest_service.get_board(user_id)})


# get the quest board
@sidequest_bp.route("/quests/board", methods=["GET"])
@jwt_required()
def get_board():
    user_id = get_jwt_identity()
    # user can skip a refresh if desired
    skip_refresh = request.json.get("skip_refresh", False)
    service = QuestService(db.session)
    if skip_refresh:
        board = service.get_board(user_id)
    else:
        board = service.get_refreshed_board(user_id)

    return jsonify({"success": True, "board": board})


@sidequest_bp.route("/quests/status/accept", methods=["PUT"])
@jwt_required()
def accept():
    user_id = get_jwt_identity()
    quest_id = request.json.get("quest_id")
    quest_service = QuestService(db.session)
    if not quest_service.validate_ownership(quest_id, user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "You do not have permission to accept this quest"
                    },
                }
            ),
            401,
        )
    quest_service.accept_quest(quest_id)
    return jsonify({"success": True, "quest": quest_service.get_quest(quest_id)})


@sidequest_bp.route("/quests/status/complete", methods=["PUT"])
@jwt_required()
def complete():
    user_id = get_jwt_identity()
    quest_id = request.json.get("quest_id")
    quest_service = QuestService(db.session)
    if not quest_service.validate_ownership(quest_id, user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "You do not have permission to complete this quest"
                    },
                }
            ),
            401,
        )
    quest_service.complete_quest(quest_id)
    return jsonify({"success": True, "quest": quest_service.get_quest(quest_id)})


@sidequest_bp.route("/quests/status/abandon", methods=["PUT"])
@jwt_required()
def abandon():
    user_id = get_jwt_identity()
    quest_id = request.json.get("quest_id")
    quest_service = QuestService(db.session)
    if not quest_service.validate_ownership(quest_id, user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "You do not have permission to abandon this quest"
                    },
                }
            ),
            401,
        )
    quest_service.abandon_quest(quest_id)
    return jsonify({"success": True, "quest": quest_service.get_quest(quest_id)})


@sidequest_bp.route("/quests/status/decline", methods=["PUT"])
@jwt_required()
def decline():
    user_id = get_jwt_identity()
    quest_id = request.json.get("quest_id")
    quest_service = QuestService(db.session)
    if not quest_service.validate_ownership(quest_id, user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "You do not have permission to decline this quest"
                    },
                }
            ),
            401,
        )
    quest_service.decline_quest(quest_id)
    return jsonify({"success": True, "quest": quest_service.get_quest(quest_id)})


@sidequest_bp.route("/quests/status/fail", methods=["PUT"])
@jwt_required()
def fail():
    user_id = get_jwt_identity()
    quest_id = request.json.get("quest_id")
    quest_service = QuestService(db.session)
    if not quest_service.validate_ownership(quest_id, user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "You do not have permission to fail this quest"
                    },
                }
            ),
            401,
        )
    quest_service.fail_quest(quest_id)
    return jsonify({"success": True, "quest": quest_service.get_quest(quest_id)})
