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
"""Project GW polarizations onto ground-based detectors."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

import lal
import numpy as np
from astropy import constants, coordinates, units
from astropy.coordinates.matrix_utilities import rotation_matrix
from astropy.time import Time
from gwpy.timeseries import TimeSeries as GWpyTimeSeries
from scipy.interpolate import interp1d

if TYPE_CHECKING:
    from gwmock_signal.detector import CustomDetector
else:
    CustomDetector = Any

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


def _get_lal_detector(prefix: str) -> lal.Detector:
    """Return one detector from LAL's cached prefix registry."""
    try:
        return cast(lal.Detector, lal.cached_detector_by_prefix[prefix])
    except KeyError as exc:
        raise ValueError(
            f"Unknown or unsupported detector {prefix!r}. Use a valid LAL interferometer code (e.g. 'H1', 'L1', 'V1')."
        ) from exc


def _gmst_accurate(t_gps: float) -> float:
    """Return Greenwich mean sidereal time in radians using Astropy."""
    return float(Time(float(t_gps), format="gps", scale="utc", location=(0, 0)).sidereal_time("mean").rad)


def _reconstructed_geometry(prefix: str) -> tuple[np.ndarray, np.ndarray]:
    """Return detector response and location reconstructed from one LAL detector."""
    fr_detector = _get_lal_detector(prefix).frDetector

    arm_response = np.array([[-1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    rotation_longitude = rotation_matrix(-fr_detector.vertexLongitudeRadians * units.rad, "z")
    rotation_latitude = rotation_matrix(-(np.pi / 2.0 - fr_detector.vertexLatitudeRadians) * units.rad, "y")

    responses: list[np.ndarray] = []
    for azimuth, altitude in (
        (fr_detector.yArmAzimuthRadians, fr_detector.yArmAltitudeRadians),
        (fr_detector.xArmAzimuthRadians, fr_detector.xArmAltitudeRadians),
    ):
        rotation_azimuth = rotation_matrix(azimuth * units.rad, "z")
        rotation_altitude = rotation_matrix(-altitude * units.rad, "y")
        rotation = rotation_longitude @ rotation_latitude @ rotation_azimuth @ rotation_altitude
        responses.append(np.asarray(rotation @ arm_response @ rotation.T / 2.0, dtype=float))

    location = coordinates.EarthLocation.from_geodetic(
        fr_detector.vertexLongitudeRadians * units.rad,
        fr_detector.vertexLatitudeRadians * units.rad,
        height=fr_detector.vertexElevation * units.meter,
    )
    return responses[0] - responses[1], np.array([location.x.value, location.y.value, location.z.value], dtype=float)


def _time_delay_from_earth_center_lal(
    prefix: str,
    *,
    right_ascension: float,
    declination: float,
    t_gps: float,
) -> float:
    """Return the geocenter time delay for one reconstructed detector geometry."""
    _, location = _reconstructed_geometry(prefix)
    gha = _gmst_accurate(t_gps) - right_ascension
    cosdec = np.cos(declination)
    propagation_direction = np.array(
        [
            cosdec * np.cos(gha),
            -cosdec * np.sin(gha),
            np.sin(declination),
        ],
        dtype=float,
    )
    earth_center = np.array([0, 0, 0])
    baseline = earth_center - location
    return float(np.dot(baseline, propagation_direction) / constants.c.value)


def _antenna_pattern_lal(
    prefix: str,
    *,
    right_ascension: float,
    declination: float,
    polarization_angle: float,
    t_gps: float,
) -> tuple[float, float]:
    """Return tensor antenna-pattern factors for one reconstructed detector geometry."""
    response, _ = _reconstructed_geometry(prefix)
    gha = _gmst_accurate(t_gps) - right_ascension
    cosgha = np.cos(gha)
    singha = np.sin(gha)
    cosdec = np.cos(declination)
    sindec = np.sin(declination)
    cospsi = np.cos(polarization_angle)
    sinpsi = np.sin(polarization_angle)

    x = np.array(
        [
            -cospsi * singha - sinpsi * cosgha * sindec,
            -cospsi * cosgha + sinpsi * singha * sindec,
            sinpsi * cosdec,
        ],
        dtype=float,
    )
    dx = response.dot(x)

    y = np.array(
        [
            sinpsi * singha - cospsi * cosgha * sindec,
            sinpsi * cosgha + cospsi * singha * sindec,
            cospsi * cosdec,
        ],
        dtype=float,
    )
    dy = response.dot(y)

    return float(np.sum(x * dx - y * dy)), float(np.sum(x * dy + y * dx))


def _make_detectors(detector_specs: Sequence[DetectorSpec]) -> list[tuple[str, str]]:
    """Resolve detector names to one LAL lookup key per output channel.

    Accepts either built-in LAL IFO code strings or
    :class:`~gwmock_signal.detector.CustomDetector` instances.
    """
    out: list[tuple[str, str]] = []

    for raw in detector_specs:
        if isinstance(raw, str):
            name = str(raw)
            _get_lal_detector(name)
            out.append((name, name))
        else:
            from gwmock_signal.detector import CustomDetector  # noqa: PLC0415

            if not isinstance(raw, CustomDetector):
                raise TypeError(f"Unsupported detector specification type: {type(raw).__name__}")
            detector = raw.to_lal()
            out.append((raw.name, detector.frDetector.prefix))
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
    """Project tensor plus/cross strains onto detectors using detector geometry.

    Built-in and custom detector codes are resolved through the LAL cached
    detector registry. Polarizations are interpolated in time with cubic
    splines (see user guide for caveats at edges).

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
            is not recognized.
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

    for name, prefix in detectors:
        if earth_rotation:
            time_delays = np.asarray(
                [
                    _time_delay_from_earth_center_lal(
                        prefix,
                        right_ascension=right_ascension,
                        declination=declination,
                        t_gps=t,
                    )
                    for t in time_array
                ],
                dtype=float,
            )
            shifted_times = time_array_wrt_reference - time_delays
            antenna = np.asarray(
                [
                    _antenna_pattern_lal(
                        prefix,
                        right_ascension=right_ascension,
                        declination=declination,
                        polarization_angle=polarization_angle,
                        t_gps=t + delay,
                    )
                    for t, delay in zip(time_array, time_delays, strict=False)
                ],
                dtype=float,
            )
            fp_vals, fc_vals = antenna[:, 0], antenna[:, 1]
        else:
            time_delay = _time_delay_from_earth_center_lal(
                prefix,
                right_ascension=right_ascension,
                declination=declination,
                t_gps=reference_time,
            )
            fp_vals, fc_vals = _antenna_pattern_lal(
                prefix,
                right_ascension=right_ascension,
                declination=declination,
                polarization_angle=polarization_angle,
                t_gps=reference_time,
            )
            shifted_times = time_array_wrt_reference - time_delay

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
