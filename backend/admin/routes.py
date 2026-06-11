import csv
import io
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from models import Lesson, Progress, Question, Session, SessionAnswer, User, db

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(int(get_jwt_identity()))
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


# ---------- User management ----------

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    search = (request.args.get("search") or "").strip().lower()
    query = User.query
    if search:
        query = query.filter(
            (func.lower(User.name).contains(search))
            | (func.lower(User.email).contains(search))
        )
    users = query.order_by(User.created_at.desc()).all()

    session_counts = dict(
        db.session.query(Session.user_id, func.count(Session.id))
        .filter(Session.completed == True)  # noqa: E712
        .group_by(Session.user_id)
        .all()
    )
    avg_scores = dict(
        db.session.query(Session.user_id, func.avg(Session.quiz_score))
        .filter(Session.completed == True)  # noqa: E712
        .group_by(Session.user_id)
        .all()
    )

    return jsonify(
        [
            {
                **u.to_dict(),
                "sessions_completed": session_counts.get(u.id, 0),
                "avg_score": round(float(avg_scores[u.id]), 3)
                if u.id in avg_scores
                else None,
                "last_active": u.last_active.isoformat() if u.last_active else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    )


@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    if "level" in data:
        if data["level"] not in ("beginner", "intermediate", "advanced"):
            return jsonify({"error": "Invalid level"}), 400
        user.level = data["level"]

    if "is_admin" in data:
        if user.id == int(get_jwt_identity()) and not data["is_admin"]:
            return jsonify({"error": "You cannot remove your own admin access"}), 400
        user.is_admin = bool(data["is_admin"])

    db.session.commit()
    return jsonify({"user": user.to_dict()})


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    if user_id == int(get_jwt_identity()):
        return jsonify({"error": "You cannot delete your own account"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    session_ids = [s.id for s in Session.query.filter_by(user_id=user_id).all()]
    if session_ids:
        SessionAnswer.query.filter(
            SessionAnswer.session_id.in_(session_ids)
        ).delete(synchronize_session=False)
    Session.query.filter_by(user_id=user_id).delete()
    Progress.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"deleted": user_id})


# ---------- Analytics ----------

def _daily_counts(rows, days):
    """rows: list of (date, value). Fill gaps over the last `days` days."""
    by_day = {d: v for d, v in rows}
    today = date.today()
    return [
        {
            "date": (today - timedelta(days=i)).isoformat(),
            "count": by_day.get(today - timedelta(days=i), 0),
        }
        for i in range(days - 1, -1, -1)
    ]


@admin_bp.route("/analytics", methods=["GET"])
@admin_required
def analytics():
    today = date.today()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = datetime.combine(today - timedelta(days=13), datetime.min.time())

    total_users = User.query.count()
    sessions_completed = Session.query.filter_by(completed=True).count()
    avg_score = (
        db.session.query(func.avg(Session.quiz_score))
        .filter(Session.completed == True)  # noqa: E712
        .scalar()
    )
    active_today = User.query.filter(User.last_active == today).count()
    active_week = User.query.filter(User.last_active >= week_ago).count()

    level_distribution = [
        {"level": level, "count": count}
        for level, count in db.session.query(User.level, func.count(User.id))
        .group_by(User.level)
        .all()
    ]

    signup_rows = (
        db.session.query(func.date(User.created_at), func.count(User.id))
        .filter(User.created_at >= two_weeks_ago)
        .group_by(func.date(User.created_at))
        .all()
    )
    session_rows = (
        db.session.query(func.date(Session.created_at), func.count(Session.id))
        .filter(
            Session.created_at >= two_weeks_ago,
            Session.completed == True,  # noqa: E712
        )
        .group_by(func.date(Session.created_at))
        .all()
    )
    # SQLite returns date strings from func.date(); normalise to date objects
    signup_rows = [
        (date.fromisoformat(d) if isinstance(d, str) else d, c) for d, c in signup_rows
    ]
    session_rows = [
        (date.fromisoformat(d) if isinstance(d, str) else d, c) for d, c in session_rows
    ]

    weak_topics = (
        db.session.query(
            Lesson.topic,
            func.count(SessionAnswer.id).label("total"),
            func.sum(
                func.cast(SessionAnswer.correct == False, db.Integer)  # noqa: E712
            ).label("wrong"),
        )
        .join(Question, SessionAnswer.question_id == Question.id)
        .join(Lesson, Question.lesson_id == Lesson.id)
        .group_by(Lesson.topic)
        .all()
    )
    weak = sorted(
        (
            {
                "topic": topic,
                "wrong": int(wrong or 0),
                "error_rate": round((wrong or 0) / total, 3) if total else 0,
            }
            for topic, total, wrong in weak_topics
            if (wrong or 0) > 0
        ),
        key=lambda t: t["wrong"],
        reverse=True,
    )[:10]

    return jsonify(
        {
            "totals": {
                "users": total_users,
                "sessions_completed": sessions_completed,
                "lessons": Lesson.query.count(),
                "questions": Question.query.count(),
                "avg_score": round(float(avg_score), 3) if avg_score else 0,
                "active_today": active_today,
                "active_week": active_week,
            },
            "level_distribution": level_distribution,
            "signups_daily": _daily_counts(signup_rows, 14),
            "sessions_daily": _daily_counts(session_rows, 14),
            "weak_topics": weak,
        }
    )


# ---------- CSV export ----------

EXPORTS = {
    "users": (
        "SELECT id, name, email, level, xp, streak_days, is_admin, "
        "last_active, created_at FROM users",
    ),
    "sessions": (
        "SELECT s.id, s.user_id, u.email AS user_email, s.lesson_id, "
        "l.title AS lesson_title, s.quiz_score, s.avg_response_time, "
        "s.error_count, s.question_count, s.completed, s.created_at "
        "FROM sessions s "
        "LEFT JOIN users u ON u.id = s.user_id "
        "LEFT JOIN lessons l ON l.id = s.lesson_id",
    ),
    "answers": (
        "SELECT a.id, a.session_id, s.user_id, a.question_id, "
        "q.type AS question_type, q.difficulty, l.topic, a.user_answer, "
        "a.correct, a.response_time, a.llm_feedback, a.created_at "
        "FROM session_answers a "
        "LEFT JOIN sessions s ON s.id = a.session_id "
        "LEFT JOIN questions q ON q.id = a.question_id "
        "LEFT JOIN lessons l ON l.id = q.lesson_id",
    ),
    "questions": (
        "SELECT id, lesson_id, type, difficulty, level, question_text, "
        "options, correct_answer, explanation, created_at FROM questions",
    ),
    "progress": (
        "SELECT p.id, p.user_id, u.email AS user_email, p.lesson_id, "
        "l.title AS lesson_title, p.completed, p.completed_at "
        "FROM progress p "
        "LEFT JOIN users u ON u.id = p.user_id "
        "LEFT JOIN lessons l ON l.id = p.lesson_id",
    ),
}


@admin_bp.route("/export/<dataset>", methods=["GET"])
@admin_required
def export_csv(dataset):
    if dataset not in EXPORTS:
        return (
            jsonify({"error": f"Unknown dataset. Choose from: {', '.join(EXPORTS)}"}),
            400,
        )

    result = db.session.execute(db.text(EXPORTS[dataset][0]))
    rows = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(result.keys())
    writer.writerows(rows)

    filename = f"linguadepth_{dataset}_{date.today().isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
