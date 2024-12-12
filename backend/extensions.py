from flask import redirect, url_for, request, Blueprint
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate(render_as_batch=True)


def create_logger(name):
    # Create a logger instance
    logger = logging.getLogger(name)

    # Remove this comment to enable the level setting
    logger.setLevel(logging.INFO)

    # Check if handler already exists to prevent duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = create_logger("app")
