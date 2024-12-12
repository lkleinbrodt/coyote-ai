from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from flask import request
from backend.config import Config
from flask_cors import CORS
from flask_session import Session
from backend.extensions import jwt
from flask import render_template
from flask import Blueprint
from flask import send_from_directory
from .twenty_questions.routes import twenty_questions
from .lifter.routes import lifter
from .routes import auth_bp
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
    )
    jwt.init_app(app)
    Session(app)

    # return send_from_directory(app.static_folder, "index.html")

    @app.route("/", defaults={"path": ""})
    @app.route("/<string:path>")
    @app.route("/<path:path>")
    def index(path):
        return send_from_directory(app.static_folder, "index.html")

    api_bp = Blueprint("api", __name__)

    api_bp.register_blueprint(twenty_questions)
    api_bp.register_blueprint(lifter)
    api_bp.register_blueprint(auth_bp)
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
