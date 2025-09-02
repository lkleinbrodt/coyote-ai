from flask import Blueprint

sidequest_bp = Blueprint("sidequest", __name__, url_prefix="/sidequest")

from . import user, quests, history
