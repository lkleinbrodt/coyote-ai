import json

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    stream_with_context,
)
from flask_jwt_extended import jwt_required
from openai import OpenAI

from backend.extensions import create_logger

logger = create_logger(__name__, level="DEBUG")
explain_bp = Blueprint("explain", __name__, url_prefix="/explain")

GPT_MODEL = "gpt-4o-mini-2024-07-18"


def generate_level_prompt(topic: str, level: str) -> str:
    """Generate a prompt for a specific complexity level"""
    level_requirements = {
        "child": "Explain like I'm a curious 5-8 year old. Use very simple terms, analogies, short sentences. Avoid jargon.",
        "student": "Explain like I'm a high school or early college student. Assume understanding of the 'child' explanation. Introduce fundamental technical terms clearly. Build upon the child explanation.",
        "professional": "Explain like I'm a professional working in a related field (but not necessarily an expert in _this_ topic). Assume understanding of the 'student' explanation. Use standard industry terminology. Focus on practical applications, mechanisms, or nuances. Build upon the student explanation.",
        "expert": "Explain like I'm a world-class expert specializing in this field. Assume mastery of the 'professional' explanation. Be highly technical, precise, and discuss advanced concepts, complexities, limitations, or research frontiers. Build directly upon the professional explanation.",
    }

    return f"""You are an expert educational AI assistant. Your task is to explain the topic "{topic}" at the {level} level of complexity.

Target Audience Level & Requirements:
{level_requirements[level]}

Tone: Informative, clear, engaging, and appropriate for this level.
Accuracy: Ensure factual correctness.
Safety: Avoid harmful, biased, or inappropriate content.

Generate a clear, concise explanation for the topic: "{topic}" """


@explain_bp.route("/stream/<level>", methods=["POST"])
@jwt_required()
def stream_explanation(level: str):
    """Stream an explanation for a specific complexity level"""
    logger.info(f"Stream request received for level: {level}")

    # Validate level
    valid_levels = ["child", "student", "professional", "expert"]
    if level not in valid_levels:
        return jsonify({"success": False, "error": {"message": "Invalid level"}}), 400

    # Get and validate request data
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided in request")
            return (
                jsonify({"success": False, "error": {"message": "No data provided"}}),
                400,
            )

        topic = data.get("topic")
        if not topic or not isinstance(topic, str) or not topic.strip():
            logger.warning("Invalid topic provided")
            return (
                jsonify(
                    {"success": False, "error": {"message": "Valid topic is required"}}
                ),
                400,
            )

        if len(topic) > 500:
            logger.warning(f"Topic exceeds maximum length: {len(topic)} characters")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Topic must be 500 characters or less"},
                    }
                ),
                400,
            )

        logger.debug(
            f"Processing stream request for topic: {topic[:50]}... (level: {level})"
        )

        def generate():
            try:
                # Make the OpenAI API call with streaming
                client = OpenAI(api_key=current_app.config.get("OPENAI_API_KEY"))
                stream = client.chat.completions.create(
                    model=GPT_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that generates explanations at different complexity levels. Provide clear, concise explanations.",
                        },
                        {
                            "role": "user",
                            "content": generate_level_prompt(topic, level),
                        },
                    ],
                    temperature=0.7,
                    stream=True,
                )

                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'error': 'Failed to generate explanation'})}\n\n"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")

    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "An unexpected error occurred"}}
            ),
            500,
        )
