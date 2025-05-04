import json
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import func

from backend.extensions import create_logger, db
from backend.src.auth import apple_signin

from .models import DailyTarget, Feeding

logger = create_logger(__name__, level="DEBUG")
poppy_bp = Blueprint("poppy", __name__)

import pytz

PACIFIC = pytz.timezone("America/Los_Angeles")


def get_pacific_date(utc_timestamp=None):
    if utc_timestamp is None:
        utc_timestamp = datetime.now(pytz.utc)
    return utc_timestamp.astimezone(PACIFIC).date()


def get_or_create_daily_target():
    """Get today's target record or create a new one if none exists"""
    today_pacific = get_pacific_date()
    target = DailyTarget.query.filter_by(date=today_pacific).first()
    if not target:
        # Get the most recent target to carry forward
        last_target = DailyTarget.query.order_by(DailyTarget.date.desc()).first()
        target_value = last_target.target if last_target else 3.0
        target = DailyTarget(date=today_pacific, target=target_value)
        db.session.add(target)
        db.session.commit()
    return target


@poppy_bp.route("/feeding", methods=["POST"])
@jwt_required(optional=True)
def add_feeding():
    logger.info("Add feeding route accessed")
    try:
        data = request.get_json()
        amount = float(data.get("amount", 0))
        user_id = get_jwt_identity()
        if not user_id:
            user = data.get("user")
            if user != "secret poppy access code":
                return (
                    jsonify(
                        {"error": {"message": "Invalid access code"}, "status": "error"}
                    ),
                    400,
                )
            else:
                user_id = -1
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
        db.session.flush()
        db.session.commit()
        logger.debug(
            f"Successfully added feeding of amount {amount} for user {user_id}"
        )

        # Get the updated daily total for today in UTC
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Step 2: convert to Pacific
        now_pacific = now_utc.astimezone(PACIFIC)

        # Step 3: get start/end of that Pacific day
        pacific_date = now_pacific.date()
        start_of_day_pacific = PACIFIC.localize(
            datetime.combine(pacific_date, datetime.min.time())
        )
        end_of_day_pacific = start_of_day_pacific + timedelta(days=1)

        # Step 4: convert those back to UTC for querying
        start_of_day_utc = start_of_day_pacific.astimezone(pytz.utc)
        end_of_day_utc = end_of_day_pacific.astimezone(pytz.utc)

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
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        now_pacific = now_utc.astimezone(PACIFIC)
        pacific_date = now_pacific.date()

        start_of_day_pacific = PACIFIC.localize(
            datetime.combine(pacific_date, datetime.min.time())
        )
        end_of_day_pacific = start_of_day_pacific + timedelta(days=1)

        start_of_day_utc = start_of_day_pacific.astimezone(pytz.utc)
        end_of_day_utc = end_of_day_pacific.astimezone(pytz.utc)

        feedings = Feeding.query.filter(
            Feeding.timestamp >= start_of_day_utc, Feeding.timestamp < end_of_day_utc
        ).all()
        logger.debug(f"Found {len(feedings)} feedings for today")
        return jsonify([feeding.to_dict() for feeding in feedings])
    except Exception as e:
        logger.error(f"Error getting daily feedings: {str(e)}", exc_info=True)
        return jsonify({"error": {"message": str(e)}, "status": "error"}), 500


@poppy_bp.route("/daily/total", methods=["GET"])
@jwt_required(optional=True)
def get_daily_total():
    logger.info("Get daily total route accessed")
    try:
        user_id = get_jwt_identity()
        if not user_id:
            user = request.get_json().get("user")
        if user != "secret poppy access code":
            return (
                jsonify(
                    {"error": {"message": "Invalid access code"}, "status": "error"}
                ),
                400,
            )
        else:
            user_id = -1
        # Get today in UTC
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Step 2: convert to Pacific
        now_pacific = now_utc.astimezone(PACIFIC)

        # Step 3: get start/end of that Pacific day
        pacific_date = now_pacific.date()
        start_of_day_pacific = PACIFIC.localize(
            datetime.combine(pacific_date, datetime.min.time())
        )
        end_of_day_pacific = start_of_day_pacific + timedelta(days=1)

        # Step 4: convert those back to UTC for querying
        start_of_day_utc = start_of_day_pacific.astimezone(pytz.utc)
        end_of_day_utc = end_of_day_pacific.astimezone(pytz.utc)

        # Filter by timestamp being within today's range in UTC
        total = (
            db.session.query(func.sum(Feeding.amount))
            .filter(Feeding.timestamp >= start_of_day_utc)
            .filter(Feeding.timestamp < end_of_day_utc)
            .scalar()
            or 0.0
        )
        logger.debug(f"Daily total: {total}")

        # get the target for today
        target = get_or_create_daily_target()

        return jsonify({"total": total, "target": target.target})

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
        # Get feedings from last 7 days ordered by timestamp
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        feedings = (
            Feeding.query.filter(Feeding.timestamp >= seven_days_ago)
            .order_by(Feeding.timestamp.desc())
            .all()
        )

        # Get all targets
        targets = {t.date: t.target for t in DailyTarget.query.all()}

        # Group feedings by date and calculate totals
        history = {}
        for feeding in feedings:
            # Extract date component from timestamp
            localized_ts = feeding.timestamp.replace(tzinfo=pytz.utc).astimezone(
                pytz.timezone("America/Los_Angeles")
            )
            feeding_date = localized_ts.date()
            # this date might be wrong because it's not converting to pacific time, so it's 7 hours shifted

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
