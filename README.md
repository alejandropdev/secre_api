# Secre API

A **practical, multi-tenant medical integration API** built with FastAPI, PostgreSQL, and Docker. Designed for real-world medical practice management with easy-to-use endpoints.

## ✨ **Key Features**

- **🏥 Multi-tenant Architecture**: Complete tenant isolation with Row Level Security (RLS)
- **📅 Doctor Availability System**: Calendar management with time slot availability
- **👥 Patient Management**: Complete CRUD operations with document-based search
- **📋 Appointment Scheduling**: Smart scheduling with conflict detection
- **🔑 API Key Authentication**: Secure, tenant-specific API keys
- **⚡ High Performance**: Async operations throughout
- **🐳 Docker Ready**: Complete containerization with docker-compose
- **📊 Flexible Schemas**: JSONB fields for tenant-specific customizations

## 🚀 **Quick Start**

### 1. Setup
```bash
git clone <repository-url>
cd secre_api
cp env.example .env
```

### 2. Start Services
```bash
make up
```

### 3. Initialize Database
```bash
make migrate
make seed
```

### 4. Access API
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 **API Keys**

**Master API Key** (for admin operations):
```
hPoRkL0mz91Ui3sPTsFflbBUPvpHC67TdNC4ytGw19evzSRRlfn9To8LmL89b5wP
```

**Miguel Parrado Tenant API Key**:
```
uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc
```

## 📖 **Complete API Documentation**

For detailed endpoint documentation, see [API_ENDPOINTS.md](./API_ENDPOINTS.md)

## 🏥 **Quick Examples**

### Create a Patient
```bash
curl -X POST http://localhost:8000/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
  -d '{
    "first_name": "Juan",
    "first_last_name": "Pérez",
    "birth_date": "1990-05-15",
    "gender_id": 1,
    "document_type_id": 1,
    "document_number": "12345678",
    "phone": "3001234567",
    "email": "juan.perez@example.com"
  }'
```

### Set Doctor Availability
```bash
curl -X POST http://localhost:8000/v1/doctor-availability/availability \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
  -d '{
    "doctor_document_type_id": 1,
    "doctor_document_number": "99999999",
    "day_of_week": 1,
    "start_time": "09:00",
    "end_time": "17:00",
    "appointment_duration_minutes": 30
  }'
```

### Create an Appointment
```bash
curl -X POST http://localhost:8000/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
  -d '{
    "start_datetime": "2025-09-25T10:00:00",
    "end_datetime": "2025-09-25T11:00:00",
    "patient_document_type_id": 1,
    "patient_document_number": "12345678",
    "doctor_document_type_id": 1,
    "doctor_document_number": "99999999",
    "modality": "presencial",
    "state": "scheduled"
  }'
```

### Check Available Time Slots
```bash
curl -X GET "http://localhost:8000/v1/doctor-availability/time-slots/1/99999999?date=2025-09-25" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc"
```

## 🏗️ **Architecture**

### Directory Structure
```
backend/
  app/
    api/v1/              # API endpoints
      ├── admin.py       # Admin operations (tenant creation)
      ├── auth.py        # Authentication & API keys
      ├── patients.py    # Patient management
      ├── appointments.py # Appointment scheduling
      ├── doctor_availability.py # Calendar & availability
      ├── health.py      # Health checks
      ├── lookup.py      # Reference data
      └── router.py      # Main router
    core/                # Configuration and dependencies
    db/                  # Database session and base
    models/              # SQLAlchemy models
    schemas/             # Pydantic schemas
    services/            # Business logic
    middleware/          # Custom middleware (auth, RLS)
    utils/               # Utility functions
  alembic/               # Database migrations
  tests/                 # Test suite
```

### Key Components

- **Models**: SQLAlchemy models with tenant isolation
- **Schemas**: Pydantic for validation and serialization  
- **Services**: Business logic layer
- **Middleware**: API key auth and RLS enforcement
- **Migrations**: Alembic with RLS policies

## 🛠️ **Development**

### Running Tests
```bash
make test
```

### Database Operations
```bash
make migrate          # Run migrations
make rollback         # Rollback last migration
make seed            # Seed lookup data
make reset-db         # Reset database
```

### Code Quality
```bash
make lint            # Run linting
make format          # Format code
make type-check      # Type checking
```

## 🔧 **Configuration**

Environment variables (see `env.example`):
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `MASTER_API_KEY`: Master API key for admin operations

## 📋 **API Endpoints Summary**

### Patients
- `POST /v1/patients/` - Create patient
- `GET /v1/patients/{id}` - Get patient by ID
- `GET /v1/patients/by-document/{type}/{number}` - Get patient by document
- `GET /v1/patients/` - List patients
- `PATCH /v1/patients/{id}` - Update patient
- `DELETE /v1/patients/{id}` - Delete patient

### Appointments
- `POST /v1/appointments/` - Create appointment
- `GET /v1/appointments/{id}` - Get appointment by ID
- `GET /v1/appointments/` - List appointments
- `GET /v1/appointments/by-date-range` - Get appointments by date range
- `PATCH /v1/appointments/{id}` - Update appointment
- `DELETE /v1/appointments/{id}` - Delete appointment

### Doctor Availability
- `POST /v1/doctor-availability/availability` - Set work hours
- `GET /v1/doctor-availability/availability/{type}/{number}` - Get availability
- `PATCH /v1/doctor-availability/availability/{id}` - Update availability
- `DELETE /v1/doctor-availability/availability/{id}` - Delete availability
- `POST /v1/doctor-availability/blocked-time` - Block time slots
- `GET /v1/doctor-availability/time-slots/{type}/{number}` - Get available slots
- `GET /v1/doctor-availability/check-availability/{type}/{number}` - Check availability

### Admin
- `POST /v1/admin/tenants` - Create tenant (master key required)
- `POST /v1/admin/bootstrap` - Bootstrap system (master key required)

## 🔒 **Security**

- **Tenant Isolation**: Complete data separation at database level
- **API Key Authentication**: Secure, tenant-specific access
- **Row Level Security**: Database-level tenant enforcement
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses

## 🎯 **Best Practices Implemented**

1. **RESTful Design**: Standard HTTP methods and status codes
2. **Practical Endpoints**: Simple, easy-to-use API design
3. **Comprehensive CRUD**: Full Create, Read, Update, Delete operations
4. **Smart Scheduling**: Automatic conflict detection and availability checking
5. **Flexible Data**: JSONB fields for custom tenant requirements
6. **Performance**: Async operations and efficient queries
7. **Documentation**: Complete API documentation with examples

## 📄 **License**

MIT License - see LICENSE file for details.