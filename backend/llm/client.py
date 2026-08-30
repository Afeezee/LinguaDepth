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
    """Run a completion that must return JSON; tolerate the common ways
    reasoning models like Qwen wrap or precede the actual JSON body.

    Handles: leading ``` fences, `<think>...</think>` reasoning blocks
    that Qwen 3 emits by default, and extra prose before/after the JSON.
    Falls back to an empty dict if nothing parseable is found — the caller
    (``generator.py``) treats an empty dict as "no questions" and retries.
    """
    raw = chat_completion(
        system,
        [{"role": "user", "content": user_message}],
        max_tokens=max_tokens,
        json_mode=True,
    )
    # Strip Qwen 3's <think>…</think> reasoning blocks — they're helpful for
    # the model but they push the JSON off the start of the response.
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    # Strip ``` code fences if the model added them despite json_mode.
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned).strip()
    # Grab the outermost {...} block. Greedy match survives nested braces.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # One retry with a stricter slice: from the first { to the last }
        # actually in the cleaned string, ignoring anything after.
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last > first:
            try:
                return json.loads(cleaned[first : last + 1])
            except json.JSONDecodeError:
                pass
        return {}
