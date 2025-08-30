# SideQuest Backend Testing Setup

This document describes the testing infrastructure we've set up for the SideQuest backend service.

## Overview

We've replaced the simple SQLite in-memory database with a proper PostgreSQL test database using Docker. This is necessary because SideQuest uses PostgreSQL-specific features like:

- **JSON columns** for storing user preferences and quest tags
- **Enums** for quest categories, difficulty levels, and ratings
- **PostgreSQL-specific data types** that aren't compatible with SQLite

## What We've Created

### 1. Docker Compose Test Configuration

- **File**: `docker-compose.test.yml`
- **Database**: PostgreSQL 15
- **Port**: 5434 (to avoid conflicts with development database)
- **Credentials**:
  - User: `sidequest_user`
  - Password: `sidequest_password`
  - Database: `sidequest_test`

### 2. Updated Testing Configuration

- **File**: `config.py` (TestingConfig class)
- **Database URI**: Points to PostgreSQL test instance
- **Fixed secret keys**: For consistent testing environment
- **JWT settings**: Configured for testing

### 3. Test Infrastructure

- **`conftest.py`**: Pytest fixtures and database setup
- **`setup_db.py`**: Test data initialization with realistic sample data
- **`pytest.ini`**: Pytest configuration and options

### 4. Test Files

- **`test_sidequest_models.py`**: Comprehensive model tests
- **`test_sidequest_services.py`**: Service layer tests with mocked external dependencies

### 5. Convenience Scripts

- **`run_tests.py`**: Python test runner with database management
- **`test_db.sh`**: Shell script for database container management

## How to Use

### Quick Start

```bash
# 1. Start test database
./test_db.sh start

# 2. Run tests
python tests/run_tests.py

# 3. Stop test database
./test_db.sh stop
```

### Manual Testing

```bash
# Start database
docker-compose -f docker-compose.test.yml up -d

# Run specific tests
python -m pytest tests/test_sidequest_models.py -v
python -m pytest tests/test_sidequest_services.py -v

# Run with coverage
python -m pytest tests/ --cov=backend.sidequest --cov-report=html

# Stop database
docker-compose -f docker-compose.test.yml down
```

## Test Database Management

### Using the Shell Script

```bash
./test_db.sh start    # Start database
./test_db.sh status   # Check status
./test_db.sh logs     # View logs
./test_db.sh stop     # Stop database
./test_db.sh clean    # Remove volumes
```

### Using Docker Compose Directly

```bash
# Start
docker-compose -f docker-compose.test.yml up -d

# Check status
docker-compose -f docker-compose.test.yml ps

# View logs
docker-compose -f docker-compose.test.yml logs -f

# Stop
docker-compose -f docker-compose.test.yml down

# Clean up (remove volumes)
docker-compose -f docker-compose.test.yml down -v
```

## Test Data

The `setup_db.py` creates realistic test data including:

- **3 regular users** + 1 Apple user
- **User balances** for each user
- **SideQuest user profiles** with varied preferences
- **20 sample quests** with different states (completed, skipped, selected)
- **10 generation logs** with realistic metadata

## Test Coverage

### Models (`test_sidequest_models.py`)

- ✅ SideQuestUser creation and defaults
- ✅ SideQuest lifecycle (creation, completion, skipping, selection)
- ✅ Quest expiration logic
- ✅ Model serialization (to_dict methods)
- ✅ Relationships between models
- ✅ Enum handling

### Services (`test_sidequest_services.py`)

- ✅ User preferences management
- ✅ Quest CRUD operations
- ✅ Quest state transitions
- ✅ Quest generation (with mocked OpenAI)
- ✅ Generation logging
- ✅ Service integration tests

## Key Benefits

1. **PostgreSQL Compatibility**: Tests run against the same database type as production
2. **Realistic Data**: Tests use actual database schemas and relationships
3. **Isolation**: Each test gets a fresh database with sample data
4. **Automation**: Easy database management with scripts
5. **Comprehensive**: Covers models, services, and integration scenarios

## Troubleshooting

### Common Issues

**Database Connection Errors**

- Ensure Docker is running
- Check if port 5434 is available
- Verify container is healthy: `docker ps --filter name=sidequest_db_test`

**Port Conflicts**

- Modify `docker-compose.test.yml` to use a different port
- Check for other PostgreSQL instances: `lsof -i :5434`

**Permission Errors**

- Ensure Docker has proper permissions
- Try running with `sudo` if needed (not recommended for production)

**Test Failures**

- Check database is running: `./test_db.sh status`
- View database logs: `./test_db.sh logs`
- Ensure virtual environment is activated

### Debugging

```bash
# Connect to test database directly
psql -h localhost -p 5434 -U sidequest_user -d sidequest_test

# View container logs
docker logs sidequest_db_test

# Check container health
docker inspect sidequest_db_test | grep Health
```

## Next Steps

1. **Add More Tests**: Expand coverage to routes and edge cases
2. **Performance Tests**: Add tests for database query performance
3. **Integration Tests**: Test with real external services (with proper mocking)
4. **CI/CD Integration**: Add GitHub Actions or similar for automated testing

## Files Created/Modified

- ✅ `docker-compose.test.yml` - Test database configuration
- ✅ `config.py` - Updated TestingConfig
- ✅ `conftest.py` - Test fixtures and setup
- ✅ `tests/setup_db.py` - Test data initialization
- ✅ `tests/test_sidequest_models.py` - Model tests
- ✅ `tests/test_sidequest_services.py` - Service tests
- ✅ `tests/run_tests.py` - Test runner
- ✅ `test_db.sh` - Database management script
- ✅ `pytest.ini` - Pytest configuration
- ✅ `README.md` - Updated with testing information
- ✅ `TESTING_SETUP.md` - This documentation

The testing setup is now complete and ready to use! 🎉
