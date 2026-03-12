# Development Tools

This guide covers the development tools configured in this template, including
pre-commit hooks, code quality tools, and how to use them effectively.

## Overview

The template includes a comprehensive set of tools for maintaining code quality,
consistency, and reliability:

- **Pre-commit hooks**: Automated checks before commits
- **Code formatting**: Ruff for consistent style
- **Linting**: Ruff for code quality
- **Spell checking**: CSpell for documentation
- **Security scanning**: Bandit for vulnerability detection

## Pre-commit Hooks

Pre-commit runs automated checks before each commit to catch issues early.

### Setup

```bash
pre-commit install
pre-commit install --hook-type commit-msg  # For commit message validation
```

### Configuration (`.pre-commit-config.yaml`)

The configuration includes hooks for:

- **Code formatting**: Ruff
- **Linting**: Ruff
- **Security**: Bandit
- **Spell checking**: CSpell
- **General**: Trailing whitespace, end-of-file fixes

### Running Pre-commit

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Run on staged files (automatic on commit)
pre-commit run
```

## Code Formatting

### Ruff

Ruff is a fast Python linter and formatter, alternative to Flake8.

**Configuration** (in `pyproject.toml`):

```toml
--8<-- "pyproject.toml:110:145"
```

**Usage**:

```bash
# Lint and fix
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/
```

## Spell Checking

### CSpell

CSpell checks spelling in code comments, documentation, and strings.

**Configuration** (`cspell.json`):

```json
--8<-- "cspell.json:5:12"
```

**Usage**:

```bash
cspell "**/*.{py,md}"
```

## Security Scanning

### Bandit

Bandit finds common security issues in Python code.

**Configuration** (in `pyproject.toml`):

```toml
--8<-- "pyproject.toml:54:58"
```

**Usage**:

```bash
bandit -r src/
```

## Testing Tools

### Pytest

Pytest is the testing framework with coverage reporting.

**Configuration** (in `pyproject.toml`):

```toml
--8<-- "pyproject.toml:66:78"
```

**Usage**:

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_specific.py::test_function
```

### Coverage

Coverage.py measures code coverage.

**Configuration** (in `pyproject.toml`):

```toml
--8<-- "pyproject.toml:60:64"
```

The default minimum coverage is set to 0%. You should aim for higher coverage as
you add tests.

## Additional Tools

### Commitlint

Validates commit messages follow conventional commits format.

**Configuration** (`commitlint.config.js`):

```javascript
--8<-- "commitlint.config.js:2:3"
```

### ShellCheck

Checks shell scripts for common issues.

**Usage**:

```bash
shellcheck scripts/*.sh
```

## Customizing Tool Configurations

### Modifying Rules

Edit configurations in `pyproject.toml`:

```toml
--8<-- "pyproject.toml:113:131"
```

### Adding New Tools

1. Add to `pyproject.toml` or separate config files
2. Include in `.pre-commit-config.yaml` if applicable
3. Update CI workflows

### Disabling Tools

Comment out or remove from `.pre-commit-config.yaml`:

```yaml
# - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
#   ...
```

## CI/CD Integration

All tools run automatically in GitHub Actions:

- **Validation workflow**: Runs on PRs and pushes
- **Publish workflow**: Runs on releases

Check `.github/workflows/` for details.

## Troubleshooting

### Pre-commit Issues

- **Hook fails**: Run `pre-commit run --all-files` locally first
- **Slow commits**: Some hooks may be slow; consider selective running

### Tool Conflicts

- **Multiple formatters**: Choose one (Ruff recommended)
- **Conflicting rules**: Adjust configurations to avoid conflicts

### Performance

- **Slow linting**: Use Ruff instead of Flake8 for speed
- **Large codebase**: Configure excludes for generated files

## Best Practices

- **Run tools locally**: Fix issues before committing
- **Consistent configuration**: Keep settings in `pyproject.toml`
- **Regular updates**: Update tool versions periodically
- **Team alignment**: Ensure all developers use the same tools

For more information, see the
[Pre-commit documentation](https://pre-commit.com/) and individual tool docs.
