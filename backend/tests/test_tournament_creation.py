"""
Test script to verify tournament creation with AI prompt generation
"""

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.integration
def test_tournament_creation_with_few_prompts(client):
    """Test tournament creation when fewer than 8 prompts are provided"""

    # Mock the OpenAI API response
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = """What is France's capital city?
Could you tell me the capital of France?
Which city serves as France's capital?
I'd like to know France's capital city"""

    with patch(
        "services.openai_service.openai_service.client.chat.completions.create",
        return_value=mock_response,
    ):
        # Test data with only 2 custom prompts (should trigger AI generation)
        test_data = {
            "input_question": "What is the capital of France?",
            "custom_prompts": [
                "Tell me the capital of France",
                "What city is the capital of France?",
            ],
        }

        # Make the request
        response = client.post(
            "/api/tournament",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()

        # Should have 8 prompts total (2 custom + 4 AI generated + 2 more to reach 8)
        assert (
            len(data["prompts"]) >= 6
        )  # At least the original prompts + some generated ones

        print("✅ Tournament creation with AI prompt generation works!")


@pytest.mark.integration
def test_tournament_creation_fallback(client):
    """Test tournament creation when AI generation fails (fallback mode)"""

    # Mock the OpenAI API to raise an exception
    with patch(
        "services.openai_service.openai_service.client.chat.completions.create",
        side_effect=Exception("API Error"),
    ):
        # Test data with only 2 prompts (should trigger fallback)
        test_data = {
            "input_question": "What is the capital of France?",
            "custom_prompts": [
                "Tell me the capital of France",
                "What city is the capital of France?",
            ],
        }

        # Make the request
        response = client.post(
            "/api/tournament",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()

        # Should have at least the original prompts + fallback prompts
        assert len(data["prompts"]) >= 2

        print("✅ Tournament creation with fallback works!")


@pytest.mark.integration
def test_tournament_creation_no_ai_needed(client):
    """Test tournament creation when enough prompts are provided (no AI generation needed)"""

    # Test data with exactly 8 prompts (should not trigger AI generation)
    test_data = {
        "input_question": "What is the capital of France?",
        "custom_prompts": [
            "Tell me the capital of France",
            "What city is the capital of France?",
            "Which city is France's capital?",
            "What is France's capital city?",
            "Can you name France's capital?",
            "I need to know France's capital",
            "Please tell me France's capital",
            "What's the capital city of France?",
        ],
    }

    # Make the request
    response = client.post(
        "/api/tournament",
        data=json.dumps(test_data),
        content_type="application/json",
    )

    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.get_json()}")

    # Verify the response
    assert response.status_code == 201
    data = response.get_json()

    # Should have exactly 8 prompts (no AI generation needed)
    assert len(data["prompts"]) == 8

    print("✅ Tournament creation without AI generation works!")
