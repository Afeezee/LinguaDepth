import random

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Lesson, Progress, Question, User, db

lessons_bp = Blueprint("lessons", __name__)


@lessons_bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required()
def list_lessons():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404

    path_type = request.args.get("path_type")
    level = request.args.get("level", user.level)

    query = Lesson.query
    if path_type:
        query = query.filter_by(path_type=path_type)
    else:
        # Default: core lessons + the user's level path
        query = query.filter(
            (Lesson.path_type == "core")
            | ((Lesson.path_type == "level_path") & (Lesson.level == level))
        )
    lessons = query.all()
    lessons.sort(key=lambda l: (0 if l.path_type == "core" else 1, l.order_index))

    completed_ids = {
        p.lesson_id
        for p in Progress.query.filter_by(user_id=user.id, completed=True).all()
    }

    result = []
    for lesson in lessons:
        data = lesson.to_dict()
        data["completed"] = lesson.id in completed_ids
        result.append(data)
    return jsonify(result)


@lessons_bp.route("/placement", methods=["GET"])
def placement_quiz():
    """10 objective questions mixed across levels. No auth required."""
    questions = []
    per_level = {"beginner": 4, "intermediate": 3, "advanced": 3}
    for level, count in per_level.items():
        pool = Question.query.filter_by(type="objective", level=level).all()
        random.shuffle(pool)
        questions.extend(pool[:count])

    # Top up from any level if a band had too few questions
    if len(questions) < 10:
        have = {q.id for q in questions}
        extra = [
            q
            for q in Question.query.filter_by(type="objective").all()
            if q.id not in have
        ]
        random.shuffle(extra)
        questions.extend(extra[: 10 - len(questions)])

    if not questions:
        return (
            jsonify(
                {
                    "error": "Placement quiz unavailable. Seed starter questions first."
                }
            ),
            503,
        )

    random.shuffle(questions)
    return jsonify([q.to_dict() for q in questions[:10]])


@lessons_bp.route("/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    user = User.query.get(int(get_jwt_identity()))
    progress = Progress.query.filter_by(
        user_id=user.id, lesson_id=lesson.id, completed=True
    ).first()

    data = lesson.to_dict()
    data["completed"] = progress is not None
    return jsonify(data)
