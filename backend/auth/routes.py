from datetime import timedelta
from flask import Blueprint, current_app, jsonify, make_response, redirect, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from sqlalchemy import text

from backend.extensions import create_logger, db
from backend.models import (
    User,
)
from backend.src.OAuthSignIn import OAuthSignIn
from backend.src.apple_auth_service import AppleAuthService

logger = create_logger(__name__, level="DEBUG")

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/authorize/<provider>")
@jwt_required(optional=True)
def oauth_authorize(provider):
    logger.info(f"OAuth authorization attempt for provider: {provider}")
    user_id = get_jwt_identity()
    if user_id:
        logger.debug(f"User {user_id} already authenticated, redirecting to frontend")
        return redirect(f"{current_app.config['FRONTEND_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize(next_path=request.args.get("next", "/"))


@auth_bp.route("/callback/<provider>")
@jwt_required(optional=True)
def oauth_callback(provider):

    user_id = get_jwt_identity()
    if user_id:
        return redirect(f"{current_app.config['FRONTEND_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    try:
        social_id, name, email, picture = oauth.callback()
    except Exception as e:
        print(e)
        return jsonify({"error": "No social id found"}), 400

    if social_id is None:
        return jsonify({"error": "No social id found"}), 400

    if provider == "google":
        user = User.query.filter_by(google_id=social_id).first()
    elif provider == "apple":
        user = User.query.filter_by(apple_id=social_id).first()
    else:
        raise ValueError(f"Invalid provider: {provider}")
    # TODO: reconcile different emails
    if not user:
        if provider == "google":
            user = User(google_id=social_id, name=name, email=email, image=picture)
        elif provider == "apple":
            user = User(apple_id=social_id, name=name, email=email, image=picture)
        else:
            raise ValueError(f"Invalid provider: {provider}")
        db.session.add(user)
        db.session.commit()
    else:
        if name:
            user.name = name
        if email:
            user.email = email
        if picture:
            user.image = picture
        db.session.commit()

    # Get the next parameter from the OAuth state
    next_path = request.args.get("state", "/")

    # Create access token with user info
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "name": user.name,
            "email": user.email,
            "image": user.image,
        },
    )

    # Create refresh token
    refresh_token = create_refresh_token(identity=str(user.id))

    # Prepare redirect URL with access token
    redirect_url = f"{current_app.config['FRONTEND_URL']}/auth?access_token={access_token}&next={next_path}"

    # Create response with redirect
    response = make_response(redirect(redirect_url))

    # Set refresh token as HttpOnly cookie
    set_refresh_cookies(
        response,
        refresh_token,
    )

    logger.debug(
        f"OAuth callback successful for user {user.id}. Redirecting with access token and refresh cookie."
    )
    return response


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """Endpoint to refresh access token using refresh token cookie"""
    current_user_identity = get_jwt_identity()

    # Fetch user from database to get latest claims
    user = User.query.get(current_user_identity)
    if not user:
        logger.error(f"User {current_user_identity} not found during token refresh")
        return jsonify({"error": "User not found"}), 404

    # Create new access token with latest user info
    new_access_token = create_access_token(
        identity=current_user_identity,
        additional_claims={
            "name": user.name,
            "email": user.email,
            "image": user.image,
        },
    )

    logger.debug(f"Token refreshed for user {current_user_identity}")
    return jsonify(access_token=new_access_token), 200


@auth_bp.route("/logout", methods=["GET"])
@jwt_required(verify_type=False, optional=True)
def logout():
    """
    Endpoint to logout user by clearing JWT cookies and redirecting to frontend homepage.
    - GET: Clears cookies and redirects browser to frontend home.
    - POST: API call for backward compatibility, returns JSON response.
    """

    # Redirect flow - create a redirect response
    frontend_home_url = f"{current_app.config['FRONTEND_URL']}/"
    response = make_response(redirect(frontend_home_url))
    unset_jwt_cookies(response)
    logger.debug(
        f"User logged out via redirect flow. Redirecting to {frontend_home_url}"
    )
    return response


# iOS/Mobile App Authentication Endpoints
@auth_bp.route("/mobile/login-with-apple", methods=["POST"])
def mobile_login_with_apple():
    """Mobile app login endpoint using Apple Sign-In"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"success": False, "error": {"message": "No data provided"}}),
                400,
            )

        # Extract Apple credential from request
        credential = data.get("appleIdToken")
        if not credential:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "No Apple credential provided"},
                    }
                ),
                400,
            )

        identity_token = credential.get("identityToken")
        if not identity_token:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": "Credential object missing identityToken"},
                    }
                ),
                400,
            )

        # Get the user's name if they provide it on first sign-up
        full_name = credential.get("fullName", {})

        apple_service = AppleAuthService(db.session)

        try:
            user = apple_service.authenticate_with_apple(
                credential, client_id=None, app_name="SideQuest"
            )
        except Exception as e:
            logger.error(f"Apple authentication failed: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"message": f"Authentication failed: {str(e)}"},
                    }
                ),
                401,
            )

        # Create long-lived access token (1 year) - simpler for mobile
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "name": user.name,
                "email": user.email,
                "image": user.image,
                "role": getattr(user, "role", "user"),
            },
            expires_delta=timedelta(days=365),  # 1 year token
        )

        logger.info(f"Mobile Apple login successful for user {user.id}")

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "access_token": access_token,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "image": user.image,
                            "role": getattr(user, "role", "user"),
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Mobile Apple login error: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Login failed"}}),
            500,
        )
