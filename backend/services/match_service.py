import random

from database import db
from models import Match, Prompt, PromptMetaData, Tournament


class MatchService:
    """Service for handling match-related operations"""

    def store_match_result(self, match_id, winner_id):
        """
        Store the result of a match and update metadata

        Args:
            match_id (int): ID of the match
            winner_id (int): ID of the winning prompt

        Returns:
            dict: Match result data including next round information
        """
        # Fetch the match and winner prompt
        match = db.get_or_404(Match, match_id)
        winner_prompt = db.get_or_404(Prompt, winner_id)

        # Validate that winner is one of the match participants
        if winner_id not in [match.prompt_1_id, match.prompt_2_id]:
            raise ValueError("Winner must be one of the match participants")

        # Check if match is already completed
        if match.status == "completed":
            raise ValueError("Match already completed")

        # Update match status
        match.winner_id = winner_prompt.id
        match.status = "completed"

        # Update PromptMetaData for winner
        prompt_metadata = PromptMetaData.query.filter_by(
            prompt_id=winner_prompt.id, tournament_id=match.tournament_id
        ).first()
        if not prompt_metadata:
            prompt_metadata = PromptMetaData(
                prompt_id=winner_prompt.id,
                tournament_id=match.tournament_id,
                win_count=1,
            )
            db.session.add(prompt_metadata)
        else:
            prompt_metadata.win_count += 1

        # Update PromptMetaData for loser
        loser_prompt = (
            match.prompt_1 if winner_prompt.id != match.prompt_1.id else match.prompt_2
        )
        loser_metadata = PromptMetaData.query.filter_by(
            prompt_id=loser_prompt.id, tournament_id=match.tournament_id
        ).first()
        if not loser_metadata:
            loser_metadata = PromptMetaData(
                prompt_id=loser_prompt.id,
                tournament_id=match.tournament_id,
                loss_count=1,
            )
            db.session.add(loser_metadata)
        else:
            loser_metadata.loss_count += 1

        db.session.commit()

        # Check if round is complete and create next round if needed
        next_round_info = self.check_and_create_next_round(
            match.tournament_id, match.round_number
        )

        return {
            "match": match,
            "winner_prompt": winner_prompt,
            "next_round_info": next_round_info,
        }

    def check_and_create_next_round(self, tournament_id, current_round):
        """
        Check if round is complete and create next round if needed

        Args:
            tournament_id (int): ID of the tournament
            current_round (int): Current round number

        Returns:
            dict: Information about round completion and next round creation
        """
        # Get all matches in current round
        current_round_matches = Match.query.filter_by(
            tournament_id=tournament_id, round_number=current_round
        ).all()

        # Check if all matches in current round are completed
        completed_matches = [
            m for m in current_round_matches if m.status == "completed"
        ]
        round_completed = len(completed_matches) == len(current_round_matches)

        result = {
            "round_completed": round_completed,
            "next_round_created": False,
            "tournament_completed": False,
            "next_round_number": None,
            "matches_created": [],
            "bye_prompts": [],
        }

        if not round_completed:
            return result

        # Get winners from current round
        winners = [match.winner for match in completed_matches]

        # Get all prompts that participated in this round
        participating_prompts = set()
        for match in current_round_matches:
            participating_prompts.add(match.prompt_1_id)
            participating_prompts.add(match.prompt_2_id)

        # Determine active prompts for this round (prompts that could potentially participate)
        active_prompts = self._get_active_prompts_for_round(
            tournament_id, current_round
        )
        bye_prompts = active_prompts - participating_prompts

        # Convert bye prompt IDs to prompt text for the response
        bye_prompt_texts = []
        for prompt_id in bye_prompts:
            prompt = db.session.get(Prompt, prompt_id)
            if prompt:
                bye_prompt_texts.append(prompt.prompt_text)

        result["bye_prompts"] = bye_prompt_texts

        # Total remaining contestants = winners from this round + bye prompts
        total_remaining = len(winners) + len(bye_prompts)

        # If only one contestant remains, tournament is complete
        if total_remaining == 1:
            result["tournament_completed"] = True
            return result

        # Create next round matches
        next_round_number = current_round + 1
        matches_created = []

        # Combine winners from this round with bye prompts to get all advancing contestants
        advancing_prompts = winners[:]  # Copy winners list

        # Add bye prompts (those that didn't participate in this round)
        for prompt_id in bye_prompts:
            prompt = db.session.get(Prompt, prompt_id)
            advancing_prompts.append(prompt)

        # Shuffle advancing prompts to ensure fair bye distribution across rounds
        random.shuffle(advancing_prompts)

        # Create matches for pairs of advancing prompts
        for i in range(0, len(advancing_prompts), 2):
            if i + 1 < len(advancing_prompts):  # Ensure we have a pair
                next_match = Match(
                    tournament_id=tournament_id,
                    prompt_1_id=advancing_prompts[i].id,
                    prompt_2_id=advancing_prompts[i + 1].id,
                    round_number=next_round_number,
                )
                db.session.add(next_match)
                matches_created.append(
                    {
                        "prompt_1": advancing_prompts[i].prompt_text,
                        "prompt_2": advancing_prompts[i + 1].prompt_text,
                    }
                )

        # Commit the new matches
        if matches_created:
            db.session.commit()
            result["next_round_created"] = True
            result["next_round_number"] = next_round_number
            result["matches_created"] = matches_created

        return result

    def _get_active_prompts_for_round(self, tournament_id, round_num):
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
            prev_active = self._get_active_prompts_for_round(
                tournament_id, round_num - 1
            )
            prev_byes = prev_active - prev_participating
            active.update(prev_byes)

            return active


# Create a singleton instance for use across the application
match_service = MatchService()
