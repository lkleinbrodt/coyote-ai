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


@sidequest_bp.route("/auth/anonymous/signin", methods=["POST"])
def anonymous_signin():
    """Handle anonymous user authentication"""
    logger.info("Anonymous signin route accessed")

    try:
        data = request.get_json(silent=True)
        if not data:
            print("No data provided")
            return (
                jsonify({"success": False, "error": {"message": "No data provided"}}),
                400,
            )

        # Extract device UUID from request
        device_uuid = data.get("device_uuid")
        if not device_uuid:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "No device UUID provided"},
                    }
                ),
                400,
            )

        # Validate UUID format - only accept UUID v4
        try:
            import uuid

            # Parse the UUID first to check if it's valid
            parsed_uuid = uuid.UUID(device_uuid)

            # Specifically reject anything not version 4
            if parsed_uuid.version != 4:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": {"message": "Invalid device UUID format"},
                        }
                    ),
                    400,
                )

        except (ValueError, TypeError):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Invalid device UUID format"},
                    }
                ),
                400,
            )

        # Check if user with this anon_id already exists
        user = User.query.filter_by(anon_id=device_uuid).first()

        if not user:
            # Create new anonymous user
            logger.info(f"Creating new anonymous user with device UUID: {device_uuid}")
            user = User(anon_id=device_uuid)
            db.session.add(user)
            db.session.commit()
            logger.debug(f"Anonymous user created with ID: {user.id}")
        else:
            logger.info(f"Anonymous user found with device UUID: {device_uuid}")

        # Check if user needs a SideQuest profile created
        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        if not sidequest_user:
            logger.info(f"Creating new SideQuest profile for anonymous user {user.id}")
            sidequest_user = SideQuestUser(
                user_id=user.id,
                onboarding_completed=False,  # New users need to complete onboarding
            )
            db.session.add(sidequest_user)
            db.session.commit()
            logger.debug(f"SideQuest profile created for anonymous user {user.id}")

        # Create long-lived access token (1 year) - same as Apple users
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "anon_id": user.anon_id,
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "role": getattr(user, "role", "user"),
            },
            expires_delta=timedelta(days=365),  # 1 year token
        )

        logger.info(f"Anonymous signin successful for user {user.id}")

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

    except Exception as e:
        logger.error(f"Anonymous signin error: {str(e)}", exc_info=True)
        print(e)
        return (
            jsonify(
                {"success": False, "error": {"message": "Anonymous signin failed"}}
            ),
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


@sidequest_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_user():
    """Delete user"""
    user_id = get_jwt_identity()
    # get sidequest profile
    sidequest_profile = SideQuestUser.query.filter_by(user_id=user_id).first()
    if not sidequest_profile:
        return (
            jsonify(
                {"success": False, "error": {"message": "SideQuest profile not found"}}
            ),
            404,
        )
    # delete sidequest profile
    db.session.delete(sidequest_profile)
    db.session.commit()
    return jsonify(
        {"success": True, "message": "SideQuest profile deleted successfully"}
    )


@sidequest_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {"success": False, "error": {"message": "Authentication required"}}
                ),
                401,
            )

        logger.info(f"Fetching profile for user {user_id}")

        user_service = UserService(db.session)
        profile = user_service.get_or_create_user_profile(user_id)
        logger.info(f"Profile fetched for user {user_id}: {profile.to_dict()}")
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


@sidequest_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_user_profile():
    """Update user profile"""
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
                        "error": {"message": "Profile data is required"},
                    }
                ),
                400,
            )

        logger.info(f"Updating preferences for user {user_id}: {data}")

        user_service = UserService(db.session)
        profile = user_service.update_user_profile(user_id, data)

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
