# CI/CD and Releases

This guide explains the continuous integration and deployment setup in this
Python package template.

## Overview

The template includes:

- **Automated testing** on every push and pull request (3.12, 3.13, 3.14)
- **Code quality checks** (linting, formatting, CodeQL security scanning)
- **Automated weekly releases** with semantic versioning and changelog
  generation
- **Draft releases** to preview upcoming changes before publishing
- **Documentation deployment** to GitHub Pages
- **Dependency updates** via Dependabot
- **Package publishing** (optional, requires setup)

## Quick Start

1. **No setup required** - CI runs automatically on pushes and pull requests
2. **Releases happen weekly** on the Tuesday of each week (automated)
3. **Optional: Enable PyPI publishing** - See [Publishing](#publishing) section

## Workflows

### CI (`.github/workflows/CI.yml`)

**Triggers:** Every push, pull request, or manual trigger

- Tests across Python 3.12, 3.13, 3.14
- Runs pytest with coverage reporting
- Uploads coverage to Codecov
- Security scanning with CodeQL

**Status checks to require:** `test (3.12)`, `test (3.13)`, `test (3.14)`

### Tag (`.github/workflows/create_tag.yml`)

**Triggers:** Weekly (Tuesday at UTC midnight) or manual trigger

1. Runs CI workflow to ensure tests pass
2. Automatically bumps version using semantic versioning
3. Creates and pushes git tag (e.g., `v1.2.3`)
4. Calls Release workflow with the new tag

### Release (`.github/workflows/release.yml`)

**Triggers:** When called by Tag workflow, or manually with a tag

1. Checks out the specified tag
2. Generates changelog from conventional commits
3. Deletes old draft release
4. Creates GitHub release with changelog
5. Optionally calls Publish workflow (requires setup)

### Draft Release (`.github/workflows/draft_release.yml`)

**Triggers:** Every push to `main`

- Generates changelog for unreleased changes
- Creates/updates `next-release` draft on GitHub Releases
- Auto-deleted when a real release is created
- Helps preview what's in the next release

### Documentation (`.github/workflows/documentation.yml`)

**Triggers:** Every push to `main` or manual trigger

- Builds documentation with Zensical
- Deploys to GitHub Pages
- Uses pip caching for faster builds

### Publish (`.github/workflows/publish.yml` & `publish_testpypi.yml`)

**Triggers:** Manual via `workflow_dispatch` or called by Release workflow

- Builds Python distribution packages
- Publishes to PyPI or TestPyPI
- Requires setup (see [Publishing](#publishing))
- **Enabled when environments are configured** (requires `pypi` or `testpypi`
  environments)

## Release Process

### Setup: Configure Your Repository URL

Before the first release, update `cliff.toml` with your repository information:

1. Open `cliff.toml`
2. Replace `https://github.com/isaac-cf-wong/python-package-template` (line 61)
   with your actual GitHub repository (e.g., `octocat/hello-world`)
3. Commit and push this change

This is used by `git-cliff` to generate links in the changelog (commits,
comparisons, etc.).

### Conventional Commits

Format commits to trigger automatic changelog generation:

```bash
feat: add new feature          # Triggers minor version bump
fix: fix a bug                 # Triggers patch version bump
feat!: breaking change         # Triggers major version bump
docs: update documentation     # No version bump
chore: update dependencies     # No version bump
```

[Learn more about Conventional Commits](https://www.conventionalcommits.org/)

### Automatic Release (Weekly)

The Tag workflow runs automatically on **Tuesday of every week at midnight
UTC**:

1. CI passes ✅
2. Version is bumped (e.g., 1.0.0 → 1.0.1)
3. Git tag is created and pushed
4. Release workflow creates a GitHub Release
5. Changelog is auto-generated from commits

**No action required** - just use conventional commits.

### Manual Release

Trigger a release anytime:

1. Go to your repository → **Actions** tab
2. Click the **Tag** workflow
3. Click **Run workflow** → **Confirm**

Or manually specify a tag for Release workflow:

1. Go to **Actions** → **Release** workflow
2. Click **Run workflow**
3. Enter tag name (e.g., `v1.2.3`)
4. Click **Run workflow**

### Verify Release

After the workflow completes:

1. **Actions tab** - Workflow should show ✅
2. **Releases page** - New release should appear with auto-generated changelog
3. **GitHub Pages** - Docs should be updated (if configured)

## Publishing

### Setup PyPI Publishing (Optional)

Publishing is **disabled by default** — it only runs when you create the
required environments.

#### To Enable Publishing

1. Go to your repository → **Settings** → **Environments**
2. Create an environment named `pypi` (for PyPI) and/or `testpypi` (for
   TestPyPI)
3. For each environment, optionally add deployment rules:
    - **Deployment branches**: Select `main` or `Selected branches`
    - **Environment secrets** (optional): Only needed if not using trusted
      publishing

#### Manual Publish

Publish manually when ready:

1. Go to **Actions** → **Publish** workflow
2. Click **Run workflow** → Enter tag name
3. Select environment from the dropdown
4. Click **Run workflow**

#### Auto-Publish on Release

The Release workflow is already configured to call the Publish workflow. Once
you create the `pypi` environment, releases will automatically publish to PyPI.

<!-- prettier-ignore-start -->
<!-- markdownlint-disable MD046 -->

!!!important "For Production Packages"
    This template includes `continue-on-error: true` in the publish workflows
    to handle the case where environments are not created.
    When you fork this template for production use, **remove these lines** from:

    - `.github/workflows/publish.yml` (line 78)
    - `.github/workflows/publish_testpypi.yml` (line 78)

    This ensures your package will fail loudly if publishing encounters errors, rather than silently skipping the publish step.

<!-- markdownlint-enable MD046 -->
<!-- prettier-ignore-end -->

### Configure Trusted Publishing (Recommended)

Use [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) instead
of API tokens:

1. Go to [PyPI](https://pypi.org) or [TestPyPI](https://test.pypi.org)
2. Go to your project → Settings → Publishing
3. Add GitHub as trusted publisher:
    - Owner: `your-username`
    - Repository: `your-repo-name`
    - Workflow: `create_tag.yml` (for automatic releases) and `publish.yml` (for
      manual publishes)
    - Environment: `pypi` (or `testpypi` for TestPyPI)

No secrets or tokens needed!

## Customization

### Change Release Schedule

Edit `.github/workflows/create_tag.yml`:

```yaml
on:
    schedule:
        - cron: '0 0 1 * *' # Change to your preferred time
```

**Cron format:** `minute hour day month weekday`

- `"0 0 1 * *"` = 1st of month, midnight UTC
- `"0 0 * * 0"` = Every Sunday, midnight UTC
- `"0 12 * * *"` = Every day at noon UTC

### Require Additional Status Checks

Edit `.github/workflows/CI.yml` to add custom checks, then add them to branch
protection:

1. Go to Settings → Branches → main
2. Under "Require status checks to pass before merging"
3. Add your new check names

### Change Python Versions

Edit `.github/workflows/CI.yml`:

```yaml
matrix:
    python-version: ['3.10', '3.11', '3.12'] # Modify as needed
```

### Disable CodeQL (Optional)

If security scanning isn't needed, remove the `codeql` job from
`.github/workflows/CI.yml`.

## Troubleshooting

### CI workflow fails

- Check test logs in Actions tab
- Verify dependencies in `pyproject.toml`
- Ensure tests pass locally: `pytest`

### Release workflow fails

- Check commits use conventional commit format
- Verify `cliff.toml` changelog configuration
- See Actions logs for detailed error

### Version not bumped correctly

- Ensure commits start with `feat:`, `fix:`, `feat!:`, etc.
- Check [Conventional Commits](https://www.conventionalcommits.org/) format

### Draft release not updating

- Check workflow concurrency settings in `.github/workflows/draft_release.yml`

### PyPI publishing fails

- Verify trusted publishing is configured on PyPI/TestPyPI
- Check that the environment name matches your workflow
- See Actions logs for authentication errors

### CodeQL configuration error

- Remove `security-events: write` permission from workflows without CodeQL
  scanning
- Only `.github/workflows/CI.yml` should have this permission

## Best Practices

- **Use conventional commits** - Ensures correct version bumping and meaningful
  changelogs
- **Review draft releases** - Check "next-release" to preview what will be
  published
- **Keep commits atomic** - One logical change per commit
- **Require status checks** - Prevent merging broken code to main
- **Use branch protection** - Require pull requests and passing checks before
  merging

## Resources

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [git-cliff documentation](https://github.com/orhun/git-cliff)
- [Zensical documentation](https://zensical.org/)
