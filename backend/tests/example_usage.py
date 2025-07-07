#!/usr/bin/env python3
"""
Example script showing how to create tournaments with AI-generated prompts
"""

import requests
import json

def create_tournament_example():
    """Example of creating a tournament with fewer than 8 prompts"""
    
    # API endpoint
    url = "http://localhost:5000/api/tournament"
    
    # Example 1: Tournament with only 3 custom prompts
    # The system will automatically generate 5 more prompts using ChatGPT API
    tournament_data = {
        "input_question": "What is the capital of Japan?",
        "custom_prompts": [
            "Tell me Japan's capital city",
            "What city is the capital of Japan?",
            "Which city serves as Japan's capital?"
        ]
    }
    
    print("Creating tournament with 3 custom prompts...")
    print(f"Input question: {tournament_data['input_question']}")
    print(f"Custom prompts: {tournament_data['custom_prompts']}")
    print()
    
    try:
        response = requests.post(url, json=tournament_data)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Tournament created successfully!")
            print(f"Tournament ID: {data['tournament_id']}")
            print(f"Total prompts generated: {len(data['prompts'])}")
            print("\nAll prompts:")
            for i, prompt in enumerate(data['prompts'], 1):
                print(f"  {i}. {prompt}")
        else:
            print(f"❌ Error creating tournament: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_tournament_with_enough_prompts():
    """Example of creating a tournament with 8 or more prompts (no AI generation needed)"""
    
    url = "http://localhost:5000/api/tournament"
    
    tournament_data = {
        "input_question": "What is the largest planet in our solar system?",
        "custom_prompts": [
            "What is the biggest planet in our solar system?",
            "Which planet is the largest in our solar system?",
            "Can you tell me the largest planet in our solar system?",
            "What planet is the biggest in our solar system?",
            "Which is the largest planet in our solar system?",
            "Tell me about the largest planet in our solar system",
            "What's the name of the largest planet in our solar system?",
            "I need to know the largest planet in our solar system"
        ]
    }
    
    print("\n" + "="*60)
    print("Creating tournament with 8 custom prompts (no AI generation needed)...")
    print(f"Input question: {tournament_data['input_question']}")
    print(f"Number of custom prompts: {len(tournament_data['custom_prompts'])}")
    print()
    
    try:
        response = requests.post(url, json=tournament_data)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Tournament created successfully!")
            print(f"Tournament ID: {data['tournament_id']}")
            print(f"Total prompts: {len(data['prompts'])}")
            print("\nAll prompts:")
            for i, prompt in enumerate(data['prompts'], 1):
                print(f"  {i}. {prompt}")
        else:
            print(f"❌ Error creating tournament: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Tournament Creation Examples")
    print("="*60)
    
    # Example 1: Few prompts (will trigger AI generation)
    create_tournament_example()
    
    # Example 2: Enough prompts (no AI generation needed)
    create_tournament_with_enough_prompts()
    
    print("\n" + "="*60)
    print("Note: To use AI generation, make sure to:")
    print("1. Set your OpenAI API key in the .env file")
    print("2. Start the Flask server: python app.py")
    print("3. Run this script: python example_usage.py")
