import random
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from llm.grader import grade_theory_answer
from llm.validator import validate_oral_answer
from ml.classifier import ProficiencyClassifier
from models import Lesson, Progress, Question, Session, SessionAnswer, User, db

quiz_bp = Blueprint("quiz", __name__)

MAX_QUESTIONS_PER_QUIZ = 5

XP_OBJECTIVE_CORRECT = 10
XP_THEORY_PASS = 15
XP_ORAL_PASS = 20
XP_LESSON_COMPLETE = 50


def _difficulty_for_user(user_id):
    """Pick a difficulty band from the user's most recent completed session score."""
    last = (
        Session.query.filter_by(user_id=user_id, completed=True)
        .order_by(Session.created_at.desc())
        .first()
    )
    if last is None:
        return "easy"
    if last.quiz_score < 0.5:
        return "easy"
    if last.quiz_score < 0.75:
        return "medium"
    return "hard"


@quiz_bp.route("/start", methods=["POST"])
@jwt_required()
def start_quiz():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}
    lesson_id = data.get("lesson_id")

    lesson = Lesson.query.get(lesson_id) if lesson_id else None
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    difficulty = _difficulty_for_user(user.id)

    answered_ids = {
        row[0]
        for row in db.session.query(SessionAnswer.question_id)
        .join(Session, SessionAnswer.session_id == Session.id)
        .filter(Session.user_id == user.id)
        .all()
    }

    pool = Question.query.filter_by(lesson_id=lesson.id).all()
    if not pool:
        return jsonify({"error": "No questions available for this lesson"}), 404
    random.shuffle(pool)

    # Prefer the user's difficulty band and questions they haven't seen yet;
    # only repeat already-answered questions when the lesson has nothing new.
    tiers = [
        [q for q in pool if q.difficulty == difficulty and q.id not in answered_ids],
        [q for q in pool if q.difficulty != difficulty and q.id not in answered_ids],
        [q for q in pool if q.difficulty == difficulty and q.id in answered_ids],
        [q for q in pool if q.difficulty != difficulty and q.id in answered_ids],
    ]
    questions = [q for tier in tiers for q in tier][:MAX_QUESTIONS_PER_QUIZ]
    random.shuffle(questions)

    session = Session(
        user_id=user.id,
        lesson_id=lesson.id,
        quiz_score=0.0,
        question_count=len(questions),
    )
    db.session.add(session)
    db.session.commit()

    return jsonify(
        {
            "session_id": session.id,
            "questions": [q.to_dict() for q in questions],
        }
    )


@quiz_bp.route("/answer", methods=["POST"])
@jwt_required()
def submit_answer():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}

    session_id = data.get("session_id")
    question_id = data.get("question_id")
    answer = (data.get("answer") or "").strip()
    skipped = bool(data.get("skipped"))
    response_time_ms = data.get("response_time_ms", 0)

    session = Session.query.get(session_id) if session_id else None
    if not session or session.user_id != user.id:
        return jsonify({"error": "Session not found"}), 404
    if session.completed:
        return jsonify({"error": "Session already completed"}), 400

    question = Question.query.get(question_id) if question_id else None
    if not question:
        return jsonify({"error": "Question not found"}), 404
    if not answer and not skipped:
        return jsonify({"error": "Answer is required"}), 400

    response_time = (response_time_ms or 0) / 1000.0

    if skipped:
        answer = answer or "(skipped)"
        correct = False
        xp_earned = 0
        feedback = None
        result = {
            "correct": False,
            "skipped": True,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "xp_earned": 0,
        }
    elif question.type == "objective":
        correct = answer.strip().lower() == question.correct_answer.strip().lower()
        xp_earned = XP_OBJECTIVE_CORRECT if correct else 0
        result = {
            "correct": correct,
            "explanation": question.explanation,
            "correct_answer": question.correct_answer,
            "xp_earned": xp_earned,
        }
        feedback = None
    elif question.type == "theory":
        graded = grade_theory_answer(
            question.question_text, question.correct_answer, answer, user.level
        )
        correct = graded["correct"]
        xp_earned = XP_THEORY_PASS if graded["score"] >= 70 else 0
        feedback = graded["feedback"]
        result = {
            "correct": correct,
            "score": graded["score"],
            "feedback": feedback,
            "xp_earned": xp_earned,
        }
    elif question.type == "oral":
        validated = validate_oral_answer(
            question.question_text, question.correct_answer, answer, user.level
        )
        correct = validated["correct"]
        xp_earned = XP_ORAL_PASS if validated["score"] >= 70 else 0
        feedback = validated["feedback"]
        result = {
            "correct": correct,
            "score": validated["score"],
            "feedback": feedback,
            "xp_earned": xp_earned,
        }
    else:
        return jsonify({"error": f"Unknown question type: {question.type}"}), 400

    db.session.add(
        SessionAnswer(
            session_id=session.id,
            question_id=question.id,
            user_answer=answer,
            correct=correct,
            response_time=response_time,
            llm_feedback=feedback,
        )
    )
    if not correct:
        session.error_count = (session.error_count or 0) + 1
    user.xp = (user.xp or 0) + xp_earned
    db.session.commit()

    return jsonify(result)


def _update_streak(user, today):
    if user.last_active == today:
        return False
    if user.last_active == today - timedelta(days=1):
        user.streak_days = (user.streak_days or 0) + 1
    else:
        user.streak_days = 1
    user.last_active = today
    return True


@quiz_bp.route("/complete", methods=["POST"])
@jwt_required()
def complete_quiz():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")

    session = Session.query.get(session_id) if session_id else None
    if not session or session.user_id != user.id:
        return jsonify({"error": "Session not found"}), 404
    if session.completed:
        return jsonify({"error": "Session already completed"}), 400

    answers = SessionAnswer.query.filter_by(session_id=session.id).all()
    answered = len(answers)
    correct_count = sum(1 for a in answers if a.correct)

    session.quiz_score = correct_count / answered if answered else 0.0
    session.avg_response_time = (
        sum(a.response_time or 0 for a in answers) / answered if answered else 0.0
    )
    session.error_count = answered - correct_count
    session.question_count = answered
    session.completed = True

    xp_earned = XP_LESSON_COMPLETE
    user.xp = (user.xp or 0) + XP_LESSON_COMPLETE

    progress = Progress.query.filter_by(
        user_id=user.id, lesson_id=session.lesson_id
    ).first()
    if not progress:
        progress = Progress(user_id=user.id, lesson_id=session.lesson_id)
        db.session.add(progress)
    progress.completed = True
    progress.completed_at = datetime.utcnow()

    streak_updated = _update_streak(user, date.today())
    db.session.commit()

    classifier = ProficiencyClassifier()
    promotion = classifier.should_promote(user.id, db.session)

    level_changed = False
    new_level = user.level
    if promotion.get("should_promote"):
        user.level = promotion["predicted_level"]
        new_level = user.level
        level_changed = True
        db.session.commit()

    return jsonify(
        {
            "final_score": session.quiz_score,
            "level_changed": level_changed,
            "new_level": new_level,
            "xp_earned": xp_earned,
            "streak_updated": streak_updated,
            "streak_days": user.streak_days,
        }
    )


@quiz_bp.route("/placement/submit", methods=["POST"])
@jwt_required(optional=True)
def submit_placement():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers") or []
    if not answers:
        return jsonify({"error": "No answers submitted"}), 400

    correct = 0
    for item in answers:
        question = Question.query.get(item.get("question_id"))
        if question and (item.get("answer") or "").strip().lower() == \
                question.correct_answer.strip().lower():
            correct += 1

    ratio = correct / len(answers)
    if ratio < 0.4:
        level = "beginner"
    elif ratio < 0.75:
        level = "intermediate"
    else:
        level = "advanced"

    identity = get_jwt_identity()
    if identity:
        user = User.query.get(int(identity))
        if user:
            user.level = level
            db.session.commit()

    messages = {
        "beginner": "Great start! We'll begin with the foundations and build up together.",
        "intermediate": "Nice work! You have a solid base — let's sharpen your skills.",
        "advanced": "Impressive! You're ready for advanced material.",
    }
    return jsonify({"level": level, "message": messages[level], "score": correct})
