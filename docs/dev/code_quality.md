# Code Quality

This guide covers the code quality assurance tools and practices used in this
Python package template, including linting, security scanning, and spell
checking.

## Overview

Code quality is maintained through a combination of automated tools and manual
reviews. The template includes:

- **Linting**: Ruff for code style and errors
- **Security scanning**: Bandit for vulnerability detection
- **Spell checking**: CSpell for documentation and comments
- **Type checking**: Pyright for static analysis
- **Automated enforcement**: Pre-commit hooks and CI checks

## Linting Tools

### Ruff

Ruff is a fast Python linter written in Rust that combines multiple tools.

**Features:**

- Extremely fast (10-100x faster than other linters)
- Comprehensive rule set covering style, errors, and complexity
- Auto-fixing capabilities
- Built-in formatter

**Configuration** (`pyproject.toml`):

```toml
--8<-- "pyproject.toml:110:145"
```

**Usage:**

```bash
# Lint code
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

## Security Scanning

### Bandit

Bandit finds common security issues in Python code.

**Configuration** (`pyproject.toml`):

```toml
--8<-- "pyproject.toml:54:58"
```

**Common security issues detected:**

- Use of `assert` statements
- Shell injection vulnerabilities
- Weak cryptographic practices
- Hardcoded passwords
- Unsafe deserialization

**Usage:**

```bash
bandit -r src/
```

## Spell Checking

### CSpell

CSpell checks spelling in code comments, documentation, and strings.

**Configuration** (`cspell.json`):

```json
--8<-- "cspell.json"
```

**Usage:**

```bash
cspell "**/*.{py,md,yml,yaml}"
```

## Pre-commit Integration

All quality tools run automatically via pre-commit hooks.

**Configuration** (`.pre-commit-config.yaml`):

```yaml
--8<-- ".pre-commit-config.yaml"
```

## CI/CD Quality Checks

Quality checks run automatically in GitHub Actions and pre-commit.ci:

- **Pull requests**: Pre-commit.ci runs all hooks and auto-fixes issues
- **Main branch**: Full quality suite via GitHub Actions
- **Releases**: Comprehensive checks

### Pre-commit.ci Setup

Pre-commit.ci provides automated pre-commit hook execution:

<!-- prettier-ignore-start -->

1. **Install the GitHub App**: Go to [pre-commit.ci](https://pre-commit.ci/) and install the app on your repository
2. **Configuration** (`.pre-commit-config.yaml`):

    ```yaml
    --8<-- ".pre-commit-config.yaml:1:12"
    ```

3. **Automatic execution**: Pre-commit.ci runs on every PR and push

<!-- prettier-ignore-end -->

## Code Quality Metrics

### Complexity Analysis

Use tools to measure code complexity:

```bash
# McCabe complexity
python -m mccabe src/your_package/

# Radon metrics
radon cc src/ -a
radon mi src/ -s
```

### Coverage Requirements

Test coverage is enforced:

```toml
--8<-- "pyproject.toml:84:85"
```

### Quality Gates

- **Linting**: Zero errors allowed
- **Security**: Critical vulnerabilities must be fixed
- **Coverage**: X% coverage required (You may gradually increase this)
- **Spelling**: No spelling errors in documentation

## Best Practices

### Code Style

- **Follow PEP 8**: Use consistent formatting
- **Descriptive names**: Use clear, meaningful identifiers
- **DRY principle**: Avoid code duplication
- **SOLID principles**: Write maintainable code

### Documentation

- **Docstrings**: Document all public functions/classes
- **Comments**: Explain complex logic
- **README**: Clear project description
- **Changelog**: Track changes systematically

### Security

- **Input validation**: Validate all inputs
- **Secure defaults**: Use secure defaults
- **Dependency updates**: Keep dependencies current
- **Secrets management**: Never commit secrets

### Performance

- **Efficient algorithms**: Choose appropriate data structures
- **Memory management**: Avoid memory leaks
- **Profiling**: Use profiling tools for optimization
- **Caching**: Implement caching where beneficial

## Tool Selection Rationale

### Why Multiple Linters

- **Ruff**: Fast, comprehensive, auto-fixing
- **Pylint**: Detailed analysis, custom rules
- **Flake8**: Legacy compatibility, extensive plugins

### Why Bandit

- **Security focus**: Catches common vulnerabilities
- **Python specific**: Understands Python security issues
- **Configurable**: Can be tuned for project needs

### Why CSpell

- **Multi-language**: Works with Python, Markdown, YAML
- **Custom dictionaries**: Project-specific terminology
- **IDE integration**: Works with editors

## Customizing Quality Checks

### Adding New Rules

```toml
[tool.ruff]
select = ["E", "F", "B", "I", "CUSTOM"]
```

### Ignoring False Positives

```toml
[tool.ruff.per-file-ignores]
"specific_file.py" = ["RULE_CODE"]
```

### Custom Security Rules

Extend Bandit with custom plugins:

```python
# custom_bandit_plugin.py
import bandit
from bandit.core import test_properties as test

@test.checks('Call')
@test.test_id('B999')
def custom_check(context):
    # Custom security check logic
    pass
```

## Troubleshooting

### Common Issues

- **False positives**: Use ignore rules judiciously
- **Performance**: Ruff is fastest, use for large codebases
- **Configuration conflicts**: Ensure consistent settings
- **CI failures**: Check tool versions and configurations

### Debugging Quality Issues

- **Verbose output**: Use `--verbose` flags
- **Specific files**: Run tools on individual files
- **Configuration validation**: Test configurations separately

### Performance Optimization

- **Parallel execution**: Use multiple cores where possible
- **Incremental checks**: Only check changed files
- **Caching**: Leverage tool caching features

## Integration with IDEs

### VS Code

```json
{
    "cSpell.words": ["pypi", "mkdocs"]
}
```

### PyCharm

- Configure external tools for Ruff, Bandit
- Enable spell checking
- Set up pre-commit integration

## Continuous Improvement

### Metrics Tracking

Track quality metrics over time:

- Code coverage trends
- Complexity measurements
- Security vulnerability counts
- Performance benchmarks

### Regular Audits

- **Dependency audits**: Check for vulnerabilities
- **Code reviews**: Manual quality checks
- **Performance reviews**: Optimization opportunities
- **Security assessments**: Penetration testing

### Tool Updates

Keep tools current:

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python packages
pip install --upgrade ruff bandit

# Update Node.js packages
npm update cspell
```

For more information, see the documentation for individual tools:
[Ruff](https://docs.astral.sh/ruff/), [Bandit](https://bandit.readthedocs.io/),
[CSpell](https://cspell.org/), [Pyright](https://microsoft.github.io/pyright/).
