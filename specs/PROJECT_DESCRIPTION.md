# Secre API

Project: Multi-tenant Medical Integration API (Python/FastAPI + Postgres)
Goal: An internal API between chatbots (n8n agents) and external medical systems. Must be multi-tenant, secure, and flexible per company. Ship with Docker for local/dev and ready for AWS deploy.

Architecture
	•	Backend: FastAPI (async), Uvicorn, Pydantic models.
	•	DB: PostgreSQL 16 with SQLAlchemy 2.x and Alembic.
	•	Tenancy: single database, shared schema, tenant_id on all tables + Postgres Row-Level Security (RLS).
	•	Flex fields: jsonb columns (custom_fields) on patient and appointment.
	•	Auth: API Key for server-to-server (header X-Api-Key), hashed at rest; optional JWT for future operator console.
	•	Observability: request logging, structured logs (JSON), basic audit trails.
	•	Versioning: prefix endpoints with /v1.

Docker
	•	Create Dockerfile for app.
	•	Create docker-compose.yml with services:
	•	api (FastAPI), db (Postgres), pgadmin (optional).
	•	Healthchecks; volumes for DB.
	•	Add Makefile targets: make up, make down, make migrate, make seed.

Data model (SQLAlchemy)
	•	Tenant(id, name, is_active, created_at)
	•	ApiKey(id, tenant_id FK, key_hash, name, last_used_at, created_at, revoked_at)
	•	Patient(id, tenant_id, first_name, second_name, first_last_name, second_last_name, birth_date, gender_id, document_type_id, document_number, phone, cell_phone, email, eps_id, habeas_data, custom_fields jsonb, created_at, updated_at)
	•	Appointment(id, tenant_id, start_utc timestamptz, end_utc timestamptz, patient_document_type_id, patient_document_number, doctor_document_type_id, doctor_document_number, modality, state, notification_state, appointment_type, clinic_id, comment, custom_fields jsonb, created_at, updated_at)
	•	(Optional) Lookup tables for document types, modality enums, etc.

RLS policies (Alembic migration)
	•	Enable RLS on all tenant tables.
	•	Add app settings: CREATE EXTENSION IF NOT EXISTS pgcrypto;
	•	Add app.tenant_id GUC pattern: API middleware executes SET LOCAL app.tenant_id = '<uuid>';
	•	Example policy (generate in migration SQL):

ALTER TABLE patient ENABLE ROW LEVEL SECURITY;
CREATE POLICY patient_tenant_isolation
  ON patient
  USING (tenant_id::text = current_setting('app.tenant_id', true));

Repeat for appointment, apikey, etc. (Include INSERT/UPDATE USING WITH CHECK.)

API middleware
	•	Read X-Api-Key, verify against ApiKey.key_hash, fetch tenant_id, reject if revoked.
	•	SET LOCAL app.tenant_id in the DB connection for the request scope (SQLAlchemy session).

Endpoints (FastAPI)
	•	POST /v1/auth/api-keys (admin-scoped): create/rotate/revoke keys for a tenant.
	•	Patients:
	•	POST /v1/patients (accepts canonical fields + custom_fields object)
	•	GET /v1/patients/{id}
	•	PATCH /v1/patients/{id}
	•	DELETE /v1/patients/{id}
	•	GET /v1/patients (filter by doc type/number, email, phone; pagination)
	•	Appointments:
	•	POST /v1/appointments
	•	GET /v1/appointments/{id}
	•	PATCH /v1/appointments/{id}
	•	DELETE /v1/appointments/{id}
	•	GET /v1/appointments (date range, modality, state; pagination)
	•	Tenants (internal/admin): POST /v1/tenants, GET /v1/tenants/{id}, etc.

DTOs / Pydantic models
	•	Mirror your client’s current tool payloads:
	•	PatientCreate: eventType="PATIENT", actionType="CREATE", canonical fields, and customFields: dict[str, Any] = {}
	•	AppointmentCreate: eventType="APPOINTMENT", actionType="CREATE", startAppointment & endAppointment as RFC3339 (Z or offset), plus canonical IDs, and customFields.
	•	Validate dates to UTC internally; store as timestamptz.

Security & robustness
	•	Rate limiting interface (can be wired later at API Gateway/WAF; add local Redis option for fastapi-limiter behind a feature flag).
	•	Input validation with descriptive errors; 4xx vs 5xx separation.
	•	Audit log table for write operations (who/what/when), including API key id.

Testing
	•	Pytest with an ephemeral Postgres (use docker compose -f docker-compose.test.yml).
	•	Integration tests for RLS (prove cross-tenant access is blocked).

Docs
	•	OpenAPI at /docs + examples matching your provided payloads.

Deliverables
	•	Full repo with: backend/, alembic/, Dockerfile, docker-compose.yml, Makefile, README.md (run/deploy steps), .env.example.
	•	Scripts: scripts/create_tenant_and_apikey.py to bootstrap demo tenant + seed data.

Non-functional
	•	P99 latency budget: <150ms intra-region read, <250ms typical write (local dev looser).
	•	Log JSON to stdout; include tenant_id and request_id.

Nice-to-haves (stubs OK)
	•	Outbound webhook dispatcher (SQS producer) for “appointment.created”.
	•	Retry/backoff utility for external EHRs.
