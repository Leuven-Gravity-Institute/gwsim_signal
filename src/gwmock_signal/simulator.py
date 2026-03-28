"""Abstract base class and CBC concrete implementation for GW signal simulation."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from gwpy.timeseries import TimeSeries

from gwmock_signal.injection import inject_strain
from gwmock_signal.multichannel.stack import DetectorStrainStack
from gwmock_signal.projection.network import project_polarizations_to_network
from gwmock_signal.waveform import WaveformFactory

logger = logging.getLogger("gwmock_signal.simulator")


class GWSimulator(ABC):
    """Abstract base class for gravitational-wave signal simulators.

    Defines the minimal source-agnostic contract: subclasses must implement
    ``required_params`` and ``simulate``. ``_validate_params`` is provided as a
    concrete helper.

    See ``docs/api/simulator/index.md`` for the API reference.
    """

    @property
    @abstractmethod
    def required_params(self) -> frozenset[str]:
        """Parameter keys that must be present in the params dict passed to ``simulate``."""

    def _validate_params(self, params: dict[str, Any]) -> None:
        """Raise ``ValueError`` naming any key in ``required_params`` missing from ``params``.

        Args:
            params: Source parameters to validate.

        Raises:
            ValueError: If any required key is absent, naming each missing key.
        """
        missing = self.required_params - set(params)
        if missing:
            raise ValueError(f"Missing required parameters: {sorted(missing)}")

    @abstractmethod
    def simulate(
        self,
        params: dict[str, Any],
        detector_names: Sequence[str],
        background: Mapping[str, TimeSeries],
        *,
        sampling_frequency: float,
        minimum_frequency: float,
    ) -> DetectorStrainStack:
        """Simulate a gravitational-wave signal and return a ``DetectorStrainStack``.

        Args:
            params: Source parameters.
            detector_names: IFO codes (e.g. ``'H1'``, ``'L1'``, ``'V1'``).
            background: Mapping of detector name to background ``TimeSeries``.
            sampling_frequency: Sample rate in Hz.
            minimum_frequency: Low-frequency cutoff in Hz.

        Returns:
            ``DetectorStrainStack`` containing the simulated strain per detector.
        """


class TransientSimulator(GWSimulator):
    """Intermediate base class for transient GW source simulators.

    Provides the concrete ``simulate`` method that orchestrates the full
    transient injection pipeline: validation → polarizations → detector
    projection → strain injection → stacking.  Subclasses must implement
    ``generate_polarizations`` and ``required_params``.
    """

    @abstractmethod
    def generate_polarizations(
        self,
        params: dict[str, Any],
        sampling_frequency: float,
        minimum_frequency: float,
    ) -> tuple[TimeSeries, TimeSeries]:
        """Generate plus and cross polarization time series.

        Args:
            params: Source parameters.
            sampling_frequency: Sample rate in Hz.
            minimum_frequency: Low-frequency cutoff in Hz.

        Returns:
            Tuple of ``(hp, hc)`` GWpy ``TimeSeries`` objects.
        """

    def simulate(  # noqa: PLR0913
        self,
        params: dict[str, Any],
        detector_names: Sequence[str],
        background: Mapping[str, TimeSeries],
        *,
        sampling_frequency: float,
        minimum_frequency: float,
        earth_rotation: bool = True,
        interpolate_if_offset: bool = True,
    ) -> DetectorStrainStack:
        """Run the full injection pipeline and return a ``DetectorStrainStack``.

        Calls ``_validate_params``, ``generate_polarizations``,
        ``project_polarizations_to_network``, and ``inject_strain`` in order,
        then assembles the result into a ``DetectorStrainStack``.

        Args:
            params: Source parameters; must contain all ``required_params`` keys
                plus ``right_ascension``, ``declination``, and ``polarization``
                for antenna-response projection.
            detector_names: IFO codes (e.g. ``'H1'``, ``'L1'``, ``'V1'``).
            background: Mapping of detector name to background
                ``TimeSeries`` (e.g. noise or zeros).
            sampling_frequency: Sample rate in Hz.
            minimum_frequency: Low-frequency cutoff in Hz.
            earth_rotation: If ``True``, evaluate antenna patterns at
                time-dependent GPS times (recommended for longer signals).
                If ``False``, use a single reference time.
            interpolate_if_offset: If ``True``, interpolate the injection
                when its start is not on a target sample boundary.

        Returns:
            ``DetectorStrainStack`` containing the injected strain for
            each detector in ``detector_names`` order.
        """
        self._validate_params(params)

        # Validate projection keys before direct params[...] access.
        # _validate_params only checks subclass-defined required_params. Non-CBC subclasses can pass validation and then fail mid-pipeline with KeyError.
        projection_keys = {"right_ascension", "declination", "polarization"}
        missing_projection = projection_keys - set(params)
        if missing_projection:
            raise ValueError(f"Missing required parameters: {sorted(missing_projection)}")

        hp, hc = self.generate_polarizations(params, sampling_frequency, minimum_frequency)
        projected = project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            detector_names,
            right_ascension=params["right_ascension"],
            declination=params["declination"],
            polarization_angle=params["polarization"],
            earth_rotation=earth_rotation,
        )
        injected = {
            name: inject_strain(
                background[name],
                projected[name],
                interpolate_if_offset=interpolate_if_offset,
            )
            for name in detector_names
        }
        return DetectorStrainStack.from_mapping(detector_names, injected)


class CBCSimulator(TransientSimulator):
    """Compact binary coalescence simulator backed by ``WaveformFactory``.

    Generates time-domain polarizations via PyCBC (or any registered model),
    projects them onto the requested detectors, and injects them into background
    strain. ``waveform_model`` is a CBC concern and is supplied at construction
    time, keeping the base-class ``simulate`` interface source-agnostic.

    Args:
        waveform_model: PyCBC time-domain approximant name or any model
            registered with ``WaveformFactory`` (e.g. ``'IMRPhenomD'``).
    """

    #: Minimum parameter keys required by the CBC pipeline.
    _REQUIRED: frozenset[str] = frozenset(
        {
            "mass1",
            "mass2",
            "tc",
            "distance",
            "inclination",
            "right_ascension",
            "declination",
            "polarization",
        }
    )

    def __init__(self, waveform_model: str) -> None:
        """Initialise with the waveform model name.

        Args:
            waveform_model: PyCBC time-domain approximant name or any model
                registered with ``WaveformFactory``.
        """
        self._waveform_model = waveform_model

    @property
    def waveform_model(self) -> str:
        """PyCBC approximant or custom model name."""
        return self._waveform_model

    @property
    def required_params(self) -> frozenset[str]:
        """Return the fixed set of required CBC parameter keys."""
        return self._REQUIRED

    def generate_polarizations(
        self,
        params: dict[str, Any],
        sampling_frequency: float,
        minimum_frequency: float,
    ) -> tuple[TimeSeries, TimeSeries]:
        """Delegate waveform generation to ``WaveformFactory``.

        Args:
            params: CBC source parameters (masses, spins, distance, etc.).
            sampling_frequency: Sample rate in Hz.
            minimum_frequency: Low-frequency cutoff in Hz.

        Returns:
            Tuple of ``(hp, hc)`` GWpy ``TimeSeries`` objects.
        """
        result = WaveformFactory().generate(
            self._waveform_model,
            params,
            sampling_frequency=sampling_frequency,
            minimum_frequency=minimum_frequency,
        )
        return result["plus"], result["cross"]
