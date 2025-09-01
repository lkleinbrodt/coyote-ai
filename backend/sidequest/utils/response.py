from flask import jsonify


def success_response(data, status_code=200):
    """
    Generates a consistent success response.
    Wrapper: { "data": ... }
    """
    return jsonify({"data": data}), status_code


def error_response(message, code, status_code=400):
    """
    Generates a consistent error response.
    Wrapper: { "error": { "message": ..., "code": ... } }
    """
    response = {"error": {"message": message, "code": code}}
    return jsonify(response), status_code
