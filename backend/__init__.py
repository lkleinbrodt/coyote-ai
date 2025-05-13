import os
from logging import ERROR
from logging.handlers import SMTPHandler

from flask import Blueprint, Flask, request, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, jwt, migrate
from flask_session import Session

from .autodraft.models import *
from .autodraft.routes import autodraft_bp
from .email.routes import email_bp
from .explain.routes import explain_bp
from .lifter.routes import lifter
from .models import *
from .poeltl.routes import poeltl
from .PoppyTracker import poppy_bp
from .routes import auth_bp, base_bp, billing_bp
from .speech.routes import speech_bp


def create_app(config_class: Config):

    app = Flask(
        __name__,
        # static_folder=config_class.ROOT_DIR / "dist",
        # static_url_path="",
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

    # @app.route("/", defaults={"path": ""})
    # @app.route("/<string:path>")
    # @app.route("/<path:path>")
    # def index(path):
    #     return send_from_directory(app.static_folder, "index.html")

    api_bp = Blueprint("api", __name__)

    api_bp.register_blueprint(poeltl)
    api_bp.register_blueprint(lifter)
    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(billing_bp)
    api_bp.register_blueprint(autodraft_bp)
    api_bp.register_blueprint(speech_bp)
    api_bp.register_blueprint(poppy_bp, url_prefix="/poppy")  # Add PoppyTracker routes
    api_bp.register_blueprint(explain_bp)  # Add explain routes
    api_bp.register_blueprint(email_bp)  # Add email routes
    app.register_blueprint(base_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

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
