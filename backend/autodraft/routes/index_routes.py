from flask import Blueprint, jsonify, request
from backend.autodraft.models import Project
from backend.autodraft.utils import update_index
from llama_index.core import Document as LlamaDocument
from flask_jwt_extended import jwt_required, current_user
from backend.autodraft.src.IndexBuilder import IndexBuilder
from backend.extensions import create_logger
from backend.src.s3 import create_s3_fs
from backend.autodraft.utils import check_index_available, delete_index
from backend.autodraft.extensions import index_cache

index_bp = Blueprint("index", __name__)
logger = create_logger(__name__, level="DEBUG")


@index_bp.route("/create-index", methods=["POST"])
def create_index():
    "user selects a project to index"
    project_id = request.get_json().get("project_id")
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    documents = []
    for file in project.files:
        documents.extend(file.documents)

    if not documents:
        logger.error(f"No documents found for project {project.id}")
        return jsonify({"error": "No documents found for project"}), 404

    llama_documents = [
        LlamaDocument(text=doc.content, metadata=doc.llama_metadata, doc_id=str(doc.id))
        for doc in documents
    ]

    try:
        builder = IndexBuilder(
            documents=llama_documents,
            project_id=project.id,
        )
    except FileExistsError:
        return jsonify({"error": "Index already exists."}), 409

    builder.build_index()

    return jsonify({"success": f"Index created for project {project.id}"}), 200


@index_bp.route("/load-index", methods=["GET"])
def load_index_route():
    project_id = request.args.get("project_id")
    logger.debug(f"Loading index for project {project_id}")

    try:
        index = index_cache.get_index(project_id)
    except FileNotFoundError:
        return jsonify({"error": "Index not found"}), 404

    return jsonify({"success": "Index loaded"}), 200


@index_bp.route("/index-available", methods=["GET"])
@jwt_required()
def index_available():
    project_id = request.args.get("project_id")
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    s3_fs = create_s3_fs()
    exists = check_index_available(project_id, s3_fs)

    return jsonify({"exists": exists}), 200


@index_bp.route("/delete-index", methods=["POST"])
@jwt_required()
def delete_index():
    project_id = request.get_json().get("project_id")
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    # validate the user has access
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    if current_user not in project.users:
        return jsonify({"error": "User does not have access to project"}), 403

    s3_fs = create_s3_fs()
    if check_index_available(project_id, s3_fs):
        delete_index(project_id, s3_fs)

    return jsonify({"success": "Index deleted"}), 200


@index_bp.route("/update-index", methods=["POST"])
@jwt_required()
def update_index_route():
    project_id = request.get_json().get("project_id")
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    project = Project.query.get(project_id)
    if not project:
        logger.error(f"Project not found for project_id {project_id}")
        return jsonify({"error": "Project not found"}), 404
    if current_user not in project.users:
        logger.error(
            f"User {current_user.id} does not have access to project {project_id}"
        )
        return jsonify({"error": "User does not have access to project"}), 403

    try:
        index = update_index(project_id)
    except FileNotFoundError:
        return jsonify({"error": "Index not found"}), 404

    return jsonify({"success": "Index updated"}), 200
