import os

from app import db
from flask import Blueprint, jsonify, request
from models import InputQuestion, Match, Prompt, PromptMetaData, Tournament
from openai import OpenAI

# Create a Blueprint for tournament-related routes
tournament_bp = Blueprint("tournament", __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Route to create a tournament
@tournament_bp.route("/tournament", methods=["POST"])
def create_tournament():
    data = request.json
    input_question_text = data["input_question"]

    # Create the InputQuestion
    input_question = InputQuestion(question_text=input_question_text)
    db.session.add(input_question)
    db.session.commit()

    # Get custom prompts or start with empty list
    prompts = data.get("custom_prompts", [])

    # Ensure we have at least 8 prompts for the tournament
    if len(prompts) < 8:
        additional_prompts_needed = 8 - len(prompts)
        try:
            ai_generated_prompts = generate_prompts_with_ai(
                input_question_text, additional_prompts_needed
            )
            prompts.extend(ai_generated_prompts)
        except Exception as e:
            # If AI generation fails, fall back to simple variations
            print(f"AI prompt generation failed: {e}")
            fallback_prompts = generate_fallback_prompts(
                input_question_text, additional_prompts_needed
            )
            prompts.extend(fallback_prompts)

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


def generate_prompts_with_ai(input_question, num_prompts_needed):
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
                    "content": f"Generate {num_prompts_needed} different ways to ask this question: '{input_question}'. Each prompt should be unique and ask for the same information but with different phrasing, tone, or approach. Return only the prompts, one per line, without numbering or bullet points.",
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


def generate_fallback_prompts(input_question, num_prompts_needed):
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
    ]

    # Return the needed number of fallback prompts
    return fallback_templates[:num_prompts_needed]
