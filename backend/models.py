from datetime import datetime, timezone

from database import db


# InputQuestion model
class InputQuestion(db.Model):
    __tablename__ = "input_questions"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    prompts = db.relationship("Prompt", backref="input_question", lazy=True)
    tournaments = db.relationship("Tournament", backref="input_question", lazy=True)


# Prompt model
class Prompt(db.Model):
    __tablename__ = "prompts"

    id = db.Column(db.Integer, primary_key=True)
    input_question_id = db.Column(
        db.Integer, db.ForeignKey("input_questions.id"), nullable=False
    )
    prompt_text = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    prompt_metadata = db.relationship("PromptMetaData", backref="prompt", lazy=True)


# Tournament model
class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)
    input_question_id = db.Column(
        db.Integer, db.ForeignKey("input_questions.id"), nullable=False
    )
    status = db.Column(db.String(50), default="active")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    rounds = db.relationship("Match", backref="tournament", lazy=True)


# Match model
class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    prompt_1_id = db.Column(db.Integer, db.ForeignKey("prompts.id"), nullable=False)
    prompt_2_id = db.Column(db.Integer, db.ForeignKey("prompts.id"), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey("prompts.id"), nullable=True)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    prompt_1 = db.relationship("Prompt", foreign_keys=[prompt_1_id])
    prompt_2 = db.relationship("Prompt", foreign_keys=[prompt_2_id])
    winner = db.relationship("Prompt", foreign_keys=[winner_id])


# PromptMetaData model
class PromptMetaData(db.Model):
    __tablename__ = "prompt_metadata"

    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompts.id"), nullable=False)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    win_count = db.Column(db.Integer, default=0)
    loss_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
