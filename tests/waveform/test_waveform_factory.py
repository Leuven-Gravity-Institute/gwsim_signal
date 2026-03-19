"""Tests for `WaveformFactory`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from astropy import units as u
from gwpy.timeseries import TimeSeries

from gwmock_signal.waveform import WaveformFactory, pycbc_waveform_wrapper


def test_get_model_unknown_raises():
    """Unknown model names raise `ValueError`."""
    factory = WaveformFactory()
    with pytest.raises(ValueError, match="not found"):
        factory.get_model("definitely_not_a_real_approximant_name_xyz")


def test_register_and_generate_toy():
    """Custom model returns consistent plus/cross GWpy series."""

    def toy(
        *,
        waveform_model: str,
        tc: float,
        sampling_frequency: float,
        minimum_frequency: float,
        **kwargs,
    ):
        width_s = float(kwargs.get("width", 0.1))
        f_hz = float(kwargs.get("f0", 150.0))
        dt = 1.0 / sampling_frequency
        n_half = max(8, int(width_s * sampling_frequency))
        t = (np.arange(-n_half, n_half + 1) * dt) + tc
        env = np.exp(-0.5 * ((t - tc) / (width_s / 3)) ** 2)
        phase = 2 * np.pi * f_hz * (t - tc)
        hp = env * np.cos(phase)
        hc = env * np.sin(phase)
        return {
            "plus": TimeSeries(hp, t0=float(t[0]), dt=dt, unit=u.dimensionless_unscaled),
            "cross": TimeSeries(hc, t0=float(t[0]), dt=dt, unit=u.dimensionless_unscaled),
        }

    factory = WaveformFactory()
    factory.register_model("toy_burst", toy)
    out = factory.generate(
        "toy_burst",
        {"tc": 1_400_000_000.0, "f0": 120.0, "width": 0.05},
        sampling_frequency=4096.0,
        minimum_frequency=20.0,
    )
    assert set(out) == {"plus", "cross"}
    assert len(out["plus"]) == len(out["cross"])


def test_register_model_string_import():
    """String `register_model` path resolves to the same callable object."""
    factory = WaveformFactory()
    factory.register_model("pycbc_alias", "gwmock_signal.waveform.pycbc_wrapper:pycbc_waveform_wrapper")
    assert factory.get_model("pycbc_alias") is pycbc_waveform_wrapper


@patch("gwmock_signal.waveform.pycbc_wrapper.get_td_waveform")
def test_factory_generate_delegates(mock_get_td):
    """Built-in model calls PyCBC `get_td_waveform` once."""
    hp = MagicMock()
    hp.start_time = 0.0
    hp.delta_t = 1 / 4096
    hp.data = np.zeros(256)
    hc = MagicMock()
    hc.start_time = 0.0
    hc.delta_t = 1 / 4096
    hc.data = np.zeros(256)
    mock_get_td.return_value = (hp, hc)

    factory = WaveformFactory()
    factory.generate(
        "IMRPhenomD",
        {"tc": 100.0, "mass1": 10.0, "mass2": 10.0},
        sampling_frequency=4096.0,
        minimum_frequency=20.0,
    )
    mock_get_td.assert_called_once()
