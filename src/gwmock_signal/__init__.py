#
# Copyright (C) 2026 Leuven Gravity Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
"""Top-level package for gwmock_signal."""

from __future__ import annotations

from gwmock_signal.detector import CustomDetector
from gwmock_signal.multichannel.stack import DetectorStrainStack
from gwmock_signal.network import Network
from gwmock_signal.simulator import CBCSimulator, GWSimulator, TransientSimulator
from gwmock_signal.version import __version__

__all__ = [
    "CBCSimulator",
    "CustomDetector",
    "DetectorStrainStack",
    "GWSimulator",
    "Network",
    "TransientSimulator",
    "__version__",
]
