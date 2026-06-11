"""Conversational practice chatbox powered by the LLM."""
from llm.client import chat_completion

MAX_HISTORY_TURNS = 10


def chat_response(history: list, user_message: str, level: str, topic: str) -> str:
    system = (
        f"You are a friendly English conversation tutor speaking with a {level} "
        f"English learner. Topic: {topic}. Rules:\n"
        "- Keep every reply to 1-2 short sentences maximum.\n"
        f"- Use vocabulary appropriate for {level}.\n"
        "- If the learner makes a grammar mistake, gently correct it in your reply "
        "naturally.\n"
        "- Never lecture. Keep it conversational and warm.\n"
        "- Do not break character or mention you are an AI."
    )

    trimmed = (history or [])[-MAX_HISTORY_TURNS:]
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in trimmed
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]
    messages.append({"role": "user", "content": user_message})

    try:
        return chat_completion(system, messages, temperature=0.7)
    except Exception:
        return "Sorry, I didn't catch that — could you say it again?"
