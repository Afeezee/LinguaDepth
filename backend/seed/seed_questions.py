"""Generate and seed quiz questions for every lesson via the Groq LLM.

Requires GROQ_API_KEY in the environment. Run from the backend/ directory:
    python seed/seed_questions.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from llm.generator import generate_questions_for_lesson
from models import Lesson, Question, db


def seed():
    app = create_app()
    with app.app_context():
        lessons = Lesson.query.order_by(Lesson.id).all()
        if not lessons:
            print("No lessons found. Run seed_lessons.py first.")
            sys.exit(1)

        for lesson in lessons:
            existing = Question.query.filter_by(lesson_id=lesson.id).count()
            if existing > 0:
                print(f"[skip] {lesson.title} — {existing} questions already exist")
                continue

            quiz_types = json.loads(lesson.quiz_types)
            print(f"[gen ] {lesson.title} ({lesson.level}, {quiz_types}) ...")
            try:
                questions = generate_questions_for_lesson(
                    lesson.id, lesson.topic, lesson.level, quiz_types
                )
            except Exception as exc:
                print(f"[fail] {lesson.title}: {exc}")
                continue

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
            print(f"[ok  ] {lesson.title}: {len(questions)} questions")
            time.sleep(1)  # be gentle with the API rate limit

        print(f"Done. Total questions: {Question.query.count()}")


if __name__ == "__main__":
    seed()
