import os
import random

from database import db
from flask import Blueprint, abort, jsonify, request
from models import InputQuestion, Match, Prompt, PromptMetaData, Tournament
from openai import OpenAI

# Create a Blueprint for tournament-related routes
tournament_bp = Blueprint("tournament", __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
DEFAULT_TOTAL_PROMPTS = 8


# Route to create a tournament
@tournament_bp.route("/tournament", methods=["POST"])
def create_tournament():
    data = request.json

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
    prompts = remove_duplicate_prompts(prompts)

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
            ai_generated_prompts = generate_prompts_with_ai(
                input_question_text, additional_prompts_needed, existing_prompts=prompts
            )
            prompts.extend(ai_generated_prompts)
        except Exception as e:
            # If AI generation fails, fall back to simple variations
            print(f"AI prompt generation failed: {e}")
            fallback_prompts = generate_fallback_prompts(
                input_question_text, additional_prompts_needed, existing_prompts=prompts
            )
            prompts.extend(fallback_prompts)

        # Remove duplicates while preserving order
        prompts = remove_duplicate_prompts(prompts)

        # If we didn't add any new unique prompts, increment attempt counter
        if len(prompts) <= previous_count:
            attempt += 1
        else:
            attempt = 0  # Reset if we made progress

    # Ensure we have exactly the requested number of prompts
    prompts = prompts[:total_prompts]

    # Add the prompts to the database
    for prompt_text in prompts:
        prompt = Prompt(input_question_id=input_question.id, prompt_text=prompt_text)
        db.session.add(prompt)

    db.session.commit()

    # Create the tournament
    tournament = Tournament(input_question_id=input_question.id)
    db.session.add(tournament)
    db.session.commit()

    return (
        jsonify(
            {
                "tournament_id": tournament.id,
                "input_question": input_question.question_text,
                "prompts": [prompt.prompt_text for prompt in input_question.prompts],
            }
        ),
        201,
    )


# Route to retrieve comprehensive tournament status
@tournament_bp.route("/tournament/<int:tournament_id>/status", methods=["GET"])
def get_tournament_status(tournament_id):
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
    def get_active_prompts_for_round(round_num):
        """Get the set of prompts that are active (not eliminated) for a given round"""
        if round_num == 1:
            # Round 1: all tournament prompts are active
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
            match = next(m for m in tournament.rounds if m.id == match_data["match_id"])
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

    # Calculate tournament progress
    total_matches = len(tournament.rounds)
    completed_matches = len([m for m in tournament.rounds if m.status == "completed"])

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
        "prompts": [prompt.prompt_text for prompt in tournament.input_question.prompts],
        "progress": {
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "completion_percentage": round(
                (completed_matches / total_matches * 100) if total_matches > 0 else 0, 1
            ),
        },
        "rounds": matches_by_round,
        "byes": byes_by_round,
        "winner": winner,
    }

    return jsonify(tournament_data)


# Route to store the result of a match and automatically advance tournament
@tournament_bp.route("/match/<int:match_id>/result", methods=["POST"])
def store_match_result(match_id):
    data = request.json
    winner_id = data["winner_id"]

    # Fetch the match and winner prompt
    match = db.get_or_404(Match, match_id)
    winner_prompt = db.get_or_404(Prompt, winner_id)

    # Validate that winner is one of the match participants
    if winner_id not in [match.prompt_1_id, match.prompt_2_id]:
        return jsonify({"error": "Winner must be one of the match participants"}), 400

    # Check if match is already completed
    if match.status == "completed":
        return jsonify({"error": "Match already completed"}), 400

    # Update match status
    match.winner_id = winner_prompt.id
    match.status = "completed"

    # Update PromptMetaData for winner
    prompt_metadata = PromptMetaData.query.filter_by(
        prompt_id=winner_prompt.id, tournament_id=match.tournament_id
    ).first()
    if not prompt_metadata:
        prompt_metadata = PromptMetaData(
            prompt_id=winner_prompt.id, tournament_id=match.tournament_id, win_count=1
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
            prompt_id=loser_prompt.id, tournament_id=match.tournament_id, loss_count=1
        )
        db.session.add(loser_metadata)
    else:
        loser_metadata.loss_count += 1

    db.session.commit()

    # Check if round is complete and create next round if needed
    next_round_info = _check_and_create_next_round(
        match.tournament_id, match.round_number
    )

    response_data = {
        "message": "Match result stored successfully",
        "match_id": match.id,
        "winner": winner_prompt.prompt_text,
        "round_completed": next_round_info["round_completed"],
    }

    if next_round_info["next_round_created"]:
        response_data["next_round"] = next_round_info["next_round_number"]
        response_data["next_round_matches"] = next_round_info["matches_created"]

        # Include bye information as array
        bye_prompts = next_round_info["bye_prompts"]
        if bye_prompts:
            response_data["bye_prompts"] = bye_prompts

    if next_round_info["tournament_completed"]:
        response_data["tournament_completed"] = True
        response_data["tournament_winner"] = winner_prompt.prompt_text
        # Update tournament status
        tournament = db.session.get(Tournament, match.tournament_id)
        tournament.status = "completed"
        db.session.commit()

    return jsonify(response_data)


# Helper function to check if round is complete and create next round
def _check_and_create_next_round(tournament_id, current_round):
    # Get all matches in current round
    current_round_matches = Match.query.filter_by(
        tournament_id=tournament_id, round_number=current_round
    ).all()

    # Check if all matches in current round are completed
    completed_matches = [m for m in current_round_matches if m.status == "completed"]
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

    tournament = db.session.get(Tournament, tournament_id)

    # Determine active prompts for this round (prompts that could potentially participate)
    def get_active_prompts_for_round(round_num):
        """Get the set of prompts that are active (not eliminated) for a given round"""
        if round_num == 1:
            # Round 1: all tournament prompts are active
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

    active_prompts = get_active_prompts_for_round(current_round)
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


# Route to start tournament bracket (automatically create first round matches)
@tournament_bp.route("/tournament/<int:tournament_id>/start-bracket", methods=["POST"])
def start_tournament_bracket(tournament_id):
    tournament = db.get_or_404(Tournament, tournament_id)

    # Check if tournament already has matches
    if tournament.rounds:
        return jsonify({"error": "Tournament bracket already started"}), 400

    # Get all prompts for this tournament
    prompts = tournament.input_question.prompts

    if len(prompts) < 2:
        return jsonify({"error": "Need at least 2 prompts to start tournament"}), 400

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

    return (
        jsonify(
            {
                "message": "Tournament bracket started",
                "tournament_id": tournament.id,
                "round_1_matches": matches_created,
                "total_matches": len(matches_created),
            }
        ),
        201,
    )


# Route to get all matches for a tournament
@tournament_bp.route("/tournament/<int:tournament_id>/matches", methods=["GET"])
def get_tournament_matches(tournament_id):
    tournament = db.get_or_404(Tournament, tournament_id)

    # Optional round filter
    round_number = request.args.get("round", type=int)

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

    return jsonify(
        {
            "tournament_id": tournament.id,
            "matches": matches_data,
            "total_matches": len(matches_data),
        }
    )


# Route to get all prompts (for debugging or UI)
@tournament_bp.route("/prompts", methods=["GET"])
def get_all_prompts():
    prompts = Prompt.query.all()
    return jsonify(
        [{"id": prompt.id, "text": prompt.prompt_text} for prompt in prompts]
    )


# Route to test a prompt with OpenAI
@tournament_bp.route("/test-prompt", methods=["POST"])
def test_prompt():
    data = request.json

    # Validate required fields
    prompt_text = data.get("prompt")
    if not prompt_text or not prompt_text.strip():
        abort(400, description="Prompt is required and cannot be empty")

    # Optional parameters with defaults
    model = data.get("model", "gpt-3.5-turbo")
    max_tokens = data.get("max_tokens", 150)
    temperature = data.get("temperature", 0.7)

    # Validate parameters
    if not isinstance(max_tokens, int) or max_tokens <= 0 or max_tokens > 4000:
        abort(400, description="max_tokens must be an integer between 1 and 4000")

    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        abort(400, description="temperature must be a number between 0 and 2")

    if model not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
        abort(
            400, description="model must be one of: gpt-3.5-turbo, gpt-4, gpt-4-turbo"
        )

    try:
        # Send prompt to OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt_text,
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract the response
        ai_response = response.choices[0].message.content.strip()

        return jsonify(
            {
                "prompt": prompt_text,
                "response": ai_response,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        )

    except Exception as e:
        print(f"Error testing prompt with OpenAI: {e}")
        abort(500, description=f"Failed to test prompt: {str(e)}")


def remove_duplicate_prompts(prompts):
    """Remove duplicate prompts while preserving order"""
    unique_prompts = []
    seen = set()
    for prompt in prompts:
        normalized = prompt.lower().strip()
        if normalized not in seen and normalized:  # Also skip empty prompts
            unique_prompts.append(prompt)
            seen.add(normalized)
    return unique_prompts


def _build_ai_prompt_content(input_question, num_prompts_needed, existing_prompts):
    """Build the content for the AI prompt, including existing prompts to avoid"""
    base_content = f"Generate {num_prompts_needed} different ways to ask this question: '{input_question}'. Each prompt should be unique and ask for the same information but with different phrasing, tone, or approach."

    if existing_prompts:
        existing_list = "\n".join(f"- {prompt}" for prompt in existing_prompts)
        base_content += f"\n\nAVOID creating prompts similar to these existing ones:\n{existing_list}"

    base_content += (
        "\n\nReturn only the prompts, one per line, without numbering or bullet points."
    )
    return base_content


def generate_prompts_with_ai(input_question, num_prompts_needed, existing_prompts=None):
    """Generate additional prompts using ChatGPT API"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates diverse prompt variations for AI testing. Generate prompts that ask the same question in different ways, with varying styles, formality levels, and approaches.",
                },
                {
                    "role": "user",
                    "content": _build_ai_prompt_content(
                        input_question, num_prompts_needed, existing_prompts
                    ),
                },
            ],
            max_tokens=500,
            temperature=0.8,
        )

        # Parse the response to extract individual prompts
        generated_text = response.choices[0].message.content.strip()
        prompts = [
            prompt.strip() for prompt in generated_text.split("\n") if prompt.strip()
        ]

        # Return only the number of prompts we need
        return prompts[:num_prompts_needed]

    except Exception as e:
        print(f"Error generating prompts with AI: {e}")
        raise e


def generate_fallback_prompts(
    input_question, num_prompts_needed, existing_prompts=None
):
    """Generate simple fallback prompts if AI generation fails"""
    fallback_templates = [
        f"Please tell me: {input_question}",
        f"I would like to know: {input_question}",
        f"Could you explain: {input_question}",
        f"Help me understand: {input_question}",
        f"What is the answer to: {input_question}",
        f"Can you provide information about: {input_question}",
        f"I need to know: {input_question}",
        f"Please clarify: {input_question}",
        f"Can you help me with: {input_question}",
        f"I'm curious about: {input_question}",
        f"Could you describe: {input_question}",
        f"What can you tell me about: {input_question}",
    ]

    # Filter out any that are similar to existing prompts
    if existing_prompts:
        existing_normalized = {prompt.lower().strip() for prompt in existing_prompts}
        fallback_templates = [
            template
            for template in fallback_templates
            if template.lower().strip() not in existing_normalized
        ]

    # Return the needed number of fallback prompts
    return fallback_templates[:num_prompts_needed]
