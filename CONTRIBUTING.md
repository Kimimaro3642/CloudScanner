# Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/my-feature`

## Development Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Code Quality

Before submitting:

```bash
# Lint with pylint
pylint scanner/src/ --exit-zero

# Check style with flake8
flake8 scanner/src/

# Run tests
pytest --cov=scanner/src
```

## Adding Tests

All new features **must** include tests:

```bash
# Create test file
touch scanner/tests/test_my_feature.py

# Run your tests
pytest scanner/tests/test_my_feature.py -v
```

Example test structure:

```python
import unittest
from unittest.mock import patch

class TestMyFeature(unittest.TestCase):
    
    @patch('scanner.src.module.dependency')
    def test_success_case(self, mock_dep):
        # Arrange
        mock_dep.return_value = expected_value
        
        # Act
        result = function_under_test()
        
        # Assert
        self.assertEqual(result, expected_value)
```

## Commit Message Format

```
feat: add new security check for X
^--^  ^---^
│     └─ description
└─ type
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **test**: Tests
- **refactor**: Code refactoring
- **chore**: Maintenance

## Pull Request Process

1. Ensure all tests pass: `pytest`
2. Code coverage should be 80%+
3. All linting checks pass
4. Documentation is updated
5. Commit messages are clear