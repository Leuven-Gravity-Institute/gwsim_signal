"""End-to-end integration tests for the CBC injection pipeline."""

from __future__ import annotations

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

pycbc = pytest.importorskip("pycbc")

from pycbc.detector import Detector  # noqa: E402
from pycbc.filter import sigma as pycbc_sigma  # noqa: E402
from pycbc.psd import from_string as psd_from_string  # noqa: E402
from pycbc.types import TimeSeries as PyCBCTimeSeries  # noqa: E402
from scipy.signal import correlate  # noqa: E402

from gwmock_signal.network import Network  # noqa: E402
from gwmock_signal.pipeline import inject_cbc_signal  # noqa: E402

# ---------------------------------------------------------------------------
# GW150914-like injection parameters
# ---------------------------------------------------------------------------

FS = 4096.0  # Hz
FMIN = 20.0  # Hz
DURATION = 8.0  # seconds
POST_MERGER_PADDING = 0.05  # 50 ms — accommodates time_delay_from_earth_center offsets

PARAMS: dict = {
    "mass1": 36.0,
    "mass2": 29.0,
    "spin1z": 0.0,
    "spin2z": 0.0,
    "distance": 410.0,
    "right_ascension": 1.375,
    "declination": -1.211,
    "polarization": 2.659,
    "inclination": 2.5,
    "coa_phase": 0.0,
    "tc": 1126259462.4,
}

RA = PARAMS["right_ascension"]
DEC = PARAMS["declination"]
TC = PARAMS["tc"]

# Reference matched-filter SNR for the H1 channel against the aLIGO design
# sensitivity PSD (aLIGODesignSensitivityP1200087).
_REFERENCE_SNR = 4.884168e01


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_background(detector_names: tuple[str, ...]) -> dict[str, TimeSeries]:
    """Return a zero-noise background for each detector in the tuple.

    Extends 50 ms past TC so that the signal peak (which arrives at TC +
    time_delay_from_earth_center, up to ~21 ms) is not truncated.
    """
    n_samples = int((DURATION + POST_MERGER_PADDING) * FS)
    t0 = TC - DURATION
    return {name: TimeSeries(np.zeros(n_samples), t0=t0, sample_rate=FS) for name in detector_names}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cbc_h1l1v1_returns_stack():
    """inject_cbc_signal on H1L1V1 returns a 3-channel stack with non-zero RMS."""
    detectors = Network.from_name("H1L1V1").detector_names
    background = _make_background(detectors)

    stack = inject_cbc_signal(
        "IMRPhenomD",
        PARAMS,
        detectors,
        background,
        sampling_frequency=FS,
        minimum_frequency=FMIN,
    )

    assert len(stack) == 3
    for name in detectors:
        rms = float(np.sqrt(np.mean(stack[name].value ** 2)))
        assert rms > 0.0, f"RMS of {name} channel is zero"


@pytest.mark.integration
def test_h1l1_time_delay_consistent():
    """Cross-correlation lag between H1 and L1 agrees with analytic time delay."""
    detectors = ("H1", "L1")
    background = _make_background(detectors)

    stack = inject_cbc_signal(
        "IMRPhenomD",
        PARAMS,
        detectors,
        background,
        sampling_frequency=FS,
        minimum_frequency=FMIN,
    )

    h1_values = stack["H1"].value
    l1_values = stack["L1"].value

    # Use the amplitude envelope (Hilbert) to remove phase-mixing between h+/hx
    # polarizations that would otherwise shift the raw CC peak.
    from scipy.signal import hilbert

    h1_env = np.abs(hilbert(h1_values))
    l1_env = np.abs(hilbert(l1_values))

    cc = correlate(h1_env, l1_env, mode="full")
    n = len(h1_values)
    lags = np.arange(-(n - 1), n)
    # Restrict search to +-60 samples (~14.6 ms) -- safely bounds the H1-L1 delay
    mid = n - 1
    search = slice(mid - 60, mid + 61)
    peak_lag_seconds = float(lags[search][np.argmax(cc[search])]) / FS

    expected_delay = Detector("H1").time_delay_from_detector(Detector("L1"), RA, DEC, TC)

    assert abs(peak_lag_seconds - expected_delay) <= 1.0 / FS


@pytest.mark.integration
def test_snr_regression():
    """Matched-filter SNR on H1 channel matches hard-coded reference within 1%."""
    detectors = Network.from_name("H1L1V1").detector_names
    background = _make_background(detectors)

    stack = inject_cbc_signal(
        "IMRPhenomD",
        PARAMS,
        detectors,
        background,
        sampling_frequency=FS,
        minimum_frequency=FMIN,
    )

    h1_ts = stack["H1"]
    h1_pycbc = PyCBCTimeSeries(
        h1_ts.value.astype(float),
        delta_t=1.0 / FS,
        epoch=float(h1_ts.t0.value),
    )
    h1_fs = h1_pycbc.to_frequencyseries()
    psd = psd_from_string("aLIGODesignSensitivityP1200087", len(h1_fs), h1_fs.delta_f, FMIN)
    snr_computed = float(pycbc_sigma(h1_fs, psd=psd, low_frequency_cutoff=FMIN))

    assert _REFERENCE_SNR > 0.0, f"_REFERENCE_SNR is not set. Update it to {snr_computed:.6e} in this file."
    assert abs(snr_computed - _REFERENCE_SNR) / _REFERENCE_SNR < 0.01


@pytest.mark.integration
def test_cbc_et_triangle_returns_stack():
    """inject_cbc_signal on ET-triangle returns a 3-channel stack."""
    network = Network.from_name("ET-triangle")
    background = _make_background(network.detector_names)

    stack = inject_cbc_signal(
        "IMRPhenomD",
        PARAMS,
        network.detector_names,
        background,
        sampling_frequency=FS,
        minimum_frequency=FMIN,
    )

    assert len(stack) == 3
