from flask import Blueprint
from .index_routes import index_bp
from .projects_routes import projects_bp
from .reports_routes import reports_bp
from .files_routes import files_bp
from .entries_routes import entries_bp
from flask import request, current_app
import jwt

autodraft_bp = Blueprint("autodraft", __name__, url_prefix="/autodraft")

autodraft_bp.register_blueprint(index_bp)
autodraft_bp.register_blueprint(projects_bp)
autodraft_bp.register_blueprint(reports_bp)
autodraft_bp.register_blueprint(files_bp)
autodraft_bp.register_blueprint(entries_bp)
