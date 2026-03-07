FROM python:3.11-slim

WORKDIR /app

COPY shared/ ./shared/

COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api/app/ ./services/api/app/

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]