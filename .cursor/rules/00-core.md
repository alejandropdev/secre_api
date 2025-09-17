Project North Star

Mission
	•	Build a multi-tenant medical integration API: FastAPI (async), Postgres with RLS, jsonb for flexible per-tenant fields, clean Docker workflow, AWS-ready.

Non-negotiables
	•	Tenant isolation is enforced at DB level with RLS and at app level. No feature may bypass it.  ￼
	•	Flexible schemas use Postgres jsonb with appropriate GIN indexes (no ad-hoc migrations for tenant-specific extras).  ￼
	•	Type-first, async FastAPI. Keep handlers thin, services testable.  ￼

Directory shape (required)

backend/
  app/
    api/v1/            # routers
    core/              # settings, logging, security, deps
    db/                # session, base, migrations glue
    models/            # SQLAlchemy
    schemas/           # Pydantic
    services/          # domain logic
    middleware/        # api-key auth, request id
    utils/
  alembic/             # migrations + RLS SQL
  tests/
Dockerfile
docker-compose.yml
Makefile
README.md

General style
	•	Python ≥3.11, ruff + black + isort + mypy.
	•	Small PRs; tests first; keep OpenAPI examples in sync.
