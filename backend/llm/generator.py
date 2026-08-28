"""Offline question generation. Called once during the seed phase, not at runtime.

Every lesson now gets a much larger question bank than the original build so
the runtime question-selection logic (in ``quiz/routes.py``) can guarantee no
repeats across many attempts:

    core lessons:        ``CORE_COUNT_PER_TYPE``  questions per assigned type
    level-path lessons:  ``LEVEL_COUNT_PER_TYPE`` questions per assigned type

Because a single Groq call for 20 questions per type in one shot regularly
truncates and returns a partial JSON object, we now request each type in its
own call and merge the results. That is slower but reliable and matches the
per-lesson resumability that ``seed/seed_questions.py`` counts on.
"""
import math

from llm.client import json_completion

CORE_COUNT_PER_TYPE = 20
LEVEL_COUNT_PER_TYPE = 12


def _difficulty_distribution(total: int) -> dict:
    """Split ``total`` roughly evenly across easy/medium/hard.

    The remainder is added to medium so the middle band always has at least
    the same count as the tails.
    """
    base = total // 3
    remainder = total - base * 3
    return {"easy": base, "medium": base + remainder, "hard": base}


def _generate_single_type(topic: str, level: str, qtype: str, count: int) -> list:
    system = (
        "You are an English language quiz designer. Return only valid JSON. "
        "No markdown, no preamble, no trailing commentary."
    )
    dist = _difficulty_distribution(count)
    dist_line = ", ".join(f"{n} {band}" for band, n in dist.items())

    if qtype == "objective":
        type_block = (
            f"Generate exactly {count} multiple-choice questions.\n"
            "Each object needs: type (\"objective\"), difficulty, question_text, "
            "options (array of exactly 4 distinct strings), correct_answer "
            "(EXACT string match to one of the options), explanation."
        )
    elif qtype == "theory":
        type_block = (
            f"Generate exactly {count} short-answer theory questions.\n"
            "Each object needs: type (\"theory\"), difficulty, question_text, "
            "correct_answer (a model answer, 1–3 sentences), explanation."
        )
    elif qtype == "oral":
        type_block = (
            f"Generate exactly {count} oral / speaking-prompt questions.\n"
            "Each object needs: type (\"oral\"), difficulty, question_text "
            "(a prompt asking the learner to say something aloud), "
            "correct_answer (a model spoken answer), explanation."
        )
    else:
        raise ValueError(f"Unknown quiz type: {qtype}")

    user_message = (
        f"Topic: {topic}. Level: {level}.\n"
        f"{type_block}\n"
        f"Distribute the {count} questions across difficulty like this: {dist_line}.\n"
        "Return JSON in this exact shape:\n"
        '{"questions": [ {"type": ..., "difficulty": ..., "question_text": ..., '
        '"options": [...], "correct_answer": ..., "explanation": ...}, ... ]}'
    )

    # Rough budget: ~150 tokens per generated question, plus overhead.
    budget = max(2000, count * 220)
    result = json_completion(system, user_message, max_tokens=budget)
    return result.get("questions", []) or []


def _valid(q: dict, qtype: str) -> bool:
    if q.get("type") != qtype:
        return False
    if not q.get("question_text") or not q.get("correct_answer"):
        return False
    if q.get("difficulty") not in ("easy", "medium", "hard"):
        q["difficulty"] = "medium"
    if qtype == "objective":
        options = q.get("options")
        if not isinstance(options, list) or len(options) != 4:
            return False
        if len(set(options)) != 4:
            return False
        if q["correct_answer"] not in options:
            return False
    return True


def generate_questions_for_lesson(
    lesson_id: int,
    topic: str,
    level: str,
    quiz_types: list,
    is_core: bool = False,
) -> list:
    """Return a merged list of validated questions for every type in ``quiz_types``.

    Core lessons (``is_core=True``) get a larger pool per type because every
    learner passes through them — sometimes more than once — and question
    repetition on the shared foundation is the highest-impact bug this fixes.
    """
    per_type = CORE_COUNT_PER_TYPE if is_core else LEVEL_COUNT_PER_TYPE
    all_valid = []

    for qtype in quiz_types:
        raw = _generate_single_type(topic, level, qtype, per_type)
        typed_valid = [q for q in raw if _valid(q, qtype)]

        # If the model returned fewer than we asked for (a common cause is a
        # dropped or malformed final object), retry once for the shortfall.
        shortfall = per_type - len(typed_valid)
        if shortfall > 0:
            extra_raw = _generate_single_type(topic, level, qtype, shortfall)
            typed_valid.extend(q for q in extra_raw if _valid(q, qtype))

        # Truncate any overshoot for tidy pool sizes.
        typed_valid = typed_valid[:per_type]
        all_valid.extend(typed_valid)

    return all_valid
