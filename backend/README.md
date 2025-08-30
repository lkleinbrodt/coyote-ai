# Coyote AI Backend

This is the backend API server that serves multiple applications including SideQuest.

## Testing Setup

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with virtual environment activated
- PostgreSQL client tools (optional, for debugging)

### Running Tests

The SideQuest backend uses PostgreSQL for testing due to PostgreSQL-specific features like JSON columns and enums.

#### 1. Start Test Database

```bash
# From the backend directory
docker-compose -f docker-compose.test.yml up -d
```

This will start a PostgreSQL 15 container on port 5434 with:

- Database: `sidequest_test`
- User: `sidequest_user`
- Password: `sidequest_password`

#### 2. Run Tests

```bash
# Run all SideQuest tests
python -m pytest tests/test_sidequest_models.py tests/test_sidequest_services.py -v

# Or use the test runner script
python tests/run_tests.py

# Run specific test file
python -m pytest tests/test_sidequest_models.py -v

# Run with coverage
python -m pytest tests/ --cov=backend.sidequest --cov-report=html
```

#### 3. Stop Test Database

```bash
docker-compose -f docker-compose.test.yml down
```

### Test Structure

- `conftest.py` - Test fixtures and database setup
- `setup_db.py` - Test data initialization
- `test_sidequest_models.py` - Model tests
- `test_sidequest_services.py` - Service layer tests
- `run_tests.py` - Convenience test runner

### Test Database

The test database is completely isolated and gets recreated for each test run. Each test function gets a fresh database with sample data.

### Troubleshooting

- **Database connection errors**: Ensure the test database container is running
- **Port conflicts**: Check if port 5434 is available, or modify `docker-compose.test.yml`
- **Permission errors**: Ensure Docker has proper permissions to create containers

## Development

### Virtual Environment

```bash
# Activate virtual environment (from coyote-ai root)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Migrations

```bash
# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "Description of changes"
```

## Applications

### SideQuest

SideQuest is a quest generation app that creates personalized daily tasks for users.

- **Models**: User preferences, quests, generation logs
- **Services**: Quest generation, user management, preferences
- **Routes**: API endpoints for quest operations

### Other Apps

- **Autodraft**: AI-powered writing assistant
- **Speech**: Speech coaching and analysis
- **Lifter**: Workout tracking and planning
- **Lyrica**: Music analysis and recommendations
