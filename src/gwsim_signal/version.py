"""A script to infer the version number from the metadata."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gwsim_signal")
except PackageNotFoundError:
    # Fallback for source checkouts or environments without installed metadata.
    __version__ = "0+unknown"
