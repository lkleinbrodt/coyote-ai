from flask import jsonify, Blueprint, request, Response, stream_with_context
from server.config import create_logger
import json
import pandas as pd
from server.src.s3 import S3
from botocore.errorfactory import ClientError
from server.config import Config

S3_BUCKET = Config.LIFTER_BUCKET

logger = create_logger(__name__, level="DEBUG")

lifter = Blueprint("lifter", __name__, url_prefix="/lifter")


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


@lifter.route("/get-last-lifts/", methods=["GET"])
def get_last_lifts():

    lift = request.args.get("lift")
    user = request.args.get("user")

    s3_client = S3(bucket=S3_BUCKET)
    try:
        data = s3_client.load_csv("lifts.csv")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.warning("No lift csv found, making a new one")
            data = pd.DataFrame()

            return jsonify([]), 200
        else:
            logger.exception(e)
            return jsonify({"error": "Error loading data"}), 500

    if lift is not None:
        data = data[data["lift"] == lift]

    if user is not None:
        data = data[data["user"].str.lower() == user]

    data = data[data["date"] == data["date"].max()]
    data = data.fillna("")

    out = []
    for i, row in data.iterrows():
        out.append(row.to_dict())

    return jsonify(out), 200


@lifter.route("/save-workout", methods=["POST"])
def save_workout():

    workout = request.json

    workout_array = []
    for exercise in workout:

        landon_array = exercise["landon"]
        erin_array = exercise["erin"]

        series_array = []
        for set in landon_array:
            series_array.append(
                pd.Series(
                    {
                        "user": "landon",
                        "weight": set["weight"],
                        "reps": set["reps"],
                    }
                )
            )
        landon_series = pd.DataFrame(series_array)
        landon_series.index.name = "set"

        series_array = []
        for set in erin_array:
            series_array.append(
                pd.Series(
                    {
                        "user": "erin",
                        "weight": set["weight"],
                        "reps": set["reps"],
                    }
                )
            )
        erin_series = pd.DataFrame(series_array)
        erin_series.index.name = "set"

        exercise_df = pd.concat([landon_series, erin_series], axis=0).reset_index()
        exercise_df["type"] = exercise["type"]
        exercise_df["name"] = exercise["name"]

        workout_array.append(exercise_df)

    workout_df = pd.concat(workout_array, axis=0)
    workout_df.reset_index(drop=True, inplace=True)

    workout_df["date"] = pd.Timestamp.now()

    s3_client = S3(bucket=S3_BUCKET)

    s3_client.write_csv(workout_df, f"workouts/{workout_df['date'].iloc[0]}.csv")

    try:
        data = s3_client.load_csv("lifts.csv")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.warning("No lift csv found, making a new one")
            data = pd.DataFrame()
        else:
            logger.exception(e)
            return jsonify({"error": "Error loading data"}), 500

    data = pd.concat([data, workout_df], axis=0)

    s3_client.write_csv(data, "lifts.csv")

    return jsonify({"message": "Workout saved"}), 200


@lifter.route("/health", methods=["GET"])
def health_check():
    response = {"status": "healthy", "message": "Server is running"}
    return jsonify(response), 200
