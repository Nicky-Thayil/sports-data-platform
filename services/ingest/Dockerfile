FROM python:3.11-slim

WORKDIR /app

COPY shared/ ./shared/

COPY services/ingest/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ingest/app/ ./services/ingest/app/

ENV PYTHONPATH=/app

CMD ["python", "-m", "services.ingest.app.main"]