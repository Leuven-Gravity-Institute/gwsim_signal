"""Project GW polarizations onto ground-based detectors (PyCBC/LAL geometry)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

import numpy as np
from gwpy.timeseries import TimeSeries as GWpyTimeSeries
from pycbc.detector import Detector as PyCBCDetector
from scipy.interpolate import interp1d

from gwmock_signal.detector import CustomDetector

DetectorSpec = str | CustomDetector


def _validate_polarizations(polarizations: Mapping[str, GWpyTimeSeries]) -> tuple[GWpyTimeSeries, GWpyTimeSeries]:
    """Validate ``plus``/``cross`` GWpy series share one time grid."""
    if not isinstance(polarizations, Mapping):
        raise TypeError("polarizations must be a mapping with 'plus' and 'cross' keys.")
    if "plus" not in polarizations or "cross" not in polarizations:
        raise ValueError("polarizations must contain both 'plus' and 'cross' keys.")
    hp = polarizations["plus"]
    hc = polarizations["cross"]
    if not isinstance(hp, GWpyTimeSeries) or not isinstance(hc, GWpyTimeSeries):
        raise TypeError("polarizations['plus'] and polarizations['cross'] must be gwpy.timeseries.TimeSeries.")
    if len(hp) != len(hc):
        raise ValueError(f"plus and cross must have the same number of samples; got {len(hp)} and {len(hc)}.")
    if hp.sample_rate != hc.sample_rate:
        raise ValueError("plus and cross must have the same sample rate.")
    hp_times = np.asarray(hp.times.value, dtype=float)
    hc_times = np.asarray(hc.times.value, dtype=float)
    dt = float(hp.dt.value)
    if not np.allclose(hp_times, hc_times, rtol=0.0, atol=max(np.finfo(float).eps, 0.5 * dt)):
        raise ValueError("plus and cross must share the same time samples (same t0, dt, and length).")
    return hp, hc


def _make_detectors(detector_specs: Sequence[DetectorSpec]) -> list[tuple[str, PyCBCDetector]]:
    """Instantiate PyCBC detectors; raise a clear error if a name is invalid.

    Accepts either PyCBC/LAL IFO code strings or :class:`~gwmock_signal.detector.CustomDetector`
    instances.
    """
    out: list[tuple[str, PyCBCDetector]] = []
    for raw in detector_specs:
        if isinstance(raw, CustomDetector):
            out.append((raw.name, raw.to_pycbc()))
        else:
            name = str(raw)
            try:
                det = PyCBCDetector(name)
            except ValueError as exc:
                raise ValueError(
                    f"Unknown or unsupported detector {name!r}. "
                    "Use a valid PyCBC/LAL interferometer code (e.g. 'H1', 'L1', 'V1')."
                ) from exc
            out.append((name, det))
    return out


def project_polarizations_to_network(  # noqa: PLR0913
    polarizations: Mapping[str, GWpyTimeSeries],
    detector_names: Sequence[DetectorSpec],
    *,
    right_ascension: float,
    declination: float,
    polarization_angle: float,
    earth_rotation: bool = True,
) -> dict[str, GWpyTimeSeries]:
    """Project tensor plus/cross strains onto detectors using PyCBC geometry.

    Uses antenna patterns ``F_plus``, ``F_cross`` and geocenter time delays from
    PyCBC [`Detector`](https://pycbc.org/pycbc/latest/html/detector.html). Polarizations are interpolated in
    time with cubic splines (see user guide for caveats at edges).

    Args:
        polarizations: Mapping containing ``plus`` and ``cross`` GWpy time series
            on a common grid.
        detector_names: Sequence of IFO codes (e.g. ``H1``, ``L1``, ``V1``) or
            :class:`~gwmock_signal.detector.CustomDetector` instances, or a mix
            of both.
        right_ascension: Source right ascension in radians.
        declination: Source declination in radians.
        polarization_angle: Polarization angle psi in radians (tensor modes).
        earth_rotation: If ``True``, evaluate antenna patterns at time-dependent
            GPS times (recommended for longer signals). If ``False``, use a single
            reference time at the segment midpoint for patterns and delays.

    Returns:
        Mapping from each detector name to the projected strain as a GWpy time
        series (same length and sample rate as the inputs).

    Raises:
        TypeError: If ``polarizations`` is not a mapping of GWpy series as required.
        ValueError: If keys are missing, time grids disagree, or a detector name
            is not recognized by PyCBC.
    """
    hp, hc = _validate_polarizations(polarizations)
    normalized_names = [d if isinstance(d, str) else d.name for d in detector_names]
    if len(set(normalized_names)) != len(normalized_names):
        raise ValueError("detector_names must not contain duplicates.")
    detectors = _make_detectors(list(detector_names))

    time_array = cast(np.ndarray, hp.times.to_value())
    reference_time = float(0.5 * (time_array[0] + time_array[-1]))
    time_array_wrt_reference = time_array - reference_time

    minimum_number_of_data_points = 4
    interp_kind = "cubic" if len(time_array_wrt_reference) >= minimum_number_of_data_points else "linear"

    hp_func = interp1d(
        time_array_wrt_reference,
        hp.to_value(),
        kind=interp_kind,
        bounds_error=False,
        fill_value=0.0,
    )
    hc_func = interp1d(
        time_array_wrt_reference,
        hc.to_value(),
        kind=interp_kind,
        bounds_error=False,
        fill_value=0.0,
    )

    strains: dict[str, GWpyTimeSeries] = {}

    for name, det in detectors:
        if earth_rotation:
            time_delays = det.time_delay_from_earth_center(
                right_ascension=right_ascension,
                declination=declination,
                t_gps=time_array,
            )
            shifted_times = time_array_wrt_reference - time_delays
            fp_vals, fc_vals = det.antenna_pattern(
                right_ascension=right_ascension,
                declination=declination,
                polarization=polarization_angle,
                t_gps=time_array + time_delays,
                polarization_type="tensor",
            )
        else:
            time_delays = det.time_delay_from_earth_center(
                right_ascension=right_ascension,
                declination=declination,
                t_gps=reference_time,
            )
            antenna = det.antenna_pattern(
                right_ascension=right_ascension,
                declination=declination,
                polarization=polarization_angle,
                t_gps=reference_time,
                polarization_type="tensor",
            )
            fp_vals, fc_vals = antenna
            shifted_times = time_array_wrt_reference - time_delays

        hp_shifted = hp_func(shifted_times)
        hc_shifted = hc_func(shifted_times)
        response = fp_vals * hp_shifted + fc_vals * hc_shifted

        strains[name] = GWpyTimeSeries(
            response,
            t0=float(time_array[0]),
            sample_rate=hp.sample_rate,
            name=name,
        )

    return strains
