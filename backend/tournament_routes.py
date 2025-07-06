import os

from app import db
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

    # Get total_prompts parameter, validate it's even, default to DEFAULT_TOTAL_PROMPTS
    total_prompts = data.get("total_prompts", DEFAULT_TOTAL_PROMPTS)

    # Validate total_prompts
    if not isinstance(total_prompts, int):
        abort(400, description="total_prompts must be an integer")
    if total_prompts <= 0:
        abort(400, description="total_prompts must be a positive number")
    if total_prompts % 2 != 0:
        abort(400, description="total_prompts must be an even number")

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


# Route to retrieve tournament details by ID
@tournament_bp.route("/tournament/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    tournament = db.get_or_404(Tournament, tournament_id)

    # Prepare the response data
    tournament_data = {
        "tournament_id": tournament.id,
        "input_question": tournament.input_question.question_text,
        "status": tournament.status,
        "rounds": [],
    }

    # Add round and match data
    for match in tournament.rounds:
        match_data = {
            "round_number": match.round_number,
            "prompt_1": match.prompt_1.prompt_text,
            "prompt_2": match.prompt_2.prompt_text,
            "status": match.status,
            "winner": match.winner_id and match.winner.prompt_text,
        }
        tournament_data["rounds"].append(match_data)

    return jsonify(tournament_data)


# Route to create a new match in the tournament
@tournament_bp.route("/match", methods=["POST"])
def create_match():
    data = request.json
    tournament_id = data["tournament_id"]
    prompt_1_id = data["prompt_1_id"]
    prompt_2_id = data["prompt_2_id"]

    # Fetch the tournament and prompts
    tournament = db.get_or_404(Tournament, tournament_id)
    prompt_1 = db.get_or_404(Prompt, prompt_1_id)
    prompt_2 = db.get_or_404(Prompt, prompt_2_id)

    # Create a new match for the tournament
    round_number = len(tournament.rounds) + 1  # New round number
    match = Match(
        tournament_id=tournament.id,
        prompt_1_id=prompt_1.id,
        prompt_2_id=prompt_2.id,
        round_number=round_number,
    )

    db.session.add(match)
    db.session.commit()

    return (
        jsonify(
            {
                "match_id": match.id,
                "tournament_id": tournament.id,
                "round_number": match.round_number,
                "prompt_1": prompt_1.prompt_text,
                "prompt_2": prompt_2.prompt_text,
            }
        ),
        201,
    )


# Route to store the result of a match (which prompt won)
@tournament_bp.route("/result", methods=["POST"])
def store_result():
    data = request.json
    match_id = data["match_id"]
    winner_id = data["winner_id"]

    # Fetch the match and winner prompt
    match = db.get_or_404(Match, match_id)
    winner_prompt = db.get_or_404(Prompt, winner_id)

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
    else:
        loser_metadata.loss_count += 1

    db.session.commit()

    return jsonify({"message": "Result stored successfully!"})


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
