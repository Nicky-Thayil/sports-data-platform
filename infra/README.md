# Infrastructure

All infrastructure is provisioned on Google Cloud Platform.

## Services
- **Cloud Run** — API service (apex-api) and ingest jobs (5 jobs)
- **Cloud Scheduler** — Monthly triggers for each ingest job
- **Artifact Registry** — Container image storage (cloud-run-source-deploy)
- **Supabase** — PostgreSQL database
- **Upstash** — Redis cache

## Deployment

### API Service
Deployed from repo root using root `Dockerfile`:
```
gcloud run deploy apex-api --source . --region us-east1
```

### Ingest Jobs
Built using Cloud Build:
```
gcloud builds submit --config infra/cloudbuild/cloudbuild-ingest.yaml .
```

## Manual Provisioning
All Cloud Run Jobs and Cloud Scheduler triggers were provisioned manually via gcloud CLI.