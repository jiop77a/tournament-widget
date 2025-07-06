from unittest.mock import MagicMock, patch

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


# Total prompts validation tests
def test_create_tournament_with_valid_total_prompts(client):
    # Test POST /tournament with valid even total_prompts
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Italy?",
            "total_prompts": 4,
            "custom_prompts": [
                "Tell me Italy's capital",
                "What city is Italy's capital?",
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["prompts"]) == 4  # Should have exactly 4 prompts


def test_create_tournament_with_odd_total_prompts_error(client):
    # Test POST /tournament with odd total_prompts - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Germany?",
            "total_prompts": 5,  # Odd number
            "custom_prompts": [
                "Tell me Germany's capital",
                "What city is Germany's capital?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_with_negative_total_prompts_error(client):
    # Test POST /tournament with negative total_prompts - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Japan?",
            "total_prompts": -4,  # Negative number
            "custom_prompts": [
                "Tell me Japan's capital",
                "What city is Japan's capital?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_with_zero_total_prompts_error(client):
    # Test POST /tournament with zero total_prompts - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Brazil?",
            "total_prompts": 0,  # Zero
            "custom_prompts": [
                "Tell me Brazil's capital",
                "What city is Brazil's capital?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_with_string_total_prompts_error(client):
    # Test POST /tournament with string total_prompts - should return 400
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Canada?",
            "total_prompts": "invalid",  # String instead of int
            "custom_prompts": [
                "Tell me Canada's capital",
                "What city is Canada's capital?",
            ],
        },
    )
    assert response.status_code == 400


def test_create_tournament_trim_excess_prompts(client):
    # Test POST /tournament with more prompts than total_prompts - should trim
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Australia?",
            "total_prompts": 4,
            "custom_prompts": [
                "Tell me Australia's capital",
                "What city is Australia's capital?",
                "Which city is the capital of Australia?",
                "What is Australia's capital city?",
                "Can you name Australia's capital?",  # This should be trimmed
                "I need to know Australia's capital",  # This should be trimmed
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["prompts"]) == 4  # Should have exactly 4 prompts
    # Should keep the first 4 prompts
    assert "Tell me Australia's capital" in data["prompts"]
    assert "Can you name Australia's capital?" not in data["prompts"]


def test_create_tournament_removes_duplicate_prompts(client):
    # Test POST /tournament with duplicate custom prompts - should remove duplicates
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Mexico?",
            "total_prompts": 4,
            "custom_prompts": [
                "Tell me Mexico's capital",
                "What city is Mexico's capital?",
                "Tell me Mexico's capital",  # Exact duplicate
                "TELL ME MEXICO'S CAPITAL",  # Case-insensitive duplicate
                "  Tell me Mexico's capital  ",  # Whitespace duplicate
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["prompts"]) == 4  # Should have exactly 4 prompts
    # Should have unique prompts (2 unique custom + 2 generated)
    prompts_lower = [p.lower().strip() for p in data["prompts"]]
    assert len(set(prompts_lower)) == 4  # All should be unique


def test_create_tournament_all_prompts_unique(client):
    # Test that all prompts in the final tournament are unique
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of India?",
            "total_prompts": 6,
            "custom_prompts": [
                "Tell me India's capital",
                "What city is India's capital?",
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["prompts"]) == 6

    # Check that all prompts are unique (case-insensitive)
    prompts_normalized = [p.lower().strip() for p in data["prompts"]]
    assert len(prompts_normalized) == len(set(prompts_normalized))  # No duplicates


# Test prompt testing route
@patch("tournament_routes.client.chat.completions.create")
def test_test_prompt_success(mock_openai, client):
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Paris is the capital of France."
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 8
    mock_response.usage.total_tokens = 18
    mock_openai.return_value = mock_response

    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of France?",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["prompt"] == "What is the capital of France?"
    assert data["response"] == "Paris is the capital of France."
    assert data["model"] == "gpt-3.5-turbo"  # Default model
    assert data["max_tokens"] == 150  # Default max_tokens
    assert data["temperature"] == 0.7  # Default temperature
    assert "usage" in data
    assert data["usage"]["total_tokens"] == 18


@patch("tournament_routes.client.chat.completions.create")
def test_test_prompt_with_custom_parameters(mock_openai, client):
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "The capital of Spain is Madrid."
    mock_response.usage.prompt_tokens = 12
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 22
    mock_openai.return_value = mock_response

    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "Tell me about Spain's capital city",
            "model": "gpt-4",
            "max_tokens": 200,
            "temperature": 0.5,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["prompt"] == "Tell me about Spain's capital city"
    assert data["response"] == "The capital of Spain is Madrid."
    assert data["model"] == "gpt-4"
    assert data["max_tokens"] == 200
    assert data["temperature"] == 0.5


def test_test_prompt_missing_prompt(client):
    # Test POST /test-prompt with missing prompt - should return 400
    response = client.post(
        "/api/test-prompt",
        json={
            "model": "gpt-3.5-turbo",
        },
    )
    assert response.status_code == 400


def test_test_prompt_empty_prompt(client):
    # Test POST /test-prompt with empty prompt - should return 400
    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "",
        },
    )
    assert response.status_code == 400


def test_test_prompt_invalid_model(client):
    # Test POST /test-prompt with invalid model - should return 400
    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of Italy?",
            "model": "invalid-model",
        },
    )
    assert response.status_code == 400


def test_test_prompt_invalid_max_tokens(client):
    # Test POST /test-prompt with invalid max_tokens - should return 400
    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of Germany?",
            "max_tokens": 5000,  # Too high
        },
    )
    assert response.status_code == 400


def test_test_prompt_invalid_temperature(client):
    # Test POST /test-prompt with invalid temperature - should return 400
    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of Japan?",
            "temperature": 3.0,  # Too high
        },
    )
    assert response.status_code == 400


@patch("tournament_routes.client.chat.completions.create")
def test_test_prompt_openai_error(mock_openai, client):
    # Mock OpenAI to raise an exception
    mock_openai.side_effect = Exception("API Error")

    response = client.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of Brazil?",
        },
    )

    assert response.status_code == 500
