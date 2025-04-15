import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    ROOT_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")
    ENV = os.environ.get("ENV", "dev").lower()

    ADMIN_EMAILS = ["lkleinbrodt@gmail.com"]
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

    SPEECH_APPLE_BUNDLE_ID = None  # Will be overridden in production
    SPEECH_DEVELOPMENT_MODE = True  # Will be False in production


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    FRONTEND_URL = "http://localhost:5173"
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(Config.ROOT_DIR, "app.db")
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://coyote-user:coyote-password@localhost:5432/coyote-db-dev"
    )

    AUTODRAFT_BUCKET = "autodraft-dev"

    SPEECH_APPLE_BUNDLE_ID = "com.development.speechcoach"
    SPEECH_DEVELOPMENT_MODE = True

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY_TESTING")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TESTING")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    FRONTEND_URL = "https://landonkleinbrodt.com"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    if SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://"
        )

    AUTODRAFT_BUCKET = "autodraft"

    SPEECH_APPLE_BUNDLE_ID = os.environ.get("SPEECH_APPLE_BUNDLE_ID")
    SPEECH_DEVELOPMENT_MODE = False

    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = os.path.join(os.getenv("TEMP", "/tmp"), "flask_cache")

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    FRONTEND_URL = "http://localhost:8000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    AUTODRAFT_BUCKET = "autodraft-test"

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY_TESTING")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TESTING")
