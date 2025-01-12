from flask import Blueprint, jsonify, request
from backend.autodraft.utils import delete_index
from backend.autodraft.models import Project
from flask_jwt_extended import jwt_required, current_user
from backend.extensions import db, create_logger

projects_bp = Blueprint("projects", __name__)
logger = create_logger(__name__, level="DEBUG")


@projects_bp.route("/new-project", methods=["POST"])
@jwt_required()
def new_project():
    project_name = request.get_json().get("name")
    if not project_name:
        return jsonify({"error": "No project name provided"}), 400

    # check if project already exists
    existing_project = Project.query.filter_by(name=project_name).first()
    if existing_project:
        return jsonify({"error": f"Project {project_name} already exists"}), 409

    new_project = Project(
        name=project_name, creator_id=current_user.id, users=[current_user]
    )
    logger.debug(f"New project: {new_project}")
    db.session.add(new_project)
    db.session.commit()

    return jsonify(new_project.to_dict()), 200


@projects_bp.route("/create-project", methods=["POST"])
@jwt_required()
def create_project():

    project_name = request.get_json().get("project_name")
    if not project_name:
        return jsonify({"error": "No project_name provided"})

    # check if project already exists
    existing_project = Project.query.filter_by(name=project_name).first()
    if existing_project:
        return jsonify({"error": f"Project {project_name} already exists"}), 409

    project = Project(name=project_name, users=[current_user])
    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 200


@projects_bp.route("/delete-project", methods=["POST"])
def delete_project():
    # TODO: can the user delete the project?
    project_id = request.get_json().get("project_id")
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)

    delete_index(project_id)

    db.session.commit()

    return jsonify({"success": f"Deleted project {project_id}"}), 200


@projects_bp.route("/projects", methods=["GET"])
@jwt_required()
def get_projects():

    projects = current_user.projects

    return jsonify([project.to_dict() for project in projects]), 200
