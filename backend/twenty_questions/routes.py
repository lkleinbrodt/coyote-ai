from flask import jsonify, Blueprint, request, Response, stream_with_context
from backend.config import create_logger
import json
import pandas as pd
from backend.src.s3 import S3
from botocore.errorfactory import ClientError
from backend.config import Config

from openai import OpenAI

S3_BUCKET = Config.LIFTER_BUCKET

logger = create_logger(__name__, level="DEBUG")

twenty_questions = Blueprint(
    "twenty_questions", __name__, url_prefix="/twenty-questions"
)


@twenty_questions.route("/chat", methods=["POST"])
def chat():
    messages = request.json.get("messages", [])

    client = OpenAI(
        api_key=Config.TWENTY_QUESTIONS_OPENAI_API_KEY,
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    def yield_stream():
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return Response(stream_with_context(yield_stream()))
