# gwsim_signal

[![Python CI](https://github.com/Leuven-Gravity-Institute/gwsim_signal/actions/workflows/ci.yml/badge.svg)](https://github.com/Leuven-Gravity-Institute/gwsim_signal/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Leuven-Gravity-Institute/gwsim_signal/main.svg)](https://results.pre-commit.ci/latest/github/Leuven-Gravity-Institute/gwsim_signal/main)
[![Documentation Status](https://github.com/Leuven-Gravity-Institute/gwsim_signal/actions/workflows/documentation.yml/badge.svg)](https://leuven-gravity-institute.github.io/gwsim_signal/)
[![codecov](https://codecov.io/gh/Leuven-Gravity-Institute/gwsim_signal/graph/badge.svg?token=COF8341N60)](https://codecov.io/gh/Leuven-Gravity-Institute/gwsim_signal)
[![PyPI Version](https://img.shields.io/pypi/v/gwsim_signal)](https://pypi.org/project/gwsim_signal/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gwsim_signal)](https://pypi.org/project/gwsim_signal/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![DOI](https://zenodo.org/badge/924023559.svg)](https://doi.org/10.5281/zenodo.18017404)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)

A Python package for simulating gravitational wave signals.

## Installation

We recommend using `uv` to manage virtual environments for installing
`gwsim_signal`.

If you don't have `uv` installed, you can install it with pip. See the project
pages for more details:

- Install via pip: `pip install --upgrade pip && pip install uv`
- Project pages: [uv on PyPI](https://pypi.org/project/uv/) |
  [uv on GitHub](https://github.com/astral-sh/uv)
- Full documentation and usage guide: [uv docs](https://docs.astral.sh/uv/)

### Requirements

- Python 3.11 or higher
- Operating System: Linux, macOS, or Windows

**Note:** The package is built and tested against Python 3.11-3.14. When
creating a virtual environment with `uv`, specify the Python version to ensure
compatibility: `uv venv --python 3.11` (replace `3.11` with your preferred
version in the 3.11-3.14 range). This avoids potential issues with unsupported
Python versions.

### Install from PyPI

The recommended way to install `gwsim_signal` is from PyPI:

```bash
# Create a virtual environment (recommended with uv)
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install gwsim_signal
```

#### Optional Dependencies

For development or specific features:

```bash
# Development dependencies (testing, linting, etc.)
uv pip install gwsim_signal[dev]

# Documentation dependencies
uv pip install gwsim_signal[docs]
```

### Install from Source

For the latest development version:

```bash
git clone git@github.com:Leuven-Gravity-Institute/gwsim_signal.git
cd gwsim_signal
# Create a virtual environment (recommended with uv)
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

#### Development Installation

To set up for development:

```bash
git clone git@github.com:Leuven-Gravity-Institute/gwsim_signal.git
cd gwsim_signal

# Create a virtual environment (recommended with uv)
uv venv --python 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --extra dev

# Install the commitlint dependencies
npm ci

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

### Verify Installation

Check that `gwsim_signal` is installed correctly:

```bash
gwsim_signal --help
```

```bash
python -c "import gwsim_signal; print(gwsim_signal.__version__)"
```

## Documentation

Full documentation to be available at
[https://leuven-gravity-institute.github.io/gwsim_signal](https://leuven-gravity-institute.github.io/gwsim_signal).

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Release Schedule

Releases follow a fixed schedule: every Tuesday at 00:00 UTC, unless an emergent
bugfix is required. This ensures predictable updates while allowing flexibility
for critical issues. Users can view upcoming changes in the draft release on the
[GitHub Releases page](https://github.com/Leuven-Gravity-Institute/gwsim_signal/releases).

## Testing

Run the test suite:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.

## Support

For questions or issues, please open an issue on
[GitHub](https://github.com/Leuven-Gravity-Institute/gwsim_signal/issues/new) or
contact the maintainers.
