# Secre API

Multi-tenant Medical Integration API built with FastAPI, PostgreSQL, and Row-Level Security (RLS).

## Overview

This API serves as an internal integration layer between chatbots (n8n agents) and external medical systems. It provides multi-tenant isolation, flexible schema support via JSONB fields, and secure API key authentication.

## Architecture

- **Backend**: FastAPI (async) with Uvicorn
- **Database**: PostgreSQL 16 with SQLAlchemy 2.x and Alembic migrations
- **Tenancy**: Single database with Row-Level Security (RLS)
- **Flexible Fields**: JSONB columns for tenant-specific custom fields
- **Authentication**: API Key-based server-to-server authentication
- **Observability**: Structured JSON logging with request tracking

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd secre_api
   cp env.example .env
   ```

2. **Start services**:
   ```bash
   make up
   ```

3. **Run migrations**:
   ```bash
   make migrate
   ```

4. **Seed sample data**:
   ```bash
   make seed
   ```

5. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - PgAdmin: http://localhost:5050 (admin@secre.com / admin)

### Available Commands

```bash
make help          # Show all available commands
make up            # Start all services
make down          # Stop all services
make logs          # Show logs
make migrate       # Run database migrations
make seed          # Seed sample data
make test          # Run tests
make clean         # Clean up containers and volumes
make lint          # Run linting
make format        # Format code
```

## API Endpoints

### Authentication
- `POST /v1/auth/api-keys` - Create/rotate/revoke API keys
- `GET /v1/auth/api-keys` - List API keys (redacts secrets)

### Patients
- `POST /v1/patients` - Create patient
- `GET /v1/patients/{id}` - Get patient by ID
- `PATCH /v1/patients/{id}` - Update patient
- `DELETE /v1/patients/{id}` - Delete patient
- `GET /v1/patients` - List patients with filters

### Appointments
- `POST /v1/appointments` - Create appointment
- `GET /v1/appointments/{id}` - Get appointment by ID
- `PATCH /v1/appointments/{id}` - Update appointment
- `DELETE /v1/appointments/{id}` - Delete appointment
- `GET /v1/appointments` - List appointments with filters

## Multi-Tenant Security

The API enforces tenant isolation at multiple levels:

1. **Database Level**: Row-Level Security (RLS) policies ensure data isolation
2. **Application Level**: API key middleware validates tenant access
3. **Request Level**: Each request is scoped to a specific tenant

## Development

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Fast linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for quality checks

### Testing

```bash
# Run all tests
make test

# Run tests locally
make test-local
```

### Database Migrations

```bash
# Create a new migration
make migrate-create message="Add new table"

# Apply migrations
make migrate
```

## Production Deployment

The application is designed to be deployed on AWS with two options:

1. **ECS Fargate + ALB**: For always-warm, low-latency scenarios
2. **API Gateway + Lambda**: For spiky traffic patterns

See the deployment documentation for detailed instructions.

## License

[Add your license information here]
