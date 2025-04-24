import json
from datetime import date, datetime

import pytz
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import func

from backend.extensions import db
from backend.openai_utils import extract_number_from_text
from backend.src.auth import apple_signin

from .models import DailyTarget, Feeding, pacific

poppy_bp = Blueprint("poppy", __name__)


def get_or_create_daily_target():
    """Get today's target record or create a new one if none exists"""
    today = datetime.now(pacific).date()
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
    try:
        data = request.get_json()
        amount = float(data.get("amount", 0))
        user_id = get_jwt_identity()

        if amount == 0:
            return jsonify({"error": "Amount cannot be zero", "status": "error"}), 400

        # No need to set date, it will default to UTC now
        feeding = Feeding(amount=amount, last_updated_by=user_id)
        db.session.add(feeding)
        db.session.commit()
        new_total = get_daily_total()
        out = feeding.to_dict()
        out["total"] = new_total
        return jsonify(out)

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount provided", "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/daily/total", methods=["GET"])
@jwt_required()
def get_daily_total():
    try:
        # Get today in Pacific timezone
        pacific_today = datetime.now(pacific).date()

        # Convert to UTC for database query
        # Start of day in Pacific converted to UTC
        start_of_day_pacific = datetime.combine(pacific_today, datetime.min.time())
        start_of_day_pacific = pacific.localize(start_of_day_pacific)
        start_of_day_utc = start_of_day_pacific.astimezone(pytz.UTC)

        # End of day in Pacific converted to UTC
        end_of_day_pacific = datetime.combine(pacific_today, datetime.max.time())
        end_of_day_pacific = pacific.localize(end_of_day_pacific)
        end_of_day_utc = end_of_day_pacific.astimezone(pytz.UTC)

        # Remove timezone info since SQLAlchemy might store naive datetimes
        start_of_day_utc = start_of_day_utc.replace(tzinfo=None)
        end_of_day_utc = end_of_day_utc.replace(tzinfo=None)

        # Calculate total from all feedings today (in Pacific time)
        total = (
            db.session.query(func.sum(Feeding.amount))
            .filter(Feeding.date >= start_of_day_utc, Feeding.date <= end_of_day_utc)
            .scalar()
            or 0.0
        )

        return jsonify({"total": total})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["GET"])
@jwt_required()
def get_target():
    try:
        target = get_or_create_daily_target()
        return jsonify({"target": target.target})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["POST"])
@jwt_required()
def update_target():
    try:
        data = request.get_json()
        target_value = float(data.get("target", 0))
        user_id = get_jwt_identity()

        if target_value <= 0:
            return jsonify({"error": "Target must be positive", "status": "error"}), 400

        target = get_or_create_daily_target()
        target.target = target_value
        target.last_updated_by = user_id
        db.session.commit()

        return jsonify({"target": target.target})

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid target provided", "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    try:
        # Get all feedings ordered by date
        feedings = Feeding.query.order_by(Feeding.date.desc()).all()

        # Get all targets
        targets = {t.date: t.target for t in DailyTarget.query.all()}

        # Group feedings by date and calculate totals
        history = {}
        for feeding in feedings:
            # Convert UTC time to Pacific date for grouping
            pacific_datetime = pytz.utc.localize(feeding.date).astimezone(pacific)
            feeding_date = pacific_datetime.date()

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
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/auth/apple/signin", methods=["POST"])
def signin():
    """Handle Sign in with Apple authentication"""
    credentials = request.get_json()

    if not credentials or not credentials.get("identityToken"):
        return jsonify({"error": "No identity token provided"}), 400

    try:
        user = apple_signin(credentials)

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
        return jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@poppy_bp.route("/feeding/adjust", methods=["POST"])
@jwt_required(optional=True)
def adjust_feeding():
    try:
        data = request.get_json()
        amount_input = data.get("amount", 0)
        user_id = get_jwt_identity()

        if not user_id:
            user = data.get("user")
            if user == "secret poppy access code":
                user_id = "poppy"
            else:
                return jsonify({"error": "Invalid user", "status": "error"}), 400

        # Try to convert input to float first
        try:
            amount = float(amount_input)
        except (ValueError, TypeError):
            # If conversion fails, try to extract number from text
            amount = extract_number_from_text(str(amount_input), context="cups of food")

        if amount == 0:
            return jsonify({"error": "Amount cannot be zero", "status": "error"}), 400

        # No need to set date, it will default to UTC now
        feeding = Feeding(amount=amount, last_updated_by=user_id)
        db.session.add(feeding)
        db.session.commit()

        return jsonify(feeding.to_dict())

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500
