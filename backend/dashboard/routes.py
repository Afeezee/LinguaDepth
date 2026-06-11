from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from models import Lesson, Progress, Question, Session, SessionAnswer, User, db

dashboard_bp = Blueprint("dashboard", __name__)


def _weekly_scores(user_id):
    """Average quiz score per day over the last 7 days (0.0–1.0)."""
    today = date.today()
    start = today - timedelta(days=6)
    sessions = (
        Session.query.filter(
            Session.user_id == user_id,
            Session.completed == True,  # noqa: E712
            Session.created_at >= datetime.combine(start, datetime.min.time()),
        ).all()
    )
    by_day = {}
    for s in sessions:
        day = s.created_at.date()
        by_day.setdefault(day, []).append(s.quiz_score)

    result = []
    for i in range(7):
        day = start + timedelta(days=i)
        scores = by_day.get(day, [])
        result.append(
            {
                "date": day.isoformat(),
                "score": round(sum(scores) / len(scores), 3) if scores else 0,
            }
        )
    return result


def _wrong_by_topic(user_id, limit=5):
    """Topics ranked by number of wrong answers, with error rate."""
    rows = (
        db.session.query(
            Lesson.topic,
            func.count(SessionAnswer.id).label("total"),
            func.sum(
                func.cast(SessionAnswer.correct == False, db.Integer)  # noqa: E712
            ).label("wrong"),
        )
        .join(Question, SessionAnswer.question_id == Question.id)
        .join(Lesson, Question.lesson_id == Lesson.id)
        .join(Session, SessionAnswer.session_id == Session.id)
        .filter(Session.user_id == user_id)
        .group_by(Lesson.topic)
        .all()
    )
    topics = [
        {
            "topic": topic,
            "count": int(wrong or 0),
            "error_rate": round((wrong or 0) / total, 3) if total else 0,
        }
        for topic, total, wrong in rows
        if (wrong or 0) > 0
    ]
    topics.sort(key=lambda t: t["count"], reverse=True)
    return topics[:limit]


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_lessons = Lesson.query.filter(
        (Lesson.path_type == "core")
        | ((Lesson.path_type == "level_path") & (Lesson.level == user.level))
    ).count()
    lessons_completed = Progress.query.filter_by(
        user_id=user.id, completed=True
    ).count()

    return jsonify(
        {
            "level": user.level,
            "xp": user.xp,
            "streak_days": user.streak_days,
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            "completion_percent": round(
                lessons_completed / total_lessons * 100 if total_lessons else 0, 1
            ),
            "weekly_scores": _weekly_scores(user.id),
            "top_weak_topics": [
                {"topic": t["topic"], "error_rate": t["error_rate"]}
                for t in _wrong_by_topic(user.id)
            ],
        }
    )


@dashboard_bp.route("/report", methods=["GET"])
@jwt_required()
def report():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404

    avg_time = (
        db.session.query(func.avg(Session.avg_response_time))
        .filter(
            Session.user_id == user.id,
            Session.completed == True,  # noqa: E712
        )
        .scalar()
    )

    return jsonify(
        {
            "weekly_scores": [
                {"date": d["date"], "avg_score": d["score"]}
                for d in _weekly_scores(user.id)
            ],
            "wrong_by_topic": [
                {"topic": t["topic"], "count": t["count"]}
                for t in _wrong_by_topic(user.id)
            ],
            "avg_quiz_time": round(float(avg_time), 1) if avg_time else 0,
        }
    )
