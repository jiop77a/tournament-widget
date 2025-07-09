"""
Test tournament widget functionality without OpenAI API key
"""

import pytest


@pytest.mark.unit
def test_openai_status_unavailable(client_no_openai):
    """Test that OpenAI status endpoint returns false when no API key is configured"""
    response = client_no_openai.get("/api/openai-status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["available"] is False


@pytest.mark.unit
def test_create_tournament_sufficient_prompts_no_openai(client_no_openai):
    """Test tournament creation with sufficient prompts when OpenAI is not available"""
    response = client_no_openai.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of France?",
            "custom_prompts": [
                "Tell me the capital of France",
                "What city is the capital of France?",
                "Which city serves as France's capital?",
                "What is France's capital city?",
            ],
            "total_prompts": 4,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["tournament_id"] is not None
    assert len(data["prompts"]) == 4


@pytest.mark.unit
def test_create_tournament_insufficient_prompts_no_openai(client_no_openai):
    """Test tournament creation with insufficient prompts when OpenAI is not available"""
    response = client_no_openai.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of France?",
            "custom_prompts": [
                "Tell me the capital of France",
                "What city is the capital of France?",
            ],
            "total_prompts": 4,
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "Not enough prompts provided" in data["error"]
    assert "You provided 2 prompts but need 4" in data["error"]
    assert "OpenAI API key" in data["error"]


@pytest.mark.unit
def test_test_prompt_no_openai(client_no_openai):
    """Test that prompt testing fails gracefully when OpenAI is not available"""
    response = client_no_openai.post(
        "/api/test-prompt",
        json={
            "prompt": "What is the capital of France?",
        },
    )
    assert response.status_code == 500
    data = response.get_json()
    assert "OpenAI API key not configured" in data["error"]


@pytest.mark.unit
def test_create_tournament_exact_prompts_no_openai(client_no_openai):
    """Test tournament creation with exact number of prompts needed"""
    response = client_no_openai.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Spain?",
            "custom_prompts": [
                "Tell me Spain's capital",
                "What city is Spain's capital?",
            ],
            "total_prompts": 2,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["tournament_id"] is not None
    assert len(data["prompts"]) == 2


@pytest.mark.unit
def test_create_tournament_more_prompts_than_needed_no_openai(client_no_openai):
    """Test tournament creation with more prompts than needed (should use only what's needed)"""
    response = client_no_openai.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Italy?",
            "custom_prompts": [
                "Tell me Italy's capital",
                "What city is Italy's capital?",
                "Which city serves as Italy's capital?",
                "What is Italy's capital city?",
                "Can you tell me Italy's capital?",
                "I need to know Italy's capital",
            ],
            "total_prompts": 4,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["tournament_id"] is not None
    assert len(data["prompts"]) == 4  # Should only use 4 out of 6 provided


@pytest.mark.unit
def test_create_tournament_duplicate_prompts_no_openai(client_no_openai):
    """Test that duplicate prompts are removed even without OpenAI"""
    response = client_no_openai.post(
        "/api/tournament",
        json={
            "input_question": "What is the capital of Germany?",
            "custom_prompts": [
                "Tell me Germany's capital",
                "What city is Germany's capital?",
                "Tell me Germany's capital",  # Duplicate
                "TELL ME GERMANY'S CAPITAL",  # Case-insensitive duplicate
                "Which city serves as Germany's capital?",
                "What is Germany's capital city?",
            ],
            "total_prompts": 4,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["tournament_id"] is not None
    assert len(data["prompts"]) == 4

    # Verify all prompts are unique
    prompt_texts = data["prompts"]  # prompts is already a list of strings
    assert len(prompt_texts) == len(set(prompt_texts))
