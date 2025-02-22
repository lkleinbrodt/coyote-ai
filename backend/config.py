from pathlib import Path
import logging
from typing import Optional
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()


class Config:
    ROOT_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")
    ENV = os.environ.get("ENV", "dev").lower()

    ADMIN_EMAILS = ["landon@coyote-ai.com"]
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    CORS_HEADERS = "Content-Type"

    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    REMEMBER_COOKIE_SECURE = True  # Same for "remember me" cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent client-side JS access to cookie

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=90)

    LIFTER_BUCKET = "coyote-lifter"

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    OAUTH_CREDENTIALS = {
        "google": {
            "id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        }
    }

    AUTODRAFT_BUCKET = "autodraft-dev"

    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    BASE_URL = "http://localhost:5173"
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(Config.ROOT_DIR, "app.db")
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://coyote-user:coyote-password@localhost:5432/coyote-db-dev"
    )

    AUTODRAFT_BUCKET = "autodraft-dev"


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    BASE_URL = "https://www.coyote-ai.com"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    AUTODRAFT_BUCKET = "autodraft"


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    BASE_URL = "http://localhost:8000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    AUTODRAFT_BUCKET = "autodraft-test"
