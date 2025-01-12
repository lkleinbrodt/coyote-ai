from flask import Blueprint, jsonify, request
from backend.autodraft.models import Report, Prompt
from backend.extensions import db, create_logger
from flask_jwt_extended import jwt_required, current_user
import tempfile
from llama_index.core import (
    SimpleDirectoryReader,
)
from werkzeug.utils import secure_filename
import os


reports_bp = Blueprint("reports", __name__)
logger = create_logger(__name__, level="DEBUG")


@reports_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_reports():

    project_id = request.args.get("project_id")

    if project_id:
        reports = Report.query.filter_by(project_id=project_id).all()
    else:
        projects = current_user.projects
        reports = []
        for project in projects:
            reports.extend(project.reports)

    reports_data = [report.to_dict() for report in reports]

    return jsonify(reports_data), 200


@reports_bp.route("/new-report", methods=["POST"])
@jwt_required()
def new_report():
    project_id = request.get_json().get("project_id")
    report_name = request.get_json().get("name")
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400
    if not report_name:
        return jsonify({"error": "No report name provided"}), 400

    new_report = Report(name=report_name, project_id=project_id)
    db.session.add(new_report)
    db.session.commit()

    return jsonify(new_report.to_dict()), 200


@reports_bp.route("/upload-template", methods=["POST"])
@jwt_required()
def upload_template():
    # User will upload a file with the template they want to use for their report
    # we need to extract the structure of the document, break it down into individual prompts, and then save those prompts to the project
    logger.info(request)
    logger.info(request.files)
    if "file" not in request.files:
        logger.error("No file provided")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    project_id = request.form.get("project_id")
    if not project_id:
        logger.error("No project_id provided")
        return jsonify({"error": "No project_id provided"}), 400
    report_id = request.form.get("report_id")
    if not report_id:
        logger.error("No report_id provided")
        return jsonify({"error": "No report_id provided"}), 400

    temp_dir = tempfile.mkdtemp()
    filename = secure_filename(file.filename)
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)

    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()

    text_chunks = []
    for docs in reader.iter_data():
        for doc in docs:
            text_chunks.append(doc.text)

    import openai

    client = openai.OpenAI()

    prompt = """
    You are an expert at extracting the structure of a document.
    You will be shown a document that is the template for a report, and your job is to extract the prompts/questions for that report and output them in JSON list format.
    
    Example:
    input:
    ```
    Project Name: Click or tap here to enter text
    Brief Summary (one paragraph): Click or tap here to enter text.
    Total cost (round up to nearest $1,000):
    Amount requested from WCB (round up to nearest $1,000):
    Start date: Click or tap to enter a date.
    End date: Click or tap to enter a date.
    
    Project Overview
    Describe the proposed project. Quantify the project’s goals and expected outcomes/benefits.
    Identify the major tasks involved in the project. Describe why the project needed. Attach a map
    of the project location (and photos if helpful), and briefly describe the project location. Be
    specific about the portion of the project that would be funded by this request.
    Click or tap here to enter text.
    Other Funding Sources
    Please list all of the sources of cost share. Please indicate if other funding sources have been
    secured or are pending (applied for but not yet awarded).
    ```
    
    output:
    {{
        "prompts": [
        "Project Name",
        "Brief Summary (one paragraph)",
        "Total cost (round up to nearest $1,000)",
        "Amount requested from WCB (round up to nearest $1,000)",
        "Start date",
        "End date",
        "Describe the proposed project. Quantify the project’s goals and expected outcomes/benefits. Identify the major tasks involved in the project. Describe why the project needed. Attach a map of the project location (and photos if helpful), and briefly describe the project location. Be specific about the portion of the project that would be funded by this request.",
            "Please list all of the sources of cost share. Please indicate if other funding sources have been secured or are pending (applied for but not yet awarded)."
        ]
    }}
    
    Now, please do the same for the following document:
    input:
    ```
    {document}
    ```
    output:
    """

    responses = []
    for chunk in text_chunks:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(document=chunk)}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        print(content)
        import json

        content = json.loads(content)
        prompts = content.get("prompts", [])
        for item in prompts:
            if item not in responses:
                responses.append(item)

    for i, response in enumerate(responses):
        new_prompt = Prompt(text=response, report_id=report_id, position=i)
        db.session.add(new_prompt)
    db.session.commit()

    return jsonify({"success": "Template uploaded"}), 200
