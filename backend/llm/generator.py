"""Offline question generation. Called once during the seed phase, not at runtime."""
from llm.client import json_completion

COUNTS = {"objective": 6, "theory": 4, "oral": 3}


def generate_questions_for_lesson(
    lesson_id: int, topic: str, level: str, quiz_types: list
) -> list:
    system = (
        "You are an English language quiz designer. Return only valid JSON. "
        "No markdown, no preamble."
    )

    type_specs = []
    if "objective" in quiz_types:
        type_specs.append(
            "- objective: 6 questions. Each has question_text, options (array of 4), "
            "correct_answer (exact string match to one option), explanation."
        )
    if "theory" in quiz_types:
        type_specs.append(
            "- theory: 4 questions. Each has question_text, correct_answer "
            "(model answer), explanation."
        )
    if "oral" in quiz_types:
        type_specs.append(
            "- oral: 3 questions. Each has question_text, correct_answer "
            "(model answer), explanation."
        )

    user_message = (
        f"Generate quiz questions for a {level} English lesson on topic: {topic}.\n"
        "For each requested type, generate the specified count:\n"
        + "\n".join(type_specs)
        + "\nTag each question with difficulty: 'easy', 'medium', or 'hard' "
        "(2 each for objective, distribute evenly for others).\n"
        'Return JSON: {"questions": [ {"type": ..., "difficulty": ..., '
        '"question_text": ..., "options": ..., "correct_answer": ..., '
        '"explanation": ...}, ... ]}'
    )

    # A full question set runs well past the default budget — give it headroom
    result = json_completion(system, user_message, max_tokens=6000)
    questions = result.get("questions", [])

    valid = []
    for q in questions:
        if q.get("type") not in quiz_types:
            continue
        if not q.get("question_text") or not q.get("correct_answer"):
            continue
        if q.get("difficulty") not in ("easy", "medium", "hard"):
            q["difficulty"] = "medium"
        if q["type"] == "objective":
            options = q.get("options")
            if not isinstance(options, list) or len(options) != 4:
                continue
            if q["correct_answer"] not in options:
                continue
        valid.append(q)
    return valid
