from datetime import datetime, timedelta
import random

# from server.models import User
from backend.config import create_logger, Config
from flask import (
    request,
    jsonify,
    url_for,
    Blueprint,
    render_template,
    send_from_directory,
    redirect,
)

# from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    current_user,
    get_jwt_identity,
)
from backend.src.OAuthSignIn import OAuthSignIn
from itsdangerous import URLSafeTimedSerializer


serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
logger = create_logger(__name__, level="DEBUG")

server_bp = Blueprint("server", __name__)


@server_bp.route("/authorize/<provider>")
def oauth_authorize(provider):
    # TODO: if user is already logged in, redirect to index
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@server_bp.route("/callback/<provider>")
def oauth_callback(provider):
    # TODO: if user is already logged in, redirect to index
    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email, picture = oauth.callback()

    # if social_id is None:
    #     # error
    #     return jsonify({"error": "No social id found"}), 400

    # user = User.query.filter_by(social_id=social_id).first()
    # if not user:
    #     # createa a new user primary
    #     user = User(social_id=social_id, name=name, email=email, image=picture)
    #     db.session.add(user)

    # # update user info if it has changed
    # user.name = name
    # user.email = email
    # user.image = picture
    # db.session.commit()

    # create a jwt
    access_token = create_access_token(
        identity={
            "id": social_id,
            "name": name,
            "email": email,
            "image": picture,
        }
    )
    print("access_token", access_token)
    redirect_url = f"http://localhost:5174/auth?access_token={access_token}"
    return redirect(redirect_url)
