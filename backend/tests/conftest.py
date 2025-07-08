"""
Pytest configuration and shared fixtures for test isolation
"""

import os
import tempfile

import pytest
from app import app, db
from dotenv import load_dotenv
from models import InputQuestion, Match, Prompt, Tournament

# Load environment variables
load_dotenv()

# Get test port from environment
TEST_PORT = int(os.getenv("FLASK_TEST_PORT", 5002))


@pytest.fixture(scope="function")
def test_app():
    """
    Create a test Flask application with isolated database
    This ensures each test gets a fresh database
    """
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Configure app for testing
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
            "SERVER_NAME": f"localhost:{TEST_PORT}",  # Use test port from config
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(test_app):
    """
    Create a test client using the test app
    """
    return test_app.test_client()


@pytest.fixture(scope="function")
def app_context(test_app):
    """
    Create an application context for tests that need it
    """
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="function")
def sample_data(app_context):
    """
    Create sample data for tests that need it
    Returns a dictionary with created objects
    """
    # Create test input question
    input_question = InputQuestion(question_text="What is the capital of France?")
    db.session.add(input_question)
    db.session.commit()

    # Create sample prompts
    prompt1 = Prompt(
        input_question_id=input_question.id,
        prompt_text="Tell me about France's capital",
    )
    prompt2 = Prompt(
        input_question_id=input_question.id,
        prompt_text="What city is France's capital?",
    )
    db.session.add(prompt1)
    db.session.add(prompt2)
    db.session.commit()

    # Create tournament
    tournament = Tournament(input_question_id=input_question.id)
    db.session.add(tournament)
    db.session.commit()

    # Create sample match
    match = Match(
        tournament_id=tournament.id,
        prompt_1_id=prompt1.id,
        prompt_2_id=prompt2.id,
        round_number=1,
    )
    db.session.add(match)
    db.session.commit()

    return {
        "input_question": input_question,
        "prompt1": prompt1,
        "prompt2": prompt2,
        "tournament": tournament,
        "match": match,
    }


@pytest.fixture(autouse=True)
def prevent_live_server_tests():
    """
    Automatically prevent tests from accidentally connecting to live servers
    """
    # Set environment variable to indicate we're in test mode
    os.environ["TESTING"] = "true"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_RUN_PORT"] = str(TEST_PORT)  # Use test port from config

    yield

    # Clean up
    os.environ.pop("TESTING", None)
    os.environ.pop("FLASK_ENV", None)
    os.environ.pop("FLASK_RUN_PORT", None)


def pytest_configure(config):
    """
    Configure pytest with custom settings
    """
    # Add custom markers
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line(
        "markers", "live_server: mark test as requiring live server (use with caution)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers and warnings
    """
    for item in items:
        # Add unit marker to tests that don't have integration or live_server markers
        if not any(
            marker.name in ["integration", "live_server"]
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)

        # Add warning for live_server tests
        if item.get_closest_marker("live_server"):
            item.add_marker(
                pytest.mark.filterwarnings(
                    "ignore::pytest.PytestUnraisableExceptionWarning"
                )
            )


def pytest_runtest_setup(item):
    """
    Setup for each test run - add safety checks
    """
    # Check if test is marked as live_server and warn
    if item.get_closest_marker("live_server"):
        print(
            f"\n⚠️  WARNING: Test '{item.name}' is marked as 'live_server' - ensure no live server is running!"
        )
