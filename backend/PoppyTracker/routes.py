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

from backend.extensions import db
from backend.openai_utils import extract_number_from_text
from backend.src.auth import apple_signin

from .models import DailyFeeding, pacific

poppy_bp = Blueprint("poppy", __name__)


def get_or_create_daily_feeding():
    """Get today's feeding record or create a new one if none exists"""
    today = datetime.now(pacific).date()
    feeding = DailyFeeding.query.filter_by(date=today).first()
    if not feeding:
        # Get the most recent target to carry forward
        last_feeding = DailyFeeding.query.order_by(DailyFeeding.date.desc()).first()
        target = last_feeding.daily_target if last_feeding else 3.0
        feeding = DailyFeeding(date=today, daily_target=target)
        db.session.add(feeding)
        db.session.commit()
    return feeding


@poppy_bp.route("/daily/total", methods=["POST"])
@jwt_required()
def set_total():
    try:
        data = request.get_json()
        amount = float(data.get("amount", 0))
        user_id = get_jwt_identity()

        if amount < 0:
            return (
                jsonify({"error": "Amount cannot be negative", "status": "error"}),
                400,
            )

        feeding = get_or_create_daily_feeding()
        feeding.total_amount = amount
        feeding.last_updated_by = user_id
        db.session.commit()

        return jsonify({"total": feeding.total_amount})

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount provided", "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/daily/total", methods=["GET"])
@jwt_required()
def get_daily_total():
    try:
        today = datetime.now(pacific).date()
        feeding = DailyFeeding.query.filter_by(date=today).first()
        total = feeding.total_amount if feeding else 0.0

        return jsonify({"total": total})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["GET"])
@jwt_required()
def get_target():
    try:
        feeding = get_or_create_daily_feeding()
        return jsonify({"target": feeding.daily_target})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/settings/target", methods=["POST"])
@jwt_required()
def update_target():
    try:
        data = request.get_json()
        target = float(data.get("target", 0))

        if target <= 0:
            return jsonify({"error": "Target must be positive", "status": "error"}), 400

        feeding = get_or_create_daily_feeding()
        feeding.daily_target = target
        db.session.commit()

        return jsonify({"target": feeding.daily_target})

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid target provided", "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@poppy_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    try:
        feedings = DailyFeeding.query.order_by(DailyFeeding.date.desc()).all()

        history = [
            {
                "date": feeding.date.isoformat(),
                "amountFed": feeding.total_amount,
                "target": feeding.daily_target,
            }
            for feeding in feedings
        ]
        print(history)
        return jsonify(history)

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


@poppy_bp.route("/daily/total/adjust", methods=["POST"])
@jwt_required(optional=True)
def adjust_total():
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

        feeding = get_or_create_daily_feeding()
        new_total = feeding.total_amount + amount

        if new_total < 0:
            return (
                jsonify(
                    {"error": "Resulting total cannot be negative", "status": "error"}
                ),
                400,
            )

        feeding.total_amount = new_total
        feeding.last_updated_by = user_id
        db.session.commit()

        return jsonify({"total": feeding.total_amount})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500
