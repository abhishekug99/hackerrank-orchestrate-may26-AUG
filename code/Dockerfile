FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USE_OPENAI=0

WORKDIR /app
COPY code/requirements.txt /app/code/requirements.txt
RUN pip install --no-cache-dir -r /app/code/requirements.txt
COPY code /app/code
COPY support_tickets /app/support_tickets
COPY data /app/data
CMD ["python", "code/main.py", "--input", "support_tickets/support_tickets.csv", "--output", "support_tickets/output.csv", "--print"]
