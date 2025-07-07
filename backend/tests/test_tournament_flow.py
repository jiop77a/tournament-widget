#!/usr/bin/env python3
"""
Simple test script to verify the tournament API endpoints work correctly
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models import InputQuestion, Match, Prompt, Tournament


def test_tournament_flow():
    """Test the complete tournament flow using the Flask test client"""

    with app.test_client() as client:
        with app.app_context():
            # Create database tables
            db.create_all()

            print("🧪 Testing Tournament Flow")
            print("=" * 50)

        # Step 1: Create a tournament
        print("\n1️⃣ Creating tournament...")
        tournament_data = {
            "input_question": "What is the best programming language?",
            "custom_prompts": [
                "Which programming language is the best?",
                "What's the top programming language?",
                "Tell me the best coding language",
                "Which language should I learn for programming?",
            ],
            "total_prompts": 4,
        }

        response = client.post("/api/tournament", json=tournament_data)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.get_json()}"

        tournament_result = response.get_json()
        tournament_id = tournament_result["tournament_id"]
        print(f"✅ Tournament created with ID: {tournament_id}")
        print(f"   Prompts: {len(tournament_result['prompts'])}")

        # Step 2: Start the tournament bracket
        print("\n2️⃣ Starting tournament bracket...")
        response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.get_json()}"

        bracket_result = response.get_json()
        print(f"✅ Bracket started with {bracket_result['total_matches']} matches")
        for i, match in enumerate(bracket_result["round_1_matches"], 1):
            print(f"   Match {i}: '{match['prompt_1']}' vs '{match['prompt_2']}'")

        # Step 3: Get tournament status
        print("\n3️⃣ Getting tournament status...")
        response = client.get(f"/api/tournament/{tournament_id}/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        status = response.get_json()
        print(f"✅ Tournament status: {status['status']}")
        print(f"   Current round: {status['current_round']}")
        print(
            f"   Progress: {status['progress']['completed_matches']}/{status['progress']['total_matches']} matches"
        )

        # Step 4: Get matches for the tournament
        print("\n4️⃣ Getting tournament matches...")
        response = client.get(f"/api/tournament/{tournament_id}/matches")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        matches_result = response.get_json()
        matches = matches_result["matches"]
        print(f"✅ Found {len(matches)} matches")

        # Step 5: Simulate first match
        if matches:
            first_match = matches[0]
            match_id = first_match["match_id"]

            print(f"\n5️⃣ Simulating first match (ID: {match_id})...")
            print(f"   '{first_match['prompt_1']}' vs '{first_match['prompt_2']}'")

            # Get prompt IDs
            response = client.get("/api/prompts")
            assert response.status_code == 200
            all_prompts = response.get_json()

            # Find the prompt IDs for this match
            prompt_1_id = None
            prompt_2_id = None
            for prompt in all_prompts:
                if prompt["text"] == first_match["prompt_1"]:
                    prompt_1_id = prompt["id"]
                elif prompt["text"] == first_match["prompt_2"]:
                    prompt_2_id = prompt["id"]

            # Choose first prompt as winner
            winner_id = prompt_1_id
            winner_text = first_match["prompt_1"]

            print(f"   🏆 Winner: '{winner_text}'")

            # Submit match result
            response = client.post(
                f"/api/match/{match_id}/result", json={"winner_id": winner_id}
            )
            assert (
                response.status_code == 200
            ), f"Expected 200, got {response.status_code}: {response.get_json()}"

            result = response.get_json()
            print(f"✅ Match result submitted successfully")
            print(f"   Round completed: {result['round_completed']}")
            if result.get("next_round_created"):
                print(f"   Next round created: Round {result['next_round']}")
            if result.get("tournament_completed"):
                print(
                    f"   🎉 Tournament completed! Winner: {result['tournament_winner']}"
                )

        # Step 6: Get updated tournament status
        print("\n6️⃣ Getting updated tournament status...")
        response = client.get(f"/api/tournament/{tournament_id}/status")
        assert response.status_code == 200

        final_status = response.get_json()
        print(f"✅ Final tournament status: {final_status['status']}")
        print(
            f"   Progress: {final_status['progress']['completed_matches']}/{final_status['progress']['total_matches']} matches"
        )
        if final_status["winner"]:
            print(f"   🏆 Winner: {final_status['winner']}")

        print("\n🎉 All tests passed!")


def test_complete_tournament():
    """Test a complete tournament from start to finish"""

    with app.test_client() as client:
        with app.app_context():
            # Create database tables
            db.create_all()

            print("\n🧪 Testing Complete Tournament")
            print("=" * 50)

        # Create a tournament with 4 prompts (2 rounds)
        tournament_data = {
            "input_question": "What is the best pizza topping?",
            "custom_prompts": [
                "What's the best pizza topping?",
                "Which pizza topping is the best?",
                "Tell me the top pizza topping",
                "What topping makes the best pizza?",
            ],
            "total_prompts": 4,
        }

        response = client.post("/api/tournament", json=tournament_data)
        tournament_id = response.get_json()["tournament_id"]
        print(f"✅ Tournament created: {tournament_id}")

        # Start bracket
        response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
        print("✅ Bracket started")

        # Simulate all matches until tournament is complete
        max_rounds = 10  # Safety limit to prevent infinite loops
        round_num = 1

        while round_num <= max_rounds:
            # Get current matches
            response = client.get(f"/api/tournament/{tournament_id}/matches")
            matches = response.get_json()["matches"]

            # Find pending matches
            pending_matches = [m for m in matches if m["status"] == "pending"]

            if not pending_matches:
                print(f"✅ No more pending matches - tournament should be complete")
                break

            print(f"\n🔄 Round {round_num} - {len(pending_matches)} pending matches")

            # Simulate each pending match in this round
            for match in pending_matches:
                match_id = match["match_id"]

                # Get all prompts to find IDs
                response = client.get("/api/prompts")
                all_prompts = response.get_json()

                # Find the actual prompt IDs for this match
                try:
                    prompt_1_id = next(
                        p["id"] for p in all_prompts if p["text"] == match["prompt_1"]
                    )
                    prompt_2_id = next(
                        p["id"] for p in all_prompts if p["text"] == match["prompt_2"]
                    )
                except StopIteration:
                    print(f"❌ Could not find prompt IDs for match {match_id}")
                    print(
                        f"   Looking for: '{match['prompt_1']}' and '{match['prompt_2']}'"
                    )
                    print(f"   Available prompts: {[p['text'] for p in all_prompts]}")
                    assert False, f"Could not find prompt IDs for match {match_id}"

                # Choose first prompt as winner (deterministic for testing)
                winner_id = prompt_1_id
                winner_text = match["prompt_1"]

                print(
                    f"   Match {match_id}: '{match['prompt_1']}' vs '{match['prompt_2']}'"
                )
                print(f"   🏆 Winner: '{winner_text}'")

                # Submit result
                response = client.post(
                    f"/api/match/{match_id}/result", json={"winner_id": winner_id}
                )

                if response.status_code != 200:
                    print(f"❌ Failed to submit match result: {response.status_code}")
                    print(f"   Error: {response.get_json()}")
                    assert (
                        False
                    ), f"Failed to submit match result: {response.status_code}"

                result = response.get_json()

                if result.get("tournament_completed"):
                    print(
                        f"   🎉 TOURNAMENT COMPLETED! Champion: '{result['tournament_winner']}'"
                    )

                    # Get final status
                    response = client.get(f"/api/tournament/{tournament_id}/status")
                    final_status = response.get_json()

                    print(f"\n📊 Final Results:")
                    print(f"   Status: {final_status['status']}")
                    print(f"   Winner: {final_status['winner']}")
                    print(
                        f"   Total matches: {final_status['progress']['total_matches']}"
                    )
                    print(
                        f"   Completion: {final_status['progress']['completion_percentage']}%"
                    )

                    return  # Tournament completed successfully

            round_num += 1

        print(f"❌ Tournament did not complete within {max_rounds} rounds")
        assert False, f"Tournament did not complete within {max_rounds} rounds"


def test_error_cases():
    """Test error handling"""

    with app.test_client() as client:
        with app.app_context():
            # Create database tables
            db.create_all()

            print("\n🧪 Testing Error Cases")
            print("=" * 50)

        # Test starting bracket on non-existent tournament
        print("\n❌ Testing non-existent tournament...")
        response = client.post("/api/tournament/99999/start-bracket")
        assert response.status_code == 404
        print("✅ Correctly returned 404 for non-existent tournament")

        # Test submitting result for non-existent match
        print("\n❌ Testing non-existent match...")
        response = client.post("/api/match/99999/result", json={"winner_id": 1})
        assert response.status_code == 404
        print("✅ Correctly returned 404 for non-existent match")

        print("\n🎉 Error case tests passed!")


if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

        try:
            test_tournament_flow()
            test_complete_tournament()
            test_error_cases()
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            sys.exit(1)
