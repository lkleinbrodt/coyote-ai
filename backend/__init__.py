from logging.handlers import SMTPHandler
from logging import ERROR
from flask import Flask
from backend.config import Config
from flask_cors import CORS

from backend.extensions import db, jwt, migrate

app = Flask(__name__, static_folder="static")

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


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


from .twenty_questions.routes import twenty_questions

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(twenty_questions)

app.register_blueprint(api_bp, url_prefix="/api")
