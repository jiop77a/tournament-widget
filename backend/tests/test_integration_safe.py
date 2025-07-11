"""
Safe integration tests that use test client instead of live server
These tests verify end-to-end functionality without external dependencies
"""

import pytest


@pytest.mark.integration
def test_tournament_flow_safe(client, app_context):
    """Test the complete tournament flow using isolated test client"""

    print("\n🧪 Testing Tournament Flow (Safe)")
    print("=" * 50)

    # Step 1: Create tournament
    print("\n1️⃣ Creating tournament...")
    response = client.post(
        "/api/tournament",
        json={
            "input_question": "What is the best coding language?",
            "custom_prompts": [
                "Tell me the best coding language",
                "Which programming language is the best?",
                "Which language should I learn for programming?",
                "What's the top programming language?",
            ],
        },
    )
    assert response.status_code == 201
    tournament_data = response.get_json()
    tournament_id = tournament_data["tournament_id"]
    print(f"✅ Tournament created with ID: {tournament_id}")
    print(f"   Prompts: {len(tournament_data['prompts'])}")

    # Step 2: Start bracket
    print("\n2️⃣ Starting tournament bracket...")
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    assert response.status_code == 201
    bracket_data = response.get_json()
    print(f"✅ Bracket started with {bracket_data['total_matches']} matches")
    for match in bracket_data["round_1_matches"]:
        print(f"   Match: '{match['prompt_1']}' vs '{match['prompt_2']}'")

    # Step 3: Get tournament status
    print("\n3️⃣ Getting tournament status...")
    response = client.get(f"/api/tournament/{tournament_id}/status")
    assert response.status_code == 200
    status_data = response.get_json()
    print(f"✅ Tournament status: {status_data['status']}")
    print(f"   Current round: {status_data['current_round']}")
    print(
        f"   Progress: {status_data['progress']['completed_matches']}/{status_data['progress']['total_matches']} matches"
    )

    # Step 4: Get matches
    print("\n4️⃣ Getting tournament matches...")
    response = client.get(f"/api/tournament/{tournament_id}/matches")
    assert response.status_code == 200
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
        print("✅ Match result submitted successfully")
        print(f"   Round completed: {result.get('round_completed', False)}")

    # Step 6: Get updated status
    print("\n6️⃣ Getting updated tournament status...")
    response = client.get(f"/api/tournament/{tournament_id}/status")
    assert response.status_code == 200
    final_status = response.get_json()
    print(f"✅ Final tournament status: {final_status['status']}")
    print(
        f"   Progress: {final_status['progress']['completed_matches']}/{final_status['progress']['total_matches']} matches"
    )

    print("\n🎉 All tests passed!")


@pytest.mark.integration
def test_complete_tournament_safe(client, app_context):
    """Test a complete tournament from start to finish using isolated test client"""

    print("\n🧪 Testing Complete Tournament (Safe)")
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

    # Create tournament
    response = client.post("/api/tournament", json=tournament_data)
    assert response.status_code == 201
    result = response.get_json()
    tournament_id = result["tournament_id"]
    print(f"✅ Tournament created: {tournament_id}")

    # Start bracket
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    assert response.status_code == 201
    print("✅ Bracket started")

    # Simulate complete tournament
    max_rounds = 10  # Safety limit
    round_num = 1

    while round_num <= max_rounds:
        print(f"\n🔄 Round {round_num}")

        # Get pending matches for current round
        response = client.get(
            f"/api/tournament/{tournament_id}/matches?round={round_num}"
        )
        assert response.status_code == 200

        matches_data = response.get_json()
        pending_matches = [
            m for m in matches_data["matches"] if m["status"] == "pending"
        ]

        if not pending_matches:
            print("   No pending matches - tournament may be complete")
            break

        print(f" - {len(pending_matches)} pending matches")

        # Process each match in the round
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

            assert (
                response.status_code == 200
            ), f"Failed to submit match result: {response.status_code} - {response.get_json()}"

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
                print(f"   Total matches: {final_status['progress']['total_matches']}")
                print(
                    f"   Completion: {final_status['progress']['completion_percentage']}%"
                )

                return  # Tournament completed successfully

        round_num += 1

    print(f"❌ Tournament did not complete within {max_rounds} rounds")
    assert False, f"Tournament did not complete within {max_rounds} rounds"


@pytest.mark.integration
def test_error_cases_safe(client, app_context):
    """Test error handling using isolated test client"""

    print("\n🧪 Testing Error Cases (Safe)")
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
