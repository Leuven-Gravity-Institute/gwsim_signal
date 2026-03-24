"""Top-level package for gwmock_signal."""

from __future__ import annotations

from gwmock_signal.pipeline import inject_cbc_signal
from gwmock_signal.version import __version__

__all__ = ["__version__", "inject_cbc_signal"]
