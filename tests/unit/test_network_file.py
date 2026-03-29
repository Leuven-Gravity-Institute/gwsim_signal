"""Unit tests for Network.from_file and the YAML/JSON network config format."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gwmock_signal.detector import CustomDetector
from gwmock_signal.network import Network

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ET_TRIANGLE_YAML = Path(__file__).parents[2] / "examples" / "networks" / "et_triangle.yaml"

_MIXED_CONFIG = {
    "name": "mixed-net",
    "detectors": [
        {"name": "H1"},
        {
            "name": "MY-DET",
            "latitude_deg": 46.455,
            "longitude_deg": -119.408,
            "elevation_m": 142.554,
            "xarm_azimuth_deg": 125.9994,
            "yarm_azimuth_deg": 215.9994,
            "xarm_tilt_rad": 0.0,
            "yarm_tilt_rad": 0.0,
        },
    ],
}


@pytest.fixture
def mixed_yaml(tmp_path: Path) -> Path:
    """Write a mixed (alias + custom) network config to a temporary YAML file."""
    p = tmp_path / "mixed.yaml"
    p.write_text(yaml.dump(_MIXED_CONFIG))
    return p


@pytest.fixture
def mixed_json(tmp_path: Path) -> Path:
    """Write a mixed (alias + custom) network config to a temporary JSON file."""
    p = tmp_path / "mixed.json"
    p.write_text(json.dumps(_MIXED_CONFIG))
    return p


# ---------------------------------------------------------------------------
# et_triangle.yaml
# ---------------------------------------------------------------------------


def test_load_et_triangle_returns_three_detectors() -> None:
    """Test that the ET-triangle network has three detectors."""
    net = Network.from_file(_ET_TRIANGLE_YAML)
    assert net.name == "ET-triangle"
    assert len(net.detector_names) == 3
    assert net.detector_names == ("E1", "E2", "E3")


def test_load_et_triangle_passes_through_project_polarizations() -> None:
    """Network.from_file result can be passed to project_polarizations_to_network."""
    import numpy as np
    from gwpy.timeseries import TimeSeries

    from gwmock_signal.projection.network import project_polarizations_to_network

    net = Network.from_file(_ET_TRIANGLE_YAML)
    n = 512
    hp = TimeSeries(np.zeros(n), t0=0.0, sample_rate=512)
    hc = TimeSeries(np.zeros(n), t0=0.0, sample_rate=512)
    projected = project_polarizations_to_network(
        {"plus": hp, "cross": hc},
        net.detector_names,
        right_ascension=0.0,
        declination=0.0,
        polarization_angle=0.0,
    )
    assert set(projected.keys()) == {"E1", "E2", "E3"}


# ---------------------------------------------------------------------------
# Mixed config (YAML and JSON)
# ---------------------------------------------------------------------------


def test_load_mixed_yaml_alias_and_custom(mixed_yaml: Path) -> None:
    """Test that a mixed (alias + custom) network config can be loaded from a YAML file."""
    net = Network.from_file(mixed_yaml)
    assert net.name == "mixed-net"
    assert len(net.detector_names) == 2
    assert net.detector_names[0] == "H1"
    assert isinstance(net.detector_names[1], CustomDetector)
    assert net.detector_names[1].name == "MY-DET"


def test_load_mixed_json_alias_and_custom(mixed_json: Path) -> None:
    """Test that a mixed (alias + custom) network config can be loaded from a JSON file."""
    net = Network.from_file(mixed_json)
    assert len(net.detector_names) == 2
    assert net.detector_names[0] == "H1"
    assert isinstance(net.detector_names[1], CustomDetector)


# ---------------------------------------------------------------------------
# Missing required geometry field raises ValueError
# ---------------------------------------------------------------------------


def test_missing_latitude_raises_value_error(tmp_path: Path) -> None:
    """Test that a missing latitude field raises a ValueError."""
    config = {
        "name": "bad-net",
        "detectors": [
            {
                "name": "MY-DET",
                # latitude_deg intentionally omitted
                "longitude_deg": -119.408,
                "elevation_m": 142.554,
                "xarm_azimuth_deg": 125.9994,
                "yarm_azimuth_deg": 215.9994,
            }
        ],
    }
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.dump(config))
    with pytest.raises(ValueError, match="latitude_deg"):
        Network.from_file(p)


# ---------------------------------------------------------------------------
# Unsupported extension raises ValueError
# ---------------------------------------------------------------------------


def test_unsupported_extension_raises(tmp_path: Path) -> None:
    """Test that an unsupported file extension raises a ValueError."""
    p = tmp_path / "network.toml"
    p.write_text("[network]\nname = 'test'\n")
    with pytest.raises(ValueError, match=r"Unsupported file extension"):
        Network.from_file(p)


# ---------------------------------------------------------------------------
# Out-of-range geometry value raises ValueError
# ---------------------------------------------------------------------------


def test_out_of_range_latitude_raises_value_error(tmp_path: Path) -> None:
    """Test that an out-of-range latitude raises a ValueError."""
    config = {
        "name": "bad-range-net",
        "detectors": [
            {
                "name": "MY-DET",
                "latitude_deg": 200.0,  # > 90 deg → latitude_rad > pi/2
                "longitude_deg": -119.408,
                "elevation_m": 142.554,
                "xarm_azimuth_deg": 125.9994,
                "yarm_azimuth_deg": 215.9994,
            }
        ],
    }
    p = tmp_path / "out_of_range.yaml"
    p.write_text(yaml.dump(config))
    with pytest.raises(ValueError, match="latitude_rad"):
        Network.from_file(p)
