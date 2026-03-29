"""CLI smoke tests for the `gwmock-signal inject cbc` command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gwmock_signal.cli.main import app

runner = CliRunner()

# ---------------------------------------------------------------------------
# Minimal params — light masses so the waveform is short even at low f_min
# ---------------------------------------------------------------------------

_PARAMS: dict = {
    "mass1": 10.0,
    "mass2": 10.0,
    "spin1z": 0.0,
    "spin2z": 0.0,
    "tc": 1126259462.4,
    "distance": 410.0,
    "right_ascension": 1.375,
    "declination": -1.211,
    "polarization": 2.659,
    "inclination": 2.5,
    "coa_phase": 0.0,
}

# Short duration + low sample rate keeps the test fast
_DURATION = "0.5"
_SAMPLE_RATE = "256"
_F_MIN = "50.0"


@pytest.fixture
def params_file(tmp_path: Path) -> Path:
    """Write minimal CBC params to a temporary JSON file."""
    p = tmp_path / "params.json"
    p.write_text(json.dumps(_PARAMS))
    return p


def test_inject_cbc_stdout_summary(params_file: Path) -> None:
    """Inject cbc without --output prints a per-detector summary."""
    result = runner.invoke(
        app,
        [
            "inject",
            "cbc",
            "--params",
            str(params_file),
            "--network",
            "H1L1",
            "--duration",
            _DURATION,
            "--sample-rate",
            _SAMPLE_RATE,
            "--f-min",
            _F_MIN,
        ],
    )
    assert result.exit_code == 0, result.output
    assert "H1" in result.output
    assert "L1" in result.output
    assert "rms=" in result.output


def test_inject_cbc_hdf5_output(params_file: Path, tmp_path: Path) -> None:
    """Inject cbc with --output writes a readable HDF5 file."""
    from gwpy.timeseries import TimeSeries

    out_path = str(tmp_path / "output.hdf5")

    result = runner.invoke(
        app,
        [
            "inject",
            "cbc",
            "--params",
            str(params_file),
            "--network",
            "H1L1",
            "--output",
            out_path,
            "--duration",
            _DURATION,
            "--sample-rate",
            _SAMPLE_RATE,
            "--f-min",
            _F_MIN,
        ],
    )
    assert result.exit_code == 0, result.output

    ts = TimeSeries.read(out_path, format="hdf5", path="H1")
    assert len(ts) > 0


def test_inject_cbc_bad_params_file(tmp_path: Path) -> None:
    """Inject cbc raises BadParameter for a missing params file."""
    result = runner.invoke(
        app,
        [
            "inject",
            "cbc",
            "--params",
            str(tmp_path / "nonexistent.json"),
            "--network",
            "H1L1",
        ],
    )
    assert result.exit_code != 0


def test_inject_cbc_invalid_json(tmp_path: Path) -> None:
    """Inject cbc raises BadParameter for invalid JSON."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    result = runner.invoke(
        app,
        [
            "inject",
            "cbc",
            "--params",
            str(bad),
            "--network",
            "H1L1",
        ],
    )
    assert result.exit_code != 0


def test_inject_cbc_unknown_network(params_file: Path) -> None:
    """Inject cbc raises BadParameter for an unknown network name."""
    result = runner.invoke(
        app,
        [
            "inject",
            "cbc",
            "--params",
            str(params_file),
            "--network",
            "UNKNOWN",
        ],
    )
    assert result.exit_code != 0


def test_inject_cbc_help() -> None:
    """`inject cbc --help` displays all expected options."""
    result = runner.invoke(app, ["inject", "cbc", "--help"])
    assert result.exit_code == 0
    for opt in [
        "--params",
        "--network",
        "--output",
        "--sample-rate",
        "--f-min",
        "--duration",
        "--approximant",
        "--seed",
    ]:
        assert opt in result.output, f"Missing option {opt!r} in --help output"
