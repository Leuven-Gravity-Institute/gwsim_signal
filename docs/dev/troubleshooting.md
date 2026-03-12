# Troubleshooting

This guide covers common issues you might encounter when using this template and
how to resolve them.

## Setup Issues

### Pre-commit Hook Installation Fails

**Problem:** `pre-commit install` returns an error or hooks don't run on commit.

**Solutions:**

<!-- prettier-ignore-start -->

1. Ensure you're in the project root directory
2. Verify Python virtual environment is activated
3. Reinstall pre-commit:

    ```bash
    pip uninstall pre-commit
    pip install pre-commit
    pre-commit install
    pre-commit install --hook-type commit-msg
    ```

4. Check if `.git` directory exists (must be a git repository)
5. Try running manually: `pre-commit run --all-files`

<!-- prettier-ignore-end -->

### commitlint Not Running

**Problem:** Commit messages aren't validated despite `npm install` being run.

**Solutions:**

<!-- prettier-ignore-start -->

1. Verify `npm install` was successful:

    ```bash
    npm list @commitlint/config-angular
    ```

2. Re-install commitlint dependencies:

    ```bash
    npm install --save-dev @commitlint/cli @commitlint/config-angular
    ```

3. Reinstall pre-commit hooks:

    ```bash
    pre-commit install --hook-type commit-msg
    ```

4. Test manually:

    ```bash
    echo "invalid message" | commitlint
    echo "feat: valid message" | commitlint
    ```

<!-- prettier-ignore-end -->

### Virtual Environment Issues

**Problem:** Packages can't be found or dependencies conflict.

**Solutions:**

<!-- prettier-ignore-start -->

1. Create a fresh virtual environment:

    ```bash
    rm -rf .venv
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2. Upgrade pip:

    ```bash
    python -m pip install --upgrade pip
    ```

3. Install dependencies:

    ```bash
    pip install -e ".[dev,docs,test]"
    ```

4. Verify installation:

    ```bash
    python -c "import your_package; print(your_package.__version__)"
    ```

<!-- prettier-ignore-end -->

### Python Version Mismatch

**Problem:** `python -m venv .venv` fails or tests don't run with wrong Python
version.

**Solutions:**

<!-- prettier-ignore-start -->

1. Check your Python version:

    ```bash
    python --version
    ```

2. Ensure Python 3.10 or higher is installed
3. Use specific Python version when creating venv:

    ```bash
    python3.11 -m venv .venv
    ```

4. Or use uv for version management:

    ```bash
    uv venv --python 3.11
    source .venv/bin/activate
    ```

<!-- prettier-ignore-end -->

## Testing Issues

### Pytest Fails to Collect Tests

**Problem:** `pytest` returns "no tests collected" or import errors.

**Solutions:**

<!-- prettier-ignore-start -->

1. Verify test file naming: Must be `test_*.py` or `*_test.py`
2. Verify test function naming: Must start with `test_`
3. Check `__init__.py` exists in test directory: `touch tests/__init__.py`
4. Run pytest with verbose output:

    ```bash
    pytest -vv
    ```

5. Check test discovery:

    ```bash
    pytest --collect-only
    ```

<!-- prettier-ignore-end -->

### Import Errors in Tests

**Problem:** Tests can't import your package modules.

**Solutions:**

<!-- prettier-ignore-start -->

1. Install package in development mode:

    ```bash
    pip install -e ".[dev,test]"
    ```

2. Verify package structure (should have `src/your_package/`)
3. Check `pyproject.toml` has correct `packages` configuration
4. Run from project root directory
5. Verify `__init__.py` exists in package directory

<!-- prettier-ignore-end -->

### Coverage Report Issues

**Problem:** Coverage report shows 0% or missing files.

**Solutions:**

<!-- prettier-ignore-start -->

1. Run pytest with coverage:

    ```bash
    pytest --cov=src/your_package --cov-report=html
    ```

2. Check `.coveragerc` or `pyproject.toml` coverage settings
3. Ensure source files have proper imports
4. Verify test files import from `src/` layout correctly

<!-- prettier-ignore-end -->

## Pre-commit Hook Issues

### Hooks Running Too Slowly

**Problem:** Pre-commit takes a very long time or times out.

**Solutions:**

<!-- prettier-ignore-start -->

1. Check which hooks are slow:

    ```bash
    pre-commit run --all-files --verbose
    ```

2. Consider excluding large files:

    ```yaml
    exclude: |
      (?x)^(
        large_data_file.csv|
        node_modules/
      )$
    ```

3. Run specific hooks:

    ```bash
    pre-commit run ruff --all-files  # Just ruff
    ```

<!-- prettier-ignore-end -->

### Formatting Changes After Commit

**Problem:** Pre-commit auto-fixes files, but you didn't expect it.

**Solutions:**

<!-- prettier-ignore-start -->

1. This is normal behavior - review the changes
2. Stage the new changes:

    ```bash
    git add .
    git commit -m "your message"  # Try again
    ```

3. Modify tool settings if behavior is unwanted (in `pyproject.toml`)
4. Disable specific hooks temporarily:

    ```bash
    SKIP=ruff pre-commit run --all-files
    ```

<!-- prettier-ignore-end -->

### "Unstaged Changes" After Running Hooks

**Problem:** Pre-commit modified files but they're not staged.

**Solutions:**

<!-- prettier-ignore-start -->

1. This is expected - review changes:

    ```bash
    git diff
    ```

2. Stage the changes:

    ```bash
    git add .
    ```

3. Try committing again
4. Or use `git add -A` to stage all changes before commit

<!-- prettier-ignore-end -->

## CI/CD Issues

### CI Workflow Fails on Push

**Problem:** GitHub Actions workflow fails unexpectedly.

**Solutions:**

<!-- prettier-ignore-start -->

1. Check the Actions tab in GitHub for error details
2. Run tests locally first:

    ```bash
    pytest
    pre-commit run --all-files
    ```

3. Common causes:

    - Dependency installation failed: Check `pip install -e ".[dev,docs,test]"`
    - Python version mismatch: Verify Python versions in workflow matrix
    - Missing dependencies: Add to `pyproject.toml`
    - Pre-commit failures: Fix locally first

4. Re-run failed jobs from GitHub Actions UI

<!-- prettier-ignore-end -->

### CodeQL Analysis Takes Too Long

**Problem:** CI is slow due to CodeQL analysis.

**Solutions:**

1. This is normal (~2-3 minutes per run)
2. To disable CodeQL:
    - Remove the `codeql` job from `.github/workflows/CI.yml`
    - Keep Bandit in pre-commit for basic security
3. Or check if it's necessary for your project
4. CodeQL provides value for security-critical projects

### Release Workflow Fails

**Problem:** Release or publish workflow doesn't work.

**Solutions:**

1. Verify tag format matches pattern: `v[0-9]+.[0-9]+.[0-9]+*`
    - Good: `v1.0.0`, `v1.2.3-alpha`
    - Bad: `1.0.0`, `release-1.0.0`
2. Check CI workflow passed first (required by release workflow)
3. Verify git-cliff configuration in `cliff.toml`
4. For publishing:
    - Check trusted publishers are configured in PyPI
    - Or verify API tokens are set as secrets
    - See
      [CI/CD guide - PyPI Publishing](../user_guide/ci_cd.md#setup-pypi-publishing-optional)

## Documentation Issues

### Zensical Site Won't Build

**Problem:** `zensical serve` or `zensical build` fails.

**Solutions:**

<!-- prettier-ignore-start -->

1. Verify Zensical is installed:

    ```bash
    pip install -e ".[docs]"
    ```

2. Check `zensical.toml` syntax (must be valid TOML)
3. Verify markdown files exist and paths are correct
4. Check for circular includes or missing includes
5. Run with verbose output:

    ```bash
    zensical build --verbose
    ```

<!-- prettier-ignore-end -->

### Documentation Not Updating on GitHub Pages

**Problem:** You pushed changes but the docs aren't updated online.

**Solutions:**

1. Verify GitHub Pages is enabled:
    - Go to repository Settings → Pages
    - Under "Build and deployment", select "GitHub Actions" as the source
    - This allows the documentation workflow to deploy directly
2. Check documentation workflow ran successfully:
    - Go to Actions tab
    - Look for "Deploy Zensical documentation to Pages" workflow
3. Verify changes were pushed to the correct branch
4. Wait 1-2 minutes for Pages to build
5. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
6. Check browser cache isn't serving old version

### API Documentation Not Generating

**Problem:** API reference pages are empty or show errors.

**Solutions:**

<!-- prettier-ignore-start -->

1. Verify docstrings are present in your code:

    ```python
    def my_function():
        """This is a docstring."""
        pass
    ```

2. Check mkdocstrings plugin is installed:

    ```bash
    pip install mkdocstrings[python]
    ```

3. Verify navigation in `zensical.toml` includes API section
4. Check `gen_ref_pages.py` script ran successfully:

    ```bash
    python docs/gen_ref_pages.py
    ```

5. Ensure modules are properly imported in `__init__.py`

<!-- prettier-ignore-end -->

## Dependencies & Package Issues

### "ModuleNotFoundError" When Running CLI

**Problem:** Running `your-package --help` fails with module not found.

**Solutions:**

<!-- prettier-ignore-start -->

1. Install package in development mode:

    ```bash
    pip install -e "."
    ```

2. Verify entry points in `pyproject.toml`:

    ```toml
    [project.scripts]
    your-package = "your_package.cli.main:app"
    ```

3. Check the specified function exists and is callable
4. Verify package name doesn't use hyphens in the module name:

    - Package: `your-package` (in `pyproject.toml`)
    - Module: `your_package` (directory name)

<!-- prettier-ignore-end -->

### Dependency Conflicts

**Problem:** `pip install` fails with conflict messages.

**Solutions:**

<!-- prettier-ignore-start -->

1. Check Python version:

    ```bash
    python --version
    ```

2. Create fresh virtual environment:

    ```bash
    rm -rf .venv && python -m venv .venv
    source .venv/bin/activate
    ```

3. Upgrade pip:

    ```bash
    python -m pip install --upgrade pip
    ```

4. Install with verbose output to see conflict:

    ```bash
    pip install -e ".[dev,docs,test]" -vv
    ```

5. Check `pyproject.toml` for overly restrictive version constraints

<!-- prettier-ignore-end -->

### Newer Version of Tool Breaks Things

**Problem:** Pre-commit hooks or tools updated and now fail.

**Solutions:**

<!-- prettier-ignore-start -->

1. Check what changed:

    ```bash
    pre-commit autoupdate --dry-run
    ```

2. Update individual tool:

    ```bash
    pre-commit autoupdate --repo https://github.com/tool-repo
    ```

3. Test changes:

    ```bash
   pre-commit run --all-files
    ```

4. Pin to known-good version in `.pre-commit-config.yaml`:

    ```yaml
    rev: v1.0.0 # Specific version instead of latest
    ```

<!-- prettier-ignore-end -->

## Getting Help

If you encounter issues not listed here:

<!-- prettier-ignore-start -->

1. **Check existing issues**: Search GitHub Issues for your problem
2. **Review logs carefully**: Error messages usually point to the root cause
3. **Search documentation**: Many issues are covered in specific tool docs
4. **Try minimal reproduction**: Isolate the problem to a single file/command
5. **Ask for help**: Open an [issue](https://github.com/isaac-cf-wong/python-package-template/issues/new/choose) with:
    - Your environment (Python version, OS)
    - Steps to reproduce
    - Full error message/logs
    - What you've already tried

<!-- prettier-ignore-end -->
