# Packaging

This guide explains the packaging setup in this Python package template,
including how dependencies are managed, the build system, and how to customize
it for your project.

## Overview

This template uses modern Python packaging standards with `pyproject.toml` as
the configuration file. It leverages:

- **Hatchling**: A fast, modern build backend
- **Hatch-VCS**: For automatic version management from Git tags
- **Optional Dependencies**: Grouped extras for different use cases

## pyproject.toml Structure

The `pyproject.toml` file contains all packaging metadata and configuration:

### Build System

```toml
--8<-- "pyproject.toml:1:3"
```

This specifies Hatchling as the build backend with VCS version management.

### Project Metadata

```toml
--8<-- "pyproject.toml:5:20"
```

Key fields:

- `name`: Package name on PyPI
- `authors`: Author information
- `description`: Short description
- `classifiers`: PyPI classifiers for discoverability
- `requires-python`: Minimum Python version
- `dynamic`: Fields computed at build time (version from Git)

### Dependencies

```toml
--8<-- "pyproject.toml:21:21"
```

Core runtime dependencies. Add your package's dependencies here.

### Optional Dependencies

```toml
--8<-- "pyproject.toml:23:36"
```

Extras allow users to install additional features:

```bash
uv pip install "your-package[dev,docs]"
```

### Scripts/Entry Points

```toml
--8<-- "pyproject.toml:38:39"
```

Defines command-line scripts. This creates the `python_package_template`
command.

### URLs

```toml
--8<-- "pyproject.toml:41:46"
```

Links for PyPI project page.

## Version Management

Version is managed automatically using Hatch-VCS:

```toml
--8<-- "pyproject.toml:48:49"
```

Versions are derived from Git tags (e.g., tag `v1.2.3` → version `1.2.3`).

## Tool Configurations

The file also includes configurations for various tools:

- **Coverage**: Test coverage settings
- **Flake8**: Linting rules
- **Black**: Code formatting
- **Pytest**: Test configuration
- **Pyright**: Type checking

## Customizing for Your Project

### 1. Update Project Metadata

Change the name, description, authors, and URLs to match your project.

### 2. Add Dependencies

Add your runtime dependencies to the `dependencies` list.

For development dependencies, add to the appropriate optional groups.

### 3. Configure Tools

Adjust tool settings in the `[tool.*]` sections to match your preferences.

### 4. Add Scripts

If your package has CLI commands, add them to `[project.scripts]`.

## Building and Publishing

### Local Building

Build the package locally:

```bash
python -m build
```

This creates `dist/` with wheel and source distributions.

### Publishing to PyPI

After building:

```bash
# Using uv (recommended)
uv publish

# Or using twine
pip install twine
twine upload dist/*
```

For Test PyPI first:

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

## Common Tasks

### Adding a New Dependency

1. Add to `dependencies` or an optional group in `pyproject.toml`
2. Update your environment: `uv pip install -e ".[dev]"` (or equivalent)
3. Test that it works

### Changing Python Version Requirements

Update `requires-python` and the classifiers list.

### Adding a New Optional Feature

Create a new key under `[project.optional-dependencies]` with the feature name.

## Troubleshooting

- **Build fails**: Ensure Hatchling and Hatch-VCS are installed
- **Version not updating**: Check Git tags match the expected format
- **Dependencies not found**: Verify extras are installed correctly

For more details, see the
[PyPA packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
and [Hatch documentation](https://hatch.pypa.io/).
