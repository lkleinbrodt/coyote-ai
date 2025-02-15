from backend.extensions import create_logger
from backend.models import User
from backend.extensions import db
from flask import (
    Blueprint,
    redirect,
    jsonify,
    request,
)
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from backend.src.OAuthSignIn import OAuthSignIn
from flask import current_app

logger = create_logger(__name__, level="DEBUG")


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/authorize/<provider>")
@jwt_required(optional=True)
def oauth_authorize(provider):

    user_id = get_jwt_identity()
    if user_id:
        return redirect(f"{current_app.config['BASE_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize(next_path=request.args.get("next", "/"))


@auth_bp.route("/callback/<provider>")
@jwt_required(optional=True)
def oauth_callback(provider):

    user_id = get_jwt_identity()
    if user_id:
        return redirect(f"{current_app.config['BASE_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    try:
        social_id, name, email, picture = oauth.callback()
    except Exception as e:
        print(e)
        return jsonify({"error": "No social id found"}), 400

    if social_id is None:
        return jsonify({"error": "No social id found"}), 400

    user = User.query.filter_by(social_id=social_id).first()

    if not user:
        user = User(social_id=social_id, name=name, email=email, image=picture)
        db.session.add(user)
        db.session.commit()
    else:
        if social_id:
            user.social_id = social_id
        if name:
            user.name = name
        if email:
            user.email = email
        if picture:
            user.image = picture
        db.session.commit()

    # Get the next parameter from the OAuth state
    next_path = request.args.get("state", "/")

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "name": user.name,
            "email": user.email,
            "image": user.image,
        },
    )

    redirect_url = f"{current_app.config['BASE_URL']}/auth?access_token={access_token}&next={next_path}"
    return redirect(redirect_url)
