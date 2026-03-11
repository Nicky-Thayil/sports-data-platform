# Apex Sports Data Platform

A two-service data platform that ingests Formula 1 and Premier League data on a schedule, normalises it into PostgreSQL, and serves it through a REST API with Redis caching.

**Live API:** https://apex-api-714166040897.us-east1.run.app  
**Interactive docs:** https://apex-api-714166040897.us-east1.run.app/docs

---

## Overview

The platform has two independent services:

- **Ingest service** — Cloud Run Jobs triggered monthly by Cloud Scheduler. Pulls from FastF1 and API-Football, writes to PostgreSQL via idempotent upserts.
- **API service** — FastAPI on Cloud Run. Reads from PostgreSQL with Redis caching. Returns consistent JSON envelopes with metadata.

---

## Architecture

```
Cloud Scheduler (monthly cron)
        ↓
Cloud Run Jobs — 5 ingest pipelines
        ↓ fetches from
API-Football / FastF1
        ↓ writes
PostgreSQL (Supabase)
        ↓ reads          ↑ cache + lag timestamps
Cloud Run Service — FastAPI
        ↓ cache reads
Redis (Upstash)
        ↑ HTTP
API consumers
```

---

## Stack

**Language:** Python 3.11  
**Framework:** FastAPI  
**Database:** PostgreSQL · SQLAlchemy (async) · asyncpg  
**Cache:** Redis · redis.asyncio  
**Infrastructure:** Google Cloud Run · Cloud Scheduler · Cloud Build  
**Managed Services:** Supabase · Upstash  
**Other:** Docker

---

## Local Development

Copy `.env.example` to `.env` and fill in the values.

```bash
# Start Postgres and Redis
docker-compose up -d postgres redis

# Run API
uvicorn services.api.app.main:app --reload --port 8000

# Run an ingest job
JOB_NAME=sync_pl_standings python -m services.ingest.app.main
```

---

## Future Plans

- Frontend dashboard for standings and lap time visualisations