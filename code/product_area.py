from __future__ import annotations

from typing import Iterable, List

from schema import RetrievalHit, Ticket
from utils import contains_any, normalize


def infer_product_area(ticket: Ticket, company: str, hits: List[RetrievalHit]) -> str:
    text = normalize(ticket.issue + " " + ticket.subject)
    if company == "HackerRank":
        if contains_any(text, ["mock interview", "practice", "apply tab", "submissions", "challenge", "certificate", "community", "resume builder"]):
            return "community"
        if contains_any(text, ["candidate", "assessment", "test", "recruiter", "score", "compatible", "zoom", "interviewer", "inactivity", "remove a user", "employee", "hiring", "subscription"]):
            return "screen"
        if contains_any(text, ["payment", "order id", "refund"]):
            return "billing"
        return hits[0].document.product_area if hits else "general_support"
    if company == "Claude":
        if contains_any(text, ["bedrock", "aws"]):
            return "amazon_bedrock"
        if contains_any(text, ["education", "professor", "lti key", "students"]):
            return "education"
        if contains_any(text, ["workspace", "team", " seat ", "admin", "remove", "sso", "scim"]):
            return "team_enterprise"
        if contains_any(text, ["crawl", "data", "privacy", "website", "model", "conversation"]):
            return "privacy"
        if contains_any(text, ["security vulnerability", "bug bounty"]):
            return "security"
        return hits[0].document.product_area if hits else "general_support"
    if company == "Visa":
        if contains_any(text, ["minimum", "spend"]):
            return "merchant_acceptance"
        if contains_any(text, ["identity", "stolen", "fraud", "dispute", "charge", "merchant", "wrong product"]):
            return "fraud_disputes"
        if contains_any(text, ["cash", "travel", "blocked", "traveller", "emergency"]):
            return "travel_support"
        return hits[0].document.product_area if hits else "general_support"
    return ""
