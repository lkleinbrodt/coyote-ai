import logging

from flask_migrate import upgrade

import pytest
from backend.models import User, UserBalance
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
        # Create tables directly instead of running migrations
        upgrade()
        db.create_all()
        init_test_db(db)
        yield app
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


# we use pytest-docker package
# it auto runs docker compose up and down for us
# creating the test db.


@pytest.fixture(scope="session")
def docker_compose_file():
    return TestingConfig.BACKEND_DIR / "docker-compose.test.yml"


@pytest.fixture(scope="session")
def docker_compose_project_name():
    return "pytest_sidequest"


@pytest.fixture(scope="session", autouse=True)
def wait_for_postgres(docker_services):
    """
    Ensure the PostgreSQL service is ready before tests start.
    """

    def is_postgres_ready():
        import psycopg2

        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5434,
                database="sidequest_test",
                user="sidequest_user",
                password="sidequest_password",
            )
            conn.close()
            return True
        except psycopg2.OperationalError:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=is_postgres_ready
    )
