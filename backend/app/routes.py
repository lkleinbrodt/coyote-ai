from datetime import datetime, timedelta
import random

# from server.models import User
from server.config import create_logger, Config
from flask import (
    request,
    jsonify,
    url_for,
    Blueprint,
    render_template,
    send_from_directory,
)

# from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    current_user,
    get_jwt_identity,
)
from server.src.MailBot import MailBot
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
logger = create_logger(__name__, level="DEBUG")

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return send_from_directory("static", "index.html")


# @app.route("/login", methods=["POST"])
# def login():
#     logger.info("User login attempt")
#     data = request.json
#     username, password = data.get("username").strip(), data.get("password").strip()
#     if not username or not password:
#         logger.error("Missing email or password")
#         return jsonify({"message": "email and password are required"}), 400
#     user = User.query.filter_by(userName=username).first()
#     if user is None or not user.check_password(password):
#         logger.error("Invalid username or password")
#         return jsonify({"message": "Invalid username or password"}), 401
#     logger.info("User logged in successfully")

#     access_token = create_access_token(identity=user)
#     refresh_token = create_refresh_token(identity=user)
#     return jsonify(access_token=access_token, refresh_token=refresh_token), 200


# @app.route("/register", methods=["POST", "OPTIONS"])
# def register():

#     data = request.json
#     username, email, password = (
#         data.get("username", "").strip(),
#         data.get("email", "").strip(),
#         data.get("password", "").strip(),
#     )
#     if not username or not email or not password:
#         logger.error("Missing fields for registration")
#         return jsonify({"message": "Missing fields"}), 400
#     if User.query.filter((User.userName == username) | (User.email == email)).first():
#         logger.error("Username or Email already registered")
#         return jsonify({"message": "Username or Email already registered"}), 400
#     try:
#         user = User(
#             userName=username,
#             email=email,
#             # storeName=f"store_{username}",
#             # reverbAccess=username + "19",
#         )

#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()

#         send_verification_email(email)

#         logger.info("User registered successfully")
#     except IntegrityError:
#         db.session.rollback()
#         logger.error("Error creating user")
#         return jsonify({"message": "Error creating user"}), 500
#     return jsonify(create_access_token(identity=user)), 200


# @jwt.additional_claims_loader
# def add_claims_to_access_token(user):
#     return {
#         "email": user.email,
#         "id": user.id,
#         "username": user.userName,
#         "emailVerified": user.email_verified,
#     }


# @jwt.user_identity_loader
# def user_identity_lookup(user):
#     return user.id


# # Register a callback function that loads a user from your database whenever
# # a protected route is accessed. This should return any python object on a
# # successful lookup, or None if the lookup failed for any reason (for example
# # if the user has been deleted from the database).
# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     return User.query.filter_by(id=identity).one_or_none()


# @app.route("/refresh", methods=["POST"])
# @jwt_required(refresh=True)
# def refresh():
#     logger.debug("Refreshing token")
#     access_token = create_access_token(identity=current_user)
#     return jsonify(access_token=access_token)


# @app.route("/change-forgot-password", methods=["POST"])
# def change_forgot_password():
#     data = request.json
#     code = data.get("verificationCode", "").strip()
#     new_password = data.get("newPassword", "").strip()
#     email = data.get("email", "").strip()

#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     if not user.can_change_password:
#         return jsonify({"error": "Change password code expired"}), 400

#     if user.can_change_password_expiry < datetime.utcnow():
#         return jsonify({"error": "Change password code expired"}), 400

#     if user.change_password_code != code:
#         logger.debug(code)
#         logger.debug(user.change_password_code)
#         return jsonify({"error": "Invalid code"}), 400

#     try:
#         user.set_password(new_password)
#         user.can_change_password = False
#         user.can_change_password_expiry = datetime.utcnow()
#         db.session.commit()
#         return jsonify({"message": "Password changed successfully"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": "Error changing password"}), 500


# @app.route("/change-password", methods=["POST"])
# @jwt_required()
# def change_password():
#     logger.info("User password update attempt")
#     data = request.json
#     old_password = data.get("oldPassword", "").strip()
#     new_password = data.get("newPassword", "").strip()

#     current_user_id = get_jwt_identity()
#     current_user = User.query.get(current_user_id)

#     if not current_user:
#         logger.error("User not found")
#         return jsonify({"message": "User not found"}), 404

#     # Check if the old password provided matches the current password
#     if not current_user.check_password(old_password):
#         logger.error("Old password does not match")
#         return jsonify({"message": "Old password is incorrect"}), 400

#     try:
#         current_user.set_password(new_password)
#         db.session.commit()
#         logger.info("Password updated successfully")
#         return jsonify({"message": "Password updated successfully"}), 200
#     except Exception as e:
#         logger.error("Error updating password: {}".format(str(e)))
#         db.session.rollback()
#         return jsonify({"message": "Error updating password"}), 500


# def generate_email_verification_token(email):
#     token = serializer.dumps(email, salt="email-verification")
#     return token


# def send_verification_email(email):

#     token = generate_email_verification_token(email)
#     mailer = MailBot()

#     user = User.query.filter_by(email=email).first()
#     if user is None:
#         return jsonify({"error": "Email not found"}), 404

#     subject = "GuitarPic: Verify Your Email"
#     url = url_for("main.verify_email", token=token, _external=True)
#     body = f"Click the following link to verify your email: {url}"

#     mailer.send_email(subject, body, email)

#     return True


# @app.route("/send-verification-email", methods=["GET"])
# @jwt_required()
# def send_verification_email_route():
#     # check if email is already verified
#     if current_user.email_verified:
#         return jsonify({"message": "Email already verified"}), 200

#     email = current_user.email
#     try:
#         send_verification_email(email)
#     except Exception as e:
#         logger.error(f"Error sending verification email: {e}")
#         return jsonify({"error": "Error sending verification email"}), 500

#     return jsonify({"message": "Verification email sent"}), 200


# @app.route("/verify-email", methods=["GET"])
# def verify_email():
#     token = request.args.get("token")
#     try:
#         email = serializer.loads(token, salt="email-verification", max_age=3600)
#         user = User.query.filter_by(email=email).first()
#         if user is None:
#             return jsonify({"error": "Email not found"}), 404
#         if user.email_verified:
#             return jsonify({"message": "Email already verified"}), 200
#         user.email_verified = True
#         db.session.commit()
#         return jsonify({"message": "Email verified"}), 200
#     except Exception as e:
#         logger.exception("Unable to verify email")

#         return jsonify({"error": "Unable to verify email"}), 400


# @app.route("/forgot-password", methods=["POST"])
# def send_forget_password_email():
#     data = request.json
#     email = data.get("email")
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"error": "Email not found"}), 404

#     current_expiration = user.can_change_password_expiry
#     if current_expiration is not None:
#         if current_expiration > datetime.utcnow():
#             return (
#                 jsonify(
#                     {
#                         "error": "There is already an active verification code. Please use that code or wait to generate a new one."
#                     }
#                 ),
#                 400,
#             )

#     token = str(random.randint(100000, 999999))
#     mailer = MailBot()
#     subject = "GuitarPic: Reset Your Password"
#     body = f"Use the following code to reset your password: {token}"
#     try:
#         mailer.send_email(subject, body, email)
#     except Exception as e:
#         logger.error(f"Error sending forget password email: {e}")
#         return jsonify({"error": "Error sending forget password email"}), 500

#     try:
#         user.can_change_password = True
#         user.can_change_password_expiry = datetime.utcnow() + timedelta(minutes=30)
#         user.change_password_code = token
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         logger.error(f"Error updating user: {e}")
#         return jsonify({"error": "Error updating user"}), 500

#     return jsonify({"message": "Forget password email sent"}), 200
