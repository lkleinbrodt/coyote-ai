from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from flask import request
from backend.config import Config
from flask_cors import CORS
from flask_session import Session
from backend.extensions import jwt, db, migrate
from flask import Blueprint
from flask import send_from_directory
from .twenty_questions.routes import twenty_questions
from .lifter.routes import lifter
from .routes import auth_bp
from .autodraft.routes import autodraft_bp
from .models import *
import os


def create_app(config_class: Config):

    app = Flask(
        __name__,
        static_folder=config_class.ROOT_DIR / "dist",
        static_url_path="",
    )

    app.config.from_object(config_class)

    CORS(
        app,
        supports_credentials=True,  # Allow credentials
        resources={
            r"/api/autodraft/*": {"origins": "http://localhost:5173"}
        },  # Specify allowed origin
        # allow_headers=["Authorization", "Content-Type"],
        # methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow necessary methods
    )

    jwt.init_app(app)
    Session(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/", defaults={"path": ""})
    @app.route("/<string:path>")
    @app.route("/<path:path>")
    def index(path):
        return send_from_directory(app.static_folder, "index.html")

    api_bp = Blueprint("api", __name__)

    api_bp.register_blueprint(twenty_questions)
    api_bp.register_blueprint(lifter)
    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(autodraft_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    if not app.debug:
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr=app.config["MAIL_USERNAME"],
            toaddrs=app.config["ADMIN_EMAILS"],
            subject="Coyote-AI Application Error",
            credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
            secure=(),
        )
        mail_handler.setLevel(ERROR)
        app.logger.addHandler(mail_handler)

    return app
