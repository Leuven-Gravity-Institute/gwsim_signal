"""High-level CBC injection orchestration helpers."""

from __future__ import annotations

from collections.abc import Sequence

from gwpy.timeseries import TimeSeries

from gwmock_signal.injection import inject_strain
from gwmock_signal.multichannel import DetectorStrainStack
from gwmock_signal.projection import project_polarizations_to_network
from gwmock_signal.waveform import WaveformFactory

_REQUIRED_PARAMS = (
    "mass1",
    "mass2",
    "spin1z",
    "spin2z",
    "tc",
    "distance",
    "right_ascension",
    "declination",
    "polarization",
    "inclination",
    "coa_phase",
)


def inject_cbc_signal(  # noqa: PLR0913
    params: dict[str, float],
    detector_names: Sequence[str],
    background: dict[str, TimeSeries],
    *,
    waveform_model: str,
    sampling_frequency: float,
    minimum_frequency: float = 20.0,
    earth_rotation: bool = True,
    interpolate_if_offset: bool = True,
) -> DetectorStrainStack:
    """Generate, project, inject, and stack a CBC signal for one detector network.

    Args:
        params: CBC and sky-location parameters. Must include the keys listed in
            ``_REQUIRED_PARAMS``.
        detector_names: Ordered detector names to project onto and stack.
        background: Background strain series keyed by detector name.
        waveform_model: Registered waveform approximant passed to ``WaveformFactory``.
        sampling_frequency: Output sample rate in Hz passed to waveform generation.
        minimum_frequency: Low-frequency cutoff in Hz passed to waveform generation.
        earth_rotation: Whether to evaluate detector response at time-dependent GPS times.
        interpolate_if_offset: Whether to interpolate injections with fractional-sample offsets.

    Returns:
        A detector-aligned stack of injected strain series.

    Raises:
        ValueError: If required CBC parameters are missing.
        KeyError: If a detector background series is missing.
    """
    missing_keys = [key for key in _REQUIRED_PARAMS if key not in params]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise ValueError(f"Missing required CBC parameters: {missing}")

    normalized_names = [str(name) for name in detector_names]
    polarizations = WaveformFactory().generate(
        waveform_model,
        params,
        sampling_frequency=sampling_frequency,
        minimum_frequency=minimum_frequency,
    )
    projected = project_polarizations_to_network(
        polarizations,
        normalized_names,
        right_ascension=params["right_ascension"],
        declination=params["declination"],
        polarization_angle=params["polarization"],
        earth_rotation=earth_rotation,
    )

    injected_strains = {
        name: inject_strain(
            background[name],
            projected[name],
            interpolate_if_offset=interpolate_if_offset,
        )
        for name in normalized_names
    }
    return DetectorStrainStack.from_mapping(normalized_names, injected_strains)
