# Support Triage Agent

Terminal-based support triage agent for HackerRank Orchestrate.

## Architecture

The design is intentionally simple and production-oriented:

1. `corpus.py` loads only local Markdown files from `data/` and builds a deterministic TF-IDF retriever.
2. `policies.py` classifies request type and applies safety/risk gates before any answer is generated.
3. `product_area.py` maps tickets to product areas using company-aware rules plus retrieved corpus metadata.
4. `agent.py` orchestrates the flow like a small LangGraph-style pipeline: infer company → retrieve evidence → classify → safety route → answer/escalate.
5. `llm.py` optionally calls ChatGPT only with retrieved excerpts and structured JSON output. By default `USE_OPENAI=0`, so the submission is deterministic and reproducible.

This avoids a heavyweight vector database because the corpus is local Markdown and small enough for in-memory retrieval. It also reduces hallucination risk: high-risk issues are escalated before generation, and low-risk replies are grounded in retrieved files when available.

## Setup

```bash
cd <repo-root>
python -m venv .venv
source .venv/Scripts/activate
pip install -r code/requirements.txt
cp code/.env.example .env
```

The deterministic fallback mode does not require an API key. To use ChatGPT wording from retrieved evidence:

```bash
export OPENAI_API_KEY="..."
export USE_OPENAI=1
export OPENAI_MODEL=gpt-4o-mini
```

## Run

```bash
python code/main.py --input support_tickets/support_tickets.csv --output support_tickets/output.csv --print
```

or:

```bash
bash code/run.sh --print
```

## Docker

```bash
docker build -f code/Dockerfile -t support-triage .
docker docker run --rm --env-file .env -v "$PWD/support_tickets:/app/support_tickets" support-triage
```

## Testing checklist

1. Run on sample tickets and compare routing shape:

```bash
python code/main.py --input support_tickets/sample_support_tickets.csv --output /tmp/sample_predictions.csv --print
```

2. Run final predictions:

```bash
python code/main.py --input support_tickets/support_tickets.csv --output support_tickets/output.csv --print
```

3. Confirm required columns exist:

```bash
head -1 support_tickets/output.csv
```

Expected columns:

```text
issue,subject,company,response,product_area,status,request_type,justification
```

## Failure modes and trade-offs

- TF-IDF is deterministic and easy to explain, but semantic paraphrases may retrieve weaker matches than embeddings.
- The rule-based escalation layer is conservative. This may escalate some tickets that a human could answer, but it avoids unsupported claims for billing, account access, fraud, security, assessment outcomes, and outages.
- If the corpus lacks a relevant article, the agent should escalate or produce a cautious boundary response rather than guessing.