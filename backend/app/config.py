from pathlib import Path
import logging
from typing import Optional
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()
ROOT_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    ENV = os.environ.get("ENV", "dev").lower()

    if ENV == "dev":
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(ROOT_DIR, "app.db")
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://"
        )

    LIFTER_BUCKET = "coyote-lifter"
    JWT_SECRET_KEY = SECRET_KEY
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # This is for if we want errors to be emailed to us
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    CORS_HEADERS = "Content-Type"
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    REMEMBER_COOKIE_SECURE = True  # Same for "remember me" cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent client-side JS access to cookie
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=90)
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SAMESITE = None  ## Allow cross-origin requests to include the session cookie. Warning: has security implications

    TWENTY_QUESTIONS_OPENAI_API_KEY = os.environ.get("TWENTY_QUESTIONS_OPENAI_API_KEY")


def create_logger(
    name: str, level: str = "INFO", file: Optional[str] = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        if file:
            log_dir = Path(__file__).parent.parent / "data" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / file, "w")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
