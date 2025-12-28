# Testing Guide for Weather Forecast API

This guide covers how to test the Weather Forecast API using the integration test script.

## Test Structure

```
tests/
└── manual_test.py       # Integration test script
```

## Prerequisites

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running Integration Tests

The manual test script tests against a running API server (local or remote).

### Prerequisites

Start the API server first:

```bash
# In one terminal, start the server
uvicorn main:app --reload --port 8000
```

### Run Manual Tests

```bash
# In another terminal, run the manual tests

# Test against local server (default)
python tests/manual_test.py

# Test against specific URL
python tests/manual_test.py http://localhost:8000

# Test against remote server
python tests/manual_test.py https://weather-api.example.com
```

### Manual Test Output

The script will:
- Test all API endpoints
- Display colored output (green = pass, red = fail)
- Show detailed response data
- Print a summary at the end

Example output:
```
======================================================================
Testing Root Endpoint: GET /
======================================================================

✓ Root endpoint returned 200 OK
✓ Response contains service info: Weather Forecast API v1.0.0
{
  "service": "Weather Forecast API",
  "version": "1.0.0",
  ...
}
```

## What the Tests Do

The integration test script:
- Requires running API server
- Tests real database connections
- Validates end-to-end functionality
- Tests against actual data

## Extending the Tests

To add new test scenarios, edit `tests/manual_test.py`:

1. Add a new method to the `APITester` class
2. Call it from `run_all_tests()`

**Example:**
```python
def test_new_endpoint(self):
    self.print_header("Testing New Endpoint")
    response = requests.get(f"{self.base_url}/new-endpoint")

    if response.status_code == 200:
        self.print_success("New endpoint works!")
    else:
        self.print_error(f"Failed: {response.status_code}")
```

## Test Data Requirements

You need actual data in the database to test:
- At least one city with a valid forecast
- Historical forecasts (optional, for history tests)

The manual test script will gracefully handle missing data:
- 404 responses for cities with no forecasts are expected
- Empty statistics are valid
- Tests focus on API behavior, not data availability

## Continuous Integration

To integrate tests into CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Start API server
  run: uvicorn main:app --port 8000 &

- name: Wait for server
  run: sleep 5

- name: Run integration tests
  run: python tests/manual_test.py http://localhost:8000
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Make sure you're in the forecast_api directory
cd forecast_api

# Run tests from there
pytest
```

### Database Connection Errors (Manual Tests)

Check:
1. Is the API server running?
2. Is the database configured correctly?
3. Are environment variables set?

## Best Practices

1. **Test against real data** - Integration tests validate actual database queries
2. **Use descriptive test names** - Clear method names for each test scenario
3. **Test both success and failure** - Happy path and error cases
4. **Check response structure** - Validate JSON schema, not just status codes
5. **Test with different cities** - Ensure tests work with various data sets

## Quick Reference

```bash
# Start the API server
uvicorn main:app --reload --port 8000

# Run integration tests (local)
python tests/manual_test.py

# Run integration tests (remote)
python tests/manual_test.py https://api.example.com
```
