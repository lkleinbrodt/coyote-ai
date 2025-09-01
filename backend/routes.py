from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text
from backend.extensions import create_logger, db
from backend.autodraft.routes import autodraft_bp
from backend.explain.routes import explain_bp
from backend.lifter.routes import lifter
from backend.models import *
from backend.poeltl.routes import poeltl
from backend.PoppyTracker import poppy_bp
from backend.auth.routes import auth_bp
from backend.billing.routes import billing_bp
from backend.sidequest.models import *
from backend.sidequest.routes import sidequest_bp
from backend.speech.routes import speech_bp


logger = create_logger(__name__, level="DEBUG")

base_bp = Blueprint("base", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(poeltl)
api_bp.register_blueprint(lifter)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(billing_bp)
api_bp.register_blueprint(autodraft_bp)
api_bp.register_blueprint(speech_bp)
api_bp.register_blueprint(poppy_bp, url_prefix="/poppy")
api_bp.register_blueprint(explain_bp)
api_bp.register_blueprint(sidequest_bp)


@base_bp.route("/")
def index():
    """API root endpoint - returns API status and basic information"""
    logger.info("Root endpoint accessed")
    return (
        jsonify(
            {
                "status": "healthy",
            }
        ),
        200,
    )


@base_bp.route("/ping-db", methods=["GET"])
def ping_db():
    """Lightweight endpoint to keep the database connection active"""
    # Verify API key
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != current_app.config["PING_DB_API_KEY"]:
        logger.warning("Invalid or missing API key for ping-db endpoint")
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Perform a lightweight database operation
        db.session.execute(text("SELECT 1"))
        logger.debug("Database ping successful")
        return (
            jsonify({"status": "success", "message": "Database connection active"}),
            200,
        )
    except Exception as e:
        logger.error(f"Database ping failed: {str(e)}")
        return jsonify({"error": "Database connection failed"}), 500
