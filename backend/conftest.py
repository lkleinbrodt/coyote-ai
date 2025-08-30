import json
import logging
from datetime import datetime, timedelta
from flask import url_for
from flask.testing import FlaskClient
from flask_migrate import upgrade

import pytest
from backend.models import User, UserBalance
from backend.sidequest.models import SideQuestUser, SideQuest, QuestGenerationLog
from backend.extensions import db
from backend import create_app
from backend.tests.setup_db import init_test_db
from backend.config import TestingConfig


@pytest.fixture(scope="function", autouse=True)
def app():
    """Create and configure a new app instance for each test."""
    logging.getLogger("alembic").setLevel(logging.ERROR)

    app = create_app(TestingConfig)
    with app.app_context(), app.test_request_context():
        # Run migrations to create tables
        upgrade()
        db.create_all()

        # Initialize test data
        init_test_db(db)

        yield app

        # Cleanup after each test
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user for testing."""
    user = User(email="test@example.com", name="Test User", google_id="test_google_id")
    db.session.add(user)
    db.session.flush()

    # Create user balance
    balance = UserBalance(user_id=user.id)
    db.session.add(balance)
    db.session.commit()

    return user
