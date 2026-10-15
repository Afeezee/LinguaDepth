"""Offline question generation. Called once during the seed phase, not at runtime.

Every lesson gets a larger question bank than the original build so the
runtime question-selection logic (in ``quiz/routes.py``) can guarantee no
repeats across many attempts:

    core lessons:        ``CORE_COUNT_PER_TYPE``  questions per assigned type
    level-path lessons:  ``LEVEL_COUNT_PER_TYPE`` questions per assigned type

To stay under Groq's free-tier output-tokens-per-minute cap for Qwen 3.8
(1000 OTPM), we split each type's generation into small per-call batches
of ``BATCH_SIZE`` questions, each with a budget well under the per-call
cap. Transient 429s between batches are handled by the retry loop in
``seed/seed_questions.py``.
"""
import time

from llm.client import json_completion

CORE_COUNT_PER_TYPE = 20
LEVEL_COUNT_PER_TYPE = 12

# Groq free tier caps qwen/qwen3.8-27b at 1000 output tokens per minute,
# refused pre-flight when a single request's max_tokens exceeds that. Each
# generated question is roughly 150–200 tokens of JSON (longer for theory
# bodies, shorter for oral prompts). Four per batch × 200 tokens ≈ 800
# token budget — comfortably under the cap with room for the JSON wrapper.
BATCH_SIZE = 4
TOKENS_PER_QUESTION = 200
# Short pause between back-to-back batches on the same lesson so the OTPM
# sliding window has time to breathe. 429s from short-term rate limits
# are still retried by the caller (``seed/seed_questions.py``).
INTRA_LESSON_BATCH_SLEEP_SECONDS = 20


def _difficulty_distribution(total: int) -> dict:
    """Split ``total`` roughly evenly across easy/medium/hard.

    The remainder is added to medium so the middle band always has at least
    the same count as the tails.
    """
    base = total // 3
    remainder = total - base * 3
    return {"easy": base, "medium": base + remainder, "hard": base}


def _build_user_message(topic: str, level: str, qtype: str, count: int) -> str:
    """Prompt body for one batch of ``count`` questions of a single type."""
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

    return (
        f"Topic: {topic}. Level: {level}.\n"
        f"{type_block}\n"
        f"Distribute the {count} questions across difficulty like this: {dist_line}.\n"
        "Return JSON in this exact shape:\n"
        '{"questions": [ {"type": ..., "difficulty": ..., "question_text": ..., '
        '"options": [...], "correct_answer": ..., "explanation": ...}, ... ]}'
    )


def _request_batch(topic: str, level: str, qtype: str, count: int) -> list:
    """One LLM round-trip for a single batch of ``count`` questions."""
    system = (
        "You are an English language quiz designer. Return only valid JSON. "
        "No markdown, no preamble, no trailing commentary."
    )
    # Budget per batch stays comfortably under the Groq free-tier OTPM cap.
    budget = min(950, max(300, count * TOKENS_PER_QUESTION))
    result = json_completion(system, _build_user_message(topic, level, qtype, count),
                              max_tokens=budget)
    return result.get("questions", []) or []


def _generate_single_type(topic: str, level: str, qtype: str, count: int) -> list:
    """Produce ``count`` validated questions of a single type, batched to fit
    under the free-tier output-tokens-per-minute cap.

    Keeps requesting batches of ``BATCH_SIZE`` until we have the target
    count or until two consecutive empty batches signal the model has run
    out of distinct ideas on this topic (further calls would waste quota).
    """
    collected = []
    empty_batches_in_a_row = 0
    while len(collected) < count:
        remaining = count - len(collected)
        this_batch_target = min(BATCH_SIZE, remaining)

        raw = _request_batch(topic, level, qtype, this_batch_target)
        valid_in_batch = [q for q in raw if _valid(q, qtype)]
        if valid_in_batch:
            collected.extend(valid_in_batch)
            empty_batches_in_a_row = 0
        else:
            empty_batches_in_a_row += 1
            if empty_batches_in_a_row >= 2:
                # Two useless rounds back-to-back → cut our losses on this
                # type. The caller logs the shortfall; seed_questions.py
                # can be re-run later to top up.
                break

        # Only sleep if we're going to make another call. Avoids an awkward
        # tail-sleep when the last batch already met the target.
        if len(collected) < count:
            time.sleep(INTRA_LESSON_BATCH_SLEEP_SECONDS)

    return collected[:count]


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
        all_valid.extend(_generate_single_type(topic, level, qtype, per_type))
    return all_valid
