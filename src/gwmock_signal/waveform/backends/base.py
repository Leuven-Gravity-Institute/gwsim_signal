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
"""Waveform backend abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from gwpy.timeseries import TimeSeries

_MISSING: Final[object] = object()


def _pop_alias(params: dict[str, object], canonical: str, *aliases: str, default: object = _MISSING) -> object:
    """Pop one canonical parameter or legacy alias from ``params``.

    Raises ``ValueError`` when multiple aliases are provided simultaneously so the
    caller cannot accidentally pass conflicting values.
    """
    names = (canonical, *aliases)
    present = [name for name in names if name in params]
    if len(present) > 1:
        joined = ", ".join(present)
        raise ValueError(f"Do not mix aliases for '{canonical}': {joined}")
    if present:
        return params.pop(present[0])
    if default is _MISSING:
        raise ValueError(f"Missing required parameter: '{canonical}'")
    return default


class WaveformBackend(ABC):
    """Abstract interface for time-domain waveform generators."""

    @abstractmethod
    def available_approximants(self) -> list[str]:
        """Return supported time-domain approximant names."""

    @abstractmethod
    def generate_td_waveform(
        self,
        approximant: str,
        tc: float,
        sampling_frequency: float,
        minimum_frequency: float,
        **params: object,
    ) -> dict[str, TimeSeries]:
        """Generate ``plus`` and ``cross`` GWpy time series."""
