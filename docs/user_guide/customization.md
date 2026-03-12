# Customization

This guide explains how to customize this Python package template for your
specific project needs, including renaming, configuration changes, and removing
unwanted features.

## Overview

The template is designed to be easily adaptable. Common customizations include:

- **Package renaming**: Change name, description, author
- **Dependency management**: Add/remove/modify dependencies
- **Tool configuration**: Adjust linting, formatting, testing settings
- **Feature removal**: Remove unused tools or features
- **Structure changes**: Modify directory layout

## Package Renaming

### 1. Update Project Metadata

Edit `pyproject.toml`:

```toml
[project]
name = "your-package-name"
description = "Your package description"
authors = [{ name = "Your Name", email = "your.email@example.com" }]
```

### 2. Rename Package Directory

```bash
# Rename the source directory
mv src/python_package_template src/your_package_name

# Update all imports in your code
find src -name "*.py" -exec sed -i 's/python_package_template/your_package_name/g' {} \;
```

### 3. Update Entry Points

In `pyproject.toml`:

```toml
[project.scripts]
your-package-name = "your_package_name.cli.main:app"
```

### 4. Update Documentation

- Change `zensical.toml` site name and URLs
- Update `README.md` and other docs
- Rename references in code comments

### 5. Update Tests

```bash
# Rename test files and update imports
mv tests/test_hello_world.py tests/test_your_feature.py
```

## Dependency Management

### Adding Dependencies

#### Runtime Dependencies

Add to `pyproject.toml`:

```toml
dependencies = [
    "requests>=2.25.0",
    "click>=8.0.0",
    "typer",  # Already included
]
```

#### Development Dependencies

Add to optional dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest",  # Already included
    "new-dev-tool>=1.0.0",
]
```

#### Documentation Dependencies

```toml
[project.optional-dependencies]
docs = [
    "zensical",  # Already included
    "mkdocs-new-plugin",
]
```

### Removing Dependencies

1. Remove from `pyproject.toml`
2. Update any code using the dependency
3. Remove related configuration
4. Update tests

## Tool Configuration

### Linting (Ruff)

Configure rules in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "B", "I"]  # Enable specific rule categories
ignore = ["E501"]  # Ignore specific rules

[tool.ruff.per-file-ignores]
"tests/*" = ["B011"]  # Ignore rules in test files
```

### Testing (Pytest)

Modify test configuration:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Type Checking (Pyright)

Adjust in `pyproject.toml`:

```toml
[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
pythonVersion = "3.10"
typeCheckingMode = "strict"  # Options: off, basic, strict
```

## Removing Features

### Remove Pre-commit Hooks

If you don't want pre-commit:

1. Delete `.pre-commit-config.yaml`
2. Remove `pre-commit` from dev dependencies
3. Update CI workflow to remove pre-commit steps

### Remove Documentation

To remove MkDocs:

1. Delete `docs/` directory
2. Remove docs dependencies from `pyproject.toml`
3. Remove MkDocs configuration from CI

### Remove CLI

If no command-line interface needed:

1. Delete `src/your_package/cli/`
2. Remove CLI dependencies (typer)
3. Remove script entry points
4. Update `__main__.py`

## Structure Changes

### Flat Layout (No src/)

If you prefer flat layout:

1. Move `src/your_package/` to `your_package/`
2. Update imports throughout codebase
3. Modify pytest pythonpath
4. Update tool configurations

### Custom Directory Structure

```bash
src/
├── your_package/
│   ├── core/      # Core functionality
│   ├── utils/     # Utilities
│   ├── cli/       # Command line
│   └── api/       # API clients
```

Update `__init__.py` to expose modules appropriately.

## Configuration Files

### Update .gitignore

Add project-specific ignores:

```gitignore
# Project specific
*.log
.cache/
.env
.DS_Store
```

### Update .pre-commit-config.yaml

Modify hook configurations:

```yaml
- repo: https://github.com/streetsidesoftware/cspell-cli
  rev: v9.6.0 # Keep this version or update to the latest stable
  hooks:
      - id: cspell
        name: Check spelling in Python, reSt, and Markdown files.
        args: ['--config', 'cspell.json']
        files: ^.*\.(py|rst|md)$ # Add additional file types to check typos
        stages: [pre-commit]
      - id: cspell
        name: Check commit message spelling.
        args:
            - --config
            - cspell.json
            - --no-must-find-files
            - --no-progress
            - --no-summary
            - --files
            - .git/COMMIT_EDITMSG
        stages: [commit-msg]
        always_run: true
```

### Update CI Workflows

Modify `.github/workflows/CI.yml`:

```yaml
jobs:
    test:
        runs-on: ubuntu-latest
        strategy:
            matrix:
                python-version: ['3.9', '3.10'] # Remove versions you don't support
```

## Documentation Customization

### Update Zensical Config

```toml
[project]
site_name = "Your Package Docs"
site_description = "Documentation for your package"
repo_url = "https://github.com/yourusername/your-repo"

[project.theme]
palette = [
    { scheme = "default", primary = "blue" },
    { scheme = "slate", primary = "blue" },
]
```

### Update Navigation

Modify `zensical.toml` nav to match your structure:

```yaml
nav:
    - Home: index.md
    - User Guide:
          - Installation: installation.md
          - API: api.md
    - API Reference: reference/
```

## Advanced Customizations

### Custom CLI Commands

Add more commands to `cli/main.py`:

```python
import typer

app = typer.Typer()

@app.command()
def new_command(param: str):
    """New command description."""
    print(f"Processing {param}")

@app.command()
def another_command():
    """Another command."""
    pass
```

### Custom Workflows

Add new GitHub Actions workflows in `.github/workflows/`:

```yaml
# .github/workflows/custom.yml
name: Custom Workflow
on:
    push:
        branches: [main]

jobs:
    custom:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4
            - name: Custom Step
              run: echo "Custom workflow"
```

### Environment-Specific Configs

Use different settings for different environments:

```toml
[tool.coverage.run]
branch = true
source = ["src"]
omit = [
    "*/tests/*",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
]
```

## Migration Checklist

- [ ] Update package name and metadata
- [ ] Rename directories and files
- [ ] Update all imports
- [ ] Modify dependencies
- [ ] Adjust tool configurations
- [ ] Update documentation
- [ ] Test everything works
- [ ] Update CI/CD settings
- [ ] Publish to PyPI

## Common Pitfalls

### Import Issues

- **Forgotten imports**: Use `grep` to find all references
- **Circular imports**: Restructure modules
- **Path issues**: Update `pythonpath` in tools

### Configuration Conflicts

- **Conflicting rules**: Review tool configurations
- **Version mismatches**: Keep tool versions consistent
- **Platform differences**: Test on multiple platforms

### CI/CD Problems

- **Workflow failures**: Check action versions
- **Secret issues**: Verify repository secrets
- **Permission problems**: Check branch protection rules

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](../dev/troubleshooting.md) guide
2. Review tool-specific documentation
3. Search existing issues in the template repository
4. Ask in relevant communities

Remember to test thoroughly after each major change, and consider updating your
documentation to reflect customizations.
