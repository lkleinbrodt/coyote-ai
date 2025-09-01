import base64
from datetime import datetime, timedelta
from flask import current_app
import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from sqlalchemy.orm import Session

from backend.extensions import create_logger, db
from backend.models import User

logger = create_logger(__name__)

# Apple Sign-In constants
# CRITICAL: Bundle ID must match your iOS app's bundle identifier
# This is used to validate Apple JWT tokens and prevent token reuse
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"

# Cache for Apple's public keys
_apple_public_keys = {}
_apple_keys_expiry = None


def _get_apple_public_keys():
    """
    Fetch and cache Apple's public keys with httpx for better performance.
    Returns cached keys if they're still valid (24 hour cache).
    """
    global _apple_public_keys, _apple_keys_expiry

    # Return cached keys if they're still valid
    if (
        _apple_public_keys
        and _apple_keys_expiry
        and datetime.now() < _apple_keys_expiry
    ):
        return _apple_public_keys

    # Fetch new keys
    try:
        with httpx.Client() as client:
            response = client.get(APPLE_KEYS_URL)
            response.raise_for_status()
            keys_data = response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch Apple public keys: {e}")
        raise Exception(f"Failed to fetch Apple public keys: {e}")

    _apple_public_keys = {}
    # Convert each key to RSA public key using cryptography library
    for key in keys_data["keys"]:
        _apple_public_keys[key["kid"]] = jwk_to_rsa_key(key)

    # Cache for 24 hours
    _apple_keys_expiry = datetime.now() + timedelta(hours=24)

    return _apple_public_keys


def jwk_to_rsa_key(jwk_key):
    """
    Convert a JWK (JSON Web Key) to an RSA public key using the cryptography library.
    This is the pythonic way recommended for PyJWT.
    """
    # Extract the modulus and exponent from the JWK
    n = jwk_key["n"]
    e = jwk_key["e"]

    # Decode the base64url-encoded values
    n_bytes = base64.urlsafe_b64decode(n + "==")  # Add padding if needed
    e_bytes = base64.urlsafe_b64decode(e + "==")  # Add padding if needed

    # Convert bytes to integers
    n_int = int.from_bytes(n_bytes, "big")
    e_int = int.from_bytes(e_bytes, "big")

    # Create RSA public numbers and then the public key
    public_numbers = RSAPublicNumbers(e_int, n_int)
    public_key = public_numbers.public_key()

    return public_key


def validate_apple_token(identity_token: str, client_id: str = None) -> dict:
    """
    Validates an Apple Sign-In identity token with enhanced error handling.

    :param identity_token: The JWT from the client.
    :param client_id: Your app's bundle identifier (the audience). Optional in development.
    :return: The decoded claims dictionary if valid.
    :raises: Exception if the token is invalid.

    Note: In development mode (current_app.debug=True), audience verification is bypassed
    for convenience, but this should NOT be used in production.
    """
    if not identity_token:
        raise Exception("No identity token provided.")

    try:
        # Get the key ID from the token's header
        header = jwt.get_unverified_header(identity_token)
        kid = header.get("kid")
        if not kid:
            raise Exception("Token is missing 'kid' in header.")

        # Fetch the public keys and find the matching key
        apple_keys = _get_apple_public_keys()
        matching_key = apple_keys.get(kid)
        if not matching_key:
            raise Exception("Could not find a matching public key.")

        # Set up decode options
        decode_options = {
            "verify_sub": True,
            # Don't verify expiration in development to make testing easier
            "verify_exp": not current_app.debug,
        }

        decode_kwargs = {
            "algorithms": ["RS256"],
            "options": decode_options,
        }

        # Handle audience verification based on environment
        if current_app.debug:
            # Development: Bypass audience verification for convenience
            # WARNING: This bypasses a security check and should NOT be used in production
            logger.warning(
                "DEVELOPMENT MODE: Bypassing Apple token audience verification. "
                "This is NOT secure for production use!"
            )
            # Get the audience from the token itself for logging purposes
            claims = jwt.decode(identity_token, options={"verify_signature": False})
            logger.debug(f"Development mode - Token audience: {claims.get('aud')}")
        elif client_id:
            decode_kwargs["audience"] = client_id
            claims = jwt.decode(identity_token, matching_key, **decode_kwargs)
        else:
            # No client_id provided and not in development - use token's own audience
            logger.info(
                "No client_id provided and not in development - using token's own audience"
            )
            unverified_payload = jwt.decode(
                identity_token, options={"verify_signature": False}
            )
            if "aud" in unverified_payload:
                decode_kwargs["audience"] = unverified_payload["aud"]
            claims = jwt.decode(identity_token, matching_key, **decode_kwargs)

        # Decode and validate the token

        return claims

    except jwt.ExpiredSignatureError:
        raise Exception("Apple token has expired.")
    except jwt.InvalidAudienceError:
        logger.info(decode_kwargs)

        raise Exception("Apple token has an invalid audience.")
    except jwt.InvalidIssuerError:
        raise Exception("Apple token has an invalid issuer.")
    except jwt.InvalidTokenError as e:
        # General catch-all for other JWT errors
        raise Exception(f"Invalid Apple token: {e}")
    except Exception as e:
        # Catch other unexpected errors
        raise Exception(f"An unexpected error occurred during token validation: {e}")


class AppleAuthService:
    """Consolidated service for handling Apple Sign-In authentication across all apps"""

    def __init__(self, session: Session = None):
        self.session = session or db.session

    def authenticate_with_apple(
        self, apple_credential: dict, client_id: str = None, app_name: str = "unknown"
    ) -> User:
        """
        Authenticate a user with Apple Sign-In. This is the main entry point
        that consolidates functionality for all apps.

        Args:
            apple_credential: Dictionary containing Apple Sign-In response data
            client_id: Optional bundle identifier for audience verification
            app_name: Name of the app for logging purposes

        Returns:
            User: The authenticated user (new or existing)
        """
        try:
            identity_token = apple_credential.get("identityToken")
            if not identity_token:
                raise ValueError("No identity token found")

            # Validate the Apple token
            claims = validate_apple_token(identity_token, client_id)

            # Extract verified claims from the token
            apple_id = claims["sub"]
            email = claims.get("email")
            email_verified = claims.get("email_verified", False)

            # Extract user information from credential
            full_name = apple_credential.get("fullName", {})
            name = self._build_full_name(full_name)

            logger.info(f"[{app_name}] Processing Apple Sign-In for user {apple_id}")

            # Check if user already exists
            user = User.query.filter_by(apple_id=apple_id).first()
            is_new_user = False

            if not user:
                # Try to find user by email as fallback
                if email:
                    user = User.query.filter_by(email=email).first()

            if not user:
                # Create new user
                logger.info(f"[{app_name}] Creating new user with Apple ID {apple_id}")
                is_new_user = True

                user = User(
                    apple_id=apple_id,
                    name=name,
                    email=email,
                    image="https://via.placeholder.com/150",  # Default avatar
                )

                # Check if this should be an admin user
                admin_emails = current_app.config.get("ADMIN_EMAILS", [])
                if email and email in admin_emails:
                    user.role = "admin"
                    logger.info(f"[{app_name}] User {email} assigned admin role")

                self.session.add(user)
                self.session.commit()

            else:
                logger.info(
                    f"[{app_name}] User with Apple ID {apple_id} already exists"
                )
                # Update user info if Apple provided new information
                self._update_user_info(user, name, email, apple_id, full_name)
                self.session.commit()

            return user

        except Exception as e:
            logger.error(f"[{app_name}] Apple authentication error: {str(e)}")
            raise e

    def _build_full_name(self, full_name: dict) -> str:
        """Build full name from Apple's name components"""
        if not full_name:
            return ""

        given_name = full_name.get("givenName", "")
        family_name = full_name.get("familyName", "")

        if given_name and family_name:
            return f"{given_name} {family_name}".strip()
        elif given_name:
            return given_name
        elif family_name:
            return family_name
        else:
            return ""

    def _update_user_info(
        self, user: User, name: str, email: str, apple_id: str, full_name: dict
    ):
        """Update existing user information with new data from Apple"""
        # Update name if provided and different
        if name and name.strip() and name != user.name:
            logger.debug(f"Updating user name from '{user.name}' to '{name}'")
            user.name = name

        # Update email if it's different, not None, and not empty
        if email and email.strip() and email != user.email:
            logger.debug(f"Updating user email from '{user.email}' to '{email}'")
            user.email = email

        # Update apple_id if different
        if apple_id and apple_id != user.apple_id:
            logger.debug(
                f"Updating user apple_id from '{user.apple_id}' to '{apple_id}'"
            )
            user.apple_id = apple_id

        # Update image if not set
        if not user.image:
            user.image = "https://via.placeholder.com/150"

    def apple_signin(self, apple_credential: dict, app_name: str = "unknown") -> User:
        """
        Legacy compatibility method that maintains the same interface
        as the old apple_signin function.

        Args:
            apple_credential: Dictionary containing Apple Sign-In response data
            app_name: Name of the app for logging purposes

        Returns:
            User: The authenticated user (new or existing)
        """
        return self.authenticate_with_apple(apple_credential, app_name=app_name)


# Global instance for backward compatibility
_apple_auth_service = None


def get_apple_auth_service() -> AppleAuthService:
    """Get a global instance of the Apple Auth Service"""
    global _apple_auth_service
    if _apple_auth_service is None:
        _apple_auth_service = AppleAuthService()
    return _apple_auth_service


# Backward compatibility functions
def validate_apple_token_legacy(identity_token: str, bundle_id: str = None) -> dict:
    """
    Legacy function for backward compatibility.
    Use validate_apple_token() instead.
    """
    return validate_apple_token(identity_token, bundle_id)


def apple_signin(apple_credential: dict) -> User:
    """
    Legacy function for backward compatibility.
    Use AppleAuthService.authenticate_with_apple() instead.
    """
    return get_apple_auth_service().apple_signin(apple_credential, "legacy")
