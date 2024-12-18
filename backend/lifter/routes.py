from flask import jsonify, Blueprint, request, Response, stream_with_context
from backend.extensions import create_logger
import json
import pandas as pd
from backend.src.s3 import S3
from botocore.errorfactory import ClientError
from backend.config import Config

S3_BUCKET = Config.LIFTER_BUCKET

logger = create_logger(__name__, level="DEBUG")

lifter = Blueprint("lifter", __name__, url_prefix="/lifter")


def load_lifts_from_s3():
    s3_client = S3(bucket=S3_BUCKET)
    return s3_client.load_json("lifts.json")


def save_lifts_to_s3(lifts_dict):
    s3_client = S3(bucket=S3_BUCKET)
    s3_client.save_json(lifts_dict, "lifts.json")


def load_workouts_from_s3():
    # cringe. upgrade this entire script
    s3_client = S3(bucket=S3_BUCKET)
    try:
        data = s3_client.load_csv("lifts.csv")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.warning("No lift csv found, making a new one")
            data = pd.DataFrame()
        else:
            logger.exception(e)
            return jsonify({"error": "Error loading data"}), 500
    return data


@lifter.route("/")
def home():
    logger.debug("Home route accessed")
    return jsonify({"message": "Hello from Lifter Flask!"})


@lifter.route("/get-types", methods=["GET"])
def get_types():
    lifts = load_lifts_from_s3()
    return jsonify(list(lifts.keys()))


@lifter.route("/get-lifts", methods=["GET"])
def get_lifts():
    lift_type = request.args.get("type")

    lifts = load_lifts_from_s3()

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

    data = load_workouts_from_s3()

    if lift is not None:
        data = data[data["name"] == lift]

    if user is not None:
        data = data[data["user"].str.lower() == user]

    data = data[data["date"] == data["date"].max()]
    data = data.fillna("")

    out = []
    for i, row in data.iterrows():
        out.append(row.to_dict())

    return jsonify(out), 200


@lifter.route("/get-all-lifts", methods=["GET"])
def get_all_lifts():
    lift = request.args.get("lift")

    data = load_workouts_from_s3()

    if lift is not None:
        data = data[data["name"] == lift]

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
        series_array = []

        # Process Landon's sets (always present)
        landon_array = exercise["landon"]
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

        # Process Erin's sets if present
        if "erin" in exercise and exercise["erin"]:
            erin_array = exercise["erin"]
            erin_series_array = []
            for set in erin_array:
                erin_series_array.append(
                    pd.Series(
                        {
                            "user": "erin",
                            "weight": set["weight"],
                            "reps": set["reps"],
                        }
                    )
                )
            erin_series = pd.DataFrame(erin_series_array)
            erin_series.index.name = "set"
            # Combine both users' data
            exercise_df = pd.concat([landon_series, erin_series], axis=0).reset_index()
        else:
            # Only use Landon's data
            exercise_df = landon_series.reset_index()

        exercise_df["type"] = exercise["type"]
        exercise_df["name"] = exercise["name"]
        exercise_df["set"] = exercise_df["set"] + 1  # so it's not 0 indexed
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


@lifter.route("/add-lift", methods=["POST"])
def add_lift():
    # user provides a lift type and a lift name
    # grab lift json
    # check that the lift type is valid
    # add the name to that lift type
    # return success

    lift_type = request.json["type"]
    lift_name = request.json["name"]

    lifts = load_lifts_from_s3()

    if lift_type not in lifts:
        return jsonify({"error": "Invalid lift type"}), 400

    lifts[lift_type].append(lift_name)

    save_lifts_to_s3(lifts)

    return jsonify({"message": "Lift added"}), 200


@lifter.route("/health", methods=["GET"])
def health_check():
    response = {"status": "healthy", "message": "Server is running"}
    return jsonify(response), 200
