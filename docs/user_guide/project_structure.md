# Project Structure

This guide explains the recommended project structure used in this Python
package template, including the rationale behind the `src/` layout and how to
organize your code effectively.

## Overview

This template follows modern Python packaging best practices with a `src/`
layout. This structure separates your package code from development files and
tools, providing better isolation and avoiding common packaging issues.

## Directory Structure

```text
your-project/
├── src/
│   └── your_package/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py
│       ├── utils/
│       │   ├── __init__.py
│       │   └── log.py
│       └── other_modules.py
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── docs/
│   ├── index.md
│   ├── user_guide/
│   └── dev/
├── .github/
│   └── workflows/
├── pyproject.toml
├── .pre-commit-config.yaml
├── zensical.toml
└── other config files...
```

## Why src/ Layout

The `src/` layout offers several advantages:

- **Clean separation**: Package code is isolated from development files
- **Avoid import issues**: Prevents accidental imports of development
  dependencies
- **Better testing**: Easier to test the installed package vs. local development
  version
- **Standard practice**: Recommended by Python packaging guides

## Package Organization

### Core Package (`src/your_package/`)

- **`__init__.py`**: Package initialization, imports, and `__version__`
- **`__main__.py`**: Entry point for `python -m your_package`
- **Modules**: Your main code files
- **Subpackages**: Organized by functionality (e.g., `cli/`, `utils/`)

### Example Structure Breakdown

#### `__init__.py`

```python
"""Top-level package for your_package."""

from __future__ import annotations

from your_package.main_module import main_function
from your_package.version import __version__

__all__ = ["__version__", "main_function"]
```

- Imports key functions/classes for easy access
- Defines `__all__` for controlled exports
- Includes version information

#### `__main__.py`

```python
"""Main entry point for the package."""

from __future__ import annotations

if __name__ == "__main__":
    from your_package.cli.main import app
    app()
```

- Allows running with `python -m your_package`
- Imports and runs the CLI app

#### CLI Structure (`cli/`)

```text
cli/
├── __init__.py
└── main.py
```

- `main.py`: Typer/Fire CLI application
- Keeps CLI logic separate from core functionality

#### Utils (`utils/`)

```text
utils/
├── __init__.py
└── helpers.py
```

- Shared utility functions
- Logging, configuration, etc.

## Tests Organization

### `tests/` Directory

- **`conftest.py`**: Shared fixtures and configuration
- **`test_*.py`**: Test files matching module names
- **Structure mirrors package**: `tests/test_utils.py` for
  `src/your_package/utils/`

### Example Test Structure

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

# tests/test_main_module.py
from your_package.main_module import main_function

def test_main_function(sample_data):
    result = main_function(sample_data)
    assert result is not None
```

## Documentation Structure

### `docs/` Directory

- **`index.md`**: Home page
- **`user_guide/`**: User-facing guides
- **`dev/`**: Developer documentation
- **`reference/`**: Auto-generated API docs

## Configuration Files

### Root Level Files

- **`pyproject.toml`**: Packaging and tool configuration
- **`.pre-commit-config.yaml`**: Pre-commit hooks
- **`zensical.toml`**: Documentation configuration
- **`.github/workflows/`**: CI/CD pipelines

## Customizing the Structure

### Renaming the Package

1. Rename `src/python_package_template/` to `src/your_package_name/`
2. Update all imports throughout the codebase
3. Update `pyproject.toml` name and entry points
4. Update `zensical.toml` and documentation references

### Adding New Modules

1. Create new `.py` files in `src/your_package/`
2. Add imports to `__init__.py` if needed
3. Create corresponding tests in `tests/`
4. Update documentation

### Adding Subpackages

1. Create new directories under `src/your_package/`
2. Add `__init__.py` to each subpackage
3. Organize related functionality
4. Update imports and tests

## Best Practices

### Import Organization

- Use absolute imports within the package
- Avoid relative imports where possible
- Keep `__init__.py` files minimal

### File Naming

- Use `snake_case` for modules and functions
- Prefix test files with `test_`
- Use descriptive names

### Code Organization

- Group related functionality in modules
- Keep functions/classes focused on single responsibilities
- Use subpackages for complex features

## Migration from Flat Layout

If migrating from a flat layout (no `src/`):

1. Move package code into `src/your_package/`
2. Update all import statements
3. Adjust tool configurations (e.g., pytest `pythonpath`)
4. Update documentation paths

## Common Issues

- **Import errors**: Ensure `src/` is in Python path during development
- **Test discovery**: Configure pytest with correct paths
- **Documentation**: Update API reference generation for new structure

For more information, see the
[Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
and
[src layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
