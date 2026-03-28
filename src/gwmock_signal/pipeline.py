"""High-level CBC injection pipeline.

See ``docs/user_guide/cbc-pipeline.md`` (examples) and ``docs/api/pipeline/index.md``
(API reference).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from gwpy.timeseries import TimeSeries

from gwmock_signal.multichannel.stack import DetectorStrainStack
from gwmock_signal.simulator import CBCSimulator


def inject_cbc_signal(  # noqa: PLR0913
    waveform_model: str,
    params: dict[str, Any],
    detector_names: Sequence[str],
    background: Mapping[str, TimeSeries],
    *,
    sampling_frequency: float,
    minimum_frequency: float,
    earth_rotation: bool = True,
    interpolate_if_offset: bool = True,
) -> DetectorStrainStack:
    """Inject a CBC signal into background strain for a network of detectors.

    Orchestrates waveform generation, detector projection, and strain injection
    for compact binary coalescence (CBC) sources. Returns a
    ``DetectorStrainStack`` containing the injected strain for each detector.

    Args:
        waveform_model: PyCBC time-domain approximant name (e.g. ``'IMRPhenomD'``).
        params: CBC injection parameters; must include ``mass1``, ``mass2``,
            ``tc``, ``distance``, ``inclination``, ``right_ascension``,
            ``declination``, and ``polarization``.
        detector_names: IFO codes for the target network
            (e.g. ``['H1', 'L1', 'V1']``).
        background: Mapping of detector name to background ``TimeSeries``
            (e.g. noise or zeros segment).
        sampling_frequency: Sample rate in Hz.
        minimum_frequency: Low-frequency cutoff in Hz, passed to the waveform
            generator.
        earth_rotation: If ``True``, evaluate antenna patterns at
            time-dependent GPS times (recommended for longer signals). If
            ``False``, use a single reference time at the segment midpoint.
        interpolate_if_offset: If ``True``, use cubic interpolation when the
            injection start is not on a target sample boundary. If ``False``,
            skip the injection silently when off-grid.

    Returns:
        ``DetectorStrainStack`` with one injected strain channel per detector in
        ``detector_names`` order.

    Raises:
        ValueError: If any required parameter key is missing from ``params``.
        ValueError: If a detector name is not recognized by PyCBC.
        KeyError: If a detector name is missing from ``background``.
    """
    return CBCSimulator(waveform_model=waveform_model).simulate(
        params,
        detector_names,
        background,
        sampling_frequency=sampling_frequency,
        minimum_frequency=minimum_frequency,
        earth_rotation=earth_rotation,
        interpolate_if_offset=interpolate_if_offset,
    )
