"""Configuration and fixtures for pytest."""

from __future__ import annotations

import pytest


@pytest.fixture
def some_name() -> str:
    """Provide a string name.

    Returns:
        A string name.

    """
    return "developer"
