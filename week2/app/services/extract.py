from __future__ import annotations

import re
import json
from typing import Any, List
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items using an Ollama-hosted LLM and return a JSON list of strings.

    The model is instructed to return *only* a JSON array (e.g. ["Do X", "Do Y"]).
    """
    prompt = (
        "Extract the actionable tasks (action items) from the input text.\n"
        "Return ONLY a valid JSON array of strings.\n"
        "Rules:\n"
        "- Each item must be a short, specific action (imperative verb).\n"
        "- Do not include numbering or bullet characters.\n"
        "- Do not include any extra keys, objects, or commentary.\n"
        "- If there are no action items, return []."
    )

    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        format="json",
    )

    content = (
        (response or {})
        .get("message", {})
        .get("content", "")
        .strip()
    )

    try:
        parsed: Any = json.loads(content)
    except json.JSONDecodeError:
        return extract_action_items(text)

    if isinstance(parsed, dict) and "action_items" in parsed:
        parsed = parsed["action_items"]

    if not isinstance(parsed, list):
        return extract_action_items(text)

    cleaned: List[str] = []
    seen: set[str] = set()
    for item in parsed:
        if not isinstance(item, str):
            continue
        s = BULLET_PREFIX_PATTERN.sub("", item).strip()
        s = s.removeprefix("[ ]").strip()
        s = s.removeprefix("[todo]").strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(s)

    return cleaned
