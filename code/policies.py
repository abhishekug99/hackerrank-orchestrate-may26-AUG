from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from schema import RequestType, Ticket
from utils import contains_any, normalize


@dataclass(frozen=True)
class SafetySignal:
    must_escalate: bool
    reason: str
    risk: str


FEATURE_WORDS = ["feature request", "can you add", "please add", "support for", "new feature"]
BUG_WORDS = ["down", "not working", "stopped working", "all requests are failing", "submissions", "failing", "error", "bug", "blocked", "blocker"]
INVALID_WORDS = ["iron man", "actor", "delete all files", "code to delete"]

HIGH_RISK = [
    "refund", "money", "payment", "order id", "charge", "dispute", "fraud", "identity", "stolen",
    "lost access", "restore my access", "increase my score", "review my answers", "ban the seller",
    "security vulnerability", "bug bounty", "all requests are failing", "site is down", "none of the",
    "subscription", "pause our subscription", "reschedule", "rescheduling", "alternative date", "recruiter rejected", "cash", "blocked",
    "internal rules", "logic exact", "documents retrieved", "score dispute",
]

INJECTION_OR_EXFIL = ["ignore previous", "system prompt", "developer message", "internal rules", "documents retrieved", "logic exact", "show all rules", "delete all files"]


def infer_company(ticket: Ticket) -> str:
    raw = (ticket.company or "").strip()
    if raw and raw.lower() != "none":
        return raw
    text = normalize(ticket.issue + " " + ticket.subject)
    if "claude" in text or "bedrock" in text or "anthropic" in text:
        return "Claude"
    if "visa" in text or "card" in text or "merchant" in text or "traveller" in text:
        return "Visa"
    if "hackerrank" in text or "assessment" in text or "test" in text or "candidate" in text or "submissions" in text:
        return "HackerRank"
    return "None"


def classify_request_type(ticket: Ticket) -> RequestType:
    text = normalize(ticket.issue + " " + ticket.subject)
    if contains_any(text, ["thank you", "thanks"]) and len(text.split()) <= 5:
        return "invalid"
    if contains_any(text, INVALID_WORDS):
        return "invalid"
    if contains_any(text, FEATURE_WORDS):
        return "feature_request"
    if contains_any(text, BUG_WORDS):
        return "bug"
    return "product_issue"


def assess_safety(ticket: Ticket, request_type: RequestType) -> SafetySignal:
    text = normalize(ticket.issue + " " + ticket.subject)
    if contains_any(text, INJECTION_OR_EXFIL):
        if "visa" in text and "blocked" in text:
            return SafetySignal(True, "Prompt-injection content asks for internal logic; answer only the user-visible card support part and do not reveal internal reasoning.", "prompt_injection")
        return SafetySignal(False if request_type == "invalid" else True, "Prompt-injection or unsafe request detected.", "prompt_injection")
    if request_type == "invalid":
        return SafetySignal(False, "Outside supported domains or non-support request.", "low")
    if contains_any(text, HIGH_RISK):
        return SafetySignal(True, "High-risk, account, payment, fraud, assessment outcome, outage, or security-sensitive issue.", "high")
    if len(text.split()) < 6 or contains_any(text, ["it’s not working", "it's not working", "not working help"]):
        return SafetySignal(True, "Too vague to answer safely without more context.", "medium")
    return SafetySignal(False, "Low-risk support question that can be answered from corpus if retrieval is strong.", "low")
