FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY src/ /app/src/

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["sh", "-c", "while true; do python3 -m src; sleep ${GRAYLOG_SEARCH_QUERY_INTERVAL}m; done"]
