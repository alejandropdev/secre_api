SPEC / TODO for the Multi-Tenant Medical Integration API

0) Project framing (read me first)
	•	Goal: Internal API between chatbots (n8n agents) and external medical systems; multi-tenant, secure, fast.
	•	Stack: FastAPI (async) + SQLAlchemy 2 + Postgres 16 with RLS + jsonb for flexible fields; Alembic migrations; Docker for dev/test; deploy on AWS (ECS Fargate or API Gateway+Lambda) later.  ￼

1) Repo + dev environment
	•	Initialize repo; add: backend/, alembic/, scripts/, .env.example, README.md.
	•	Create Dockerfile (FastAPI + Uvicorn) and docker-compose.yml with services: api, db (Postgres 16), optional pgadmin.
	•	Add Makefile targets: make up, make down, make migrate, make seed, make test.
	•	Set up pre-commit (black, isort, ruff, mypy).

2) Tenancy & security foundations
	•	Create Tenant model (id, name, is_active, timestamps).
	•	Create ApiKey model (id, tenant_id, key_hash, name, last_used_at, revoked_at). Keys are hashed at rest; expose one-time plaintext only on creation.
	•	Middleware: read X-Api-Key → resolve tenant_id → attach to request context.
	•	DB session hook: SET LOCAL app.tenant_id = <tenant_uuid> per request (for RLS).
	•	RLS policies: enable RLS on all multi-tenant tables; USING (tenant_id::text = current_setting('app.tenant_id', true)) (and matching WITH CHECK). Prove with a test.  ￼

3) Canonical data models (+ flexible jsonb)
	•	Patient: canonical fields (names, birth_date, gender_id, doc_type_id, doc_number, phones, email, eps_id, habeas_data) + custom_fields jsonb.
	•	Appointment: canonical fields (start_utc, end_utc, patient_doc_type_id/number, doctor_doc_type_id/number, modality, state, notification_state, appointment_type, clinic_id, comment) + custom_fields jsonb.
	•	Add indexes for common lookups (tenant_id, doc_number, date ranges) + GIN index on custom_fields for ad-hoc queries. (JsonB is the standard hybrid approach for flexible per-tenant schemas.)  ￼

4) Pydantic schemas (I/O contracts)
	•	Mirror the client’s tool payloads:
	•	PatientCreate: requires eventType="PATIENT", actionType="CREATE", canonical fields + customFields: dict = {}.
	•	AppointmentCreate: requires eventType="APPOINTMENT", actionType="CREATE", startAppointment/endAppointment as RFC3339; convert to UTC.
	•	Response models: return canonical fields + custom_fields.

5) Auth endpoints (admin/internal)
	•	POST /v1/auth/api-keys (create/rotate/revoke for a tenant).
	•	GET /v1/auth/api-keys (list) – redacts secrets.
	•	Rate limit later at edge; keep hooks for WAF/API Gateway usage plans.  ￼

6) Patients CRUD (multi-tenant)
	•	POST /v1/patients
	•	GET /v1/patients/{id}
	•	PATCH /v1/patients/{id}
	•	DELETE /v1/patients/{id}
	•	GET /v1/patients with filters: doc type/number, email/phone, pagination; support custom_fields filters.

7) Appointments CRUD (multi-tenant)
	•	POST /v1/appointments
	•	GET /v1/appointments/{id}
	•	PATCH /v1/appointments/{id}
	•	DELETE /v1/appointments/{id}
	•	GET /v1/appointments with filters: date range, modality/state, pagination; support custom_fields filters.

8) Validation & normalization
	•	Enforce UTC storage for datetimes; accept offsets; reject end < start.
	•	Validate document types, modality enums; allow tenant-level extensions via custom_fields.

9) Observability & errors
	•	Structured JSON logs (include request_id, tenant_id, path, latency).
	•	Error model: 4xx validation vs 5xx unexpected; include trace id.
	•	Audit log table for writes (resource, action, actor api_key_id, before/after snapshots).

10) Tests (prove isolation & contracts)
	•	Pytest setup with ephemeral Postgres (docker).
	•	Tests:
	•	API key auth happy/sad paths.
	•	RLS: tenant A cannot see tenant B (CRUD attempts fail).
	•	Patient/Appointment lifecycle.
	•	Date parsing & UTC conversion.
	•	custom_fields round-trip.
	•	Contract tests using OpenAPI examples.

11) API docs
	•	OpenAPI at /docs with request/response examples reflecting provided Patient/Appointment payloads (Spanish field explanations OK as descriptions).

12) Integration stubs (future)
	•	Outbound webhooks: publish appointment.created to SQS (stub interface for now).
	•	External EHR adapters folder (adapters/), with retry/backoff utilities.

13) Deployment (AWS-ready)
	•	Parameterize env (DB url, secrets). Use AWS Secrets Manager in prod; KMS for encryption.  ￼
	•	Two paths:
	•	ECS Fargate + ALB (always-warm, low latency).  ￼
	•	API Gateway + Lambda (Mangum) + RDS Proxy (spiky traffic, lower ops).  ￼
	•	VPC: private subnets for DB; security groups locked to tasks/Lambda.
	•	CI: build/push container, run migrations, deploy service.

14) Ops & guardrails
	•	Basic rate limiting plan at edge (API Gateway usage plans/WAF or ALB+WAF).  ￼
	•	Backup/restore plan for Postgres; slow query logging.
	•	Seed script: scripts/create_tenant_and_apikey.py for demo.
