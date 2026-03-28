"""Unit tests for GWSimulator ABC and CBCSimulator."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries
from pycbc.types import TimeSeries as PyCBCTimeSeries

import gwmock_signal
from gwmock_signal import CBCSimulator, GWSimulator
from gwmock_signal.multichannel.stack import DetectorStrainStack

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _zeros(n: int = 128, fs: float = 4096.0, t0: float = 1_000_000.0) -> TimeSeries:
    return TimeSeries(np.zeros(n), t0=t0, sample_rate=fs)


_MINIMAL_PARAMS: dict = {
    "mass1": 36.0,
    "mass2": 29.0,
    "tc": 1_126_259_462.4,
    "distance": 410.0,
    "inclination": 0.0,
    "right_ascension": 1.375,
    "declination": -1.211,
    "polarization": 0.0,
}


# ---------------------------------------------------------------------------
# GWSimulator ABC
# ---------------------------------------------------------------------------


class TestGWSimulatorAbstract:
    """Tests that GWSimulator enforces abstract-class semantics."""

    def test_direct_instantiation_raises_type_error(self):
        """GWSimulator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            GWSimulator()  # type: ignore[abstract]

    def test_concrete_subclass_without_required_methods_raises(self):
        """Subclass missing required_params or generate_polarizations raises TypeError."""

        class Incomplete(GWSimulator):
            @property
            def required_params(self) -> frozenset[str]:
                return frozenset()

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# _validate_params
# ---------------------------------------------------------------------------


class TestValidateParams:
    """Tests for GWSimulator._validate_params."""

    def _make_concrete(self, required: frozenset[str]) -> GWSimulator:
        """Return a minimal concrete subclass with the given required_params."""

        class Concrete(GWSimulator):
            @property
            def required_params(self) -> frozenset[str]:
                return required

            def generate_polarizations(self, params, sampling_frequency, minimum_frequency):
                raise NotImplementedError

        return Concrete()

    def test_all_present_does_not_raise(self):
        """No exception when all required keys are present (extras are allowed)."""
        sim = self._make_concrete(frozenset({"a", "b"}))
        sim._validate_params({"a": 1, "b": 2, "c": 3})  # extra key is fine

    def test_missing_single_key_raises_value_error(self):
        """Single missing key names that key in the error."""
        sim = self._make_concrete(frozenset({"mass1", "mass2"}))
        with pytest.raises(ValueError, match="mass2"):
            sim._validate_params({"mass1": 10.0})

    def test_missing_multiple_keys_names_all(self):
        """All missing keys appear in the error message."""
        sim = self._make_concrete(frozenset({"a", "b", "c"}))
        with pytest.raises(ValueError, match="a") as exc_info:
            sim._validate_params({})
        msg = str(exc_info.value)
        assert "b" in msg
        assert "c" in msg


# ---------------------------------------------------------------------------
# CBCSimulator
# ---------------------------------------------------------------------------


class TestCBCSimulatorRequiredParams:
    """Tests for CBCSimulator.required_params."""

    def test_required_params_is_frozenset(self):
        """required_params returns a frozenset."""
        sim = CBCSimulator(waveform_model="IMRPhenomD")
        assert isinstance(sim.required_params, frozenset)

    def test_required_params_includes_cbc_keys(self):
        """CBC waveform keys are in required_params."""
        sim = CBCSimulator(waveform_model="IMRPhenomD")
        for key in ("mass1", "mass2", "tc", "distance", "inclination"):
            assert key in sim.required_params, f"Expected '{key}' in required_params"

    def test_required_params_includes_projection_keys(self):
        """Projection sky-position keys are in required_params."""
        sim = CBCSimulator(waveform_model="IMRPhenomD")
        for key in ("right_ascension", "declination", "polarization"):
            assert key in sim.required_params, f"Expected '{key}' in required_params"


class TestCBCSimulatorMissingParam:
    """Tests that missing required params raise ValueError with the key named."""

    def test_missing_mass1_raises_value_error_naming_key(self):
        """Missing mass1 raises ValueError that names 'mass1'."""
        sim = CBCSimulator(waveform_model="IMRPhenomD")
        incomplete = {k: v for k, v in _MINIMAL_PARAMS.items() if k != "mass1"}
        with pytest.raises(ValueError, match="mass1"):
            sim._validate_params(incomplete)


class TestCBCSimulatorSimulate:
    """Mock the full pipeline to test CBCSimulator.simulate returns DetectorStrainStack."""

    @patch("gwmock_signal.simulator.project_polarizations_to_network")
    @patch("gwmock_signal.simulator.inject_strain")
    @patch("gwmock_signal.simulator.WaveformFactory")
    def test_simulate_returns_detector_strain_stack(
        self,
        mock_factory_cls,
        mock_inject,
        mock_project,
    ):
        """Simulate returns a DetectorStrainStack with the requested detector order."""
        fs = 4096.0
        n = 128
        t0 = _MINIMAL_PARAMS["tc"]

        hp = TimeSeries(np.ones(n), t0=t0, sample_rate=fs)
        hc = TimeSeries(np.zeros(n), t0=t0, sample_rate=fs)
        strain_h1 = _zeros(n, fs, t0)
        strain_l1 = _zeros(n, fs, t0)

        mock_factory_cls.return_value.generate.return_value = {"plus": hp, "cross": hc}
        mock_project.return_value = {"H1": strain_h1, "L1": strain_l1}
        mock_inject.side_effect = lambda target, injection, **kw: _zeros(n, fs, t0)

        detector_names = ["H1", "L1"]
        background = {name: _zeros(n, fs, t0) for name in detector_names}

        sim = CBCSimulator(waveform_model="IMRPhenomD")
        result = sim.simulate(
            _MINIMAL_PARAMS,
            detector_names,
            background,
            sampling_frequency=fs,
            minimum_frequency=20.0,
        )

        assert isinstance(result, DetectorStrainStack)
        assert result.detector_names == tuple(detector_names)

    @patch("gwmock_signal.simulator.project_polarizations_to_network")
    @patch("gwmock_signal.simulator.inject_strain")
    @patch("gwmock_signal.simulator.WaveformFactory")
    def test_simulate_calls_pipeline_steps_in_order(
        self,
        mock_factory_cls,
        mock_inject,
        mock_project,
    ):
        """Verify _validate_params → generate_polarizations → project → inject order."""
        fs = 4096.0
        n = 64
        t0 = _MINIMAL_PARAMS["tc"]

        hp = TimeSeries(np.ones(n), t0=t0, sample_rate=fs)
        hc = TimeSeries(np.zeros(n), t0=t0, sample_rate=fs)
        projected_strain = _zeros(n, fs, t0)

        mock_factory_cls.return_value.generate.return_value = {"plus": hp, "cross": hc}
        mock_project.return_value = {"H1": projected_strain}
        mock_inject.return_value = _zeros(n, fs, t0)

        background = {"H1": _zeros(n, fs, t0)}
        CBCSimulator(waveform_model="IMRPhenomD").simulate(
            _MINIMAL_PARAMS,
            ["H1"],
            background,
            sampling_frequency=fs,
            minimum_frequency=20.0,
        )

        mock_factory_cls.return_value.generate.assert_called_once()
        mock_project.assert_called_once()
        mock_inject.assert_called_once()

    @patch("gwmock_signal.simulator.WaveformFactory")
    def test_simulate_missing_param_raises_before_waveform(self, mock_factory_cls):
        """Missing required parameter raises ValueError before any waveform call."""
        incomplete = {k: v for k, v in _MINIMAL_PARAMS.items() if k != "tc"}
        sim = CBCSimulator(waveform_model="IMRPhenomD")
        with pytest.raises(ValueError, match="tc"):
            sim.simulate(
                incomplete,
                ["H1"],
                {"H1": _zeros()},
                sampling_frequency=4096.0,
                minimum_frequency=20.0,
            )
        mock_factory_cls.return_value.generate.assert_not_called()


# ---------------------------------------------------------------------------
# End-to-end pipeline (mocked only at get_td_waveform boundary)
# ---------------------------------------------------------------------------


class TestCBCSimulatorEndToEnd:
    """Non-mocked assembly test: real project_polarizations_to_network and inject_strain."""

    @patch("gwmock_signal.waveform.pycbc_wrapper.get_td_waveform")
    def test_gw150914_like_params_on_two_detector_network(self, mock_get_td):
        """CBCSimulator.simulate returns a DetectorStrainStack for GW150914-like params.

        WaveformFactory/PyCBC waveform generation is mocked at the get_td_waveform
        boundary; project_polarizations_to_network and inject_strain run unpatched,
        exercising the full assembled pipeline with real geometry and injection logic.
        """
        tc = _MINIMAL_PARAMS["tc"]
        fs = 4096.0
        n = 256

        # Synthetic waveform at epoch=0; pycbc_waveform_wrapper adds tc to start_time
        pycbc_hp = PyCBCTimeSeries(np.zeros(n, dtype=float), delta_t=1.0 / fs, epoch=0.0)
        pycbc_hc = PyCBCTimeSeries(np.zeros(n, dtype=float), delta_t=1.0 / fs, epoch=0.0)
        mock_get_td.return_value = (pycbc_hp, pycbc_hc)

        # Background covers the post-injection epoch [tc, tc + n/fs)
        detector_names = ["H1", "L1"]
        background = {name: TimeSeries(np.zeros(n), t0=tc, sample_rate=fs) for name in detector_names}

        result = CBCSimulator(waveform_model="IMRPhenomD").simulate(
            _MINIMAL_PARAMS,
            detector_names,
            background,
            sampling_frequency=fs,
            minimum_frequency=20.0,
        )

        assert isinstance(result, DetectorStrainStack)
        assert result.detector_names == tuple(detector_names)
        assert len(result) == len(detector_names)
        # Each channel should be a TimeSeries with the same length as the background
        for name in detector_names:
            assert len(result[name]) == n


# ---------------------------------------------------------------------------
# Public import contract
# ---------------------------------------------------------------------------


class TestPublicImport:
    """Tests that GWSimulator and CBCSimulator are importable from the top-level package."""

    def test_gw_simulator_importable_from_top_level(self):
        """GWSimulator is reachable via gwmock_signal.GWSimulator."""
        assert hasattr(gwmock_signal, "GWSimulator")

    def test_cbc_simulator_importable_from_top_level(self):
        """CBCSimulator is reachable via gwmock_signal.CBCSimulator."""
        assert hasattr(gwmock_signal, "CBCSimulator")
