from flask import Blueprint, jsonify, request
from backend.autodraft.utils import delete_index, check_index_available
from backend.autodraft.models import Project
from flask_jwt_extended import jwt_required, current_user
from backend.extensions import db, create_logger
from backend.src.s3 import create_s3_fs

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


@projects_bp.route("/update-project", methods=["POST"])
@jwt_required()
def update_project():
    data = request.get_json()
    project_id = data.get("project_id")
    updates = {k: v for k, v in data.items() if k != "project_id"}

    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Verify user has access to this project
    if project not in current_user.projects:
        return jsonify({"error": "Unauthorized"}), 403

    # Apply updates
    for key, value in updates.items():
        if hasattr(project, key):
            setattr(project, key, value)

    try:
        db.session.commit()
        return jsonify(project.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating project: {str(e)}")
        return jsonify({"error": "Failed to update project"}), 500


@projects_bp.route("/delete-project", methods=["POST"])
@jwt_required()
def delete_project():
    data = request.get_json()
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Verify user has access to this project
    if project not in current_user.projects:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Delete the project's index if it exists
        if project.index_id:
            # TODO: Add your index deletion logic here
            pass

        db.session.delete(project)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        return jsonify({"error": "Failed to delete project"}), 500


@projects_bp.route("/projects", methods=["GET"])
@jwt_required()
def get_projects():

    projects = current_user.projects

    # TODO: this is kinda dumb
    s3_fs = create_s3_fs()
    out = []
    for project in projects:
        x = project.to_dict()
        x["index_available"] = check_index_available(project.id, s3_fs)
        out.append(x)

    return jsonify(out), 200
