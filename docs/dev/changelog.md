# Changelog

This guide explains how changelogs are automatically generated in this Python
package template using git-cliff and conventional commits.

## Overview

The template uses git-cliff for automated changelog generation based on
conventional commit messages. This ensures:

- **Consistent formatting**: Standardized changelog structure
- **Automatic updates**: No manual changelog maintenance
- **Conventional commits**: Structured commit messages
- **Release integration**: Changelogs generated on releases

## Conventional Commits

All commits must follow the
[Conventional Commits](https://conventionalcommits.org/) specification:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- **`feat`**: New features
- **`fix`**: Bug fixes
- **`docs`**: Documentation changes
- **`style`**: Code style changes (formatting, etc.)
- **`refactor`**: Code refactoring
- **`test`**: Test additions or modifications
- **`chore`**: Maintenance tasks
- **`perf`**: Performance improvements
- **`ci`**: CI/CD changes
- **`build`**: Build system changes

### Examples

<!--- cSpell:disable -->

```bash
# Feature commit
git commit -m "feat: add user authentication"

# Bug fix with scope
git commit -m "fix(api): resolve login timeout issue"

# Breaking change
git commit -m "feat!: change API response format

BREAKING CHANGE: The response format has changed from XML to JSON"

# Commit with body and footer
git commit -m "fix: correct typo in documentation

The word 'recieve' was misspelled as 'receive'.

Closes #123"
```

<!--- cSpell:enable -->

## Git-cliff Configuration

### Basic Setup (`cliff.toml`)

```toml
--8<-- "cliff.toml"
```

### Configuration Sections

#### Changelog Template

The `body` template defines the changelog format using Tera templating:

- **Version headers**: Automatic version and date formatting
- **Commit grouping**: Commits grouped by type with emojis
- **Link generation**: Automatic GitHub links for commits and comparisons
- **Contributor recognition**: New contributors section

#### Git Configuration

- **`conventional_commits`**: Enforce conventional commit format
- **`commit_preprocessors`**: Transform commit messages (e.g., issue links)
- **`commit_parsers`**: Define how commits are categorized
- **`tag_pattern`**: Pattern for recognizing version tags

## Generating Changelogs

### Manual Generation

```bash
# Generate changelog for latest release
git cliff --latest --strip header

# Generate full changelog
git cliff -o CHANGELOG.md

# Generate for specific version
git cliff --tag v1.2.3

# Preview unreleased changes
git cliff --unreleased
```

### Pre-commit Integration

Changelog generation can be automated via pre-commit:

```yaml
repos:
    - repo: https://github.com/orhun/git-cliff
      rev: v2.4.0
      hooks:
          - id: git-cliff
            args: [--latest, --strip header]
```

### CI/CD Integration

Changelogs are automatically generated during releases:

```yaml
# In release workflow
- name: Generate Changelog
  run: |
      git cliff --latest --strip header > changelog.md
```

## Commit Message Validation

### Commitlint Configuration

Commit messages are validated using commitlint:

**Configuration** (`commitlint.config.js`):

```javascript
--8<-- "commitlint.config.js"
```

### Pre-commit Hook

```yaml
--8<-- ".pre-commit-config.yaml:15:20"
```

## Release Process

### Version Tagging

1. **Create annotated tag**:

    ```bash
    git tag -a v1.2.3 -m "Release v1.2.3"
    git push origin v1.2.3
    ```

2. **GitHub Actions will**:
    - Generate changelog
    - Create release
    - Publish to PyPI

### Automated Changelog

The changelog is automatically included in GitHub releases:

```yaml
# In release workflow
- name: Create Release
  uses: actions/create-release@v1
  env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
      tag_name: ${{ github.ref }}
      release_name: Release ${{ github.ref }}
      body: |
          $(git cliff --latest --strip header)
```

## Customizing Changelog

### Modifying Groups

Add custom commit groups:

```toml
commit_parsers = [
    { message = "^feat", group = "<!-- 0 -->🚀 Features" },
    { message = "^custom", group = "<!-- 11 -->🎯 Custom Changes" },
]
```

### Changing Template

Modify the changelog template:

```toml
[changelog]
body = """
# Custom Changelog Format

{% for group, commits in commits | group_by(attribute="group") %}
## {{ group }}

{% for commit in commits %}
- {{ commit.message }}
{% endfor %}
{% endfor %}
"""
```

### Adding Links

Include additional links in commits:

```toml
commit_preprocessors = [
    { pattern = '#(\d+)', replace = "[#$1](https://github.com/org/repo/issues/$1)" },
    { pattern = '@(\w+)', replace = "[@$1](https://github.com/$1)" },
]
```

## Best Practices

### Commit Message Guidelines

- **Be descriptive**: Explain what and why, not just what
- **Use scopes**: Group related changes (e.g., `fix(api)`)
- **Reference issues**: Include issue numbers when relevant
- **Keep it concise**: Subject line under 72 characters

### Version Management

- **Semantic versioning**: Major.minor.patch
- **Breaking changes**: Use `!` suffix for breaking changes
- **Pre-releases**: Use alpha/beta/rc suffixes

### Changelog Maintenance

- **Review before release**: Check generated changelog
- **Manual edits**: Edit template for special cases
- **Consistency**: Keep formatting consistent
- **Automation**: Let tools handle routine updates

## Troubleshooting

### Common Issues

- **Commits not appearing**: Check conventional commit format
- **Wrong grouping**: Verify commit parser patterns
- **Links not working**: Check remote URL configuration
- **Template errors**: Validate Tera template syntax

### Debugging

```bash
# Debug commit parsing
git cliff --verbose

# Test template
git cliff --template cliff.toml

# Check commit format
git log --oneline | head -10
```

### Configuration Validation

```bash
# Validate cliff.toml
git cliff --config cliff.toml --dry-run

# Test with sample commits
git cliff --with-commit "feat: test feature"
```

## Integration Examples

### With GitHub Releases

```yaml
name: Release
on:
    push:
        tags: ['v*']

jobs:
    release:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4
              with:
                  fetch-depth: 0
            - name: Generate Changelog
              run: git cliff --latest --strip header > changelog.md
            - name: Create Release
              uses: softprops/action-gh-release@v1
              with:
                  body_path: changelog.md
```

### With Release Drafter

```yaml
name: Release Drafter
on:
    push:
        branches: [main]

jobs:
    update_release_draft:
        runs-on: ubuntu-latest
        steps:
            - uses: release-drafter/release-drafter@v6
              env:
                  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

For more information, see the [git-cliff documentation](https://git-cliff.org/)
and [Conventional Commits specification](https://conventionalcommits.org/).
