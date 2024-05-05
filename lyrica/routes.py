from flask import jsonify, Blueprint
from server.config import create_logger
from lyrica.src import *


logger = create_logger(__name__, level="DEBUG")

lyrica = Blueprint("lyrica", __name__, url_prefix="/lyrica")


@lyrica.route("/")
def home():
    logger.debug("Home route accessed")
    return jsonify({"message": "Hello from Lyrica Flask!"})
