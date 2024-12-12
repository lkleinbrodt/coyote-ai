from backend.config import Config
from backend.extensions import create_logger
from flask import (
    Blueprint,
    redirect,
    jsonify,
    request,
)
from flask_jwt_extended import (
    create_access_token,
)
from backend.src.OAuthSignIn import OAuthSignIn
from flask import current_app

logger = create_logger(__name__, level="DEBUG")


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/authorize/<provider>")
def oauth_authorize(provider):
    # TODO: if user is already logged in, redirect to index

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize(next_path=request.args.get("next", "/"))


@auth_bp.route("/callback/<provider>")
def oauth_callback(provider):

    oauth = OAuthSignIn.get_provider(provider)
    try:
        social_id, name, email, picture = oauth.callback()
    except Exception as e:
        print(e)
        return jsonify({"error": "No social id found"}), 400
    next_path = request.args.get("state", "/")

    if social_id is None:
        return jsonify({"error": "No social id found"}), 400

    # Get the next parameter from the OAuth state
    next_path = request.args.get("state", "/")

    # create a jwt
    access_token = create_access_token(
        identity={
            "id": social_id,
            "name": name,
            "email": email,
            "image": picture,
        }
    )

    redirect_url = f"{current_app.config['BASE_URL']}/auth?access_token={access_token}&next={next_path}"
    return redirect(redirect_url)
