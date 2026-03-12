# Testing

This guide explains the testing setup in this Python package template, including
how to write tests, run them, and measure coverage.

## Overview

The template uses Pytest as the testing framework with the following features:

- **Comprehensive test discovery**: Automatic test finding
- **Fixtures**: Reusable test setup/teardown
- **Coverage reporting**: Code coverage measurement
- **Parameterized tests**: Multiple test cases from single function
- **Markers**: Categorize and filter tests

## Test Structure

### Directory Layout

```text
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_hello_world.py  # Tests for hello_world module
└── test_*.py           # Other test files
```

### Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Fixtures: Descriptive names

## Writing Tests

### Basic Test

```python
# tests/test_example.py
from your_package.example import add_numbers

def test_add_numbers():
    """Test basic addition."""
    result = add_numbers(2, 3)
    assert result == 5

def test_add_negative():
    """Test addition with negative numbers."""
    result = add_numbers(-1, 1)
    assert result == 0
```

### Using Fixtures

Fixtures provide reusable test data and setup.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"name": "test", "value": 42}

@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    return file_path

# tests/test_example.py
def test_with_fixture(sample_data):
    assert sample_data["name"] == "test"

def test_file_operations(temp_file):
    assert temp_file.exists()
```

### Parameterized Tests

Run the same test with different inputs.

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (10, 11),
])
def test_increment(input, expected):
    from your_package.example import increment
    assert increment(input) == expected
```

### Mocking

Use `pytest-mock` for mocking dependencies.

```python
def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok"}

    # Mock the requests.get call
    mock_get = mocker.patch('requests.get')
    mock_get.return_value = mock_response

    from your_package.api import fetch_data
    result = fetch_data()
    assert result["status"] == "ok"
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_example.py

# Run specific test function
pytest tests/test_example.py::test_add_numbers

# Run tests matching pattern
pytest -k "add"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Open HTML report
open htmlcov/index.html
```

### Test Categories

```bash
# Run only unit tests
pytest -m "unit"

# Skip integration tests
pytest -m "not integration"

# Run slow tests
pytest -m "slow"
```

## Configuration

### pytest.ini Options (`pyproject.toml`)

```toml
--8<-- "pyproject.toml:117:129"
```

### Coverage Configuration

```toml
--8<-- "pyproject.toml:81:85"
```

## Test Types

### Unit Tests

Test individual functions/classes in isolation.

```python
def test_calculator_add():
    calc = Calculator()
    assert calc.add(1, 2) == 3
```

### Integration Tests

Test interactions between components.

```python
@pytest.mark.integration
def test_full_workflow():
    # Test complete user flow
    pass
```

### Fixtures for Setup

```python
@pytest.fixture
def database():
    """Set up test database."""
    db = create_test_db()
    yield db
    db.cleanup()
```

## Best Practices

### Test Organization

- **One test per behavior**: Each test should verify one thing
- **Descriptive names**: Test names should explain what they verify
- **Arrange-Act-Assert**: Structure tests clearly
- **DRY principle**: Use fixtures for common setup

### Coverage Goals

- **Aim for high coverage**: Target >90% for critical code
- **Focus on logic**: Cover branches, error paths
- **Don't test generated code**: Exclude auto-generated files

### Mocking Guidelines

- **Mock external dependencies**: APIs, databases, file I/O
- **Don't mock your own code**: Test real implementations
- **Verify interactions**: Check that mocks were called correctly

### Test Data

- **Use realistic data**: Test with data similar to production
- **Edge cases**: Test boundaries, empty inputs, errors
- **Fixtures for reuse**: Share test data across tests

## CI/CD Integration

Tests run automatically in GitHub Actions:

- **On pull requests**: Full test suite with coverage
- **On pushes**: Quick validation
- **On releases**: Complete test run

## Debugging Tests

### Running Failed Tests

```bash
# Run only failed tests
pytest --lf

# Run failed tests first
pytest --ff
```

### Debugging Output

```bash
# Show print statements
pytest -s

# Debug with pdb
pytest --pdb
```

### Test Isolation

- **Clean up after tests**: Use fixtures with `yield`
- **Avoid shared state**: Don't rely on test execution order
- **Use unique names**: For files, databases, etc.

## Common Issues

### Import Errors

- **Path issues**: Ensure `src` is in `pythonpath`
- **Missing dependencies**: Install test dependencies

### Slow Tests

- **Mark as slow**: Use `@pytest.mark.slow`
- **Parallel execution**: Use `pytest-xdist` for speedup

### Coverage Problems

- **Missing lines**: Add tests for uncovered code
- **False positives**: Use `# pragma: no cover` judiciously

## Advanced Features

### Custom Markers

```python
# tests/conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")
```

### Test Factories

```python
def create_test_data(size):
    return [i for i in range(size)]

@pytest.fixture(params=[10, 100, 1000])
def test_data(request):
    return create_test_data(request.param)
```

For more information, see the [Pytest documentation](https://docs.pytest.org/)
and [Coverage.py docs](https://coverage.readthedocs.io/).
