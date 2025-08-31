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
from .services import QuestGenerationService, UserService, QuestService
from .models import QuestCategory, QuestDifficulty, SideQuestUser

logger = create_logger(__name__)
sidequest_bp = Blueprint("sidequest", __name__, url_prefix="/sidequest")


@sidequest_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_daily_quests():
    """Generate daily quests for the authenticated user"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        if not user_id:
            logger.warning("No user ID found in JWT token")
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided in request")
            return (
                jsonify({"success": False, "error": {"message": "No data provided"}}),
                400,
            )

        preferences = data.get("preferences")
        context = data.get("context")

        if not preferences:
            logger.warning("No preferences provided in request")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "User preferences are required"},
                    }
                ),
                400,
            )

        # Validate preferences structure
        if not isinstance(preferences, dict):
            logger.warning("Preferences must be a dictionary")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Preferences must be a dictionary"},
                    }
                ),
                400,
            )

        # Validate required preference fields
        required_fields = ["categories", "difficulty", "max_time"]
        for field in required_fields:
            if field not in preferences:
                logger.warning(f"Missing required preference field: {field}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": {
                                "message": f"Missing required preference field: {field}"
                            },
                        }
                    ),
                    400,
                )

        # Validate categories
        if (
            not isinstance(preferences["categories"], list)
            or not preferences["categories"]
        ):
            logger.warning("Categories must be a non-empty list")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Categories must be a non-empty list"},
                    }
                ),
                400,
            )

        # Validate difficulty
        try:
            QuestDifficulty(preferences["difficulty"])
        except ValueError:
            logger.warning(f"Invalid difficulty level: {preferences['difficulty']}")
            return (
                jsonify(
                    {"success": False, "error": {"message": "Invalid difficulty level"}}
                ),
                400,
            )

        # Validate max_time
        if not isinstance(preferences["max_time"], int) or preferences["max_time"] <= 0:
            logger.warning(f"Invalid max_time: {preferences['max_time']}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "max_time must be a positive integer"},
                    }
                ),
                400,
            )

        logger.info(
            f"Generating quests for user {user_id} with preferences: {preferences}"
        )

        # Get OpenAI API key from config
        openai_api_key = current_app.config.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY not configured")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Quest generation service unavailable"},
                    }
                ),
                503,
            )

        # Check if user has available quests first
        quest_service = QuestService(db.session)
        available_quests = quest_service.get_available_quests(user_id)

        if available_quests:
            # User has open quests within generation window, return those
            logger.info(
                f"User {user_id} has {len(available_quests)} available quests, returning existing ones"
            )
            quests_data = [quest.to_dict() for quest in available_quests]
        else:
            # No available quests, generate new ones
            logger.info(f"User {user_id} has no available quests, generating new ones")
            quest_generation_service = QuestGenerationService(
                db.session, openai_api_key
            )
            quests = quest_generation_service.generate_daily_quests(
                user_id, preferences, context
            )
            quests_data = [quest.to_dict() for quest in quests]

        logger.info(f"Returning {len(quests_data)} quests for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "quests": quests_data,
                        "metadata": {
                            "generatedAt": datetime.now().isoformat(),
                            "count": len(quests_data),
                            "user_id": user_id,
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error generating quests: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to generate quests"}}
            ),
            500,
        )


@sidequest_bp.route("/quests/active", methods=["GET"])
@jwt_required()
def get_active_quests():
    """Get active quests for the authenticated user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        quest_service = QuestService(db.session)
        quests = quest_service.get_active_quests(user_id)

        quests_data = [quest.to_dict() for quest in quests]

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "quests": quests_data,
                        "count": len(quests_data),
                        "user_id": user_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting active quests: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to get active quests"}}
            ),
            500,
        )


@sidequest_bp.route("/quests/available", methods=["GET"])
@jwt_required()
def get_available_quests():
    """Get available quests for the authenticated user (open quests within generation window)"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"Fetching available quests for user {user_id}")

        quest_service = QuestService(db.session)
        quests = quest_service.get_available_quests(user_id)

        quests_data = [quest.to_dict() for quest in quests]

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "quests": quests_data,
                        "count": len(quests_data),
                        "user_id": user_id,
                        "generated_at": datetime.now().isoformat(),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching available quests: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": {"message": "Failed to fetch available quests"},
                }
            ),
            500,
        )


@sidequest_bp.route("/quests", methods=["GET"])
@jwt_required()
def get_user_quests():
    """Get quests for the authenticated user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get query parameters
        date_str = request.args.get("date")
        include_expired = request.args.get("include_expired", "false").lower() == "true"

        # Parse date if provided
        date = None
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": {
                                "message": "Invalid date format. Use ISO format (YYYY-MM-DD)"
                            },
                        }
                    ),
                    400,
                )

        logger.info(
            f"Fetching quests for user {user_id}, date: {date}, include_expired: {include_expired}"
        )

        # Get quests

        quest_service = QuestService(db.session)
        quests = quest_service.get_user_quests(user_id, date, include_expired)

        quests_data = [quest.to_dict() for quest in quests]

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "quests": quests_data,
                        "count": len(quests_data),
                        "user_id": user_id,
                        "date": date.isoformat() if date else None,
                        "include_expired": include_expired,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching quests: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Failed to fetch quests"}}),
            500,
        )


@sidequest_bp.route("/quests/<int:quest_id>/select", methods=["POST"])
@jwt_required()
def select_quest(quest_id: int):
    """Mark a quest as selected by the user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"User {user_id} selecting quest {quest_id}")

        quest_service = QuestService(db.session)
        success = quest_service.mark_quest_selected(quest_id, user_id)

        if not success:
            logger.warning(
                f"Quest {quest_id} not found or not accessible to user {user_id}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Quest not found or not accessible"},
                    }
                ),
                404,
            )

        logger.info(f"Quest {quest_id} successfully selected by user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Quest selected successfully",
                        "quest_id": quest_id,
                        "user_id": user_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error selecting quest: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Failed to select quest"}}),
            500,
        )


@sidequest_bp.route("/quests/<int:quest_id>/complete", methods=["POST"])
@jwt_required()
def complete_quest(quest_id: int):
    """Mark a quest as completed with feedback"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get and validate feedback data
        data = request.get_json()
        if not data:
            logger.warning("No feedback data provided")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Feedback data is required"},
                    }
                ),
                400,
            )

        feedback = data.get("feedback")
        if not feedback:
            logger.warning("No feedback object provided")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Feedback object is required"},
                    }
                ),
                400,
            )

        # Validate feedback structure
        if not isinstance(feedback, dict):
            logger.warning("Feedback must be a dictionary")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Feedback must be a dictionary"},
                    }
                ),
                400,
            )

        logger.info(
            f"User {user_id} completing quest {quest_id} with feedback: {feedback}"
        )

        quest_service = QuestService(db.session)
        success = quest_service.mark_quest_completed(quest_id, user_id, feedback)

        if not success:
            logger.warning(
                f"Quest {quest_id} not found or not accessible to user {user_id}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Quest not found or not accessible"},
                    }
                ),
                404,
            )

        logger.info(f"Quest {quest_id} successfully completed by user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Quest completed successfully",
                        "quest_id": quest_id,
                        "user_id": user_id,
                        "feedback": feedback,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error completing quest: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to complete quest"}}
            ),
            500,
        )


@sidequest_bp.route("/quests/refresh", methods=["POST"])
@jwt_required()
def refresh_quests():
    """Refresh quests for the authenticated user - mark old ones as skipped and generate new ones"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get and validate request data
        data = request.get_json() or {}
        preferences = data.get("preferences")
        context = data.get("context")

        if not preferences:
            logger.warning("No preferences provided in refresh request")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "User preferences are required"},
                    }
                ),
                400,
            )

        # Validate preferences structure
        if not isinstance(preferences, dict):
            logger.warning("Preferences must be a dictionary")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Preferences must be a dictionary"},
                    }
                ),
                400,
            )

        # Validate required preference fields
        required_fields = ["categories", "difficulty", "max_time"]
        for field in required_fields:
            if field not in preferences:
                logger.warning(f"Missing required preference field: {field}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": {
                                "message": f"Missing required preference field: {field}"
                            },
                        }
                    ),
                    400,
                )

        # Validate categories
        if (
            not isinstance(preferences["categories"], list)
            or not preferences["categories"]
        ):
            logger.warning("Categories must be a non-empty list")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Categories must be a non-empty list"},
                    }
                ),
                400,
            )

        # Validate difficulty
        try:
            QuestDifficulty(preferences["difficulty"])
        except ValueError:
            logger.warning(f"Invalid difficulty level: {preferences['difficulty']}")
            return (
                jsonify(
                    {"success": False, "error": {"message": "Invalid difficulty level"}}
                ),
                400,
            )

        # Validate max_time
        if not isinstance(preferences["max_time"], int) or preferences["max_time"] <= 0:
            logger.warning(f"Invalid max_time: {preferences['max_time']}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "max_time must be a positive integer"},
                    }
                ),
                400,
            )

        logger.info(f"Refreshing quests for user {user_id}")

        # Get OpenAI API key from config
        openai_api_key = current_app.config.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY not configured")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Quest generation service unavailable"},
                    }
                ),
                503,
            )

        # Refresh quests: mark old ones as skipped and generate new ones
        quest_service = QuestService(db.session)
        refresh_result = quest_service.refresh_user_quests(
            user_id, preferences, context, openai_api_key
        )

        if not refresh_result["success"]:
            return (
                jsonify(
                    {"success": False, "error": {"message": refresh_result["error"]}}
                ),
                500,
            )

        quests_data = [quest.to_dict() for quest in refresh_result["quests"]]

        logger.info(f"Successfully refreshed quests for user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "quests": quests_data,
                        "metadata": {
                            "refreshedAt": datetime.now().isoformat(),
                            "count": len(quests_data),
                            "user_id": user_id,
                            "oldQuestsSkipped": refresh_result["old_quests_skipped"],
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error refreshing quests: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to refresh quests"}}
            ),
            500,
        )


@sidequest_bp.route("/quests/<int:quest_id>/skip", methods=["POST"])
@jwt_required()
def skip_quest(quest_id: int):
    """Mark a quest as skipped by the user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"User {user_id} skipping quest {quest_id}")

        quest_service = QuestService(db.session)
        success = quest_service.mark_quest_skipped(quest_id, user_id)

        if not success:
            logger.warning(
                f"Quest {quest_id} not found or not accessible to user {user_id}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Quest not found or not accessible"},
                    }
                ),
                404,
            )

        logger.info(f"Quest {quest_id} successfully skipped by user {user_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Quest skipped successfully",
                        "quest_id": quest_id,
                        "user_id": user_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error skipping quest: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Failed to skip quest"}}),
            500,
        )


@sidequest_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_user_preferences():
    """Get user preferences and profile"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"Fetching preferences for user {user_id}")

        user_service = UserService(db.session)
        profile = user_service.get_or_create_user_profile(user_id)
        logger.info(f"Preferences fetched for user {user_id}: {profile.to_dict()}")
        return (
            jsonify({"success": True, "data": profile.to_dict()}),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to fetch preferences"}}
            ),
            500,
        )


@sidequest_bp.route("/preferences", methods=["PUT"])
@jwt_required()
def update_user_preferences():
    """Update user preferences"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("No preference data provided")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Preference data is required"},
                    }
                ),
                400,
            )

        logger.info(f"Updating preferences for user {user_id}: {data}")

        user_service = UserService(db.session)
        profile = user_service.update_user_preferences(user_id, data)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Preferences updated successfully",
                        "preferences": profile.to_dict(),
                        "user_id": user_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to update preferences"}}
            ),
            500,
        )


@sidequest_bp.route("/onboarding/complete", methods=["POST"])
@jwt_required()
def complete_onboarding():
    """Mark user's onboarding as completed"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"Marking onboarding completed for user {user_id}")

        user_service = UserService(db.session)
        profile = user_service.mark_onboarding_completed(user_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Onboarding completed successfully",
                        "onboarding_completed": True,
                        "user_id": user_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": {"message": "Failed to complete onboarding"},
                }
            ),
            500,
        )


@sidequest_bp.route("/history", methods=["GET"])
@jwt_required()
def get_quest_history():
    """Get quest history and statistics for the user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        # Get query parameters
        days = request.args.get("days", "7")
        try:
            days = int(days)
            if days <= 0 or days > 365:
                raise ValueError("Days must be between 1 and 365")
        except ValueError:
            logger.warning(f"Invalid days parameter: {days}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {
                            "message": "Days must be a positive integer between 1 and 365"
                        },
                    }
                ),
                400,
            )

        logger.info(f"Fetching quest history for user {user_id}, last {days} days")

        quest_service = QuestService(db.session)
        history = quest_service.get_quest_history(user_id, days)

        return (
            jsonify(
                {"success": True, "data": {"history": history, "user_id": user_id}}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching quest history: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": {"message": "Failed to fetch quest history"},
                }
            ),
            500,
        )


@sidequest_bp.route("/auth/apple/signin", methods=["POST"])
def signin():
    """Handle Sign in with Apple authentication"""
    logger.info("Apple signin route accessed")

    try:
        credentials = request.get_json()
        if not credentials:
            return (
                jsonify({"success": False, "error": {"message": "No data provided"}}),
                400,
            )

        # Extract Apple credential from request
        credential = credentials.get("appleIdToken")
        if not credential:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "No Apple credential provided"},
                    }
                ),
                400,
            )

        identity_token = credential.get("identityToken")
        if not identity_token:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Credential object missing identityToken"},
                    }
                ),
                400,
            )

        # Use the consolidated Apple Auth Service with SideQuest bundle ID
        user = get_apple_auth_service().authenticate_with_apple(
            credential, client_id="com.lkleinbrodt.SideQuest", app_name="SideQuest"
        )
        logger.debug(f"Successfully authenticated user: {user.id}")

        # Check if user needs a SideQuest profile created
        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        if not sidequest_user:
            logger.info(f"Creating new SideQuest profile for user {user.id}")
            sidequest_user = SideQuestUser(
                user_id=user.id,
                onboarding_completed=False,  # New users need to complete onboarding
            )
            db.session.add(sidequest_user)
            db.session.commit()
            logger.debug(f"SideQuest profile created for user {user.id}")

        # Create long-lived access token (1 year) - simpler for mobile
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "role": getattr(user, "role", "user"),
            },
            expires_delta=timedelta(days=365),  # 1 year token
        )

        logger.info(f"Mobile Apple login successful for user {user.id}")

        return jsonify(
            {
                "success": True,
                "data": {
                    "access_token": access_token,
                    "user": {
                        "id": str(user.id),
                        "name": user.name,
                        "email": user.email,
                        "image": user.image,
                        "role": getattr(user, "role", "user"),
                    },
                },
            }
        )

    except ValueError as e:
        logger.error(f"Apple signin error: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": str(e)}}),
            400,
        )
    except Exception as e:
        logger.error(f"Mobile Apple login error: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Login failed"}}),
            500,
        )


@sidequest_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for SideQuest service"""
    try:
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "service": "SideQuest",
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return (
            jsonify({"success": False, "error": {"message": "Service unhealthy"}}),
            500,
        )
