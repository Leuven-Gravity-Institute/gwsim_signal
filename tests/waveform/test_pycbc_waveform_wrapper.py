"""Unit tests for `pycbc_waveform_wrapper`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

from gwmock_signal.waveform.pycbc_wrapper import pycbc_waveform_wrapper


class TestPyCBCWaveformWrapper:
    """Test suite for `pycbc_waveform_wrapper`."""

    @pytest.fixture
    def mock_pycbc_waveform(self):
        """Return a pair of mocks mimicking PyCBC `TimeSeries` objects."""
        hp = MagicMock()
        hp.start_time = 0.0
        hp.delta_t = 1.0 / 4096
        hp.sample_rate = 4096
        hp.data = np.random.randn(16384)
        hc = MagicMock()
        hc.start_time = 0.0
        hc.delta_t = 1.0 / 4096
        hc.sample_rate = 4096
        hc.data = np.random.randn(16384)
        return hp, hc

    @pytest.fixture
    def default_params(self):
        """Keyword arguments for a minimal `pycbc_waveform_wrapper` call."""
        return {
            "tc": 1234567890.0,
            "sampling_frequency": 4096,
            "waveform_model": "IMRPhenomD",
            "mass1": 40.0,
            "mass2": 30.0,
            "spin1z": 0.5,
            "spin2z": -0.3,
            "minimum_frequency": 20.0,
        }

    def test_wrapper_basic_call(self, default_params, mock_pycbc_waveform):
        """`get_td_waveform` receives approximant, delta_t, masses, and f_lower."""
        with patch("gwmock_signal.waveform.pycbc_wrapper.get_td_waveform") as mock_get_td:
            mock_get_td.return_value = mock_pycbc_waveform
            _result = pycbc_waveform_wrapper(**default_params)
            mock_get_td.assert_called_once()
            call_kwargs = mock_get_td.call_args[1]
            assert call_kwargs["approximant"] == "IMRPhenomD"
            assert call_kwargs["delta_t"] == 1.0 / 4096
            assert call_kwargs["mass1"] == default_params["mass1"]
            assert call_kwargs["mass2"] == default_params["mass2"]
            assert call_kwargs["f_lower"] == default_params["minimum_frequency"]

    def test_wrapper_returns_dict_with_plus_cross(self, default_params, mock_pycbc_waveform):
        """Output keys are exactly `plus` and `cross`."""
        with patch("gwmock_signal.waveform.pycbc_wrapper.get_td_waveform") as mock_get_td:
            mock_get_td.return_value = mock_pycbc_waveform
            result = pycbc_waveform_wrapper(**default_params)
            assert isinstance(result, dict)
            assert "plus" in result
            assert "cross" in result
            assert len(result) == len(("plus", "cross"))

    def test_wrapper_returns_gwpy_timeseries(self, default_params, mock_pycbc_waveform):
        """Polarizations are GWpy `TimeSeries` instances."""
        with patch("gwmock_signal.waveform.pycbc_wrapper.get_td_waveform") as mock_get_td:
            mock_get_td.return_value = mock_pycbc_waveform
            result = pycbc_waveform_wrapper(**default_params)
            assert isinstance(result["plus"], TimeSeries)
            assert isinstance(result["cross"], TimeSeries)
