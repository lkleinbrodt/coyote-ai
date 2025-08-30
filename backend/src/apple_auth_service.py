import base64
from flask import current_app
import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from openai import OpenAI
from sqlalchemy.orm import Session

from backend.extensions import create_logger
from backend.models import User

logger = create_logger(__name__)

# Apple Sign-In constants
# CRITICAL: Bundle ID must match your iOS app's bundle identifier
# This is used to validate Apple JWT tokens and prevent token reuse
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"


def jwk_to_rsa_key(jwk_key):
    """
    Convert a JWK (JSON Web Key) to an RSA public key using the cryptography library.
    This is the pythonic way recommended for PyJWT.
    """
    import base64

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


def get_apple_public_keys() -> dict:
    """
    Fetches Apple's public keys for verifying identity tokens.
    """
    try:
        with httpx.Client() as client:
            response = client.get(APPLE_KEYS_URL)
            response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch Apple public keys: {e}")
        raise Exception(f"Failed to fetch Apple public keys: {e}")


def validate_apple_token(identity_token: str, client_id: str) -> dict:
    """
    Validates an Apple Sign-In identity token.

    :param identity_token: The JWT from the client.
    :param client_id: Your app's bundle identifier (the audience).
    :return: The decoded claims dictionary if valid.
    :raises: Exception if the token is invalid.
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
        apple_keys = get_apple_public_keys().get("keys", [])
        matching_key = next((key for key in apple_keys if key["kid"] == kid), None)
        if not matching_key:
            raise Exception("Could not find a matching public key.")

        # Convert JWK to RSA public key using cryptography library
        public_key = jwk_to_rsa_key(matching_key)

        # Decode and validate the token
        claims = jwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=APPLE_ISSUER,
        )
        return claims

    except jwt.ExpiredSignatureError:
        raise Exception("Apple token has expired.")
    except jwt.InvalidAudienceError:
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
    """Service for handling Apple Sign-In authentication"""

    def __init__(self, session: Session):
        self.session = session

    def authenticate_with_apple(
        self, identity_token: str, full_name: dict = None
    ) -> User:
        """
        Authenticate a user with Apple Sign-In.

        Args:
            identity_token: The Apple identity token from the client
            full_name: Optional full name from Apple (only on first sign-up)

        Returns:
            User: The authenticated user (new or existing)
        """
        try:
            # Validate the Apple token
            claims = validate_apple_token(
                identity_token, "com.landokleinbrodt.sidequest"
            )

            # Extract verified claims from the token
            apple_id = claims["sub"]
            email = claims.get("email")
            email_verified = claims.get("email_verified", False)

            # Check if user already exists
            user = User.query.filter_by(apple_id=apple_id).first()
            is_new_user = False

            if not user:
                # Create new user
                logger.info(f"Creating new user with Apple ID {apple_id}")
                is_new_user = True

                user = User(
                    apple_id=apple_id,
                    name=(
                        full_name.get("givenName", "")
                        + " "
                        + full_name.get("familyName", "")
                        if full_name
                        else ""
                    ),
                    email=email,
                    image="https://via.placeholder.com/150",  # Default avatar
                )

                # Check if this should be an admin user
                # grab ADMIN_EMAILS from config
                admin_emails = current_app.config["ADMIN_EMAILS"]
                if email and email in admin_emails:
                    user.role = "admin"

                self.session.add(user)
                self.session.commit()

            else:
                logger.info(f"User with Apple ID {apple_id} already exists")
                # Update user info if Apple provided new information
                if full_name:
                    given_name = full_name.get("givenName")
                    family_name = full_name.get("familyName")
                    if given_name or family_name:
                        user.name = f"{given_name or ''} {family_name or ''}".strip()

                # Only update email if it's different, not None, and not empty
                if email and email.strip() and email != user.email:
                    logger.info(f"Updating user email from {user.email} to {email}")
                    user.email = email

                self.session.commit()

            return user

        except Exception as e:
            logger.error(f"Apple authentication error: {str(e)}")
            raise e
