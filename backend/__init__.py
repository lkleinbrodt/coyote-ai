from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from flask import request
from backend.config import Config, ROOT_DIR
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


def create_app():

    app = Flask(
        __name__,
        static_folder=ROOT_DIR / "dist",
        static_url_path="",
    )

    app.config.from_object(Config)

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
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
