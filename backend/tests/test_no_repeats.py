"""End-to-end assertion that a user never sees the same question twice
until the lesson × type pool is genuinely exhausted.

The test spins up an in-memory SQLite app, seeds a single core lesson
with a small but realistic question pool, simulates a user completing
its quiz 15 times back-to-back, and asserts zero question-id overlap
across all 15 attempts.

Run from the backend/ directory:
    python -m pytest tests/test_no_repeats.py -v
    python tests/test_no_repeats.py        # runs the assertions directly
"""
import json
import os
import sys
import tempfile
from pathlib import Path

# Force an isolated SQLite file (the app's config re-anchors bare sqlite paths
# relative to the backend dir, so we hand it an absolute path).
_TMP_DB = Path(tempfile.mkdtemp(prefix="linguadepth-test-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from models import (  # noqa: E402
    Lesson,
    Question,
    SeenQuestion,
    User,
    db,
)
from quiz.routes import (  # noqa: E402
    MAX_QUESTIONS_PER_QUIZ,
    _select_questions_for_type,
    _split_per_type,
)


ATTEMPTS = 15
# The runtime splits MAX_QUESTIONS_PER_QUIZ (=5) into 3 of type[0] + 2 of
# type[1], so the type-0 pool has to be at least ATTEMPTS * 3 = 45 to avoid
# genuine exhaustion within the test window. 50 is a comfortable margin.
POOL_PER_TYPE = 50


def _seed_test_data(app):
    with app.app_context():
        db.create_all()
        user = User(name="Test", email="t@t.com", password_hash="x", level="beginner")
        db.session.add(user)

        lesson = Lesson(
            title="No-Repeats Test Lesson",
            content="body",
            content_markdown="## body",
            estimated_minutes=5,
            level="beginner",
            topic="test",
            path_type="core",
            order_index=1,
            quiz_types=json.dumps(["objective", "theory"]),
        )
        db.session.add(lesson)
        db.session.commit()

        for qtype in ("objective", "theory"):
            for i in range(POOL_PER_TYPE):
                difficulty = ("easy", "medium", "hard")[i % 3]
                if qtype == "objective":
                    options = [f"opt{j}-{i}" for j in range(4)]
                    correct = options[0]
                    q = Question(
                        lesson_id=lesson.id,
                        type=qtype,
                        difficulty=difficulty,
                        level="beginner",
                        question_text=f"{qtype} q{i}?",
                        options=json.dumps(options),
                        correct_answer=correct,
                        explanation=f"exp{i}",
                    )
                else:
                    q = Question(
                        lesson_id=lesson.id,
                        type=qtype,
                        difficulty=difficulty,
                        level="beginner",
                        question_text=f"{qtype} q{i}?",
                        options=None,
                        correct_answer=f"answer {i}",
                        explanation=f"exp{i}",
                    )
                db.session.add(q)
        db.session.commit()
        return user.id, lesson.id


def _run_one_attempt(user_id: int, lesson_id: int, active_types: list) -> list:
    split = _split_per_type(active_types)
    picked = []
    for qtype, count in split.items():
        picked.extend(
            _select_questions_for_type(user_id, lesson_id, qtype, "easy", count)
        )
    return [q.id for q in picked]


def test_no_repeats_across_15_attempts():
    app = create_app()
    user_id, lesson_id = _seed_test_data(app)
    active_types = ["objective", "theory"]

    seen_this_run = set()
    per_attempt = []

    with app.app_context():
        for attempt in range(1, ATTEMPTS + 1):
            ids = _run_one_attempt(user_id, lesson_id, active_types)
            per_attempt.append(ids)

            assert len(ids) == MAX_QUESTIONS_PER_QUIZ, (
                f"Attempt {attempt}: expected {MAX_QUESTIONS_PER_QUIZ} "
                f"questions, got {len(ids)}"
            )
            overlap = seen_this_run.intersection(ids)
            assert not overlap, (
                f"Attempt {attempt}: repeated question ids {overlap} — "
                f"selection logic served a question the user already saw."
            )
            seen_this_run.update(ids)

        # After 15 attempts of 5 questions each, we've served 75 unique ids
        # out of a pool of 80. The seen_questions table should reflect that.
        total_seen = SeenQuestion.query.filter_by(user_id=user_id).count()
        assert total_seen == ATTEMPTS * MAX_QUESTIONS_PER_QUIZ, (
            f"Expected {ATTEMPTS * MAX_QUESTIONS_PER_QUIZ} seen rows, "
            f"got {total_seen}"
        )

    print(
        f"PASS — {ATTEMPTS} attempts × {MAX_QUESTIONS_PER_QUIZ} questions "
        f"= {ATTEMPTS * MAX_QUESTIONS_PER_QUIZ} unique picks, zero repeats."
    )


if __name__ == "__main__":
    test_no_repeats_across_15_attempts()
