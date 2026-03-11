FROM python:3.11-slim

WORKDIR /app

COPY shared/ ./shared/
COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api/ ./services/api/

ENV PYTHONPATH=/app

CMD ["sh", "-c", "uvicorn services.api.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]