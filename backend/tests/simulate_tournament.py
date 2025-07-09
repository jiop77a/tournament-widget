#!/usr/bin/env python3
"""
End-to-end tournament simulation script

This script demonstrates the complete tournament workflow:
1. Create a tournament with prompts
2. Start the tournament bracket
3. Simulate matches with random winners
4. Retrieve tournament results at each stage
"""

import os
import random
import sys
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
port = os.getenv("FLASK_RUN_PORT", "5001")
BASE_URL = f"http://localhost:{port}/api"
DELAY_BETWEEN_MATCHES = 1  # seconds


class TournamentSimulator:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.tournament_id = None

    def create_tournament(
        self,
        input_question: str,
        custom_prompts: List[str] = None,
        total_prompts: int = 8,
    ) -> Dict[str, Any]:
        """Create a new tournament with the given parameters"""
        print(f"\n🏆 Creating tournament with question: '{input_question}'")

        data = {"input_question": input_question, "total_prompts": total_prompts}

        if custom_prompts:
            data["custom_prompts"] = custom_prompts
            print(f"   Custom prompts provided: {len(custom_prompts)}")

        response = requests.post(f"{self.base_url}/tournament", json=data)

        if response.status_code == 201:
            result = response.json()
            self.tournament_id = result["tournament_id"]
            print(f"✅ Tournament created successfully! ID: {self.tournament_id}")
            print(f"   Total prompts: {len(result['prompts'])}")
            for i, prompt in enumerate(result["prompts"], 1):
                print(f"   {i}. {prompt}")
            return result
        else:
            print(f"❌ Failed to create tournament: {response.status_code}")
            print(f"   Error: {response.text}")
            sys.exit(1)

    def start_bracket(self) -> Dict[str, Any]:
        """Start the tournament bracket by creating first round matches"""
        print(f"\n🎯 Starting tournament bracket for tournament {self.tournament_id}")

        response = requests.post(
            f"{self.base_url}/tournament/{self.tournament_id}/start-bracket"
        )

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Tournament bracket started!")
            print(f"   Round 1 matches created: {result['total_matches']}")
            for i, match in enumerate(result["round_1_matches"], 1):
                print(f"   Match {i}: '{match['prompt_1']}' vs '{match['prompt_2']}'")
            return result
        else:
            print(f"❌ Failed to start bracket: {response.status_code}")
            print(f"   Error: {response.text}")
            sys.exit(1)

    def get_tournament_status(self) -> Dict[str, Any]:
        """Get comprehensive tournament status"""
        response = requests.get(
            f"{self.base_url}/tournament/{self.tournament_id}/status"
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get tournament status: {response.status_code}")
            print(f"   Error: {response.text}")
            sys.exit(1)

    def get_pending_matches(self) -> List[Dict[str, Any]]:
        """Get all pending matches in the tournament"""
        status = self.get_tournament_status()
        pending_matches = []

        for round_num, matches in status["rounds"].items():
            for match in matches:
                if match["status"] == "pending":
                    match["round_number"] = int(round_num)
                    pending_matches.append(match)

        return pending_matches

    def simulate_match(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a match by randomly selecting a winner"""
        match_id = match["match_id"]

        # Get the prompt IDs (we need to fetch them from the API)
        response = requests.get(f"{self.base_url}/prompts")
        if response.status_code != 200:
            print(f"❌ Failed to get prompts: {response.status_code}")
            sys.exit(1)

        all_prompts = response.json()
        prompt_1_id = None
        prompt_2_id = None

        for prompt in all_prompts:
            if prompt["text"] == match["prompt_1"]:
                prompt_1_id = prompt["id"]
            elif prompt["text"] == match["prompt_2"]:
                prompt_2_id = prompt["id"]

        if not prompt_1_id or not prompt_2_id:
            print(f"❌ Could not find prompt IDs for match {match_id}")
            sys.exit(1)

        # Randomly select winner
        winner_id = random.choice([prompt_1_id, prompt_2_id])
        winner_text = (
            match["prompt_1"] if winner_id == prompt_1_id else match["prompt_2"]
        )

        print(f"\n⚔️  Simulating match {match_id} (Round {match['round_number']})")
        print(f"   '{match['prompt_1']}' vs '{match['prompt_2']}'")
        print(f"   🏆 Winner: '{winner_text}'")

        # Submit the result
        response = requests.post(
            f"{self.base_url}/match/{match_id}/result", json={"winner_id": winner_id}
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("round_completed"):
                print(f"   ✅ Round {match['round_number']} completed!")
                if result.get("next_round_created"):
                    print(
                        f"   🎯 Round {result['next_round']} created with {len(result['next_round_matches'])} matches"
                    )
                if result.get("tournament_completed"):
                    print(
                        f"   🎉 TOURNAMENT COMPLETED! Winner: '{result['tournament_winner']}'"
                    )
            return result
        else:
            print(f"❌ Failed to submit match result: {response.status_code}")
            print(f"   Error: {response.text}")
            sys.exit(1)

    def run_full_simulation(
        self,
        input_question: str,
        custom_prompts: List[str] = None,
        total_prompts: int = 8,
    ):
        """Run a complete tournament simulation from start to finish"""
        print("🚀 Starting full tournament simulation...")

        # Step 1: Create tournament
        self.create_tournament(input_question, custom_prompts, total_prompts)

        # Step 2: Start bracket
        self.start_bracket()

        # Step 3: Simulate all matches until tournament is complete
        round_number = 1
        while True:
            pending_matches = self.get_pending_matches()

            if not pending_matches:
                break

            current_round = pending_matches[0]["round_number"]
            if current_round != round_number:
                print(f"\n🔄 Moving to Round {current_round}")
                round_number = current_round

            # Simulate one match at a time
            match = pending_matches[0]
            result = self.simulate_match(match)

            # Check if tournament is complete
            if result.get("tournament_completed"):
                break

            # Small delay for readability
            time.sleep(DELAY_BETWEEN_MATCHES)

        # Step 4: Show final results
        self.show_final_results()

    def show_final_results(self):
        """Display comprehensive final tournament results"""
        print("\n" + "=" * 60)
        print("🏆 FINAL TOURNAMENT RESULTS")
        print("=" * 60)

        status = self.get_tournament_status()

        print(f"Tournament ID: {status['tournament_id']}")
        print(f"Question: {status['input_question']}")
        print(f"Status: {status['status']}")
        print(f"Total Prompts: {status['total_prompts']}")
        print(
            f"Progress: {status['progress']['completed_matches']}/{status['progress']['total_matches']} matches ({status['progress']['completion_percentage']}%)"
        )

        if status["winner"]:
            print(f"\n🎉 CHAMPION: {status['winner']}")

        print(f"\n📊 Round-by-Round Results:")
        for round_num in sorted(status["rounds"].keys(), key=int):
            matches = status["rounds"][round_num]
            print(f"\n   Round {round_num}:")
            for i, match in enumerate(matches, 1):
                winner_indicator = (
                    f" → 🏆 {match['winner']}" if match["winner"] else " (pending)"
                )
                print(
                    f"     Match {i}: {match['prompt_1']} vs {match['prompt_2']}{winner_indicator}"
                )


def main():
    """Main function to run the simulation"""
    simulator = TournamentSimulator()

    # Example 1: Tournament with custom prompts
    print("Example 1: Tournament with custom prompts")
    custom_prompts = [
        "What is the capital of France?",
        "Tell me France's capital city",
        "Which city is the capital of France?",
        "What city serves as France's capital?",
    ]

    simulator.run_full_simulation(
        input_question="What is the capital of France?",
        custom_prompts=custom_prompts,
        total_prompts=8,  # Will generate 4 more prompts automatically
    )

    print("\n" + "=" * 60)
    print("Simulation completed! 🎉")


if __name__ == "__main__":
    main()
