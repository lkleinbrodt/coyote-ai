from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from backend.config import Config
from flask_cors import CORS
from flask_session import Session
from backend.extensions import db, jwt, migrate

app = Flask(__name__, static_folder="./dist", static_url_path="")

app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)

CORS(
    app,
)
jwt.init_app(app)
Session(app)
from flask import Blueprint
from flask import send_from_directory
import os


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    try:
        return send_from_directory(app.static_folder, path)
    except FileNotFoundError:
        return send_from_directory(app.static_folder, "index.html")


from .twenty_questions.routes import twenty_questions
from .routes import auth_bp

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(twenty_questions)
app.register_blueprint(auth_bp, url_prefix="/")
app.register_blueprint(api_bp, url_prefix="/api")
