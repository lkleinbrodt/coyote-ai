from llama_index.core.schema import NodeWithScore
from typing import List
from flask import Blueprint, jsonify, request
from backend.autodraft.models import (
    Report,
    Prompt,
    Response,
    Document,
    SourceDoc,
)
from backend.extensions import db, create_logger
from backend.autodraft.extensions import index_cache
from backend.autodraft.src.Writer import Writer
from flask_jwt_extended import (
    jwt_required,
)
from backend.autodraft.utils import load_index

logger = create_logger(__name__)
entries_bp = Blueprint("entries", __name__)


@entries_bp.route("/add-prompt", methods=["POST"])
def add_prompt():
    prompt = request.get_json().get("prompt")
    report_id = request.get_json().get("report_id")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    if not report_id:
        return jsonify({"error": "No report provided"}), 400

    report = Report.query.get(report_id)

    if not report:
        return jsonify({"error": "Report not found"}), 404

    new_prompt = Prompt(text=prompt, report_id=report_id, position=len(report.prompts))

    db.session.add(new_prompt)
    db.session.commit()

    return jsonify(new_prompt.to_dict()), 200


@entries_bp.route("/update-prompt", methods=["POST"])
def update_prompt():
    prompt_id = request.get_json().get("prompt_id")
    text = request.get_json().get("text")

    if not prompt_id:
        logger.error("No prompt_id provided")
        return jsonify({"error": "No prompt_id provided"}), 400

    prompt = Prompt.query.get(prompt_id)

    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    prompt.text = text
    db.session.commit()

    return jsonify(prompt.to_dict()), 200


@entries_bp.route("/delete-prompt", methods=["POST"])
def delete_prompt():
    prompt_id = request.get_json().get("prompt_id")

    if not prompt_id:
        return jsonify({"error": "No prompt_id provided"}), 400

    prompt = Prompt.query.get(prompt_id)

    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    db.session.delete(prompt)
    db.session.commit()

    return jsonify({"success": "Prompt deleted"}), 200


@entries_bp.route("/add-response", methods=["POST"])
def add_response():
    prompt_id = request.get_json().get("prompt_id")
    text = request.get_json().get("text")

    if not prompt_id:
        return jsonify({"error": "No prompt_id provided"}), 400

    prompt = Prompt.query.get(prompt_id)

    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    new_response = _add_response(prompt_id, text)

    return jsonify({"success": "Response added"}), 200


# TODO: should live elsewhere
def create_source_document(response_id, source_node: NodeWithScore):

    source_doc = SourceDoc(
        response_id=response_id,
        document_id=source_node.node.ref_doc_id,
        score=source_node.score,
    )
    return source_doc


def _add_response(prompt_id, text, source_nodes: List[NodeWithScore] = None):
    prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError(f"Prompt not found: {prompt_id}")

    new_response = Response(
        text=text,
        prompt_id=prompt_id,
        position=len(prompt.responses),
        selected=True,
    )

    db.session.add(new_response)
    db.session.flush()

    # add source docs
    if source_nodes:
        for source_node in source_nodes:
            # Get the document from the database using the llama_id
            document = Document.query.filter_by(
                llama_id=source_node.node.ref_doc_id
            ).first()
            if document:
                source_doc = SourceDoc(
                    response_id=new_response.id,
                    document_id=document.id,  # Use the integer ID from our database
                    score=source_node.score,
                )
                db.session.add(source_doc)

    # set all other responses to not selected
    for response in prompt.responses:
        response.selected = False

    db.session.commit()

    return new_response


@entries_bp.route("/update-response", methods=["POST"])
def update_response():
    response_id = request.get_json().get("response_id")
    text = request.get_json().get("text")
    selected = request.get_json().get("selected", True)

    if not response_id:
        logger.error("No response_id provided")
        return jsonify({"error": "No response_id provided"}), 400

    response = Response.query.get(response_id)

    if not response:
        logger.error(f"Response not found: {response_id}")
        return jsonify({"error": "Response not found"}), 404

    response = _update_response(
        response_id=response_id,
        text=text,
        source_nodes=None,
        selected=selected,
    )
    return jsonify(response.to_dict()), 200


def _update_response(
    response_id,
    text,
    source_nodes: List[NodeWithScore] = None,
    selected=True,
):
    response: Response = Response.query.get(response_id)
    if not response:
        raise ValueError(f"Response not found: {response_id}")
    prompt_id = response.prompt_id
    prompt: Prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError(f"Prompt not found: {prompt_id}")
    response.text = text
    response.selected = selected

    # if the user has changed the source nodes, remove all old source docs
    if source_nodes:
        SourceDoc.query.filter_by(response_id=response_id).delete()
        # add new source docs
        for source_node in source_nodes:
            # Get the document from the database using the llama_id
            document = Document.query.filter_by(
                llama_id=source_node.node.ref_doc_id
            ).first()
            if document:
                source_doc = SourceDoc(
                    response_id=response_id,
                    document_id=document.id,  # Use the integer ID from our database
                    score=source_node.score,
                )
                db.session.add(source_doc)

    # if this response is selected, set all other responses to not selected
    if selected:
        for r in prompt.responses:
            if r.id != response_id:
                r.selected = False
    db.session.commit()
    return response


@entries_bp.route("/prompts", methods=["GET", "OPTIONS"])
@jwt_required()
def get_prompts():

    report_id = request.args.get("report_id")

    if not report_id:
        return jsonify({"error": "No report_id provided"}), 400

    prompts = Prompt.query.filter_by(report_id=report_id).all()

    prompts_data = [prompt.to_dict() for prompt in prompts]

    return jsonify(prompts_data), 200


@entries_bp.route("/new-prompt", methods=["POST"])
@jwt_required()
def new_prompt():
    text = request.get_json().get("text")
    report_id = request.get_json().get("report_id")
    if not text:
        return jsonify({"error": "No prompt text provided"}), 400
    if not report_id:
        return jsonify({"error": "No report_id provided"}), 400

    # existing prompts
    prompts = Prompt.query.filter_by(report_id=report_id).all()
    new_prompt = Prompt(text=text, report_id=report_id, position=len(prompts))
    db.session.add(new_prompt)
    db.session.commit()

    return jsonify(new_prompt.to_dict()), 200


def _generate_response(prompt_text: str, prompt_id: int, project_id: int):
    """Helper function to generate a response for a single prompt"""
    try:
        index = index_cache.get_index(project_id)
    except FileNotFoundError:
        raise FileNotFoundError("Index not found")

    writer = Writer(index)
    response = writer.write(prompt_text)
    text = response.response
    source_nodes = response.source_nodes

    # Check for existing response and update or create new one
    existing_response = Response.query.filter_by(prompt_id=prompt_id).first()
    if existing_response:
        return _update_response(
            response_id=existing_response.id,
            text=text,
            source_nodes=source_nodes,
        )
    else:
        return _add_response(prompt_id, text, source_nodes)


@entries_bp.route("/generate-all", methods=["POST"])
@jwt_required()
def generate_all():
    report_id = request.get_json().get("report_id")
    if not report_id:
        return jsonify({"error": "No report_id provided"}), 400

    prompts = Prompt.query.filter_by(report_id=report_id).all()
    project_id = Report.query.get(report_id).project_id

    try:
        for prompt in prompts:
            _generate_response(prompt.text, prompt.id, project_id)
        db.session.commit()
    except FileNotFoundError:
        return jsonify({"error": "Index not found"}), 404

    return jsonify({"success": "All responses generated"}), 200


@entries_bp.route("/generate-response", methods=["POST"])
def write():
    prompt = request.get_json().get("prompt")
    prompt_id = request.get_json().get("prompt_id")
    project_id = request.get_json().get("project_id")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    if not prompt_id:
        return jsonify({"error": "No prompt_id provided"}), 400
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    try:
        new_response = _generate_response(prompt, prompt_id, project_id)
        return jsonify(new_response.to_dict()), 200
    except FileNotFoundError:
        return jsonify({"error": "Index not found"}), 404
