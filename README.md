# gwmock-signal

[![Python CI](https://github.com/Leuven-Gravity-Institute/gwmock-signal/actions/workflows/ci.yml/badge.svg)](https://github.com/Leuven-Gravity-Institute/gwmock-signal/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Leuven-Gravity-Institute/gwmock-signal/main.svg)](https://results.pre-commit.ci/latest/github/Leuven-Gravity-Institute/gwmock-signal/main)
[![Documentation Status](https://github.com/Leuven-Gravity-Institute/gwmock-signal/actions/workflows/documentation.yml/badge.svg)](https://leuven-gravity-institute.github.io/gwmock-signal/)
[![codecov](https://codecov.io/gh/Leuven-Gravity-Institute/gwmock-signal/graph/badge.svg?token=COF8341N60)](https://codecov.io/gh/Leuven-Gravity-Institute/gwmock-signal)
[![PyPI Version](https://img.shields.io/pypi/v/gwmock-signal)](https://pypi.org/project/gwmock-signal/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gwmock-signal)](https://pypi.org/project/gwmock-signal/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![DOI](https://zenodo.org/badge/924023559.svg)](https://doi.org/10.5281/zenodo.18017404)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)

A Python package for simulating gravitational wave signals.

## Installation

We recommend using `uv` to manage virtual environments for installing
`gwmock-signal`.

If you don't have `uv` installed, you can install it with pip. See the project
pages for more details:

- Install via pip: `pip install --upgrade pip && pip install uv`
- Project pages: [uv on PyPI](https://pypi.org/project/uv/) |
  [uv on GitHub](https://github.com/astral-sh/uv)
- Full documentation and usage guide: [uv docs](https://docs.astral.sh/uv/)

### Requirements

- Python 3.12 or higher (We adopt the SPEC 0 policy for the Python support
  version)
- Operating System: Linux, macOS, or Windows

**Note:** The package is built and tested against Python 3.12-3.14. When
creating a virtual environment with `uv`, specify the Python version to ensure
compatibility: `uv venv --python 3.12` (replace `3.12` with your preferred
version in the 3.12-3.14 range). This avoids potential issues with unsupported
Python versions.

### Install from PyPI

The recommended way to install `gwmock-signal` is from PyPI:

```bash
# Create a virtual environment (recommended with uv)
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install gwmock-signal
```

#### Optional Dependencies

For development or specific features:

```bash
# Development dependencies (testing, linting, etc.)
uv pip install gwmock-signal[dev]

# Documentation dependencies
uv pip install gwmock-signal[docs]
```

### Install from Source

For the latest development version:

```bash
git clone git@github.com:Leuven-Gravity-Institute/gwmock-signal.git
cd gwmock-signal
# Create a virtual environment (recommended with uv)
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

#### Development Installation

To set up for development:

```bash
git clone git@github.com:Leuven-Gravity-Institute/gwmock-signal.git
cd gwmock-signal

# Create a virtual environment (recommended with uv)
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --extra dev

# Install the commitlint dependencies
npm ci

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

### Verify Installation

Check that `gwmock-signal` is installed correctly:

```bash
gwmock-signal --help
```

```bash
python -c "import gwmock_signal; print(gwmock_signal.__version__)"
```

## Documentation

Full documentation to be available at
[https://leuven-gravity-institute.github.io/gwmock-signal](https://leuven-gravity-institute.github.io/gwmock-signal).

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
[GitHub Releases page](https://github.com/Leuven-Gravity-Institute/gwmock-signal/releases).

## Testing

Run the test suite:

```bash
uv run pytest
```

## License

This project is licensed under the BSD 3-Clause License - see the
[LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open an issue on
[GitHub](https://github.com/Leuven-Gravity-Institute/gwmock-signal/issues/new)
or contact the maintainers.
