from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

_WORD_RE = re.compile(r"[a-zA-Z0-9']+")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "has", "have",
    "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "our", "please", "that",
    "the", "their", "this", "to", "us", "we", "what", "when", "where", "which", "with", "you",
    "your", "urgent", "help", "need", "issue", "problem", "support", "thanks", "thank",
}


def normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def tokens(text: str) -> List[str]:
    return [t for t in _WORD_RE.findall(normalize(text)) if t not in STOPWORDS and len(t) > 1]


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    haystack = normalize(text)
    return any(p.lower() in haystack for p in phrases)


def repo_root_from_code() -> Path:
    return Path(__file__).resolve().parents[1]


def truncate_sentence(text: str, max_chars: int = 900) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[:max_chars].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "."
