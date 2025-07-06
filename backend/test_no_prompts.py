#!/usr/bin/env python3
"""
Test what happens when no custom prompts are provided
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def test_tournament_creation_no_custom_prompts():
    """Test tournament creation when no custom prompts are provided"""
    
    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Mock the OpenAI API response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = """What is France's capital city?
Could you tell me the capital of France?
Which city serves as France's capital?
I'd like to know France's capital city
Please tell me about France's capital
What city is the capital of France?
Can you name France's capital?
Which city is France's main city?"""
            
            with patch('tournament_routes.client.chat.completions.create', return_value=mock_response):
                # Test data with NO custom prompts
                test_data = {
                    "input_question": "What is the capital of France?"
                    # No custom_prompts field at all
                }
                
                # Make the request
                response = client.post('/api/tournament', 
                                     data=json.dumps(test_data),
                                     content_type='application/json')
                
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.get_json()}")
                
                # Verify the response
                assert response.status_code == 201
                data = response.get_json()
                
                # Should have 8 prompts total (all AI generated)
                assert len(data['prompts']) == 8
                
                print("✅ Tournament creation with no custom prompts works!")
                print(f"Generated {len(data['prompts'])} prompts using AI")
                
                # Clean up
                db.drop_all()

if __name__ == "__main__":
    print("Testing tournament creation with no custom prompts...")
    
    # Set a dummy API key for testing
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    try:
        test_tournament_creation_no_custom_prompts()
        print("\n🎉 Test passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
