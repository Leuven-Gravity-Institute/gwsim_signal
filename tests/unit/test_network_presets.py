"""Tests for bundled detector geometry presets."""

from __future__ import annotations

from importlib.resources import files

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

from gwmock_signal.detector import CustomDetector
from gwmock_signal.network import Network
from gwmock_signal.projection.network import project_polarizations_to_network

_PRESET_NAMES = {
    "ET-Triangle-Sardinia": ("ET1_SARD", "ET2_SARD", "ET3_SARD"),
    "ET-Triangle-EMR": ("ET1_EMR", "ET2_EMR", "ET3_EMR"),
    "ET-2L-Aligned": ("ET1_2L_ALIGNED_SARD", "ET2_2L_ALIGNED_EMR"),
    "ET-2L-Misaligned": ("ET1_2L_MISALIGNED_SARD", "ET2_2L_MISALIGNED_EMR"),
}

_REFERENCE_TRIANGLE_SARDINIA = (
    {
        "name": "ET1_SARD",
        "latitude_deg": 40.5166666668747,
        "longitude_deg": 9.416666666888249,
        "elevation_m": 51.884,
        "xarm_azimuth_deg": 70.56739976526205,
        "yarm_azimuth_deg": 130.56739976543332,
        "xarm_tilt_rad": 2.64278457158e-10,
        "yarm_tilt_rad": 2.64278469515e-10,
    },
    {
        "name": "ET2_SARD",
        "latitude_deg": 40.60158246647564,
        "longitude_deg": 9.455973799867088,
        "elevation_m": 59.739,
        "xarm_azimuth_deg": 190.5418104128176,
        "yarm_azimuth_deg": 250.54184090066977,
        "xarm_tilt_rad": -0.000783862464265,
        "yarm_tilt_rad": -0.0015710370848,
    },
    {
        "name": "ET3_SARD",
        "latitude_deg": 40.585048823916765,
        "longitude_deg": 9.339849816516432,
        "elevation_m": 59.73,
        "xarm_azimuth_deg": 310.6173402960931,
        "yarm_azimuth_deg": 10.61737063612216,
        "xarm_tilt_rad": -0.00156913521227,
        "yarm_tilt_rad": -0.000781960584882,
    },
)


def _custom_detector(entry: dict[str, float | str]) -> CustomDetector:
    return CustomDetector(
        name=str(entry["name"]),
        latitude_rad=np.deg2rad(float(entry["latitude_deg"])),
        longitude_rad=np.deg2rad(float(entry["longitude_deg"])),
        elevation_m=float(entry["elevation_m"]),
        xarm_azimuth_rad=np.deg2rad(float(entry["xarm_azimuth_deg"])),
        yarm_azimuth_rad=np.deg2rad(float(entry["yarm_azimuth_deg"])),
        xarm_tilt_rad=float(entry["xarm_tilt_rad"]),
        yarm_tilt_rad=float(entry["yarm_tilt_rad"]),
    )


@pytest.mark.parametrize(("preset", "expected_names"), sorted(_PRESET_NAMES.items()))
def test_from_preset_returns_custom_detectors(preset: str, expected_names: tuple[str, ...]) -> None:
    """Bundled ET presets resolve to ordered CustomDetector objects."""
    net = Network.from_preset(preset)
    assert net.name == preset
    assert tuple(det.name for det in net.detector_names) == expected_names
    assert all(isinstance(det, CustomDetector) for det in net.detector_names)


def test_from_name_supports_file_backed_preset() -> None:
    """from_name resolves the bundled triangle Sardinia preset."""
    net = Network.from_name("ET-Triangle-Sardinia")
    assert net.name == "ET-Triangle-Sardinia"
    assert tuple(det.name for det in net.detector_names) == ("ET1_SARD", "ET2_SARD", "ET3_SARD")


def test_from_name_supports_compatibility_alias() -> None:
    """Roadmap compatibility aliases resolve to the bundled preset geometry."""
    canonical = Network.from_preset("ET-Triangle-Sardinia")
    alias = Network.from_name("ET-Sardinia")
    assert alias.name == canonical.name
    assert alias.detector_names == canonical.detector_names


def test_list_names_includes_bundled_presets() -> None:
    """Bundled preset names and compatibility aliases appear in list_names()."""
    names = Network.list_names()
    assert {
        "ET-Triangle-Sardinia",
        "ET-Triangle-EMR",
        "ET-2L-Aligned",
        "ET-2L-Misaligned",
        "ET-Sardinia",
        "ET-EMR",
    } <= set(names)


def test_from_preset_unknown_name_raises_value_error() -> None:
    """Unknown bundled preset names raise a helpful ValueError."""
    with pytest.raises(ValueError, match="Known presets"):
        Network.from_preset("not-a-preset")


def test_preset_yaml_is_packaged_as_resource() -> None:
    """Preset YAML files are accessible through importlib.resources."""
    resource = files("gwmock_signal.data.detectors").joinpath("et-triangle-sardinia.yaml")
    assert resource.is_file()


def test_triangle_sardinia_projection_matches_reference_geometry() -> None:
    """The packaged Sardinia triangle preset matches the current gwmock geometry."""
    n = 256
    fs = 2048.0
    t0 = 1126259462.4 - 0.0625
    times = np.arange(n) / fs
    taper = np.hanning(n)
    hp = TimeSeries(np.sin(2 * np.pi * 32.0 * times) * taper, t0=t0, sample_rate=fs)
    hc = TimeSeries(np.cos(2 * np.pi * 32.0 * times) * taper, t0=t0, sample_rate=fs)

    preset = Network.from_preset("ET-Triangle-Sardinia")
    reference = tuple(_custom_detector(entry) for entry in _REFERENCE_TRIANGLE_SARDINIA)
    kwargs = {
        "right_ascension": 1.375,
        "declination": -1.211,
        "polarization_angle": 0.0,
        "earth_rotation": False,
    }

    projected = project_polarizations_to_network({"plus": hp, "cross": hc}, preset.detector_names, **kwargs)
    expected = project_polarizations_to_network({"plus": hp, "cross": hc}, reference, **kwargs)

    assert tuple(projected) == ("ET1_SARD", "ET2_SARD", "ET3_SARD")
    for name in projected:
        np.testing.assert_allclose(projected[name].value, expected[name].value, rtol=0.0, atol=1e-12)
