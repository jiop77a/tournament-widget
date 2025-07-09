"""
Test error handling consistency across API routes
"""

import json

import pytest
from app import app
from database import db


@pytest.fixture
def client():
    """Create a test client"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


class TestErrorHandling:
    """Test consistent error handling across API routes"""

    def test_tournament_not_found_returns_consistent_json(self, client):
        """Test that 404 errors return consistent JSON format"""
        response = client.get("/api/tournament/99999/status")

        assert response.status_code == 404
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_invalid_tournament_creation_returns_400(self, client):
        """Test that validation errors return 400 with consistent format"""
        response = client.post(
            "/api/tournament", json={"input_question": ""}
        )  # Empty question

        assert response.status_code == 400
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_invalid_match_result_returns_404(self, client):
        """Test that match operations on nonexistent match return 404"""
        response = client.post("/api/match/99999/result", json={"winner_id": 1})

        assert response.status_code == 404
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_start_bracket_nonexistent_tournament_returns_404(self, client):
        """Test that starting bracket for nonexistent tournament returns 404"""
        response = client.post("/api/tournament/99999/start-bracket")

        assert response.status_code == 404
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_get_matches_nonexistent_tournament_returns_404(self, client):
        """Test that getting matches for nonexistent tournament returns 404"""
        response = client.get("/api/tournament/99999/matches")

        assert response.status_code == 404
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)
