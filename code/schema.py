from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

Status = Literal["replied", "escalated"]
RequestType = Literal["product_issue", "feature_request", "bug", "invalid"]


@dataclass(frozen=True)
class Ticket:
    issue: str
    subject: str
    company: str


@dataclass(frozen=True)
class Document:
    doc_id: str
    company: str
    product_area: str
    title: str
    text: str
    path: str


@dataclass(frozen=True)
class RetrievalHit:
    document: Document
    score: float


@dataclass(frozen=True)
class TriageDecision:
    status: Status
    product_area: str
    response: str
    justification: str
    request_type: RequestType
    evidence_titles: List[str]

    def to_output_row(self) -> Dict[str, str]:
        return {
            "status": self.status,
            "product_area": self.product_area,
            "response": self.response,
            "justification": self.justification,
            "request_type": self.request_type,
        }
