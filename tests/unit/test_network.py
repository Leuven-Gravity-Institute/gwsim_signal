"""Unit tests for the Network named-catalog class."""

from __future__ import annotations

import pytest

from gwmock_signal.network import _CATALOG, Network


class TestNetworkFromName:
    """Tests for Network.from_name."""

    @pytest.mark.parametrize("alias", list(_CATALOG.keys()))
    def test_from_name_round_trip(self, alias: str) -> None:
        """Test the round-trip from name to network and back."""
        net = Network.from_name(alias)
        assert net.name == alias
        assert net.detector_names == _CATALOG[alias]

    def test_h1l1v1_detector_names(self) -> None:
        """Test the detector names for the H1L1V1 network."""
        net = Network.from_name("H1L1V1")
        assert net.detector_names == ("H1", "L1", "V1")

    def test_unknown_alias_raises_value_error(self) -> None:
        """Test that an unknown alias raises a ValueError."""
        with pytest.raises(ValueError, match="Unknown network 'unknown'"):
            Network.from_name("unknown")

    def test_unknown_alias_lists_known_names(self) -> None:
        """Test that an unknown alias lists the known networks."""
        with pytest.raises(ValueError, match="Known networks:"):
            Network.from_name("not-a-network")

    def test_et_triangle_has_three_detectors(self) -> None:
        """Test that the ET-triangle network has three detectors."""
        net = Network.from_name("ET-triangle")
        assert len(net.detector_names) == 3

    def test_et_triangle_detector_names(self) -> None:
        """Test the detector names for the ET-triangle network."""
        net = Network.from_name("ET-triangle")
        assert net.detector_names == ("E1", "E2", "E3")

    def test_hlvk_includes_kagra(self) -> None:
        """Test that the HLVK network includes the K1 detector."""
        net = Network.from_name("HLVK")
        assert "K1" in net.detector_names


class TestNetworkListNames:
    """Tests for Network.list_names."""

    def test_returns_sorted_list(self) -> None:
        """Test that the list of names is sorted."""
        names = Network.list_names()
        assert names == sorted(names)

    def test_contains_all_expected_aliases(self) -> None:
        """Test that the list of names contains all expected aliases."""
        names = Network.list_names()
        expected = {"H1L1", "H1L1V1", "HLVK", "ET-triangle", "ET-L"}
        assert expected.issubset(set(names))

    def test_returns_at_least_five_aliases(self) -> None:
        """Test that the list of names contains at least five aliases."""
        assert len(Network.list_names()) >= 5


class TestNetworkProjection:
    """Integration-style: ET-triangle codes are valid PyCBC detector codes."""

    def test_et_triangle_passes_pycbc_detector_construction(self) -> None:
        """Test that the ET-triangle network passes PyCBC detector construction."""
        from pycbc.detector import Detector

        net = Network.from_name("ET-triangle")
        for code in net.detector_names:
            Detector(code)  # must not raise

    def test_et_l_passes_pycbc_detector_construction(self) -> None:
        """Test that the ET-L network passes PyCBC detector construction."""
        from pycbc.detector import Detector

        net = Network.from_name("ET-L")
        for code in net.detector_names:
            Detector(code)  # must not raise

    def test_et_triangle_passes_through_project_polarizations_to_network(self) -> None:
        """ET-triangle codes produce valid strain output from the projection function."""
        import numpy as np
        from gwpy.timeseries import TimeSeries

        from gwmock_signal.projection.network import project_polarizations_to_network

        n, fs, t0 = 128, 4096.0, 1000000000.0
        t = np.arange(n) / fs
        hp = TimeSeries(np.sin(2 * np.pi * 10.0 * t), t0=t0, sample_rate=fs)
        hc = TimeSeries(np.cos(2 * np.pi * 10.0 * t), t0=t0, sample_rate=fs)

        net = Network.from_name("ET-triangle")
        result = project_polarizations_to_network(
            {"plus": hp, "cross": hc},
            list(net.detector_names),
            right_ascension=0.5,
            declination=0.3,
            polarization_angle=0.1,
            earth_rotation=False,
        )
        assert set(result.keys()) == set(net.detector_names)
        for code in net.detector_names:
            assert len(result[code]) == n


class TestNetworkImport:
    """Network is importable from the top-level package."""

    def test_import_from_package(self) -> None:
        """Test the import from package."""
        from gwmock_signal import Network as NetworkFromPkg

        assert NetworkFromPkg is Network
