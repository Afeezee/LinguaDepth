"""LLM validation for oral (speech-to-text transcript) answers."""
from llm.client import json_completion


def validate_oral_answer(
    question: str, expected: str, transcript: str, level: str
) -> dict:
    system = (
        f"You are an English language tutor evaluating a spoken answer from a {level} "
        "learner. The answer has been transcribed by speech recognition and may have "
        "minor errors. Evaluate the meaning and grammar, not exact wording. Return "
        "only valid JSON. No markdown. No preamble. Keys: correct (boolean), score "
        "(0-100), feedback (one sentence — identify the grammatical or vocabulary "
        "issue if wrong, or affirm what was good if correct)."
    )
    user_message = (
        f"Question: {question}\n"
        f"Expected: {expected}\n"
        f"Learner said: {transcript}"
    )
    try:
        result = json_completion(system, user_message)
        return {
            "correct": bool(result.get("correct", False)),
            "score": int(result.get("score", 0)),
            "feedback": str(result.get("feedback", "")),
        }
    except Exception:
        return {
            "correct": False,
            "score": 0,
            "feedback": "We couldn't check this answer right now — please try again.",
        }
