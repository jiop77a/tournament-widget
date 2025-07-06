import pytest
from app import app, db
from models import InputQuestion, Match, Prompt, Tournament


@pytest.fixture
def client():
    # Create a temporary database for testing
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create test data
            input_question = InputQuestion(
                question_text="What is the capital of France?"
            )
            db.session.add(input_question)
            db.session.commit()

            # Create some sample prompts
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

            tournament = Tournament(input_question_id=input_question.id)
            db.session.add(tournament)
            db.session.commit()

            # Create a sample match
            match = Match(
                tournament_id=tournament.id,
                prompt_1_id=prompt1.id,
                prompt_2_id=prompt2.id,
                round_number=1,
            )
            db.session.add(match)
            db.session.commit()

            yield client

            # Clean up more carefully
            db.session.remove()
            db.drop_all()


def test_create_tournament(client):
    # Test POST /tournament route
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Spain?",
            "custom_prompts": [
                "Can you tell me the capital of Spain?",
                "Which city is the capital of Spain?",
            ],
        },
    )
    assert response.status_code == 201  # Expecting a successful response
    data = response.get_json()
    assert "tournament_id" in data
    assert data["input_question"] == "What is the capital of Spain?"


def test_get_tournament(client):
    # Test GET /tournament/{id} route
    tournament = Tournament.query.first()
    response = client.get(f"/api/tournament/{tournament.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "tournament_id" in data
    assert data["input_question"] == tournament.input_question.question_text


def test_create_match(client):
    # Test POST /match route
    tournament = Tournament.query.first()
    prompt_1 = Prompt.query.first()
    prompt_2 = Prompt.query.first()
    response = client.post(
        "/api/match",
        json={
            "tournament_id": tournament.id,
            "prompt_1_id": prompt_1.id,
            "prompt_2_id": prompt_2.id,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "match_id" in data
    assert (
        data["round_number"] == 2
    )  # Should be round 2 since we already have a match in round 1
    assert data["prompt_1"] == prompt_1.prompt_text
    assert data["prompt_2"] == prompt_2.prompt_text


def test_store_result(client):
    # Test POST /result route
    match = Match.query.first()
    prompt_1 = Prompt.query.first()
    response = client.post(
        "/api/result", json={"match_id": match.id, "winner_id": prompt_1.id}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Result stored successfully!"


# Error handling tests
def test_create_tournament_missing_input_question(client):
    # Test POST /tournament with missing input_question - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "custom_prompts": [
                "Can you tell me the capital of Spain?",
                "Which city is the capital of Spain?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_empty_input_question(client):
    # Test POST /tournament with empty input_question - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "",
            "custom_prompts": [
                "Can you tell me the capital of Spain?",
                "Which city is the capital of Spain?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_whitespace_input_question(client):
    # Test POST /tournament with whitespace-only input_question - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "   ",
            "custom_prompts": [
                "Can you tell me the capital of Spain?",
                "Which city is the capital of Spain?",
            ],
        },
    )
    assert response.status_code == 400


def test_get_tournament_not_found(client):
    # Test GET /tournament/{id} with non-existent tournament - should return 404
    response = client.get("/api/tournament/99999")
    assert response.status_code == 404


def test_create_match_tournament_not_found(client):
    # Test POST /match with non-existent tournament - should return 404
    prompt_1 = Prompt.query.first()
    prompt_2 = Prompt.query.first()
    response = client.post(
        "/api/match",
        json={
            "tournament_id": 99999,
            "prompt_1_id": prompt_1.id,
            "prompt_2_id": prompt_2.id,
        },
    )
    assert response.status_code == 404


def test_create_match_prompt_not_found(client):
    # Test POST /match with non-existent prompt - should return 404
    tournament = Tournament.query.first()
    response = client.post(
        "/api/match",
        json={
            "tournament_id": tournament.id,
            "prompt_1_id": 99999,
            "prompt_2_id": 99999,
        },
    )
    assert response.status_code == 404


def test_store_result_match_not_found(client):
    # Test POST /result with non-existent match - should return 404
    prompt_1 = Prompt.query.first()
    response = client.post(
        "/api/result", json={"match_id": 99999, "winner_id": prompt_1.id}
    )
    assert response.status_code == 404


def test_store_result_winner_not_found(client):
    # Test POST /result with non-existent winner - should return 404
    match = Match.query.first()
    response = client.post(
        "/api/result", json={"match_id": match.id, "winner_id": 99999}
    )
    assert response.status_code == 404
