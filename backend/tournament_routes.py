from flask import Blueprint, jsonify, request
from models import Prompt
from services.match_service import match_service
from services.prompt_service import prompt_service
from services.tournament_service import tournament_service
from utils.error_handlers import handle_api_errors

# Create a Blueprint for tournament-related routes
tournament_bp = Blueprint("tournament", __name__)


# Route to create a tournament
@tournament_bp.route("/tournament", methods=["POST"])
@handle_api_errors
def create_tournament():
    data = request.json
    result = tournament_service.create_tournament(data)
    return jsonify(result), 201


# Route to retrieve comprehensive tournament status
@tournament_bp.route("/tournament/<int:tournament_id>/status", methods=["GET"])
@handle_api_errors
def get_tournament_status(tournament_id):
    tournament_data = tournament_service.get_tournament_status(tournament_id)
    return jsonify(tournament_data)


# Route to store the result of a match and automatically advance tournament
@tournament_bp.route("/match/<int:match_id>/result", methods=["POST"])
@handle_api_errors
def store_match_result(match_id):
    data = request.json
    winner_id = data["winner_id"]

    result = match_service.store_match_result(match_id, winner_id)
    match = result["match"]
    winner_prompt = result["winner_prompt"]
    next_round_info = result["next_round_info"]

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
        from database import db
        from models import Tournament

        tournament = db.session.get(Tournament, match.tournament_id)
        tournament.status = "completed"
        db.session.commit()

    return jsonify(response_data)


# Route to start tournament bracket (automatically create first round matches)
@tournament_bp.route("/tournament/<int:tournament_id>/start-bracket", methods=["POST"])
@handle_api_errors
def start_tournament_bracket(tournament_id):
    result = tournament_service.start_tournament_bracket(tournament_id)
    return jsonify(result), 201


# Route to get all matches for a tournament
@tournament_bp.route("/tournament/<int:tournament_id>/matches", methods=["GET"])
@handle_api_errors
def get_tournament_matches(tournament_id):
    # Optional round filter
    round_number = request.args.get("round", type=int)
    result = tournament_service.get_tournament_matches(tournament_id, round_number)
    return jsonify(result)


# Route to get all prompts (for debugging or UI)
@tournament_bp.route("/prompts", methods=["GET"])
@handle_api_errors
def get_all_prompts():
    prompts = Prompt.query.all()
    return jsonify(
        [{"id": prompt.id, "text": prompt.prompt_text} for prompt in prompts]
    )


# Route to test a prompt with OpenAI
@tournament_bp.route("/test-prompt", methods=["POST"])
@handle_api_errors
def test_prompt():
    data = request.json
    result = prompt_service.test_prompt_with_openai(data)
    return jsonify(result)
