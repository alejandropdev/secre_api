# Secre API Test Suite

This directory contains comprehensive tests for the Secre API multi-tenant medical integration system.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_auth.py`** - API key authentication tests
- **`test_rls.py`** - Row-Level Security (RLS) tenant isolation tests
- **`test_patient_lifecycle.py`** - Patient CRUD lifecycle tests
- **`test_appointment_lifecycle.py`** - Appointment CRUD lifecycle tests
- **`test_validation.py`** - Data validation and normalization tests
- **`test_contracts.py`** - OpenAPI contract compliance tests

### Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.rls` - RLS/tenant isolation tests
- `@pytest.mark.api` - API endpoint tests

## Running Tests

### Prerequisites

1. **Docker and Docker Compose** - For containerized testing
2. **Python 3.11+** - For local testing
3. **PostgreSQL 16** - Test database

### Test Commands

#### Using Make (Recommended)

```bash
# Run all tests with Docker
make test

# Run tests locally (requires local DB)
make test-local

# Run specific test categories
make test-unit
make test-integration
make test-auth
make test-rls
make test-api

# Run with coverage report
make test-coverage

# Run in watch mode
make test-watch
```

#### Using Docker Compose Directly

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Run specific test file
docker-compose -f docker-compose.test.yml run test-api pytest tests/test_auth.py -v
```

#### Using Python Script

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test types
python scripts/run_tests.py --type auth
python scripts/run_tests.py --type rls
python scripts/run_tests.py --type unit

# Run with coverage
python scripts/run_tests.py --coverage

# Run in watch mode
python scripts/run_tests.py --watch

# Run with Docker
python scripts/run_tests.py --docker
```

#### Using Pytest Directly

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with markers
pytest tests/ -m "auth" -v
pytest tests/ -m "rls" -v

# Run with coverage
pytest tests/ -v --cov=backend/app --cov-report=html
```

## Test Configuration

### Environment Variables

- `TEST_DATABASE_URL` - Test database connection string
- `LOG_LEVEL` - Logging level for tests (default: WARNING)

### Database Setup

Tests use a separate test database (`secre_test`) to avoid conflicts with development data. The test database is automatically created and cleaned up for each test run.

### Fixtures

Key fixtures available in all tests:

- `test_db` - Database session for tests
- `test_client` - FastAPI test client
- `async_test_client` - Async HTTP client
- `test_tenant` - Test tenant
- `test_tenant_2` - Second test tenant for isolation tests
- `test_api_key` - Test API key
- `test_api_key_2` - Second test API key
- `auth_headers` - Authentication headers
- `auth_headers_2` - Second tenant auth headers
- `sample_patient_data` - Sample patient data
- `sample_appointment_data` - Sample appointment data

## Test Coverage

The test suite covers:

### Authentication & Authorization
- ✅ Valid API key authentication
- ✅ Invalid/missing API key rejection
- ✅ Revoked API key handling
- ✅ Inactive tenant handling
- ✅ API key case sensitivity
- ✅ Header name case insensitivity

### Row-Level Security (RLS)
- ✅ Tenant A cannot see tenant B's patients
- ✅ Tenant A cannot update tenant B's patients
- ✅ Tenant A cannot delete tenant B's patients
- ✅ Tenant A cannot see tenant B's appointments
- ✅ Search results are tenant-isolated
- ✅ Database-level RLS policy enforcement

### Patient Lifecycle
- ✅ Create patient with validation
- ✅ Get patient by ID
- ✅ Update patient information
- ✅ Delete patient
- ✅ Search patients with filters
- ✅ Pagination support
- ✅ Duplicate document number validation

### Appointment Lifecycle
- ✅ Create appointment with validation
- ✅ Get appointment by ID
- ✅ Update appointment information
- ✅ Delete appointment
- ✅ Search appointments with filters
- ✅ Date range filtering
- ✅ Pagination support

### Data Validation
- ✅ RFC3339 date parsing and UTC conversion
- ✅ Invalid date format rejection
- ✅ End time before start time validation
- ✅ Document type validation
- ✅ Modality validation
- ✅ Custom fields round-trip preservation
- ✅ Custom fields with nested objects
- ✅ Custom fields with null values

### API Contracts
- ✅ Patient CRUD response schemas
- ✅ Appointment CRUD response schemas
- ✅ Error response schemas
- ✅ Pagination response schemas
- ✅ Health check response schema

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

1. **Docker-based testing** - Ensures consistent environment
2. **Coverage reporting** - Enforces minimum coverage thresholds
3. **Parallel execution** - Fast test execution
4. **Isolated tests** - No test interdependencies

## Debugging Tests

### Running Individual Tests

```bash
# Run specific test
pytest tests/test_auth.py::TestAPIAuthentication::test_valid_api_key_success -v

# Run with debug output
pytest tests/test_auth.py -v -s --tb=long

# Run with pdb debugger
pytest tests/test_auth.py -v -s --pdb
```

### Test Database Inspection

```bash
# Connect to test database
docker-compose -f docker-compose.test.yml exec test-db psql -U postgres -d secre_test

# View test data
SELECT * FROM patients;
SELECT * FROM appointments;
SELECT * FROM audit_log;
```

### Logging

Tests use structured JSON logging. To see detailed logs:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
pytest tests/ -v -s
```

## Best Practices

1. **Test Isolation** - Each test is independent and can run in any order
2. **Clean State** - Database is reset between tests
3. **Realistic Data** - Use fixtures with realistic test data
4. **Error Testing** - Test both success and failure scenarios
5. **Edge Cases** - Test boundary conditions and edge cases
6. **Performance** - Tests should complete quickly (< 1 second each)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check connection string format
   - Verify database exists

2. **Import Errors**
   - Ensure PYTHONPATH includes project root
   - Check virtual environment activation

3. **Permission Errors**
   - Ensure test database user has proper permissions
   - Check file permissions for test scripts

4. **Timeout Errors**
   - Increase test timeout in pytest configuration
   - Check for hanging database connections

### Getting Help

- Check test output for specific error messages
- Use `--tb=long` for detailed tracebacks
- Enable debug logging with `LOG_LEVEL=DEBUG`
- Review test database state if needed
