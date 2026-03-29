"""Top-level package for gwmock_signal."""

from __future__ import annotations

from gwmock_signal.detector import CustomDetector
from gwmock_signal.network import Network
from gwmock_signal.simulator import CBCSimulator, GWSimulator, TransientSimulator
from gwmock_signal.version import __version__

__all__ = ["CBCSimulator", "CustomDetector", "GWSimulator", "Network", "TransientSimulator", "__version__"]
