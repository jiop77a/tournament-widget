"""
Example script demonstrating how to use the test-prompt route
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


def test_prompt_example():
    """Example of testing a prompt with the API"""

    with app.test_client() as client:
        with app.app_context():

            # Example 1: Basic prompt test
            print("=== Example 1: Basic Prompt Test ===")
            response = client.post(
                "/api/test-prompt",
                data=json.dumps({"prompt": "What is the capital of France?"}),
                content_type="application/json",
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"Prompt: {data['prompt']}")
                print(f"Response: {data['response']}")
                print(f"Model: {data['model']}")
                print(f"Tokens used: {data['usage']['total_tokens']}")
            else:
                print(f"Error: {response.status_code}")

            print("\n" + "=" * 50 + "\n")

            # Example 2: Custom parameters
            print("=== Example 2: Custom Parameters ===")
            response = client.post(
                "/api/test-prompt",
                data=json.dumps(
                    {
                        "prompt": "Explain quantum computing in simple terms",
                        "model": "gpt-4",
                        "max_tokens": 100,
                        "temperature": 0.3,
                    }
                ),
                content_type="application/json",
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"Prompt: {data['prompt']}")
                print(f"Response: {data['response']}")
                print(f"Model: {data['model']}")
                print(f"Temperature: {data['temperature']}")
                print(f"Max tokens: {data['max_tokens']}")
                print(f"Tokens used: {data['usage']['total_tokens']}")
            else:
                print(f"Error: {response.status_code}")

            print("\n" + "=" * 50 + "\n")

            # Example 3: Error case
            print("=== Example 3: Error Case (Empty Prompt) ===")
            response = client.post(
                "/api/test-prompt",
                data=json.dumps({"prompt": ""}),
                content_type="application/json",
            )

            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print("Expected error for empty prompt")


if __name__ == "__main__":
    # Set a dummy API key for testing (won't actually call OpenAI in this example)
    os.environ["OPENAI_API_KEY"] = "test-key"

    print("Testing the test-prompt route...")
    print("Note: This example uses mock responses, not real OpenAI calls\n")

    try:
        test_prompt_example()
        print("\n✅ Test-prompt route examples completed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
