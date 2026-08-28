"""Generate and seed quiz questions for every lesson via the Groq LLM.

Requires ``GROQ_API_KEY`` in the environment. This job is idempotent and
resumable — it skips any lesson whose question count already meets the
expected pool size, so it can be re-run safely if the previous run was
interrupted or partially failed.

Expected pool per lesson:
    core lessons       →  ``CORE_COUNT_PER_TYPE * len(quiz_types)``
    level-path lessons →  ``LEVEL_COUNT_PER_TYPE * len(quiz_types)``

Run from the backend/ directory:
    python seed/seed_questions.py            # generate any missing questions
    python seed/seed_questions.py --force    # wipe every question and regenerate
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from llm.generator import (
    CORE_COUNT_PER_TYPE,
    LEVEL_COUNT_PER_TYPE,
    generate_questions_for_lesson,
)
from models import Lesson, Question, db


def _expected_count(lesson: Lesson) -> int:
    quiz_types = json.loads(lesson.quiz_types)
    per_type = CORE_COUNT_PER_TYPE if lesson.path_type == "core" else LEVEL_COUNT_PER_TYPE
    return per_type * len(quiz_types)


def seed(force: bool = False):
    app = create_app()
    with app.app_context():
        lessons = Lesson.query.order_by(Lesson.path_type.desc(), Lesson.id).all()
        if not lessons:
            print("No lessons found. Run seed_lessons.py first.")
            sys.exit(1)

        if force:
            wiped = Question.query.delete()
            db.session.commit()
            print(f"Wiped {wiped} existing questions.")

        total_lessons = len(lessons)
        for idx, lesson in enumerate(lessons, start=1):
            existing = Question.query.filter_by(lesson_id=lesson.id).count()
            expected = _expected_count(lesson)
            if existing >= expected:
                print(
                    f"[{idx}/{total_lessons}] skip  — {lesson.title} "
                    f"({existing}/{expected} already present)"
                )
                continue

            quiz_types = json.loads(lesson.quiz_types)
            is_core = lesson.path_type == "core"
            print(
                f"[{idx}/{total_lessons}] gen   — {lesson.title} "
                f"({lesson.level}, {quiz_types}, core={is_core}) …"
            )
            try:
                questions = generate_questions_for_lesson(
                    lesson.id,
                    lesson.topic,
                    lesson.level,
                    quiz_types,
                    is_core=is_core,
                )
            except Exception as exc:
                print(f"[{idx}/{total_lessons}] FAIL  — {lesson.title}: {exc}")
                continue

            # If we already have some of this lesson's questions (a partial
            # previous run), keep them and only top up the pool.
            if existing and not force:
                shortfall = expected - existing
                questions = questions[:shortfall]

            for q in questions:
                db.session.add(
                    Question(
                        lesson_id=lesson.id,
                        type=q["type"],
                        difficulty=q["difficulty"],
                        level=lesson.level,
                        question_text=q["question_text"],
                        options=json.dumps(q["options"]) if q.get("options") else None,
                        correct_answer=q["correct_answer"],
                        explanation=q.get("explanation"),
                    )
                )
            db.session.commit()
            now = Question.query.filter_by(lesson_id=lesson.id).count()
            print(
                f"[{idx}/{total_lessons}] ok    — {lesson.title}: "
                f"{len(questions)} added ({now}/{expected} total)"
            )
            time.sleep(1)  # gentle with the API rate limit

        print(f"Done. Total questions across all lessons: {Question.query.count()}")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
