from datetime import datetime, timedelta
from typing import Dict, Any

from flask import Blueprint, current_app, request
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
from backend.sidequest.utils.response import success_response, error_response
import humps

logger = create_logger(__name__)


@sidequest_bp.route("/auth/apple/signin", methods=["POST"])
def signin():
    """Handle Sign in with Apple authentication"""
    logger.info("Apple signin route accessed")

    try:
        credentials = request.get_json()
        if not credentials:
            return error_response("No data provided", "MISSING_DATA", 400)

        # Extract Apple credential from request
        credential = credentials.get("appleIdToken")
        if not credential:
            return error_response(
                "No Apple credential provided", "MISSING_CREDENTIAL", 400
            )

        identity_token = credential.get("identityToken")
        if not identity_token:
            return error_response(
                "Credential object missing identityToken", "INVALID_CREDENTIAL", 400
            )

        # Use the consolidated Apple Auth Service with SideQuest bundle ID
        user = get_apple_auth_service().authenticate_with_apple(
            credential, client_id="com.lkleinbrodt.SideQuest", app_name="SideQuest"
        )
        logger.debug(f"Successfully authenticated user: {user.id}")

        # Check if user needs a SideQuest profile created
        sidequest_user = SideQuestUser.query.filter_by(user_id=user.id).first()
        if not sidequest_user:
            user_service = UserService(db.session)
            sidequest_user = user_service.create_user(user.id, {})
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

        return success_response(
            {
                "access_token": access_token,
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "image": user.image,
                    "role": getattr(user, "role", "user"),
                },
            }
        )

    except ValueError as e:
        print(e)
        logger.error(f"Apple signin error: {str(e)}", exc_info=True)
        return error_response(str(e), "VALIDATION_ERROR", 400)
    except Exception as e:
        print(e)
        logger.error(f"Mobile Apple login error: {str(e)}", exc_info=True)
        return error_response("Login failed", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/auth/anonymous/signin", methods=["POST"])
def anonymous_signin():
    """Handle anonymous user authentication"""
    logger.info("Anonymous signin route accessed")

    try:
        data = request.get_json(silent=True)
        if not data:
            print("No data provided")
            return error_response("No data provided", "MISSING_DATA", 400)

        # Extract device UUID from request
        device_uuid = data.get("device_uuid")
        if not device_uuid:
            return error_response("No device UUID provided", "MISSING_DEVICE_UUID", 400)

        # Validate UUID format - only accept UUID v4
        try:
            import uuid

            # Parse the UUID first to check if it's valid
            parsed_uuid = uuid.UUID(device_uuid)

            # Specifically reject anything not version 4
            if parsed_uuid.version != 4:
                print(parsed_uuid.version)
                return error_response(
                    "Invalid device UUID format", "INVALID_UUID_FORMAT", 400
                )

        except (ValueError, TypeError) as e:
            print("Invalid device UUID format")
            print(e)
            return error_response(
                "Invalid device UUID format", "INVALID_UUID_FORMAT", 400
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
        user_service = UserService(db.session)
        if not sidequest_user:
            # If they provide initial profile data, use it

            logger.info(f"Creating new SideQuest profile for anonymous user {user.id}")

            sidequest_user = user_service.create_user(user.id, {})
            logger.debug(f"SideQuest profile created for anonymous user {user.id}")

        profile_data = data.get("profile", {})
        if profile_data:
            sidequest_user = user_service.update_user_profile(user.id, profile_data)

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

        return success_response(
            {
                "access_token": access_token,
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "image": user.image,
                    "role": getattr(user, "role", "user"),
                },
            },
        )

    except Exception as e:
        logger.error(f"Anonymous signin error: {str(e)}", exc_info=True)
        print(e)
        return error_response("Anonymous signin failed", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for SideQuest service"""
    try:
        return success_response(
            {
                "service": "SideQuest",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return error_response("Service unhealthy", "SERVICE_UNHEALTHY", 500)


@sidequest_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_user():
    """Delete user"""
    user_id = get_jwt_identity()
    # get sidequest profile
    sidequest_profile = SideQuestUser.query.filter_by(user_id=user_id).first()
    if not sidequest_profile:
        return error_response("SideQuest profile not found", "PROFILE_NOT_FOUND", 404)
    # delete sidequest profile
    db.session.delete(sidequest_profile)
    db.session.commit()
    return success_response({"message": "SideQuest profile deleted successfully"})


@sidequest_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return error_response(
                "Authentication required", "AUTHENTICATION_REQUIRED", 401
            )

        logger.info(f"Fetching profile for user {user_id}")

        user_service = UserService(db.session)
        profile = user_service.get_or_create_user_profile(user_id)
        logger.info(f"Profile fetched for user {user_id}: {profile.to_dict()}")

        data = profile.to_dict()
        return success_response(data)

    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}", exc_info=True)
        return error_response("Failed to fetch preferences", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_user_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return error_response(
                "Authentication required", "AUTHENTICATION_REQUIRED", 401
            )

        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("No preference data provided")
            return error_response("Profile data is required", "MISSING_DATA", 400)

        logger.info(f"Updating preferences for user {user_id}: {data}")

        # Convert incoming camelCase keys to snake_case for the service layer
        snake_case_data = humps.decamelize(data)

        user_service = UserService(db.session)
        profile = user_service.update_user_profile(user_id, snake_case_data)

        return success_response(profile.to_dict())

    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
        return error_response("Failed to update preferences", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/onboarding/complete", methods=["POST"])
@jwt_required()
def complete_onboarding():
    """Mark user's onboarding as completed"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return error_response(
                "Authentication required", "AUTHENTICATION_REQUIRED", 401
            )

        logger.info(f"Marking onboarding completed for user {user_id}")

        user_service = UserService(db.session)
        profile = user_service.mark_onboarding_completed(user_id)

        return success_response(
            {
                "message": "Onboarding completed successfully",
                "onboardingCompleted": True,
                "preferences": profile.to_dict(),
                "userId": user_id,
            }
        )

    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}", exc_info=True)
        return error_response("Failed to complete onboarding", "INTERNAL_ERROR", 500)


@sidequest_bp.route("/local-time", methods=["GET"])
@jwt_required()
def get_local_time():
    """Get user's local time"""
    user_id = get_jwt_identity()
    user_service = UserService(db.session)
    return success_response(
        {"localTime": user_service.get_user_time(user_id).isoformat()}
    )


@sidequest_bp.route("/me/reset", methods=["POST"])
@jwt_required()
def reset_user_profile():
    """Reset user profile"""
    user_id = get_jwt_identity()
    user_service = UserService(db.session)
    user_service.reset_user_profile(user_id)
    return success_response({"message": "User profile reset successfully"})
