# Testing Guide

## Quick Reference

```bash
# Run all unit tests
pytest scanner/tests/

# Run with coverage report
pytest scanner/tests/ --cov=scanner/src --cov-report=html

# Run specific test file
pytest scanner/tests/test_nsg.py -v

# Run with detailed output
pytest -vv -s
```

## Generate Test Reports (Without Azure Credentials)

Sample reports can be generated without running against a real Azure subscription to demonstrate the output format:

```bash
# Generate sample findings and create test reports
python test_reports.py

# View the HTML report in browser
start reports/test_run.html      # Windows
open reports/test_run.html       # macOS/Linux

# View the JSON output
cat reports/test_run.json
```

This is useful for:
- Testing the report generation without Azure credentials
- Demonstrating how the scanner's output looks
- Development and documentation purposes

## Test Structure

Each test follows **Arrange-Act-Assert** pattern:

```python
def test_example(self):
    # Arrange: Set up test data and mocks
    mock_data = {'key': 'value'}
    
    # Act: Execute the function being tested
    result = function_under_test(mock_data)
    
    # Assert: Verify the result
    self.assertEqual(result, expected_value)
```

## Mocking Azure SDK

Use `unittest.mock.patch` to mock Azure client calls:

```python
from unittest.mock import patch

@patch('scanner.src.checks.nsg.azure_client')
def test_example(self, mock_azure_client):
    mock_azure_client.list_nsgs.return_value = [mock_nsg]
    findings = check_nsg_rules()
    self.assertTrue(len(findings) > 0)
```

## Coverage Goals

- Overall: 80%+ code coverage
- Security checks: 100% coverage
- Report generation: 90%+ coverage

## Running Tests by Category

```bash
# Unit tests only
pytest scanner/tests/ -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

## Debugging Tests

```bash
# Print output during test
pytest -s -v

# Drop into debugger on failure
pytest --pdb
```

## View Coverage Report

```bash
# Generate HTML report
pytest --cov=scanner/src --cov-report=html

# Open in browser
open htmlcov/index.html
```