"""Top-level package for gwmock_signal."""

from __future__ import annotations

from gwmock_signal.simulator import CBCSimulator, GWSimulator
from gwmock_signal.version import __version__

__all__ = ["CBCSimulator", "GWSimulator", "__version__"]
