import json
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import and_, extract, func
from sqlalchemy.types import Date

from backend.extensions import create_logger, db
from backend.openai_utils import extract_number_from_text
from backend.src.auth import apple_signin

from .models import DailyTarget, Feeding

logger = create_logger(__name__, level="DEBUG")
poppy_bp = Blueprint("poppy", __name__)


def get_or_create_daily_target():
    """Get today's target record or create a new one if none exists"""
    today = datetime.utcnow().date()
    target = DailyTarget.query.filter_by(date=today).first()
    if not target:
        # Get the most recent target to carry forward
        last_target = DailyTarget.query.order_by(DailyTarget.date.desc()).first()
        target_value = last_target.target if last_target else 3.0
        target = DailyTarget(date=today, target=target_value)
        db.session.add(target)
        db.session.commit()
    return target


@poppy_bp.route("/feeding", methods=["POST"])
@jwt_required()
def add_feeding():
    logger.info("Add feeding route accessed")
    try:
        data = request.get_json()
        amount = float(data.get("amount", 0))
        user_id = get_jwt_identity()
        logger.debug(f"User {user_id} adding feeding of amount {amount}")

        if amount == 0:
            logger.warning(f"User {user_id} attempted to add feeding with amount 0")
            return (
                jsonify(
                    {"error": {"message": "Amount cannot be zero"}, "status": "error"}
                ),
                400,
            )

        # Create feeding with timestamp default (current time in UTC)
        feeding = Feeding(amount=amount, last_updated_by=user_id)
        db.session.add(feeding)
        db.session.commit()
        logger.debug(
            f"Successfully added feeding of amount {amount} for user {user_id}"
        )

        # Get the updated daily total for today in UTC
        today_utc = datetime.utcnow().date()

        # Create UTC date range for query
        start_of_day_utc = datetime.combine(today_utc, datetime.min.time())
        end_of_day_utc = start_of_day_utc + timedelta(days=1)

        total = (
            db.session.query(func.sum(Feeding.amount))
            .filter(Feeding.timestamp >= start_of_day_utc)
            .filter(Feeding.timestamp < end_of_day_utc)
            .scalar()
            or 0.0
        )
        logger.debug(f"Updated daily total: {total}")

        out = feeding.to_dict()
        out["total"] = total
        return jsonify(out)

    except (ValueError, TypeError) as e:
        logger.error(f"Invalid amount provided: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"error": {"message": "Invalid amount provided"}, "status": "error"}
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Error adding feeding: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/daily/feedings", methods=["GET"])
@jwt_required()
def get_daily_feedings():
    logger.info("Get daily feedings route accessed")
    try:
        # Get today in UTC
        today_utc = datetime.utcnow().date()
        feedings = Feeding.query.filter(Feeding.timestamp >= today_utc).all()
        logger.debug(f"Found {len(feedings)} feedings for today")
        return jsonify([feeding.to_dict() for feeding in feedings])
    except Exception as e:
        logger.error(f"Error getting daily feedings: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/daily/total", methods=["GET"])
@jwt_required()
def get_daily_total():
    logger.info("Get daily total route accessed")
    try:
        # Get today in UTC
        today_utc = datetime.utcnow().date()

        # Create UTC date range for query
        start_of_day_utc = datetime.combine(today_utc, datetime.min.time())
        end_of_day_utc = start_of_day_utc + timedelta(days=1)

        # Filter by timestamp being within today's range in UTC
        total = (
            db.session.query(func.sum(Feeding.amount))
            .filter(Feeding.timestamp >= start_of_day_utc)
            .filter(Feeding.timestamp < end_of_day_utc)
            .scalar()
            or 0.0
        )
        logger.debug(f"Daily total: {total}")

        return jsonify({"total": total})

    except Exception as e:
        logger.error(f"Error getting daily total: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["GET"])
@jwt_required()
def get_target():
    logger.info("Get target route accessed")
    try:
        target = get_or_create_daily_target()
        logger.debug(f"Current target: {target.target}")
        return jsonify({"target": target.target})

    except Exception as e:
        logger.error(f"Error getting target: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["POST"])
@jwt_required()
def update_target():
    try:
        data = request.get_json()
        target_value = float(data.get("target", 0))
        user_id = get_jwt_identity()

        if target_value <= 0:
            return (
                jsonify(
                    {"error": {"message": "Target must be positive"}, "status": "error"}
                ),
                400,
            )

        target = get_or_create_daily_target()
        target.target = target_value
        target.last_updated_by = user_id
        db.session.commit()

        return jsonify({"target": target.target})

    except (ValueError, TypeError):
        return (
            jsonify(
                {"error": {"message": "Invalid target provided"}, "status": "error"}
            ),
            400,
        )
    except Exception as e:
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    try:
        # Get all feedings ordered by timestamp
        feedings = Feeding.query.order_by(Feeding.timestamp.desc()).all()

        # Get all targets
        targets = {t.date: t.target for t in DailyTarget.query.all()}

        # Group feedings by date and calculate totals
        history = {}
        for feeding in feedings:
            # Extract date component from timestamp
            feeding_date = feeding.timestamp.date()

            if feeding_date not in history:
                history[feeding_date] = {
                    "date": feeding_date.isoformat(),
                    "amountFed": 0.0,
                    "target": targets.get(feeding_date, 3.0),
                    "feedings": [],
                }
            history[feeding_date]["amountFed"] += feeding.amount
            history[feeding_date]["feedings"].append(feeding.to_dict())

        # Convert to list and sort by date descending
        history_list = sorted(history.values(), key=lambda x: x["date"], reverse=True)

        return jsonify(history_list)

    except Exception as e:
        print(e)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/auth/apple/signin", methods=["POST"])
def signin():
    """Handle Sign in with Apple authentication"""
    logger.info("Apple signin route accessed")
    credentials = request.get_json()

    if not credentials or not credentials.get("identityToken"):
        logger.error("No identity token provided in Apple signin request")
        return jsonify({"error": {"message": "No identity token provided"}}), 400

    try:
        user = apple_signin(credentials)
        logger.debug(f"Successfully authenticated user: {user.id}")

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
        )
        logger.info(f"Successfully created tokens for user: {user.id}")
        return jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    except ValueError as e:
        logger.error(f"Apple signin error: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}}), 400
    except Exception as e:
        logger.error(f"Unexpected error during Apple signin: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": "Internal server error"}}), 500
