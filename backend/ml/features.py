import numpy as np

FEATURE_NAMES = [
    "avg_score",
    "avg_response_time",
    "error_rate",
    "score_trend",
    "quiz_count",
]


def extract_features(user_id, db_session):
    """Build the 5-feature vector for a user from their last 5 completed sessions.

    Returns (features: np.ndarray | None, session_count: int).
    features is None when the user has no completed sessions.
    """
    from models import Session

    completed = (
        db_session.query(Session)
        .filter_by(user_id=user_id, completed=True)
        .order_by(Session.created_at.desc())
        .all()
    )
    quiz_count = len(completed)
    if quiz_count == 0:
        return None, 0

    last_five = completed[:5]
    scores = [s.quiz_score for s in last_five]
    response_times = [s.avg_response_time or 0.0 for s in last_five]
    total_errors = sum(s.error_count or 0 for s in last_five)
    total_questions = sum(s.question_count or 0 for s in last_five)

    avg_score = float(np.mean(scores))
    avg_response_time = float(np.mean(response_times))
    error_rate = total_errors / total_questions if total_questions else 0.0

    if len(scores) >= 2:
        # Oldest-first so a rising score gives a positive slope
        chronological = list(reversed(scores))
        slope = np.polyfit(range(len(chronological)), chronological, 1)[0]
        score_trend = float(slope)
    else:
        score_trend = 0.0

    features = np.array(
        [avg_score, avg_response_time, error_rate, score_trend, quiz_count]
    )
    return features, quiz_count
