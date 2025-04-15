import json
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import or_

from backend.extensions import create_logger, db
from backend.models import (
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
    UserBalance,
)
from backend.speech.models import Analysis, Recording, SpeechOperation, SpeechProfile
from backend.speech.openai_client import (
    OpenAICosts,
    analyze_speech,
    get_title,
    moderate_speech,
    transcribe_audio,
)
from backend.src.auth import apple_signin

logger = create_logger(__name__, level="DEBUG")
speech_bp = Blueprint("speech", __name__, url_prefix="/speech")


@speech_bp.route("/auth/apple/signin", methods=["POST"])
def signin():
    """Handle Sign in with Apple authentication"""
    credentials = request.get_json()

    if not credentials or not credentials.get("identityToken"):
        logger.error("No identity token provided")
        return jsonify({"error": "No identity token provided"}), 400

    try:
        user = apple_signin(credentials)

        # check if they have a speech profile
        speech_profile = SpeechProfile.query.filter_by(user_id=user.id).first()
        if not speech_profile:
            # create a new speech profile
            speech_profile = SpeechProfile(user_id=user.id)
            db.session.add(speech_profile)
            db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": speech_profile.role,
            },
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
        )
        return jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    except ValueError as e:
        logger.error("Apple Sign In failed: %s", str(e))
        return jsonify({"error": str(e)}), 400


@speech_bp.route("/me")
@jwt_required()
def get_current_user():
    """Get current user profile with speech-specific data"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    speech_profile = SpeechProfile.query.get_or_404(user.id)

    return jsonify(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "speakingLevel": (
                speech_profile.speaking_level if speech_profile else None
            ),
            "totalRecordings": (
                speech_profile.total_recordings if speech_profile else 0
            ),
            "totalPracticeTime": (
                speech_profile.total_practice_time if speech_profile else 0
            ),
            "lastPractice": (
                speech_profile.last_practice.isoformat()
                if speech_profile and speech_profile.last_practice
                else None
            ),
        }
    )


@speech_bp.route("/signout", methods=["POST"])
@jwt_required()
def signout():
    """Handle user sign out"""
    # In a JWT-based system, we don't need to do anything server-side
    # The client will remove the token
    return jsonify({"message": "Successfully signed out"})


@speech_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_recording():
    """Analyze a recording"""

    audio_file = request.files.get("audio")
    duration = request.form.get("duration")
    if not audio_file or not duration:
        logger.error("Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Get user and profile
        user_id = get_jwt_identity()
        speech_profile = SpeechProfile.query.filter_by(user_id=user_id).first()
        if not speech_profile:
            logger.error("Speech profile not found for user %s", user_id)
            return jsonify({"error": "Speech profile not found"}), 404

        # Get user balance from central billing system
        balance = UserBalance.query.filter_by(user_id=user_id).first()
        if not balance:
            balance = UserBalance(user_id=user_id)
            db.session.add(balance)
            db.session.commit()

        # 1. Calculate transcription cost
        duration_seconds = int(duration)
        estimated_cost = OpenAICosts.estimate_analysis_cost(duration_seconds)

        # Check if user has sufficient balance
        if not balance.has_sufficient_balance(estimated_cost):
            return (
                jsonify(
                    {
                        "error": "Insufficient balance",
                        "required": float(estimated_cost),
                        "balance": float(balance.balance),
                    }
                ),
                402,
            )

        try:
            # 2. Transcribe audio and charge for it
            audio_data = audio_file.read()
            transcript = transcribe_audio(audio_data)
            transcription_cost = OpenAICosts.calculate_whisper_cost(duration_seconds)

            # Create and complete transcription transaction
            transaction = Transaction(
                user_id=user_id,
                balance_id=balance.id,
                application="speech",
                amount=-transcription_cost,
                transaction_type=TransactionType.USAGE,
                operation=SpeechOperation.TRANSCRIPTION.value,
                status=TransactionStatus.COMPLETED,
            )
            db.session.add(transaction)
            balance.debit(transcription_cost)
            db.session.commit()

            # 3. Check moderation
            moderation_response = moderate_speech(transcript)
            moderation_cost = OpenAICosts.calculate_moderation_cost()

            # Charge for moderation
            transaction = Transaction(
                user_id=user_id,
                balance_id=balance.id,
                application="speech",
                amount=-moderation_cost,
                transaction_type=TransactionType.USAGE,
                operation=SpeechOperation.MODERATION.value,
                status=TransactionStatus.COMPLETED,
            )
            db.session.add(transaction)
            balance.debit(moderation_cost)
            db.session.commit()

            if moderation_response.flagged:
                reason = moderation_response.get_reason()
                return jsonify({"message": f"Content Flagged for {reason}"}), 400

            # 4. Get title
            title = get_title(transcript)
            title_cost = OpenAICosts.calculate_gpt4_cost(transcript, title)

            transaction = Transaction(
                user_id=user_id,
                balance_id=balance.id,
                application="speech",
                amount=-title_cost,
                transaction_type=TransactionType.USAGE,
                operation=SpeechOperation.TITLE.value,
                status=TransactionStatus.COMPLETED,
            )
            db.session.add(transaction)
            balance.debit(title_cost)
            db.session.commit()

            # 5. Analyze speech
            analysis_data = analyze_speech(transcript)
            analysis_cost = OpenAICosts.calculate_gpt4_cost(
                transcript, json.dumps(analysis_data)
            )

            # Charge for analysis
            transaction = Transaction(
                user_id=user_id,
                balance_id=balance.id,
                application="speech",
                amount=-analysis_cost,
                transaction_type=TransactionType.USAGE,
                operation=SpeechOperation.ANALYSIS.value,
                status=TransactionStatus.COMPLETED,
            )
            db.session.add(transaction)
            balance.debit(analysis_cost)
            db.session.commit()

            # Create recording record
            recording = Recording(
                profile_id=speech_profile.id,
                title=title,
                duration=duration_seconds,
                file_path="",  # TODO: Save file and store path
                created_at=datetime.utcnow(),
            )
            db.session.add(recording)
            db.session.commit()

            # Create analysis record
            analysis = Analysis(
                recording_id=recording.id,
                transcript=transcript,
                clarity_score=analysis_data["clarity"],
                pace_score=analysis_data["pace"],
                filler_word_count=analysis_data["fillerWords"],
                tone_analysis=analysis_data["toneAnalysis"],
                content_structure=analysis_data["contentStructure"],
                feedback=analysis_data["suggestions"],
                created_at=datetime.utcnow(),
            )
            db.session.add(analysis)

            # Update profile stats
            speech_profile.total_recordings += 1
            speech_profile.last_practice = datetime.utcnow()
            db.session.commit()

            return jsonify(recording.to_dict())

        except Exception as e:
            db.session.rollback()
            logger.error("Error during analysis: %s", str(e))
            raise e

    except Exception as e:
        logger.error("Error analyzing recording: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to analyze recording: {str(e)}"}), 500


@speech_bp.route("/recordings", methods=["GET"])
@jwt_required()
def get_recordings():
    """Get all recordings for the current user"""

    user_id = get_jwt_identity()
    speech_profile = SpeechProfile.query.filter_by(user_id=user_id).first()
    if not speech_profile:
        logger.error("Speech profile not found for user %s", user_id)
        return jsonify({"error": "Speech profile not found"}), 404

    recordings = Recording.query.filter_by(profile_id=speech_profile.id).all()
    return jsonify([recording.to_dict() for recording in recordings])


@speech_bp.route("/recordings/<int:id>", methods=["GET"])
@jwt_required()
def get_recording(id: int):
    """Get a recording by id"""
    recording = Recording.query.filter_by(id=id).first()
    # ensure the recording belongs to the current user
    user_id = get_jwt_identity()
    speech_profile = SpeechProfile.query.filter_by(user_id=user_id).first()
    if not speech_profile:
        logger.error("Speech profile not found for user %s", user_id)
        return jsonify({"error": "Speech profile not found"}), 404

    if not recording or recording.profile_id != speech_profile.id:
        logger.error("Recording not found for id %s", id)
        return jsonify({"error": "Recording not found"}), 404

    return jsonify(recording.to_dict())


@speech_bp.route("/recordings/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_recording(id: int):
    """Delete a recording by id"""
    # Get the recording
    recording = Recording.query.filter_by(id=id).first()
    if not recording:
        logger.error("Recording not found for id %s", id)
        return jsonify({"error": "Recording not found"}), 404

    # Ensure the recording belongs to the current user
    user_id = get_jwt_identity()
    speech_profile = SpeechProfile.query.filter_by(user_id=user_id).first()
    if not speech_profile:
        logger.error("Speech profile not found for user %s", user_id)
        return jsonify({"error": "Speech profile not found"}), 404

    if recording.profile_id != speech_profile.id:
        logger.error(
            "Unauthorized deletion attempt for recording %s by user %s", id, user_id
        )
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Delete associated analysis first (due to foreign key constraint)
        Analysis.query.filter_by(recording_id=id).delete()

        # Delete the recording
        db.session.delete(recording)

        # Update profile stats
        speech_profile.total_recordings -= 1

        # Commit the changes
        db.session.commit()

        logger.info("Successfully deleted recording %s", id)
        return jsonify({"message": "Recording deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error("Error deleting recording: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to delete recording: {str(e)}"}), 500


@speech_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_speech_profile():
    """Delete the current user's speech profile"""
    user_id = get_jwt_identity()
    speech_profile = SpeechProfile.query.filter_by(user_id=user_id).first()
    if not speech_profile:
        logger.error("Speech profile not found for user %s", user_id)
        return jsonify({"error": "Speech profile not found"}), 404

    try:
        # Delete all recordings and their analyses
        recordings = Recording.query.filter_by(profile_id=speech_profile.id).all()
        for recording in recordings:
            # Delete associated analysis first (due to foreign key constraint)
            Analysis.query.filter_by(recording_id=recording.id).delete()
            db.session.delete(recording)

        # Delete the speech profile
        db.session.delete(speech_profile)
        db.session.commit()

        logger.info("Successfully deleted speech profile for user %s", user_id)
        return jsonify({"message": "Speech profile deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error("Error deleting speech profile: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to delete speech profile: {str(e)}"}), 500
