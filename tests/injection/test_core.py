"""Tests for strain injection."""

from __future__ import annotations

import numpy as np
import pytest
from gwpy.timeseries import TimeSeries

from gwmock_signal.injection import inject_strain, inject_strains_sequential


def _segment(n: int = 32, fs: float = 128.0, t0: float = 100.0) -> TimeSeries:
    return TimeSeries(np.zeros(n), t0=t0, sample_rate=fs)


def test_inject_returns_new_object():
    """Result is never the same instance as target (contract)."""
    target = _segment()
    inj = TimeSeries(np.ones(8), t0=target.t0.value, sample_rate=target.sample_rate)
    out = inject_strain(target, inj)
    assert out is not target


def test_inject_aligned_adds_in_window():
    """Aligned injection adds samples where grids overlap."""
    target = _segment(n=16, fs=4.0, t0=0.0)
    inj = TimeSeries(np.full(4, 2.0), t0=1.0, sample_rate=4.0)
    out = inject_strain(target, inj)
    assert np.allclose(out.value[4:8], 2.0)
    assert np.allclose(out.value[:4], 0.0)
    assert np.allclose(out.value[8:], 0.0)


def test_no_overlap_returns_copy():
    """Injection entirely after target returns unchanged values on a new object."""
    target = _segment(n=8, fs=4.0, t0=0.0)
    inj = TimeSeries(np.ones(4), t0=10.0, sample_rate=4.0)
    out = inject_strain(target, inj)
    assert out is not target
    assert np.allclose(out.value, target.value)


def test_sequential_empty_is_copy():
    """Empty injection list yields a copy of target."""
    target = _segment()
    out = inject_strains_sequential(target, [])
    assert out is not target
    assert np.array_equal(out.value, target.value)


def test_sequential_two():
    """Two aligned injections accumulate on the segment."""
    target = _segment(n=16, fs=4.0, t0=0.0)
    a = TimeSeries(np.ones(2), t0=0.0, sample_rate=4.0)
    b = TimeSeries(np.full(2, 2.0), t0=0.5, sample_rate=4.0)
    out = inject_strains_sequential(target, [a, b], interpolate_if_offset=True)
    assert out.value[0] == pytest.approx(1.0)
    assert out.value[2] == pytest.approx(2.0)


def test_incompatible_raises():
    """Mismatched sample rates should fail GWpy compatibility."""
    target = _segment(fs=128.0)
    inj = TimeSeries(np.ones(4), t0=target.t0.value, sample_rate=256.0)
    with pytest.raises(ValueError, match="sample sizes"):
        inject_strain(target, inj)
