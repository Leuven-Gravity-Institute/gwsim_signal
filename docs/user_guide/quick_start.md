# Quick Start

Welcome to the **Python Package Template**! This template provides a
standardized, production-ready setup for building Python packages. It includes
modern tooling, best practices, and configurations to help you get started
quickly.

## What This Template Provides

This template includes:

- **Modern Python Packaging**: Uses `pyproject.toml` with Hatchling and
  Hatch-VCS for version management
- **Development Tools**: Pre-configured with Ruff, Pre-commit hooks, and more
- **Testing Framework**: Pytest with coverage reporting and fixtures
- **Documentation**: Zensical theme for API docs and user guides
- **CI/CD**: GitHub Actions workflows for validation, testing, and publishing
- **Code Quality**: Linting, formatting, spell checking, and security scanning
- **Example Code**: A sample `hello_world` module with CLI

## Getting Started

### 1. Create a New Repository

1. Go to [GitHub](https://github.com/isaac-cf-wong/python-package-template)
2. Click **"Use this template"** to create your own repository
3. Clone your new repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Set Up Your Development Environment

We recommend using [uv](https://docs.astral.sh/uv/) for fast Python environment
management:

```bash
# Install uv (if not already installed)
pip install uv

# Create a virtual environment
uv venv --python 3.10

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode with all dependencies
uv pip install -e ".[dev,docs,test]"
```

Alternatively, use pip:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,docs,test]"
```

### 3. Set Up Pre-commit Hooks and Commit Message Validation

The template uses pre-commit hooks to automatically check code quality before
commits, and commitlint to validate commit messages follow the
[conventional commits](https://www.conventionalcommits.org/) standard. This
ensures consistent, well-documented changes.

**Install commitlint dependencies:**

```bash
npm install
```

This installs `@commitlint/cli` and `@commitlint/config-angular`, which validate
that your commit messages follow the conventional commits format (e.g.,
`feat: add new feature`, `fix: resolve bug`).

**Install pre-commit hooks:**

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

This sets up automatic checks that run before each commit, including:

- Code formatting (Ruff)
- Linting (Ruff)
- Security scanning (Bandit)
- Spell checking (CSpell)
- Commit message validation (commitlint)

Hooks will automatically fix many issues or prevent commits that violate rules,
helping maintain code quality.

### 4. Run Tests

Verify everything works:

```bash
pytest
```

You should see all tests pass with coverage reporting.

### 5. Build Documentation

Generate and view the documentation:

```bash
zensical serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser to see the
docs.

## Development Workflow

### Code Structure

Your package code goes in `src/YOUR_PACKAGE_NAME/`:

- `src/YOUR_PACKAGE_NAME/__init__.py`: Package initialization and exports
- `src/YOUR_PACKAGE_NAME/__main__.py`: Entry point for
  `python -m YOUR_PACKAGE_NAME`
- Add your modules in subdirectories as needed

### Writing Code

1. **Follow the Style**: Code is automatically formatted with Ruff (120 char
   line length)
2. **Add Type Hints**: Use modern Python typing
3. **Write Tests**: Add tests in `tests/` directory
4. **Update Docs**: Add docstrings for API documentation

### Example: Running the Sample Code

Try the included example:

```bash
# Run as a module
python -m python_package_template

# Or use the CLI (if configured)
python_package_template --help
```

### Building and Publishing

When ready to release:

1. Run tests and checks locally: `pytest && pre-commit run --all-files`
2. Create a git tag for the new version: `git tag v1.0.0` (replace with your
   version)
3. Push the tag to the remote repository: `git push origin v1.0.0`
4. The GitHub Actions workflow will automatically create a release and publish
   to PyPI

## Key Configurations

- **pyproject.toml**: Package metadata, dependencies, tool configs
- **.pre-commit-config.yaml**: Pre-commit hooks for code quality
- **cliff.toml**: Configuration for automatic changelog generation using
  git-cliff
- **zensical.toml**: Documentation configuration
- **.github/workflows/**: CI/CD pipelines

## Next Steps

- Customize package name and metadata in `pyproject.toml`
- Replace example code with your functionality
- Update documentation in `docs/`
- Configure CI secrets for PyPI publishing
- Add your own dependencies and tools
