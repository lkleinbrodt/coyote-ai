from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from llama_index.core import Document as LlamaDocument

from backend.autodraft.extensions import index_cache
from backend.autodraft.models import Project
from backend.autodraft.src.IndexBuilder import IndexBuilder
from backend.autodraft.utils import check_index_available, delete_index, update_index
from backend.extensions import create_logger
from backend.src.s3 import create_s3_fs

index_bp = Blueprint("index", __name__)
logger = create_logger(__name__, level="DEBUG")


@index_bp.route("/create-index", methods=["POST"])
def create_index():
    """User selects a project to index"""
    logger.info("Create index route accessed")
    try:
        project_id = request.get_json().get("project_id")
        logger.debug(f"Creating index for project {project_id}")

        project = Project.query.get(project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return jsonify({"error": "Project not found"}), 404

        documents = []
        for file in project.files:
            documents.extend(file.documents)
            logger.debug(f"Added {len(file.documents)} documents from file {file.id}")

        if not documents:
            logger.error(f"No documents found for project {project.id}")
            return jsonify({"error": "No documents found for project"}), 404

        llama_documents = [
            LlamaDocument(
                text=doc.content, metadata=doc.llama_metadata, doc_id=str(doc.id)
            )
            for doc in documents
        ]
        logger.debug(f"Created {len(llama_documents)} Llama documents")

        try:
            builder = IndexBuilder(
                documents=llama_documents,
                project_id=project.id,
            )
            logger.debug("Successfully created IndexBuilder")
        except FileExistsError:
            logger.warning(f"Index already exists for project {project.id}")
            return jsonify({"error": "Index already exists."}), 409

        builder.build_index()
        logger.info(f"Successfully built index for project {project.id}")
        return jsonify({"success": f"Index created for project {project.id}"}), 200

    except Exception as e:
        logger.error(f"Error creating index: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to create index: {str(e)}"}), 500


@index_bp.route("/load-index", methods=["GET"])
def load_index_route():
    logger.info("Load index route accessed")
    project_id = request.args.get("project_id")
    logger.debug(f"Loading index for project {project_id}")

    try:
        index = index_cache.get_index(project_id)
        logger.debug(f"Successfully loaded index for project {project_id}")
        return jsonify({"success": "Index loaded"}), 200
    except FileNotFoundError:
        logger.error(f"Index not found for project {project_id}")
        return jsonify({"error": "Index not found"}), 404
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to load index: {str(e)}"}), 500


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
    logger.info("Update index route accessed")
    try:
        project_id = request.get_json().get("project_id")
        if not project_id:
            logger.error("No project_id provided")
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
            logger.info(f"Successfully updated index for project {project_id}")
            return jsonify({"success": "Index updated"}), 200
        except FileNotFoundError:
            logger.error(f"Index not found for project {project_id}")
            return jsonify({"error": "Index not found"}), 404
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to update index: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error in update index route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
