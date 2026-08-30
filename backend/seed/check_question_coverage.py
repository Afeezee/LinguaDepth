"""Report every lesson whose question pool is missing types or under-filled.

Use this after a big seed run (``seed_questions.py``) to see which lessons
Qwen dropped so you can re-run generation for just those. It reads the DB
directly — no LLM calls, no writes.

Run from the backend/ directory:
    python seed/check_question_coverage.py
    python seed/check_question_coverage.py --verbose
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from llm.generator import CORE_COUNT_PER_TYPE, LEVEL_COUNT_PER_TYPE
from models import Lesson, Question


def main():
    verbose = "--verbose" in sys.argv
    app = create_app()
    with app.app_context():
        lessons = Lesson.query.order_by(Lesson.path_type.desc(), Lesson.id).all()
        total_expected = 0
        total_actual = 0
        broken = []
        thin = []

        for lesson in lessons:
            quiz_types = json.loads(lesson.quiz_types)
            per_type = (
                CORE_COUNT_PER_TYPE if lesson.path_type == "core"
                else LEVEL_COUNT_PER_TYPE
            )
            expected = per_type * len(quiz_types)
            total_expected += expected

            counts = defaultdict(int)
            for q in lesson.questions:
                counts[q.type] += 1
            actual_total = sum(counts.values())
            total_actual += actual_total

            missing_types = [t for t in quiz_types if counts[t] == 0]
            has_any = actual_total > 0

            if missing_types and not has_any:
                broken.append((lesson, quiz_types, counts, expected, "EMPTY"))
            elif missing_types:
                broken.append((lesson, quiz_types, counts, expected, "MISSING TYPE"))
            elif actual_total < expected:
                thin.append((lesson, quiz_types, counts, expected))
            elif verbose:
                print(
                    f"  ok    {lesson.title:<50} "
                    f"{actual_total:>3}/{expected:<3} "
                    f"{dict(counts)}"
                )

        print("=" * 78)
        print(f"Lessons total:      {len(lessons)}")
        print(f"Questions expected: {total_expected}")
        print(f"Questions actual:   {total_actual}")
        print(f"Shortfall:          {total_expected - total_actual}")
        print("=" * 78)

        if broken:
            print(f"\nBROKEN lessons ({len(broken)}) — learners hit a dead end here:")
            for lesson, quiz_types, counts, expected, tag in broken:
                print(
                    f"  [{tag}] id={lesson.id:<3} {lesson.path_type:<10} "
                    f"{lesson.title:<50} "
                    f"assigned={quiz_types}  got={dict(counts)}"
                )

        if thin:
            print(f"\nTHIN lessons ({len(thin)}) — usable but under target:")
            for lesson, quiz_types, counts, expected in thin:
                total = sum(counts.values())
                print(
                    f"  id={lesson.id:<3} {lesson.path_type:<10} "
                    f"{lesson.title:<50} "
                    f"{total}/{expected}  got={dict(counts)}"
                )

        if not broken and not thin:
            print("\nAll lessons at target. Nothing to do.")
        else:
            print(
                "\nTo top up thin/broken lessons, run:"
                "\n    python seed/seed_questions.py"
                "\n(no --force). It skips lessons already at target and "
                "regenerates only the shortfall."
            )


if __name__ == "__main__":
    main()
