import os
from logging import ERROR
from logging.handlers import SMTPHandler

from flask import Blueprint, Flask, request, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, jwt, migrate
from flask_session import Session

from backend.routes import api_bp, base_bp


def create_app(config_class: Config):

    app = Flask(
        __name__,
    )

    app.config.from_object(config_class)

    CORS(
        app,
        supports_credentials=True,  # Allow credentials
        # resources={
        #     r"/api/autodraft/*": {"origins": "http://localhost:5173"},
        #     r"/api/poeltl/*": {"origins": "http://localhost:5173"},
        # },
        # allow_headers=["Authorization", "Content-Type"],
        # methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow necessary methods
    )

    jwt.init_app(app)
    Session(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # JWT Error Handlers for consistent responses
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        """Handle missing or invalid JWT tokens"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "Authentication required",
                        "code": "UNAUTHORIZED",
                    },
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        """Handle invalid JWT tokens"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "Invalid authentication token",
                        "code": "INVALID_TOKEN",
                    },
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT tokens"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "Authentication token has expired",
                        "code": "TOKEN_EXPIRED",
                    },
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked JWT tokens"""
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "message": "Authentication token has been revoked",
                        "code": "TOKEN_REVOKED",
                    },
                }
            ),
            401,
        )

    # @app.route("/", defaults={"path": ""})
    # @app.route("/<string:path>")
    # @app.route("/<path:path>")
    # def index(path):
    #     return send_from_directory(app.static_folder, "index.html")

    app.register_blueprint(base_bp)
    app.register_blueprint(api_bp)

    if not app.debug:
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr=app.config["MAIL_USERNAME"],
            toaddrs=app.config["ADMIN_EMAILS"],
            subject="LK API Application Error",
            credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
            secure=(),
        )
        mail_handler.setLevel(ERROR)
        app.logger.addHandler(mail_handler)

    return app
