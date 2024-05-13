from flask import jsonify, Blueprint, request, Response, stream_with_context
from server.config import create_logger
import json
import time
from server.src import s3
from botocore.errorfactory import ClientError

logger = create_logger(__name__, level="DEBUG")

lifter = Blueprint("lifter", __name__, url_prefix="/lifter")
BUCKET = "cheffrey"


@lifter.route("/")
def home():
    logger.debug("Home route accessed")
    return jsonify({"message": "Hello from Lifter Flask!"})


@lifter.route("/get-types", methods=["GET"])
def get_types():
    with open("./lifter/lifts.json", "r") as f:
        lifts = json.load(f)
    return jsonify(list(lifts.keys()))


@lifter.route("/get-lifts", methods=["GET"])
def get_lifts():
    lift_type = request.args.get("type")

    # load lifts from a json "./lifter/lifts.json"
    with open("./lifter/lifts.json", "r") as f:
        lifts = json.load(f)

    if lift_type is not None:
        if lift_type not in lifts:
            return jsonify({"error": "Invalid lift type"}), 400
        else:
            return jsonify(lifts[lift_type]), 200

    return jsonify(lifts), 200


@lifter.route("/get-last-lifts", methods=["GET"])
def get_last_lifts():

    lift = request.args.get("lift")

    s3_client = s3.S3(bucket=BUCKET)
    try:
        data = s3_client.load_csv("lifts.csv")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            import pandas as pd

            data = pd.read_csv("~/Desktop/lift_sample.csv")
        else:
            logger.exception(e)
            return jsonify({"error": "Error loading data"}), 500

    if lift is not None:
        data = data[data["lift"] == lift]

    data = data[data["date"] == data["date"].max()]

    out = []
    for i, row in data.iterrows():
        out.append(row.to_dict())

    return jsonify(out)
