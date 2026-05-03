"""Tests for `project_polarizations_to_network`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

from gwmock_signal.projection.network import project_polarizations_to_network


def _uniform_series(n: int = 128, fs: float = 4096.0, t0: float = 100.0) -> TimeSeries:
    t = np.arange(n) / fs + t0
    return TimeSeries(np.sin(2 * np.pi * 10.0 * t), t0=t0, sample_rate=fs)


def test_polarizations_not_a_mapping_raises_type_error() -> None:
    """Passing a non-mapping raises TypeError."""
    with pytest.raises(TypeError, match="mapping"):
        project_polarizations_to_network(
            [1, 2, 3],  # type: ignore[arg-type]
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_polarizations_wrong_series_type_raises_type_error() -> None:
    """Plus/cross values that are not GWpy TimeSeries raise TypeError."""
    with pytest.raises(TypeError, match=r"gwpy.timeseries.TimeSeries"):
        project_polarizations_to_network(
            {"plus": np.ones(8), "cross": np.zeros(8)},  # type: ignore[arg-type]
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_mismatched_sample_rates_raises_value_error() -> None:
    """Plus and cross with different sample rates raise ValueError."""
    hp = _uniform_series(fs=4096.0)
    hc = _uniform_series(fs=2048.0)
    with pytest.raises(ValueError, match="same sample rate"):
        project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_mismatched_time_grids_raises_value_error() -> None:
    """Plus and cross on different time grids raise ValueError."""
    hp = _uniform_series(t0=100.0)
    hc = _uniform_series(t0=200.0)
    with pytest.raises(ValueError, match="same time samples"):
        project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_duplicate_detector_names_raises_value_error() -> None:
    """Duplicate entries in detector_names raise ValueError."""
    hp = hc = _uniform_series()
    with pytest.raises(ValueError, match="duplicates"):
        project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            ["H1", "H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_requires_plus_cross_keys():
    """Polarizations mapping must include plus and cross."""
    hp = _uniform_series()
    with pytest.raises(ValueError, match=r"plus.*cross"):
        project_polarizations_to_network(
            {"plus": hp},
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_requires_matching_length():
    """Plus and cross must have the same number of samples."""
    hp = _uniform_series(n=64)
    hc = _uniform_series(n=32)
    with pytest.raises(ValueError, match="same number of samples"):
        project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            ["H1"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


def test_unknown_detector_name():
    """Invalid IFO codes raise ValueError with a helpful message."""
    hp = hc = _uniform_series()
    with pytest.raises(ValueError, match="Unknown or unsupported"):
        project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            ["NOT_A_REAL_DETECTOR_XYZ"],
            right_ascension=0.0,
            declination=0.0,
            polarization_angle=0.0,
        )


@patch("gwmock_signal.projection.network._antenna_pattern_lal", return_value=(1.0, 0.0))
@patch("gwmock_signal.projection.network._time_delay_from_earth_center_lal", return_value=0.0)
@patch("gwmock_signal.projection.network.lalsimulation.DetectorPrefixToLALDetector")
def test_delegates_to_lal(mock_detector_lookup, mock_time_delay, mock_antenna_pattern):
    """Each built-in detector name resolves through the LAL detector path."""
    mock_detector_lookup.return_value = MagicMock()
    t0 = 0.0
    fs = 8.0
    hp = TimeSeries(np.ones(8), t0=t0, sample_rate=fs)
    hc = TimeSeries(np.zeros(8), t0=t0, sample_rate=fs)

    names = ["H1", "L1"]
    out = project_polarizations_to_network(
        {"plus": hp, "cross": hc},
        names,
        right_ascension=0.1,
        declination=0.2,
        polarization_angle=0.3,
        earth_rotation=False,
    )
    assert set(out) == set(names)
    assert mock_detector_lookup.call_count == len(names)
    assert mock_time_delay.call_count == len(names)
    assert mock_antenna_pattern.call_count == len(names)
