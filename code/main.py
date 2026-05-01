from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List

from agent import SupportTriageAgent
from schema import Ticket

OUTPUT_FIELDS = ["issue", "subject", "company", "response", "product_area", "status", "request_type", "justification"]


def read_tickets(path: Path) -> List[Ticket]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        tickets: List[Ticket] = []
        for row in reader:
            tickets.append(Ticket(
                issue=row.get("Issue") or row.get("issue") or "",
                subject=row.get("Subject") or row.get("subject") or "",
                company=(row.get("Company") or row.get("company") or "").strip(),
            ))
        return tickets


def write_output(path: Path, tickets: List[Ticket], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for ticket, pred in zip(tickets, rows):
            writer.writerow({
                "issue": ticket.issue,
                "subject": ticket.subject,
                "company": ticket.company,
                "response": pred["response"],
                "product_area": pred["product_area"],
                "status": pred["status"],
                "request_type": pred["request_type"],
                "justification": pred["justification"],
            })


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Terminal support triage agent for HackerRank Orchestrate.")
    parser.add_argument("--input", type=Path, default=root / "support_tickets" / "support_tickets.csv")
    parser.add_argument("--output", type=Path, default=root / "support_tickets" / "output.csv")
    parser.add_argument("--data", type=Path, default=root / "data")
    parser.add_argument("--print", action="store_true", help="Print predictions to terminal as they are generated.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = SupportTriageAgent(args.data)
    tickets = read_tickets(args.input)
    predictions: List[Dict[str, str]] = []
    for idx, ticket in enumerate(tickets, 1):
        decision = agent.triage(ticket)
        row = decision.to_output_row()
        predictions.append(row)
        if args.print:
            print(f"[{idx}] {row['status']} | {row['request_type']} | {row['product_area']} | {row['response'][:120]}")
    write_output(args.output, tickets, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
