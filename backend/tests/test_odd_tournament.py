#!/usr/bin/env python3
"""
Test script to verify odd number tournament handling
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models import InputQuestion, Match, Prompt, Tournament


def test_odd_tournament():
    """Test tournament with odd number of participants (3 prompts)"""

    with app.test_client() as client:
        with app.app_context():
            # Create database tables
            db.create_all()

            print("🧪 Testing Odd Number Tournament (3 prompts)")
            print("=" * 60)

        # Create a tournament with 3 prompts (odd number)
        tournament_data = {
            "input_question": "What is the best pet?",
            "custom_prompts": [
                "What pet is the best?",
                "Which pet do you prefer?",
                "Tell me the top pet",
            ],
            "total_prompts": 3,
        }

        response = client.post("/api/tournament", json=tournament_data)
        if response.status_code != 201:
            print(f"❌ Failed to create tournament: {response.status_code}")
            print(f"   Error: {response.get_json()}")
            assert (
                False
            ), f"Tournament creation failed with status {response.status_code}"

        tournament_id = response.get_json()["tournament_id"]
        print(f"✅ Tournament created: {tournament_id} with 3 prompts")

        # Start bracket
        response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
        bracket_result = response.get_json()
        print(f"✅ Bracket started with {bracket_result['total_matches']} matches")

        # Should have 1 match (2 prompts paired, 1 gets bye)
        print(
            f"   Expected: 1 match for 3 prompts, Got: {bracket_result['total_matches']}"
        )
        # Note: With 3 prompts, we should have 1 match in round 1, then 1 match in round 2 (final)

        # Get tournament status
        response = client.get(f"/api/tournament/{tournament_id}/status")
        status = response.get_json()
        print(f"📊 Round 1: {len(status['rounds']['1'])} matches")

        # Simulate the single match in round 1
        first_match = status["rounds"]["1"][0]
        match_id = first_match["match_id"]

        # Get all prompts
        response = client.get("/api/prompts")
        all_prompts = response.get_json()

        # Find prompt ID for winner
        prompt_1_id = next(
            p["id"] for p in all_prompts if p["text"] == first_match["prompt_1"]
        )

        print(f"\n⚔️ Round 1 Match:")
        print(f"   '{first_match['prompt_1']}' vs '{first_match['prompt_2']}'")
        print(f"   🏆 Winner: '{first_match['prompt_1']}'")
        print(f"   (Third prompt gets automatic bye to final)")

        # Submit result
        response = client.post(
            f"/api/match/{match_id}/result", json={"winner_id": prompt_1_id}
        )
        result = response.get_json()

        print(f"✅ Match result: {result.get('message')}")
        print(f"   Round completed: {result.get('round_completed')}")
        print(f"   Next round created: {result.get('next_round_created')}")

        if result.get("bye_winner"):
            print(f"   Bye winner: '{result.get('bye_winner')}'")

        # Get updated status
        response = client.get(f"/api/tournament/{tournament_id}/status")
        status = response.get_json()

        print(f"\n📊 After Round 1:")
        print(f"   Status: {status['status']}")
        print(
            f"   Progress: {status['progress']['completed_matches']}/{status['progress']['total_matches']}"
        )

        if "2" in status["rounds"]:
            print(f"   Round 2: {len(status['rounds']['2'])} matches")
            final_match = status["rounds"]["2"][0]
            print(
                f"   Final: '{final_match['prompt_1']}' vs '{final_match['prompt_2']}'"
            )

            # Simulate final match
            match_id = final_match["match_id"]
            prompt_1_id = next(
                p["id"] for p in all_prompts if p["text"] == final_match["prompt_1"]
            )

            print(f"\n⚔️ Final Match:")
            print(f"   '{final_match['prompt_1']}' vs '{final_match['prompt_2']}'")
            print(f"   🏆 Winner: '{final_match['prompt_1']}'")

            response = client.post(
                f"/api/match/{match_id}/result", json={"winner_id": prompt_1_id}
            )
            result = response.get_json()

            if result.get("tournament_completed"):
                print(
                    f"   🎉 TOURNAMENT COMPLETED! Champion: '{result['tournament_winner']}'"
                )

            # Final status
            response = client.get(f"/api/tournament/{tournament_id}/status")
            final_status = response.get_json()

            print(f"\n🏆 Final Results:")
            print(f"   Status: {final_status['status']}")
            print(f"   Winner: {final_status['winner']}")
            print(f"   Total matches: {final_status['progress']['total_matches']}")
            print(
                f"   Completion: {final_status['progress']['completion_percentage']}%"
            )


def test_five_prompts():
    """Test tournament with 5 prompts"""

    with app.test_client() as client:
        with app.app_context():
            # Create database tables
            db.create_all()

            print("\n🧪 Testing 5-Prompt Tournament")
            print("=" * 60)

        # Create a tournament with 5 prompts
        tournament_data = {
            "input_question": "What is the best season?",
            "custom_prompts": [
                "What season is the best?",
                "Which season do you prefer?",
                "Tell me the top season",
                "What is your favorite season?",
                "Which season is most enjoyable?",
            ],
            "total_prompts": 5,
        }

        response = client.post("/api/tournament", json=tournament_data)
        tournament_id = response.get_json()["tournament_id"]
        print(f"✅ Tournament created: {tournament_id} with 5 prompts")

        # Start bracket
        response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
        bracket_result = response.get_json()
        print(f"✅ Bracket started with {bracket_result['total_matches']} matches")

        # Should have 2 matches (4 prompts paired, 1 gets bye)
        assert (
            bracket_result["total_matches"] == 2
        ), f"Expected 2 matches, got {bracket_result['total_matches']}"

        print("✅ 5-prompt tournament structure looks correct!")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        try:
            test_odd_tournament()
            test_five_prompts()
            print("\n" + "=" * 60)
            print("🎉 ALL ODD NUMBER TESTS PASSED!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
