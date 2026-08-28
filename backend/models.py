from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    level = db.Column(db.Text, default="beginner")  # beginner | intermediate | advanced
    xp = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("Session", backref="user", lazy=True)
    progress = db.relationship("Progress", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "level": self.level,
            "xp": self.xp,
            "streak_days": self.streak_days,
            "is_admin": bool(self.is_admin),
        }


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    # `content` is kept for backward compatibility and TTS-safe plaintext.
    # The source of truth for on-screen lesson body is `content_markdown`.
    content = db.Column(db.Text, nullable=False)
    content_markdown = db.Column(db.Text, nullable=False, default="")
    estimated_minutes = db.Column(db.Integer, default=5)
    level = db.Column(db.Text, nullable=False)  # beginner | intermediate | advanced
    topic = db.Column(db.Text, nullable=False)
    path_type = db.Column(db.Text, nullable=False)  # core | level_path
    order_index = db.Column(db.Integer, nullable=False)
    quiz_types = db.Column(db.Text, nullable=False)  # JSON array string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship("Question", backref="lesson", lazy=True)

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "content_markdown": self.content_markdown or "",
            "estimated_minutes": self.estimated_minutes or 5,
            "level": self.level,
            "topic": self.topic,
            "path_type": self.path_type,
            "order_index": self.order_index,
            "quiz_types": json.loads(self.quiz_types),
        }


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"))
    type = db.Column(db.Text, nullable=False)  # objective | theory | oral
    difficulty = db.Column(db.Text, nullable=False)  # easy | medium | hard
    level = db.Column(db.Text, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON array of 4 strings (objective only)
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_answer=False):
        import json
        import random

        options = json.loads(self.options) if self.options else None
        if options:
            # Shuffle at serve time so the correct answer's position varies
            # between quizzes (generated banks bias it toward early slots)
            random.shuffle(options)
        data = {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "type": self.type,
            "difficulty": self.difficulty,
            "level": self.level,
            "question_text": self.question_text,
            "options": options,
        }
        if include_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"] = self.explanation
        return data


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"))
    quiz_score = db.Column(db.Float, nullable=False, default=0.0)  # 0.0 to 1.0
    avg_response_time = db.Column(db.Float)  # seconds per question
    error_count = db.Column(db.Integer, default=0)
    question_count = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship("SessionAnswer", backref="session", lazy=True)


class SessionAnswer(db.Model):
    __tablename__ = "session_answers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    user_answer = db.Column(db.Text)
    correct = db.Column(db.Boolean)
    response_time = db.Column(db.Float)  # seconds for this question
    llm_feedback = db.Column(db.Text)  # populated for theory and oral types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship("Question", lazy=True)


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"))
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)


class PasswordResetToken(db.Model):
    """A time-limited token that lets a user set a new password.

    Only the SHA-256 hash of the token ever lives in the database, so a
    leaked database dump never gives an attacker a working reset link.
    The plaintext token is delivered to the user (by email when SMTP is
    configured, or by a server-log fallback for dev environments).
    """

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token_hash = db.Column(db.Text, nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SeenQuestion(db.Model):
    """Every question a user has already been served, regardless of session.

    The quiz start route consults this to guarantee a learner never sees the
    same question twice until the lesson-and-type pool is genuinely exhausted.
    """

    __tablename__ = "seen_questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id"), nullable=False
    )
    seen_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_seen_user_question"),
    )
