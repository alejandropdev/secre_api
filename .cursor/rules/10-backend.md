API & FastAPI Rules

Framework
	•	Use FastAPI + Uvicorn (ASGI). One app factory; routers under api/v1. Keep “bigger app” layout.  ￼

Schemas & I/O
	•	Pydantic models mirror client payloads; parse incoming datetimes as RFC3339 and store UTC.
	•	Expose canonical fields + custom_fields: dict[str, Any].

Endpoints (v1)
	•	Patients: POST/GET/{id}/PATCH/DELETE + GET (filters: doc, email/phone, pagination).
	•	Appointments: same + filters (date range, state, modality).
	•	Auth (admin): API key create/list/revoke (plaintext returned only once).

OpenAPI
	•	Autodoc required at /docs; include sample payloads from the spec. (FastAPI auto-generates this—use it.)  ￼

Validation
	•	Reject end < start; normalize to UTC; validate enums; allow custom_fields passthrough.

Observability
	•	JSON logs with request_id, tenant_id, route, duration. Map exceptions to 4xx/5xx with trace id.
