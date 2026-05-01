from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from schema import Document, RetrievalHit
from utils import tokens

AREA_ALIASES = {
    "hacker_rank": "hackerrank",
    "hackerrank_community": "community",
    "general-help": "general_help",
    "claude-api-and-console": "api_console",
    "team-and-enterprise-plans": "team_enterprise",
    "identity-management-sso-jit-scim": "identity_management",
    "privacy-and-legal": "privacy",
    "pro-and-max-plans": "billing_plans",
    "amazon-bedrock": "amazon_bedrock",
    "claude-for-education": "education",
    "support": "general_support",
}


def _company_from_path(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "hackerrank" in parts:
        return "HackerRank"
    if "claude" in parts:
        return "Claude"
    if "visa" in parts:
        return "Visa"
    return "None"


def _area_from_path(path: Path, data_root: Path) -> str:
    rel = path.relative_to(data_root)
    parts = list(rel.parts)
    area = parts[1] if len(parts) > 2 else path.stem
    area = AREA_ALIASES.get(area, area)
    return area.replace("-", "_").replace(" ", "_").lower()


def _title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    return fallback


def load_corpus(data_root: Path) -> List[Document]:
    docs: List[Document] = []
    if not data_root.exists():
        return docs
    for path in sorted(data_root.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        if not text.strip():
            continue
        company = _company_from_path(path)
        area = _area_from_path(path, data_root)
        doc_id = str(path.relative_to(data_root)).replace("/", "::")
        docs.append(Document(doc_id=doc_id, company=company, product_area=area, title=_title_from_markdown(text, path.stem), text=text, path=str(path)))
    return docs


class TfidfRetriever:
    """Small deterministic retriever with no external service requirement."""

    def __init__(self, docs: Sequence[Document]):
        self.docs = list(docs)
        self.doc_tokens: List[List[str]] = [tokens(d.title + " " + d.text) for d in self.docs]
        self.tf: List[Counter[str]] = [Counter(ts) for ts in self.doc_tokens]
        df: Counter[str] = Counter()
        for ts in self.doc_tokens:
            df.update(set(ts))
        n = max(len(self.docs), 1)
        self.idf: Dict[str, float] = {term: math.log((1 + n) / (1 + freq)) + 1.0 for term, freq in df.items()}
        self.norms: List[float] = []
        for counter in self.tf:
            self.norms.append(math.sqrt(sum((count * self.idf.get(term, 1.0)) ** 2 for term, count in counter.items())) or 1.0)

    def search(self, query: str, company: Optional[str] = None, top_k: int = 4) -> List[RetrievalHit]:
        q_tokens = tokens(query)
        if not q_tokens or not self.docs:
            return []
        q_tf = Counter(q_tokens)
        q_norm = math.sqrt(sum((count * self.idf.get(term, 1.0)) ** 2 for term, count in q_tf.items())) or 1.0
        hits: List[RetrievalHit] = []
        for i, doc in enumerate(self.docs):
            if company and company != "None" and doc.company.lower() != company.lower():
                continue
            dot = 0.0
            for term, q_count in q_tf.items():
                dot += (q_count * self.idf.get(term, 1.0)) * (self.tf[i].get(term, 0) * self.idf.get(term, 1.0))
            score = dot / (q_norm * self.norms[i])
            if score > 0:
                hits.append(RetrievalHit(document=doc, score=score))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]
