from unittest.mock import MagicMock, patch

import pytest
from models import InputQuestion, Match, Prompt, Tournament


@pytest.mark.unit
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


@pytest.mark.unit
def test_get_tournament(client, sample_data):
    # Test GET /tournament/{id}/status route (updated API)
    tournament = sample_data["tournament"]
    response = client.get(f"/api/tournament/{tournament.id}/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "tournament_id" in data
    assert "status" in data
    assert "rounds" in data
    assert data["input_question"] == tournament.input_question.question_text


def test_create_match(client):
    # Test tournament bracket creation (matches are created automatically)
    # Create a fresh tournament without pre-existing matches
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the best programming language?",
            "custom_prompts": [
                "Which programming language is best?",
                "What language should I learn?",
                "Tell me the top programming language",
                "What is your favorite programming language?",
            ],
            "total_prompts": 4,
        },
    )
    assert response.status_code == 201
    tournament_data = response.get_json()
    tournament_id = tournament_data["tournament_id"]

    # Start the tournament bracket to create matches automatically
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "round_1_matches" in data
    assert data["total_matches"] >= 1  # Should have at least one match

    # Verify matches were created by checking tournament status
    response = client.get(f"/api/tournament/{tournament_id}/status")
    assert response.status_code == 200
    status_data = response.get_json()
    assert "rounds" in status_data
    assert "1" in status_data["rounds"]  # Should have round 1


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


def test_start_bracket_tournament_not_found(client):
    # Test POST /tournament/{id}/start-bracket with non-existent tournament - should return 404
    response = client.post("/api/tournament/99999/start-bracket")
    assert response.status_code == 404


def test_start_bracket_already_started(client):
    # Test POST /tournament/{id}/start-bracket when bracket already started - should return 400
    # Create a fresh tournament without pre-existing matches
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the best sport?",
            "custom_prompts": [
                "Which sport is best?",
                "What sport should I play?",
            ],
            "total_prompts": 2,
        },
    )
    assert response.status_code == 201
    tournament_data = response.get_json()
    tournament_id = tournament_data["tournament_id"]

    # Start bracket first time - should succeed
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    assert response.status_code == 201

    # Try to start bracket again - should fail
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    assert response.status_code == 400
    data = response.get_json()
    assert "already started" in data["error"].lower()


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


def test_create_tournament_with_odd_total_prompts_success(client):
    # Test POST /tournament with odd total_prompts - should succeed (bye logic handles odd numbers)
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Germany?",
            "total_prompts": 5,  # Odd number - should work with bye logic
            "custom_prompts": [
                "Tell me Germany's capital",
                "What city is Germany's capital?",
            ],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "tournament_id" in data
    assert len(data["prompts"]) == 5  # Should have exactly 5 prompts


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
@patch("services.openai_service.openai_service.client.chat.completions.create")
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


@patch("services.openai_service.openai_service.client.chat.completions.create")
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


@patch("services.openai_service.openai_service.client.chat.completions.create")
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
