import random

from database import db
from flask import abort
from models import InputQuestion, Match, Prompt, Tournament
from services.prompt_service import prompt_service

# Constants
DEFAULT_TOTAL_PROMPTS = 8


class TournamentService:
    """Service for handling tournament-related operations"""

    def create_tournament(self, data):
        """
        Create a new tournament with prompts

        Args:
            data (dict): Tournament creation data

        Returns:
            dict: Created tournament data
        """
        # Check if input_question exists and is not empty
        input_question_text = data.get("input_question")
        if not input_question_text or not input_question_text.strip():
            abort(400, description="Input question is required and cannot be empty")

        # Create the InputQuestion
        input_question = InputQuestion(question_text=input_question_text)
        db.session.add(input_question)
        db.session.commit()

        # Get custom prompts or start with empty list
        prompts = data.get("custom_prompts", [])

        # Remove duplicates from custom prompts first
        prompts = prompt_service.remove_duplicate_prompts(prompts)

        # Get total_prompts parameter, default to DEFAULT_TOTAL_PROMPTS
        total_prompts = data.get("total_prompts", DEFAULT_TOTAL_PROMPTS)

        # Validate total_prompts
        if not isinstance(total_prompts, int):
            abort(400, description="total_prompts must be an integer")
        if total_prompts <= 0:
            abort(400, description="total_prompts must be a positive number")
        if total_prompts < 2:
            abort(400, description="total_prompts must be at least 2 for a tournament")

        # Generate additional prompts if needed, ensuring uniqueness
        max_attempts = 3  # Limit attempts to avoid infinite loops
        attempt = 0

        while len(prompts) < total_prompts and attempt < max_attempts:
            additional_prompts_needed = total_prompts - len(prompts)
            previous_count = len(prompts)

            try:
                ai_generated_prompts = prompt_service.generate_prompts_with_ai(
                    input_question_text,
                    additional_prompts_needed,
                    existing_prompts=prompts,
                )
                prompts.extend(ai_generated_prompts)
            except Exception as e:
                # If AI generation fails, fall back to simple variations
                print(f"AI prompt generation failed: {e}")
                fallback_prompts = prompt_service.generate_fallback_prompts(
                    input_question_text,
                    additional_prompts_needed,
                    existing_prompts=prompts,
                )
                prompts.extend(fallback_prompts)

            # Remove duplicates while preserving order
            prompts = prompt_service.remove_duplicate_prompts(prompts)

            # If we didn't add any new unique prompts, increment attempt counter
            if len(prompts) <= previous_count:
                attempt += 1
            else:
                attempt = 0  # Reset if we made progress

        # Ensure we have exactly the requested number of prompts
        prompts = prompts[:total_prompts]

        # Add the prompts to the database
        for prompt_text in prompts:
            prompt = Prompt(
                input_question_id=input_question.id, prompt_text=prompt_text
            )
            db.session.add(prompt)

        db.session.commit()

        # Create the tournament
        tournament = Tournament(input_question_id=input_question.id)
        db.session.add(tournament)
        db.session.commit()

        return {
            "tournament_id": tournament.id,
            "input_question": input_question.question_text,
            "prompts": [prompt.prompt_text for prompt in input_question.prompts],
        }

    def get_tournament_status(self, tournament_id):
        """
        Get comprehensive tournament status

        Args:
            tournament_id (int): ID of the tournament

        Returns:
            dict: Tournament status data
        """
        tournament = db.get_or_404(Tournament, tournament_id)

        # Get all matches organized by round
        matches_by_round = {}
        for match in tournament.rounds:
            round_num = match.round_number
            if round_num not in matches_by_round:
                matches_by_round[round_num] = []

            match_data = {
                "match_id": match.id,
                "prompt_1": match.prompt_1.prompt_text,
                "prompt_2": match.prompt_2.prompt_text,
                "prompt_1_id": match.prompt_1_id,
                "prompt_2_id": match.prompt_2_id,
                "status": match.status,
                "winner": match.winner.prompt_text if match.winner else None,
            }
            matches_by_round[round_num].append(match_data)

        # Calculate byes for each round
        byes_by_round = self._calculate_byes_by_round(tournament_id, matches_by_round)

        # Calculate tournament progress
        total_matches = len(tournament.rounds)
        completed_matches = len(
            [m for m in tournament.rounds if m.status == "completed"]
        )

        # Get current round (highest round number with pending matches, or highest completed round)
        current_round = 1
        if tournament.rounds:
            pending_rounds = [
                m.round_number for m in tournament.rounds if m.status == "pending"
            ]
            if pending_rounds:
                current_round = min(pending_rounds)
            else:
                current_round = max(m.round_number for m in tournament.rounds)

        # Get tournament winner if completed
        winner = None
        if tournament.status == "completed" and tournament.rounds:
            final_matches = [m for m in tournament.rounds if m.status == "completed"]
            if final_matches:
                # Find the match with the highest round number
                final_match = max(final_matches, key=lambda m: m.round_number)
                winner = final_match.winner.prompt_text if final_match.winner else None

        # Prepare the response data
        tournament_data = {
            "tournament_id": tournament.id,
            "input_question": tournament.input_question.question_text,
            "status": tournament.status,
            "current_round": current_round,
            "total_prompts": len(tournament.input_question.prompts),
            "prompts": [
                prompt.prompt_text for prompt in tournament.input_question.prompts
            ],
            "progress": {
                "total_matches": total_matches,
                "completed_matches": completed_matches,
                "completion_percentage": round(
                    (
                        (completed_matches / total_matches * 100)
                        if total_matches > 0
                        else 0
                    ),
                    1,
                ),
            },
            "rounds": matches_by_round,
            "byes": byes_by_round,
            "winner": winner,
        }

        return tournament_data

    def start_tournament_bracket(self, tournament_id):
        """
        Start tournament bracket by creating first round matches

        Args:
            tournament_id (int): ID of the tournament

        Returns:
            dict: Tournament bracket start data
        """
        tournament = db.get_or_404(Tournament, tournament_id)

        # Check if tournament already has matches
        if tournament.rounds:
            raise ValueError("Tournament bracket already started")

        # Get all prompts for this tournament
        prompts = tournament.input_question.prompts

        if len(prompts) < 2:
            raise ValueError("Need at least 2 prompts to start tournament")

        # Shuffle prompts for random pairing
        prompt_list = list(prompts)
        random.shuffle(prompt_list)

        # Create first round matches
        matches_created = []
        for i in range(0, len(prompt_list), 2):
            if i + 1 < len(prompt_list):  # Ensure we have a pair
                match = Match(
                    tournament_id=tournament.id,
                    prompt_1_id=prompt_list[i].id,
                    prompt_2_id=prompt_list[i + 1].id,
                    round_number=1,
                )
                db.session.add(match)
                matches_created.append(
                    {
                        "prompt_1": prompt_list[i].prompt_text,
                        "prompt_2": prompt_list[i + 1].prompt_text,
                    }
                )

        # Update tournament status
        tournament.status = "in_progress"
        db.session.commit()

        return {
            "message": "Tournament bracket started",
            "tournament_id": tournament.id,
            "round_1_matches": matches_created,
            "total_matches": len(matches_created),
        }

    def get_tournament_matches(self, tournament_id, round_number=None):
        """
        Get all matches for a tournament, optionally filtered by round

        Args:
            tournament_id (int): ID of the tournament
            round_number (int, optional): Filter by specific round

        Returns:
            dict: Tournament matches data
        """
        tournament = db.get_or_404(Tournament, tournament_id)

        matches_query = Match.query.filter_by(tournament_id=tournament.id)
        if round_number:
            matches_query = matches_query.filter_by(round_number=round_number)

        matches = matches_query.order_by(Match.round_number, Match.id).all()

        matches_data = []
        for match in matches:
            match_data = {
                "match_id": match.id,
                "round_number": match.round_number,
                "prompt_1": match.prompt_1.prompt_text,
                "prompt_2": match.prompt_2.prompt_text,
                "prompt_1_id": match.prompt_1_id,
                "prompt_2_id": match.prompt_2_id,
                "status": match.status,
                "winner": match.winner.prompt_text if match.winner else None,
            }
            matches_data.append(match_data)

        return {
            "tournament_id": tournament.id,
            "matches": matches_data,
            "total_matches": len(matches_data),
        }

    def _calculate_byes_by_round(self, tournament_id, matches_by_round):
        """Calculate byes for each round"""

        def get_active_prompts_for_round(round_num):
            """Get the set of prompts that are active (not eliminated) for a given round"""
            if round_num == 1:
                # Round 1: all tournament prompts are active
                tournament = db.session.get(Tournament, tournament_id)
                return set(p.id for p in tournament.input_question.prompts)
            else:
                # Later rounds: winners from previous round + byes from previous round
                prev_matches = Match.query.filter_by(
                    tournament_id=tournament_id, round_number=round_num - 1
                ).all()

                # Get winners from previous round
                active = set()
                prev_participating = set()

                for match in prev_matches:
                    prev_participating.add(match.prompt_1_id)
                    prev_participating.add(match.prompt_2_id)
                    if match.winner:
                        active.add(match.winner.id)

                # Get active prompts from the previous round and find byes
                prev_active = get_active_prompts_for_round(round_num - 1)
                prev_byes = prev_active - prev_participating
                active.update(prev_byes)

                return active

        byes_by_round = {}
        for round_num in matches_by_round.keys():
            # Get all prompts that participated in this round
            participating_prompts = set()
            for match_data in matches_by_round[round_num]:
                # Find the actual match object to get prompt IDs
                tournament = db.session.get(Tournament, tournament_id)
                match = next(
                    m for m in tournament.rounds if m.id == match_data["match_id"]
                )
                participating_prompts.add(match.prompt_1_id)
                participating_prompts.add(match.prompt_2_id)

            # Get active prompts for this round
            active_prompts = get_active_prompts_for_round(round_num)
            bye_prompt_ids = active_prompts - participating_prompts

            # Convert bye prompt IDs to prompt text
            bye_prompts = []
            for prompt_id in bye_prompt_ids:
                prompt = db.session.get(Prompt, prompt_id)
                if prompt:
                    bye_prompts.append(prompt.prompt_text)

            byes_by_round[round_num] = bye_prompts

        return byes_by_round


# Create a singleton instance for use across the application
tournament_service = TournamentService()
