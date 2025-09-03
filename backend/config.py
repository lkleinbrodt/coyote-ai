import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    BACKEND_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")
    ENV = os.environ.get("ENV", "dev").lower()

    # API Keys
    PING_DB_API_KEY = os.environ.get("PING_DB_API_KEY")
    if not PING_DB_API_KEY:
        raise ValueError("PING_DB_API_KEY is not set")

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")

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

    # JWT Configuration
    # CRITICAL: This hybrid setup supports both web (cookies) and mobile (headers) clients
    # Web apps use short-lived tokens with refresh, mobile apps use long-lived tokens
    # DO NOT change JWT_TOKEN_LOCATION without understanding the implications
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived access token for web
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Long-lived refresh token for web

    # Mobile tokens can override this with custom expiration in the route

    # Tell Flask-JWT-Extended to look for JWTs in headers and cookies
    # Headers are for mobile apps, cookies are for web apps
    JWT_TOKEN_LOCATION = ["headers", "cookies"]

    # Only allow JWT cookies to be sent over HTTPS
    JWT_COOKIE_SECURE = ENV.lower() == "production"  # True in production, False in dev

    # Set SameSite for CSRF protection
    JWT_COOKIE_SAMESITE = "Lax"  # "Lax" or "Strict". "Lax" is often a good balance

    # Configure which cookie(s) to look for JWTs in
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"
    JWT_COOKIE_PATH = "/api/auth"
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    # CSRF protection for cookie-based JWTs
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True

    # Header configuration for mobile apps
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

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

    # Character Explorer Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
    EMBEDDING_DIMENSION = 384
    DIALOGUE_EXTRACTION_MODEL = "anthropic/claude-3-haiku"

    # SideQuest Config
    QUEST_GENERATION_MODEL = "mistralai/mistral-large"
    QUEST_METADATA_EXTRACTION_MODEL = "meta-llama/llama-3.3-70b-instruct"


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    FRONTEND_URL = "http://localhost:5173"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://coyote-user:coyote-password@localhost:5432/coyote-db-dev"
    )

    AUTODRAFT_BUCKET = "autodraft-dev"

    SPEECH_APPLE_BUNDLE_ID = "com.development.speechcoach"
    SPEECH_DEVELOPMENT_MODE = True

    JWT_COOKIE_SECURE = False  # Allow HTTP for localhost development
    JWT_COOKIE_CSRF_PROTECT = False  # Simplify development
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

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

    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True

    SPEECH_APPLE_BUNDLE_ID = os.environ.get("SPEECH_APPLE_BUNDLE_ID")
    SPEECH_DEVELOPMENT_MODE = False

    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = os.path.join(os.getenv("TEMP", "/tmp"), "flask_cache")

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")


class TestingConfig(Config):
    ENV = "testing"
    TESTING = True
    DEBUG = True
    FRONTEND_URL = "http://localhost:8000"

    # PostgreSQL test database
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://sidequest_user:sidequest_password@localhost:5434/sidequest_test"
    )

    AUTODRAFT_BUCKET = "autodraft-test"

    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY_TESTING")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TESTING")

    SPEECH_DEVELOPMENT_MODE = True
    SPEECH_APPLE_BUNDLE_ID = "com.test.speechcoach"

    # Fixed secret keys for testing
    SECRET_KEY = "testing-secret-key"
    JWT_SECRET_KEY = "testing-secret-key"
    OPENAI_API_KEY = "test_openai_key"
    PING_DB_API_KEY = "test_ping_db_key"

    # Mail configuration for tests
    MAIL_SERVER = "localhost"
    MAIL_PORT = 587
    MAIL_USERNAME = "test@example.com"
    MAIL_PASSWORD = "test_password"
    ADMIN_EMAILS = ["admin@example.com"]
