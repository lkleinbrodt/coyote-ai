from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from backend.config import Config
from flask_cors import CORS

from backend.extensions import db, jwt, migrate

app = Flask(__name__, static_folder="../dist", static_url_path="")

app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)

CORS(
    app,
)
jwt.init_app(app)

from flask import Blueprint
from flask import send_from_directory
import os


@app.route("/")
def index():
    return send_from_directory("../dist", "index.html")


from .twenty_questions.routes import twenty_questions
from .routes import server_bp

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(twenty_questions)
app.register_blueprint(server_bp, url_prefix="/")
app.register_blueprint(api_bp, url_prefix="/api")
