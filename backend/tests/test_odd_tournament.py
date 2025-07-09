#!/usr/bin/env python3
"""
Test script to verify odd number tournament handling
"""


def test_odd_tournament(client):
    """Test tournament with odd number of participants (3 prompts)"""

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
        assert False, f"Tournament creation failed with status {response.status_code}"

    tournament_id = response.get_json()["tournament_id"]
    print(f"✅ Tournament created: {tournament_id} with 3 prompts")

    # Start bracket
    response = client.post(f"/api/tournament/{tournament_id}/start-bracket")
    bracket_result = response.get_json()
    print(f"✅ Bracket started with {bracket_result['total_matches']} matches")

    # Should have 1 match (2 prompts paired, 1 gets bye)
    print(f"   Expected: 1 match for 3 prompts, Got: {bracket_result['total_matches']}")
    assert (
        bracket_result["total_matches"] == 1
    ), f"Expected 1 match, got {bracket_result['total_matches']}"

    # Get tournament status
    response = client.get(f"/api/tournament/{tournament_id}/status")
    status = response.get_json()
    print(f"📊 Round 1: {len(status['rounds']['1'])} matches")

    # Get all prompts
    response = client.get("/api/prompts")
    all_prompts = response.get_json()

    # Get the first match
    first_match = status["rounds"]["1"][0]
    match_id = first_match["match_id"]
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

    if result.get("bye_prompts"):
        print(f"   Bye prompts: {result.get('bye_prompts')}")

    # Get updated status
    response = client.get(f"/api/tournament/{tournament_id}/status")
    status = response.get_json()

    print(f"\n📊 After Round 1:")
    print(f"   Status: {status['status']}")
    print(f"   Current round: {status['current_round']}")
    print(f"   Total rounds: {len(status['rounds'])}")

    if "2" in status["rounds"]:
        print(f"   Round 2: {len(status['rounds']['2'])} matches")
        final_match = status["rounds"]["2"][0]
        print(f"   Final: '{final_match['prompt_1']}' vs '{final_match['prompt_2']}'")

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

    print("✅ 3-prompt tournament structure looks correct!")


def test_five_prompts(client):
    """Test tournament with 5 prompts"""

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


def test_bye_randomness(client):
    """Test that byes are distributed fairly across multiple tournaments"""

    print("\n🧪 Testing Bye Randomness (multiple 5-prompt tournaments)")
    print("=" * 60)

    bye_counts = {}  # Track which prompts get byes across tournaments
    num_tournaments = 10  # Run multiple tournaments to test randomness

    for tournament_num in range(num_tournaments):
        # Create a tournament with 5 prompts (same prompts each time for consistency)
        tournament_data = {
            "input_question": f"Test question {tournament_num}",
            "custom_prompts": [
                "Prompt Alpha",
                "Prompt Beta",
                "Prompt Gamma",
                "Prompt Delta",
                "Prompt Epsilon",
            ],
            "total_prompts": 5,
        }

        response = client.post("/api/tournament", json=tournament_data)
        tournament_id = response.get_json()["tournament_id"]

        # Start bracket
        client.post(f"/api/tournament/{tournament_id}/start-bracket")

        # Get tournament status to see which prompt got the bye in round 1
        response = client.get(f"/api/tournament/{tournament_id}/status")
        status = response.get_json()

        # Check for byes in round 1
        if "1" in status.get("byes_by_round", {}):
            round_1_byes = status["byes_by_round"]["1"]
            for bye_prompt in round_1_byes:
                bye_counts[bye_prompt] = bye_counts.get(bye_prompt, 0) + 1

    print(f"📊 Bye distribution across {num_tournaments} tournaments:")
    for prompt, count in sorted(bye_counts.items()):
        percentage = (count / num_tournaments) * 100
        print(f"   '{prompt}': {count}/{num_tournaments} ({percentage:.1f}%)")

    # Verify that byes are somewhat distributed (not all going to same prompt)
    if bye_counts:
        max_byes = max(bye_counts.values())
        min_byes = min(bye_counts.values())

        # With randomness, no prompt should get ALL the byes
        assert (
            max_byes < num_tournaments
        ), f"One prompt got all {max_byes} byes - randomness not working"

        # With 5 prompts and good randomness, difference shouldn't be too extreme
        # Allow some variance but ensure it's not completely skewed
        assert (
            max_byes - min_byes <= num_tournaments * 0.7
        ), f"Bye distribution too skewed: max={max_byes}, min={min_byes}"

        print(f"✅ Bye distribution looks random (max: {max_byes}, min: {min_byes})")
    else:
        print("⚠️  No byes detected in any tournament")
