"""Main entry point for the python_package_template package."""

from __future__ import annotations

if __name__ == "__main__":
    from python_package_template.utils.log import setup_logger

    setup_logger(print_version=True)
