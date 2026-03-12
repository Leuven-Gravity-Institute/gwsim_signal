# Documentation

This guide explains how documentation is set up in this Python package template,
including Zensical configuration, API reference generation, and best practices
for writing docs.

## Overview

The template uses Zensical for documentation, featuring:

- **Modern, responsive theme**: Built-in dark mode support
- **API Documentation**: Auto-generated from docstrings
- **Multi-page Structure**: Organized user guides and developer docs
- **Search**: Built-in search functionality with advanced filtering
- **Versioning**: Support for multiple versions
- **Customizable**: Easy customization of colors, fonts, and layout

## Zensical Configuration

### Basic Setup (`zensical.toml`)

```toml
--8<-- "zensical.toml:1:30"
```

### Navigation Structure

```toml
--8<-- "zensical.toml:47:59"
```

## Writing Documentation

### Markdown Basics

Use standard Markdown with Zensical extensions:

````markdown
# Heading 1

## Heading 2

**Bold text** and _italic text_

- Bullet list
- Another item

1. Numbered list
2. Second item

[Link text](url)

```python
# Code block
def function():
    pass
```
````

<!-- prettier-ignore-start -->

```text
!!! note
    Admonition for notes, warnings, etc.
```

<!-- prettier-ignore-end -->

### Front Matter

Add metadata to pages:

```yaml
---
title: Page Title
description: Page description for SEO
tags:
    - tag1
    - tag2
---
```

## API Documentation

### MkDocstrings Setup

The template uses mkdocstrings for automatic API docs with Zensical integration:

```toml
--8<-- "zensical.toml:332:334"
```

### Writing Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> str:
    """Brief description of what the function does.

    More detailed description explaining the function's purpose,
    behavior, and any important notes.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.

    Returns:
        Description of return value.

    Raises:
        ValueError: When something goes wrong.

    Examples:
        >>> function_name("hello", 1)
        'hello1'
    """
    return f"{param1}{param2}"
```

### Class Documentation

```python
class MyClass:
    """Brief description of the class.

    Longer description explaining the class purpose
    and how to use it.

    Attributes:
        attribute1: Description of attribute1.
        attribute2: Description of attribute2.
    """

    def __init__(self, param: str):
        """Initialize the class.

        Args:
            param: Description of initialization parameter.
        """
        self.attribute1 = param
        self.attribute2 = None
```

## Building and Serving

### Local Development

```bash
# Serve documentation locally
zensical serve

# Open http://localhost:8000
```

### Building for Production

```bash
# Build static site
zensical build

# Output in site/ directory
```

### Deployment

The template includes GitHub Actions for automatic deployment:

- **GitHub Pages**: Automatic deployment on pushes to main

## Documentation Structure

### Home Page (`docs/index.md`)

Introduction to your package:

````markdown
# Welcome to Your Package

Brief description of what your package does.

## Quick Start

```bash
pip install your-package
```

## Features

- Feature 1
- Feature 2
- Feature 3
````

### User Guides (`docs/user_guide/`)

Step-by-step guides for users:

- **Installation**: How to install and set up
- **Quick Start**: Basic usage examples
- **Advanced Usage**: Complex features
- **Troubleshooting**: Common issues

### API Reference (`docs/api/`)

Auto-generated API docs (handled by `gen_ref_pages.py`).

### Developer Guide (`docs/dev/`)

For contributors:

- **Contributing**: How to contribute
- **Development Setup**: For developers
- **Architecture**: System design
- **Changelog**: Version history

## Best Practices

### Content Organization

- **Progressive disclosure**: Start simple, get complex
- **Cross-references**: Link related pages
- **Consistent structure**: Use similar layouts

### Writing Style

- **Clear and concise**: Avoid jargon
- **Active voice**: "Install the package" vs "The package can be installed"
- **Examples**: Include code examples
- **Screenshots**: For UI components

### SEO and Accessibility

- **Descriptive titles**: For search engines
- **Alt text**: For images
- **Semantic HTML**: Proper headings hierarchy

## Advanced Features

### Versioning

Support multiple versions:

```toml
plugins:
    - mike:
          version_selector: true
          canonical_version: latest
```

### Custom Theme

Customize theme appearance:

```toml
[project.theme]
variant = "classic"  # or "material"
```

### Plugins

Additional useful plugins:

```toml
plugins:
    - mkdocs-minify-plugin
    - mkdocs-git-revision-date-localized-plugin
    - mkdocs-glightbox
```

## Customization

### Changing Theme

Switch to other themes:

```toml
[project.theme]
# Default Zensical theme
variant = "material"
```

### Adding Pages

1. Create `.md` file in appropriate directory
2. Add to `zensical.toml` nav
3. Link from other pages

### Custom CSS/JavaScript

Add custom styles:

```toml
[project]
extra_css = ["styles/custom.css"]

extra_javascript = ["js/custom.js"]
```

## CI/CD Integration

Documentation builds automatically:

- **Pull requests**: Build check
- **Main branch**: Deploy to GitHub Pages
- **Releases**: Versioned documentation

## Setting Up GitHub Pages

To deploy your documentation to GitHub Pages, follow these steps:

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Build and deployment":
    - **Source**: Select "GitHub Actions"
    - This allows the documentation workflow to deploy directly
4. Click **Save**

### 2. Configure Site URL (Optional but Recommended)

Update `zensical.toml` to use your GitHub Pages URL:

```toml
[project]
site_url = "https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/"
site_name = "Your Package Name"
```

This ensures links and assets work correctly on GitHub Pages.

### 3. Verify Documentation Workflow

The documentation is deployed automatically by the GitHub Actions workflow:

1. Go to **Actions** tab in your repository
2. Look for **"Deploy Zensical documentation to Pages"** workflow
3. Verify it runs successfully on pushes to main branch
4. Check the workflow logs if there are issues

### 4. Access Your Documentation

After the first successful deployment:

1. Go back to **Settings** → **Pages**
2. You'll see a message like "Your site is live at:
   `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`"
3. Click the link to view your published documentation
4. Bookmark this URL for future reference

### 5. Custom Domain (Optional)

If you want to use a custom domain:

1. In **Settings** → **Pages**, enter your custom domain in "Custom domain"
2. Update DNS settings with your domain registrar
3. GitHub will automatically provision an SSL certificate

## Troubleshooting Documentation Deployment

### Documentation Not Updating

**Problem:** You pushed changes but the docs still show old content.

**Solution:**

1. Verify the documentation workflow succeeded:
    - Check **Actions** tab
    - Look for "Deploy Zensical documentation to Pages" workflow
    - Re-run if it failed
2. Clear browser cache (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
3. Wait 1-2 minutes for GitHub Pages to rebuild
4. Verify changes were committed and pushed to main branch

### Workflow Fails with Build Error

**Problem:** Documentation workflow fails with "Zensical build failed".

**Solution:**

<!-- prettier-ignore-start -->

1. Check markdown file syntax
2. Verify all navigation links in `zensical.toml` point to existing files
3. Run locally to debug:

    ```bash
    zensical build --strict
    ```

4. Fix any errors and push again

<!-- prettier-ignore-end -->

### 404 - Site Not Found

**Problem:** GitHub Pages shows 404 error.

**Solution:**

1. Verify GitHub Pages is enabled in Settings → Pages
2. Check the deployment source is set correctly
3. Wait a few minutes after enabling GitHub Pages
4. Try accessing from an incognito/private browser window

## Troubleshooting

### Common Issues

- **Build fails**: Check Markdown syntax and verify all files exist
- **Links broken**: Ensure relative paths are correct and files exist
- **API docs missing**: Verify docstrings are present and properly formatted
- **Deployment fails**: Check Actions tab for workflow errors

### Debugging

```bash
# Strict mode (catches all issues)
zensical build --strict

# Verbose output (more details)
zensical build -v

# Local preview
zensical serve  # Visit http://localhost:8000
```

For more information, see the [Zensical documentation](https://zensical.org/)
and [MkDocs documentation](https://www.mkdocs.org/)
