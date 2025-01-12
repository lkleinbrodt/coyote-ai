# from flask import Blueprint, jsonify, session, request, redirect, url_for
# from config import create_logger
# from server.models import User
# from server.extensions import db
# from flask_jwt_extended import create_access_token
# from server.OAuthSignIn import OAuthSignIn

# logger = create_logger(__name__, level="DEBUG")

# server_bp = Blueprint("server", __name__)


# @server_bp.route("/", methods=["GET"])
# def index():
#     return jsonify({"message": "Hello, World!"})


# @server_bp.route("/session", methods=["GET"])
# def get_session():
#     logger.debug(f"Session:\n{session}")

#     return jsonify(session)


# @server_bp.route("/authorize/<provider>")
# def oauth_authorize(provider):
#     # TODO: if user is already logged in, redirect to index
#     oauth = OAuthSignIn.get_provider(provider)
#     return oauth.authorize()


# @server_bp.route("/callback/<provider>")
# def oauth_callback(provider):
#     # TODO: if user is already logged in, redirect to index
#     oauth = OAuthSignIn.get_provider(provider)
#     social_id, name, email, picture = oauth.callback()

#     if social_id is None:
#         # error
#         return jsonify({"error": "No social id found"}), 400

#     user = User.query.filter_by(social_id=social_id).first()
#     if not user:
#         # createa a new user primary
#         user = User(social_id=social_id, name=name, email=email, image=picture)
#         db.session.add(user)

#     # update user info if it has changed
#     user.name = name
#     user.email = email
#     user.image = picture
#     db.session.commit()

#     # create a jwt
#     access_token = create_access_token(
#         identity={
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "image": user.image,
#         }
#     )

#     redirect_url = f"http://localhost:3000/auth?access_token={access_token}"
#     return redirect(redirect_url)
