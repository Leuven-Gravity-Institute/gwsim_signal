"""Stack per-detector GWpy strains with a fixed channel order."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
from gwpy.timeseries import TimeSeries


def _validate_aligned_channels(channels: Sequence[TimeSeries]) -> None:
    """Require identical length, sample rate, and time samples across channels."""
    if len(channels) == 0:
        raise ValueError("At least one channel is required.")
    ref = channels[0]
    ref_times = ref.times.value
    for i, s in enumerate(channels[1:], start=1):
        if not s.is_compatible(ref):
            raise ValueError(
                f"Channel {i} is not compatible with reference channel 0 (mismatched unit or sample rate)."
            )
        if len(s) != len(ref):
            raise ValueError(f"Channel {i} length {len(s)} does not match reference length {len(ref)}.")
        if not np.array_equal(s.times.value, ref_times):
            raise ValueError(
                f"Channel {i} time grid does not match reference (channel 0); "
                "all detectors must share identical sample times."
            )


class DetectorStrainStack:
    """Aligned strains for a fixed list of detectors (one GWpy series per row).

    See ``docs/user_guide/multi-channel-strains.md`` (examples) and
    ``docs/api/multichannel/index.md`` (API reference).
    """

    def __init__(self, detector_names: tuple[str, ...], channels: tuple[TimeSeries, ...]) -> None:
        """Prefer the ``from_mapping`` classmethod for public construction.

        Args:
            detector_names: Channel order; row ``i`` of ``data`` corresponds to
                ``detector_names[i]``.
            channels: Tuple of GWpy time series objects, one per detector.

        Raises:
            ValueError: If ``detector_names`` and ``channels`` have different lengths.
            ValueError: If ``channels`` is empty.
            TypeError: If a channel is not a GWpy [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/).
            ValueError: If the channels are not aligned on the same grid.
            ValueError: If the channels are not compatible (mismatched unit or sample rate).

        """
        if len(detector_names) != len(channels):
            raise ValueError("detector_names and channels must have the same length.")
        for i, s in enumerate(channels):
            if not isinstance(s, TimeSeries):
                raise TypeError(f"channels[{i}] must be gwpy.timeseries.TimeSeries, got {type(s)}")
        _validate_aligned_channels(channels)
        self._names = detector_names
        self._channels = channels

    @classmethod
    def from_mapping(
        cls,
        detector_names: Sequence[str],
        strains: Mapping[str, TimeSeries],
    ) -> DetectorStrainStack:
        """Build a stack in the given detector order; validate a single shared time grid.

        Args:
            detector_names: Channel order; row ``i`` of ``data`` corresponds to
                ``detector_names[i]``.
            strains: Mapping containing every listed name. Extra keys are ignored.

        Returns:
            New ``DetectorStrainStack`` instance.

        Raises:
            KeyError: If any ``detector_names`` entry is missing from ``strains``.
            ValueError: If channels are not aligned on the same grid.
            TypeError: If a strain is not a GWpy [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/).
        """
        names = tuple(str(n) for n in detector_names)
        if not names:
            raise ValueError("detector_names must be non-empty.")
        missing = [n for n in names if n not in strains]
        if missing:
            raise KeyError(f"Missing strain keys for detectors: {missing}")
        channels = []
        for n in names:
            s = strains[n]
            if not isinstance(s, TimeSeries):
                raise TypeError(f"strains[{n!r}] must be gwpy.timeseries.TimeSeries, got {type(s)}")
            channels.append(s)
        ch_tuple = tuple(channels)
        _validate_aligned_channels(ch_tuple)
        return cls(names, ch_tuple)

    @property
    def detector_names(self) -> tuple[str, ...]:
        """IFO order used for stacking (immutable)."""
        return self._names

    @property
    def t0(self):
        """GPS start of the first sample (same for every channel)."""
        return self._channels[0].t0

    @property
    def sample_rate(self):
        """Sample rate (GWpy quantity), identical for every channel."""
        return self._channels[0].sample_rate

    @property
    def data(self) -> np.ndarray:
        """Strain samples shaped ``(n_detectors, n_samples)`` (C-contiguous copy)."""
        rows = [np.asarray(s.value, dtype=float) for s in self._channels]
        return np.stack(rows, axis=0).copy()

    def __getitem__(self, key: int | str) -> TimeSeries:
        """Return one channel by index or detector name (same object as stored)."""
        if isinstance(key, str):
            try:
                idx = self._names.index(key)
            except ValueError as exc:
                raise KeyError(key) from exc
            return self._channels[idx]
        if isinstance(key, int):
            return self._channels[key]
        raise TypeError(f"index must be int or str, got {type(key)}")

    def __len__(self) -> int:
        """Number of detectors (channels)."""
        return len(self._channels)

    def to_dict(self) -> dict[str, TimeSeries]:
        """Map detector name to GWpy series (same objects as ``__getitem__``)."""
        return dict(zip(self._names, self._channels, strict=True))
