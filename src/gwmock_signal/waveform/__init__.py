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
"""Waveform generation (PyCBC-backed and extensible)."""

from __future__ import annotations

from gwmock_signal.waveform.factory import WaveformFactory
from gwmock_signal.waveform.pycbc_wrapper import pycbc_waveform_wrapper

__all__ = [
    "WaveformFactory",
    "pycbc_waveform_wrapper",
]
