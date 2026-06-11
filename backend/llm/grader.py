"""LLM grading for theory (written short-answer) questions."""
from llm.client import json_completion


def grade_theory_answer(
    question: str, model_answer: str, user_answer: str, level: str
) -> dict:
    system = (
        f"You are an English language tutor grading a written answer from a {level} "
        "learner. Be encouraging but accurate. Return only valid JSON. No markdown. "
        "No preamble. Keys: correct (boolean), score (0-100), feedback (one "
        "encouraging sentence that names the specific error if wrong, or praises "
        "the specific strength if correct)."
    )
    user_message = (
        f"Question: {question}\n"
        f"Expected answer: {model_answer}\n"
        f"Learner wrote: {user_answer}"
    )
    try:
        result = json_completion(system, user_message)
        return {
            "correct": bool(result.get("correct", False)),
            "score": int(result.get("score", 0)),
            "feedback": str(result.get("feedback", "")),
        }
    except Exception:
        # Fail soft: never block the quiz on a grading error
        return {
            "correct": False,
            "score": 0,
            "feedback": "We couldn't grade this answer right now — please try again.",
        }
