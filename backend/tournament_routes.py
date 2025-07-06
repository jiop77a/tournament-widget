from app import db
from flask import Blueprint, jsonify, request
from models import InputQuestion, Match, Prompt, PromptMetaData, Tournament

# Create a Blueprint for tournament-related routes
tournament_bp = Blueprint("tournament", __name__)


# Route to create a tournament
@tournament_bp.route("/tournament", methods=["POST"])
def create_tournament():
    data = request.json
    input_question_text = data["input_question"]

    # Create the InputQuestion
    input_question = InputQuestion(question_text=input_question_text)
    db.session.add(input_question)
    db.session.commit()

    # Generate Prompts or use provided custom prompts
    prompts = data.get("custom_prompts", auto_generate_prompts(input_question_text))

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


# Helper function to auto-generate prompts
def auto_generate_prompts(input_question):
    return [
        f"Can you tell me the capital city of {input_question.split()[-1]}?",
        f"Which city is the capital of {input_question.split()[-1]}?",
        f"Where is the capital of {input_question.split()[-1]} located?",
        f"What is the name of {input_question.split()[-1]} capital city?",
    ]


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
