# Testing Strategy - Tournament Widget

This document outlines our testing strategy to prevent accidental testing against live servers and ensure proper test isolation.

## Problem We're Solving

Previously, tests could accidentally run against a live Flask server, causing:

- Data contamination between tests
- Unpredictable test results
- Potential data loss in development databases
- False test failures due to existing data

## Our Solution

### 1. Test Isolation with Fixtures

We use pytest fixtures in `tests/conftest.py` that:

- Create temporary databases for each test
- Automatically clean up after tests
- Prevent tests from using the main application database

### 2. Test Categories with Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests using test client
- `@pytest.mark.live_server` - Tests requiring live server (use with caution)

### 3. Safe Test Runner

The `run_tests.py` script provides:

- Automatic detection of running Flask servers on ports 5001-5002
- Option to stop live servers before testing
- Environment variable management (including test port 5002)
- Test type selection

## How to Run Tests Safely

### Quick Start (Recommended)

```bash
# Run safe tests (no live server dependencies)
python run_tests.py safe

# Run with verbose output
python run_tests.py safe -v
```

### Test Categories

```bash
# Unit tests only (fastest)
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# All tests (includes potentially risky ones)
python run_tests.py all
```

### Traditional pytest (with safety checks)

```bash
# Run all safe tests
pytest tests/test_app.py tests/test_integration_safe.py -v

# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v
```

## Test File Organization

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_app.py                 # Unit tests for core functionality
├── test_integration_safe.py    # Safe integration tests
├── test_odd_tournament.py      # Specific feature tests
├── test_tournament_creation.py # AI generation tests
└── test_tournament_flow.py     # Legacy integration tests (use with caution)
```

## Safety Features

### 1. Automatic Database Isolation

Every test gets a fresh, temporary database:

```python
@pytest.fixture(scope="function")
def test_app():
    # Creates temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    # ... test runs ...
    # Automatically cleans up database file
```

### 2. Live Server Detection

The test runner automatically detects if Flask is running on ports 5001-5002:

```bash
⚠️  WARNING: Live Flask server(s) detected:
   Port 5001 (PID: 12345)
Do you want to stop them before running tests? (y/N):
```

### 3. Environment Variable Protection

Tests automatically set safe environment variables:

```python
os.environ['TESTING'] = 'true'
os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_RUN_PORT'] = '5002'  # Use test port
```

### 4. Test Markers and Warnings

Tests that might be risky are clearly marked:

```python
@pytest.mark.live_server
def test_with_live_server():
    # This will show a warning when run
```

## Best Practices

### ✅ DO

- Use `python run_tests.py safe` for regular testing
- Write new tests using the `client` fixture from `conftest.py`
- Mark tests appropriately (`@pytest.mark.unit`, `@pytest.mark.integration`)
- Stop live servers before running tests

### ❌ DON'T

- Run tests while Flask server is running (unless intentional)
- Write tests that depend on existing database data
- Use `python tests/test_file.py` directly (bypasses safety checks)
- Skip the test runner for integration tests

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install pytest pytest-cov psutil

# Run safe tests with coverage
python run_tests.py safe -v
```

## Troubleshooting

### "Tests are failing randomly"

- Check if Flask server is running: `lsof -i :5001`
- Use the test runner: `python run_tests.py safe`

### "Database errors in tests"

- Ensure you're using the `client` fixture from `conftest.py`
- Check that tests aren't sharing database state

### "Live server warnings"

- Stop Flask server: `pkill -f "flask run"`
- Or let the test runner stop it automatically

## Migration from Old Tests

Old test files that run against live servers should be:

1. **Updated** to use new fixtures from `conftest.py`
2. **Marked** with appropriate pytest markers
3. **Converted** to use test client instead of HTTP requests
4. **Moved** to `test_integration_safe.py` if they're integration tests

## Example: Converting a Live Server Test

**Before (risky):**

```python
def test_tournament():
    response = requests.post("http://localhost:5001/api/tournament", json=data)
    assert response.status_code == 201
```

**After (safe):**

```python
@pytest.mark.integration
def test_tournament(client):
    response = client.post("/api/tournament", json=data)
    assert response.status_code == 201
```

This ensures tests are isolated, fast, and reliable!
