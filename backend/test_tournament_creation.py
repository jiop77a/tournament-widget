"""
Test script to verify tournament creation with AI prompt generation
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import InputQuestion, Prompt, Tournament


def test_tournament_creation_with_few_prompts():
    """Test tournament creation when fewer than 8 prompts are provided"""

    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()

            # Mock the OpenAI API response
            mock_response = MagicMock()
            mock_response.choices[
                0
            ].message.content = """What is France's capital city?
Could you tell me the capital of France?
Which city serves as France's capital?
I'd like to know France's capital city"""

            with patch(
                "tournament_routes.client.chat.completions.create",
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

                # Clean up
                db.drop_all()


def test_tournament_creation_fallback():
    """Test tournament creation when AI generation fails (fallback mode)"""

    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()

            # Mock the OpenAI API to raise an exception
            with patch(
                "tournament_routes.client.chat.completions.create",
                side_effect=Exception("API Error"),
            ):
                # Test data with only 2 custom prompts
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

                print(f"Fallback response status: {response.status_code}")
                print(f"Fallback response data: {response.get_json()}")

                # Verify the response
                assert response.status_code == 201
                data = response.get_json()

                # Should have 8 prompts total using fallback generation
                assert len(data["prompts"]) == 8

                print("✅ Tournament creation with fallback prompt generation works!")

                # Clean up
                db.drop_all()


def test_tournament_creation_with_enough_prompts():
    """Test tournament creation when 8 or more prompts are already provided"""

    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()

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

            print(f"Full prompts response status: {response.status_code}")
            print(f"Full prompts response data: {response.get_json()}")

            # Verify the response
            assert response.status_code == 201
            data = response.get_json()

            # Should have exactly 8 prompts (no AI generation needed)
            assert len(data["prompts"]) == 8

            print("✅ Tournament creation with sufficient prompts works!")

            # Clean up
            db.drop_all()


if __name__ == "__main__":
    print("Testing tournament creation with AI prompt generation...")

    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key"

    try:
        test_tournament_creation_with_few_prompts()
        test_tournament_creation_fallback()
        test_tournament_creation_with_enough_prompts()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
