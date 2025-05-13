import json
import os
import socket

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import build_http

from backend.extensions import create_logger

logger = create_logger(__name__)
email_bp = Blueprint("email", __name__, url_prefix="/email")

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Number of emails to fetch
EMAIL_LIMIT = 200

# Timeout settings (in seconds)
SOCKET_TIMEOUT = 120  # Increase from default 60 seconds

# Set socket default timeout
socket.setdefaulttimeout(SOCKET_TIMEOUT)


def authenticate_gmail():
    """
    Authenticate with Gmail API and return service

    Note: You need to create a credentials.json file following these steps:
    1. Go to Google Cloud Console: https://console.cloud.google.com/
    2. Create a project and enable Gmail API
    3. Create OAuth 2.0 credentials (Web application type)
    4. Download the JSON file and rename it to credentials.json
    5. Place it in the location specified by current_app.config.get("INSTANCE_PATH")
       which defaults to the Flask instance folder

    For detailed instructions, see gmail_setup_instructions.md
    """
    creds = None
    token_path = os.path.join(current_app.config.get("INSTANCE_PATH", ""), "token.json")
    credentials_path = os.path.join(
        current_app.config.get("INSTANCE_PATH", ""), "credentials.json"
    )

    # For development, if INSTANCE_PATH isn't set, check project root
    if not os.path.exists(credentials_path):
        alt_credentials_path = os.path.join(os.getcwd(), "credentials.json")
        if os.path.exists(alt_credentials_path):
            credentials_path = alt_credentials_path
            # Use same directory for token
            token_path = os.path.join(os.getcwd(), "token.json")
            logger.info(f"Using credentials from project root: {credentials_path}")

    # Check if token.json exists (saved credentials)
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(open(token_path).read()), SCOPES
            )
        except Exception as e:
            logger.error(f"Error loading token.json: {str(e)}", exc_info=True)

    # If credentials don't exist or are invalid, go through auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {str(e)}", exc_info=True)
                creds = None

        # If still no valid creds, need to go through auth flow
        if not creds:
            try:
                if not os.path.exists(credentials_path):
                    error_msg = f"credentials.json not found at {credentials_path}. See gmail_setup_instructions.md for setup guide."
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                # Use a consistent port (8080) so it can be added to Google's authorized redirects
                logger.info(
                    "Starting Gmail authorization flow with redirect to localhost:8080"
                )
                try:
                    creds = flow.run_local_server(port=8080)
                except OSError as e:
                    # If port 8080 is not available, try an alternative port
                    logger.warning(
                        f"Port 8080 not available, trying port 8090: {str(e)}"
                    )
                    creds = flow.run_local_server(port=8090)

                # Save the credentials for next run
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Error in authentication flow: {str(e)}", exc_info=True)
                raise

    # Build and return the Gmail service
    try:
        # Create service with increased timeout
        service = build("gmail", "v1", credentials=creds)
        # Log the timeout setting
        logger.info(f"Gmail API service created with socket timeout: {SOCKET_TIMEOUT}s")
        return service
    except Exception as e:
        logger.error(f"Error building Gmail service: {str(e)}", exc_info=True)
        raise


def get_emails(service, limit=EMAIL_LIMIT):
    """Get list of recent emails"""
    try:
        # Get list of messages
        results = (
            service.users().messages().list(userId="me", maxResults=limit).execute()
        )
        messages = results.get("messages", [])

        if not messages:
            logger.info("No messages found.")
            return []

        # Process each message to get details
        emails = []

        # Process in smaller batches to reduce timeout risk
        batch_size = 10
        total_messages = len(messages)
        logger.info(f"Processing {total_messages} messages in batches of {batch_size}")

        for i in range(0, total_messages, batch_size):
            batch = messages[i : i + batch_size]
            logger.info(
                f"Processing batch {(i//batch_size)+1}/{(total_messages//batch_size)+1} ({len(batch)} messages)"
            )

            for message in batch:
                try:
                    msg = (
                        service.users()
                        .messages()
                        .get(userId="me", id=message["id"])
                        .execute()
                    )

                    # Extract headers
                    headers = msg["payload"]["headers"]
                    subject = next(
                        (h["value"] for h in headers if h["name"].lower() == "subject"),
                        "(No subject)",
                    )
                    sender = next(
                        (h["value"] for h in headers if h["name"].lower() == "from"),
                        "(No sender)",
                    )

                    # Create email object
                    email = {
                        "id": msg["id"],
                        "sender": sender,
                        "subject": subject,
                        "snippet": msg.get("snippet", ""),
                        "is_unread": "UNREAD" in msg.get("labelIds", []),
                    }
                    emails.append(email)
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {str(e)}")
                    # Continue with next message instead of failing the entire batch
                    continue

        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
        raise


def delete_emails(service, email_ids):
    """Delete emails by ID"""
    try:
        for email_id in email_ids:
            service.users().messages().trash(userId="me", id=email_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting emails: {str(e)}", exc_info=True)
        raise


@email_bp.route("/fetch", methods=["GET"])
@jwt_required()
def fetch_emails():
    """Fetch recent emails from connected Gmail account"""
    try:
        # Get Gmail service
        service = authenticate_gmail()

        # Fetch emails
        emails = get_emails(service)

        return jsonify({"success": True, "emails": emails}), 200
    except HttpError as e:
        error_message = f"Gmail API error: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"success": False, "error": {"message": error_message}}), 503
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "error": {"message": "Failed to fetch emails"}}),
            500,
        )


@email_bp.route("/delete", methods=["POST"])
@jwt_required()
def delete_emails_route():
    """Delete emails by ID"""
    try:
        # Get and validate request data
        data = request.get_json()
        if not data or not isinstance(data.get("email_ids"), list):
            logger.warning("Invalid request data for email deletion")
            return (
                jsonify(
                    {"success": False, "error": {"message": "Invalid request data"}}
                ),
                400,
            )

        email_ids = data.get("email_ids")
        if not email_ids:
            return jsonify({"success": True, "message": "No emails to delete"}), 200

        logger.info(f"Email deletion requested for {len(email_ids)} emails")

        # Get Gmail service
        service = authenticate_gmail()

        # Delete emails
        delete_emails(service, email_ids)

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Successfully deleted {len(email_ids)} emails",
                }
            ),
            200,
        )
    except HttpError as e:
        error_message = f"Gmail API error: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"success": False, "error": {"message": error_message}}), 503
    except Exception as e:
        logger.error(f"Error deleting emails: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "error": {"message": "Failed to delete emails"}}
            ),
            500,
        )
