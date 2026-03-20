"""Add simulated strain into a GWpy segment (time-domain superposition)."""

from __future__ import annotations

import logging
from collections.abc import Sequence

import numpy as np
from astropy.units import second
from gwpy.timeseries import TimeSeries
from scipy.interpolate import interp1d

logger = logging.getLogger("gwmock_signal.injection")


def inject_strain(
    target: TimeSeries,
    injection: TimeSeries,
    *,
    interpolate_if_offset: bool = True,
) -> TimeSeries:
    """Return a new series equal to ``target`` plus ``injection`` on overlapping samples.

    Uses [`TimeSeries.is_compatible`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries.html#gwpy.timeseries.TimeSeries.is_compatible)
    to require matching sample spacing and units. The injection is cropped to the
    target span when needed. Non-integer sample alignment can use cubic
    interpolation (see ``interpolate_if_offset``).

    If nothing is added (no overlap, empty injection after crop, or offset skipped),
    returns a **copy** of ``target`` so the result is never the same object as
    ``target``.

    Args:
        target: Background segment (e.g. zeros or noise).
        injection: Strain to add (e.g. a projected waveform).
        interpolate_if_offset: If ``False`` and the injection start is not on a
            target sample boundary, return ``target.copy()`` without resampling.

    Returns:
        New [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/)
        with injected strain.

    Raises:
        ValueError: If GWpy compatibility checks fail (units, sample rate, etc.).
    """
    if not target.is_compatible(injection):
        raise ValueError("Injection is not compatible with target (sample rate, units, or epoch mismatch).")

    other = injection
    if (target.xunit == second) and (other.xspan[0] < target.xspan[0]):
        other = other.crop(start=target.xspan[0])
    if (target.xunit == second) and (other.xspan[1] > target.xspan[1]):
        other = other.crop(end=target.xspan[1])

    if len(other.times) == 0:
        logger.debug("Injection empty after crop; returning copy of target.")
        return target.copy()

    target_times = target.times.value
    other_times = other.times.value
    sample_spacing = float(target.dt.value)
    offset = (other_times[0] - target_times[0]) / sample_spacing

    if not np.isclose(offset, round(offset)):
        if not interpolate_if_offset:
            logger.debug("Non-integer sample offset; not interpolating; returning copy of target.")
            return target.copy()

        logger.debug("Injecting with interpolation (offset %.6f samples).", offset)
        start_idx = int(np.searchsorted(target_times, other_times[0], side="left"))
        end_idx = int(np.searchsorted(target_times, other_times[-1], side="right")) - 1

        if start_idx >= len(target_times) or end_idx < 0 or start_idx > end_idx:
            logger.debug("No overlap after index search; returning copy of target.")
            return target.copy()

        interp_func = interp1d(other_times, other.value, kind="cubic", axis=0, bounds_error=False, fill_value=0.0)
        resampled = interp_func(target_times[start_idx : end_idx + 1])
        injected_data = target.value.copy()
        injected_data[start_idx : end_idx + 1] += resampled
        return TimeSeries(
            injected_data,
            t0=target.t0,
            dt=target.dt,
            unit=target.unit,
        )

    start_idx = round(offset)
    end_idx = start_idx + len(other.value) - 1
    if start_idx < 0 or end_idx >= len(target_times) or start_idx >= len(target_times):
        logger.warning(
            "Injection range [%s:%s] out of bounds for length %s; returning copy of target.",
            start_idx,
            end_idx,
            len(target_times),
        )
        return target.copy()

    injected_data = target.value.copy()
    inject_len = min(len(other.value), end_idx - start_idx + 1)
    injected_data[start_idx : start_idx + inject_len] += other.value[:inject_len]
    return TimeSeries(
        injected_data,
        t0=target.t0,
        dt=target.dt,
        unit=target.unit,
    )


def inject_strains_sequential(
    target: TimeSeries,
    injections: Sequence[TimeSeries],
    *,
    interpolate_if_offset: bool = True,
) -> TimeSeries:
    """Apply ``inject_strain`` to each series in order.

    Args:
        target: Initial segment.
        injections: Strain series applied in list order.
        interpolate_if_offset: Forwarded to each ``inject_strain`` call.

    Returns:
        Final [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/).
        If ``injections`` is empty, returns ``target.copy()``.
    """
    if not injections:
        return target.copy()
    result = inject_strain(target, injections[0], interpolate_if_offset=interpolate_if_offset)
    for inj in injections[1:]:
        result = inject_strain(result, inj, interpolate_if_offset=interpolate_if_offset)
    return result
