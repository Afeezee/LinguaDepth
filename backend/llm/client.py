"""Shared Groq client and JSON-safe completion helper."""
import json
import os
import re

from groq import Groq

# Single source of truth: pick the model from GROQ_MODEL. Default is the
# newest Qwen preview currently live on Groq (qwen/qwen3.8-27b) — Llama 4
# Scout was decommissioned and qwen/qwen3-32b was deprecated 2026-06-17.
# Keeping the value in one env variable means the next model swap is a
# one-line change in .env, not a hunt through the codebase.
MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=api_key)
    return _client


def chat_completion(
    system: str,
    messages: list,
    temperature: float = 0.3,
    max_tokens: int = 512,
    json_mode: bool = False,
) -> str:
    client = get_client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, *messages],
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    return response.choices[0].message.content.strip()


def json_completion(system: str, user_message: str, max_tokens: int = 1024) -> dict:
    """Run a completion that must return JSON; strip markdown fences if present."""
    raw = chat_completion(
        system,
        [{"role": "user", "content": user_message}],
        max_tokens=max_tokens,
        json_mode=True,
    )
    # Models sometimes wrap JSON in ```json fences despite instructions
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)
