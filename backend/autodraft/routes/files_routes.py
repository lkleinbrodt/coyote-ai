from flask import Blueprint, jsonify, request
import tempfile
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.autodraft.models import File, Project, Document
from llama_index.core import SimpleDirectoryReader
from flask_jwt_extended import jwt_required, current_user

files_bp = Blueprint("files", __name__)


@files_bp.route("/upload-file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    overwrite = request.form.get("overwrite", "false").lower() == "true"
    project_id = request.form.get("project_id")

    if not project_id:
        return jsonify({"error": "No project_id provided"})

    temp_dir = tempfile.mkdtemp()
    file_paths = []
    uploaded_files = []

    filename = secure_filename(file.filename)
    file_path = os.path.join(temp_dir, filename)

    existing_file = File.query.filter_by(name=filename, project_id=project_id).first()
    if existing_file:
        if not overwrite:
            return (
                jsonify(
                    {
                        "error": f"File {filename} already exists in project {project_id}. Set overwrite=True to overwrite."
                    }
                ),
                409,
            )
        else:
            db.session.delete(existing_file)

    new_file = File(name=filename, project_id=project_id)
    db.session.add(new_file)
    file.save(file_path)
    file_paths.append(file_path)
    uploaded_files.append(new_file)

    # holding off on committing until we have all the documents
    # db.session.commit()

    reader = SimpleDirectoryReader(input_files=file_paths)

    all_docs = []
    for docs in reader.iter_data():
        for doc in docs:
            file_name = doc.metadata.get("file_name")
            file = File.query.filter_by(name=file_name, project_id=project_id).first()
            creation_date_str = doc.metadata.get("creation_date")
            last_modified_date_str = doc.metadata.get("last_modified_date")

            creation_date = (
                datetime.strptime(creation_date_str, "%Y-%m-%d")
                if creation_date_str
                else None
            )
            last_modified_date = (
                datetime.strptime(last_modified_date_str, "%Y-%m-%d")
                if last_modified_date_str
                else None
            )

            document = Document(
                llama_id=doc.doc_id,
                created_at=creation_date,
                last_modified=last_modified_date,
                llama_metadata=doc.metadata,
                content=doc.text,
                file_id=file.id,
                page_label=doc.metadata.get("page_label"),
            )
            db.session.add(document)
            all_docs.append(doc)

    db.session.commit()

    for path in file_paths:
        os.remove(path)
    os.rmdir(temp_dir)

    file_infos = [file.to_dict() for file in uploaded_files]
    file = file_infos[0]
    return jsonify(file), 200


@files_bp.route("/files", methods=["GET"])
@jwt_required()
def get_files():
    project_id = request.args.get("project_id")
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    files = File.query.filter_by(project_id=project_id).all()

    return jsonify([file.to_dict() for file in files]), 200


@files_bp.route("/delete-file", methods=["POST"])
@jwt_required()
def delete_file():

    file_id = request.get_json().get("file_id")
    if not file_id:
        return jsonify({"error": "No file_id provided"}), 400

    file = File.query.get(file_id)
    if not file:
        return jsonify({"error": "File not found"}), 404

    # ensure the user has access to the project
    project = Project.query.get(file.project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    if current_user not in project.users:
        return jsonify({"error": "User does not have access to project"}), 403

    db.session.delete(file)

    # now update the index
    # TODO: update the index
    # this takes a long time, so we'll do it in the background

    return jsonify({"success": "File deleted"}), 200
