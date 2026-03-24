"""Tests for the high-level CBC injection pipeline."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

from gwmock_signal.multichannel import DetectorStrainStack
from gwmock_signal.pipeline import inject_cbc_signal


def _series(value: float, *, n: int = 8, fs: float = 4.0, t0: float = 100.0) -> TimeSeries:
    return TimeSeries(np.full(n, value), t0=t0, sample_rate=fs)


def _params() -> dict[str, float]:
    return {
        "mass1": 36.0,
        "mass2": 29.0,
        "spin1z": 0.1,
        "spin2z": -0.2,
        "tc": 1126259462.4,
        "distance": 410.0,
        "right_ascension": 1.2,
        "declination": -0.4,
        "polarization": 0.8,
        "inclination": 0.3,
        "coa_phase": 1.1,
    }


@patch("gwmock_signal.pipeline.inject_strain")
@patch("gwmock_signal.pipeline.project_polarizations_to_network")
@patch("gwmock_signal.pipeline.WaveformFactory")
def test_inject_cbc_signal_orchestrates_pipeline(mock_factory_cls, mock_project, mock_inject):
    """The pipeline should call waveform, projection, injection, and stacking in order."""
    detector_names = ["H1", "L1"]
    params = _params()
    background = {"H1": _series(0.0), "L1": _series(0.0)}
    polarizations = {"plus": _series(1.0), "cross": _series(-1.0)}
    projected = {"H1": _series(2.0), "L1": _series(3.0)}
    injected_h1 = _series(4.0)
    injected_l1 = _series(5.0)
    calls: list[str] = []

    mock_factory = MagicMock()
    mock_factory.generate.side_effect = lambda *args, **kwargs: calls.append("generate") or polarizations
    mock_factory_cls.return_value = mock_factory
    mock_project.side_effect = lambda *args, **kwargs: calls.append("project") or projected
    inject_results: Iterator[tuple[str, TimeSeries]] = iter(
        (
            ("inject:H1", injected_h1),
            ("inject:L1", injected_l1),
        )
    )

    def _inject_side_effect(*args, **kwargs):
        label, injected = next(inject_results)
        calls.append(label)
        return injected

    mock_inject.side_effect = _inject_side_effect

    result = inject_cbc_signal(
        params,
        detector_names,
        background,
        waveform_model="IMRPhenomD",
        sampling_frequency=4096.0,
        minimum_frequency=25.0,
        earth_rotation=False,
        interpolate_if_offset=False,
    )

    mock_factory_cls.assert_called_once_with()
    mock_factory.generate.assert_called_once_with(
        "IMRPhenomD",
        params,
        sampling_frequency=4096.0,
        minimum_frequency=25.0,
    )
    mock_project.assert_called_once_with(
        polarizations,
        detector_names,
        right_ascension=params["right_ascension"],
        declination=params["declination"],
        polarization_angle=params["polarization"],
        earth_rotation=False,
    )
    mock_inject.assert_has_calls(
        [
            call(background["H1"], projected["H1"], interpolate_if_offset=False),
            call(background["L1"], projected["L1"], interpolate_if_offset=False),
        ]
    )
    assert calls == ["generate", "project", "inject:H1", "inject:L1"]
    assert isinstance(result, DetectorStrainStack)
    assert result.detector_names == ("H1", "L1")
    assert result["H1"] is injected_h1
    assert result["L1"] is injected_l1


def test_inject_cbc_signal_requires_all_params():
    """Missing required CBC parameters should raise a descriptive ValueError."""
    params = _params()
    del params["mass2"]
    del params["polarization"]

    with pytest.raises(ValueError, match=r"mass2") as exc_info:
        inject_cbc_signal(
            params,
            ["H1"],
            {},
            waveform_model="IMRPhenomD",
            sampling_frequency=4096.0,
        )

    message = str(exc_info.value)
    assert "mass2" in message
    assert "polarization" in message
