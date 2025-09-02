from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.sidequest.services.voting_service import VotingService
from backend.sidequest.utils.response import success_response, error_response
from backend.extensions import db, create_logger
from backend.sidequest.routes import sidequest_bp


logger = create_logger(__name__)


@sidequest_bp.route("/voting/quests", methods=["GET"])
@jwt_required()
def get_quests_to_vote_on():
    """Get quest templates for the user to vote on"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 5, type=int)

        # Validate limit
        if limit < 1 or limit > 20:
            return error_response("Limit must be between 1 and 20", 400)

        voting_service = VotingService(db.session)
        quest_templates = voting_service.get_quests_to_vote_on(user_id, limit)

        return success_response(
            {"quest_templates": [template.to_dict() for template in quest_templates]}
        )

    except Exception as e:
        logger.error(f"Error getting quests to vote on: {str(e)}")
        return error_response("Failed to get quests to vote on", 500)


@sidequest_bp.route("/voting/vote", methods=["POST"])
@jwt_required()
def submit_vote():
    """Submit a vote on a quest template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("Request body is required", 400)

        quest_template_id = data.get("quest_template_id")
        vote = data.get("vote")

        if not quest_template_id:
            return error_response("quest_template_id is required", 400)

        if not vote:
            return error_response("vote is required", 400)

        if vote not in ["thumbs_up", "thumbs_down"]:
            return error_response("vote must be 'thumbs_up' or 'thumbs_down'", 400)

        voting_service = VotingService(db.session)
        vote_obj = voting_service.submit_vote(user_id, quest_template_id, vote)

        return success_response({"vote": vote_obj.to_dict()})

    except ValueError as e:
        logger.warning(f"Invalid vote data: {str(e)}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error submitting vote: {str(e)}")
        return error_response("Failed to submit vote", 500)


@sidequest_bp.route("/voting/my-votes", methods=["GET"])
@jwt_required()
def get_my_votes():
    """Get all votes by the current user"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 50, type=int)

        # Validate limit
        if limit < 1 or limit > 100:
            return error_response("Limit must be between 1 and 100", 400)

        voting_service = VotingService(db.session)
        votes = voting_service.get_user_votes(user_id, limit)

        return success_response({"votes": [vote.to_dict() for vote in votes]})

    except Exception as e:
        logger.error(f"Error getting user votes: {str(e)}")
        return error_response("Failed to get user votes", 500)


@sidequest_bp.route("/voting/stats/<int:quest_template_id>", methods=["GET"])
@jwt_required()
def get_template_vote_stats(quest_template_id):
    """Get voting statistics for a quest template"""
    try:
        voting_service = VotingService(db.session)
        stats = voting_service.get_template_vote_stats(quest_template_id)

        return success_response(stats)

    except Exception as e:
        logger.error(f"Error getting template vote stats: {str(e)}")
        return error_response("Failed to get template vote stats", 500)
