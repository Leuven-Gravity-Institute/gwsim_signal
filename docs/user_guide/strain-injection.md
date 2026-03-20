---
title: Strain injection
description:
    Examples for adding simulated strain into a target GWpy time series segment.
---

After producing detector strain (e.g. with [Waveform generation](waveform.md)
and [Detector strain projection](detector-projection.md)), you often need to
**embed that strain into a longer segment** aligned to a science run—typically
starting from **zeros** or from a **noise** realization (noise generation can
live in a separate package). This step is central to **software injections**,
**end-to-end mock challenges**, and **pipeline validation**.

This guide describes typical usage. **Full signatures and exceptions** are in
**[API → Injection](../api/injection/)** (generated from docstrings).

<!-- markdownlint-disable -->

!!! tip "API reference"

    See **API → Injection** for `inject_strain` and `inject_strains_sequential`.

<!-- markdownlint-enable -->

## Public API

The package provides:

```python
from gwpy.timeseries import TimeSeries


def inject_strain(
    target: TimeSeries,
    injection: TimeSeries,
    *,
    interpolate_if_offset: bool = True,
) -> TimeSeries:
    """Add ``injection`` into ``target`` in-place on the time grid (new series returned).

    Both arguments must be compatible GWpy time series (same sample spacing and
    compatible epochs). The injection is **added** to the target samples where
    times overlap; out-of-range parts of the injection may be cropped. If the
    injection start time does not fall on an exact sample boundary of the
    target, optional cubic interpolation can align it (see pitfalls).
    """
```

Optional helper (same module) for clarity:

```python
def inject_strains_sequential(
    target: TimeSeries,
    injections: list[TimeSeries],
    *,
    interpolate_if_offset: bool = True,
) -> TimeSeries:
    """Apply ``inject_strain`` in order, returning the final series."""
```

Behavior matches the usual GW analysis expectation: **h_total = h_target +
h_inj** on overlapping samples.

## Example 1 — Inject one CBC into a zero-filled segment

```python
import numpy as np
from gwpy.timeseries import TimeSeries

from gwmock_signal.waveform import pycbc_waveform_wrapper
from gwmock_signal.projection import project_polarizations_to_network
from gwmock_signal.injection import inject_strain

fs = 4096.0
duration = 8.0
t0 = 1_400_000_000.0
n = int(duration * fs)

target = TimeSeries(np.zeros(n), t0=t0, sample_rate=fs)

pol = pycbc_waveform_wrapper(
    tc=t0 + 2.0,
    sampling_frequency=fs,
    minimum_frequency=20.0,
    waveform_model="IMRPhenomD",
    mass1=30.0,
    mass2=25.0,
    spin1z=0.0,
    spin2z=0.0,
)
strains = project_polarizations_to_network(
    pol,
    ["H1"],
    right_ascension=1.0,
    declination=0.5,
    polarization_angle=0.2,
    earth_rotation=False,
)
h1 = strains["H1"]

out = inject_strain(target, h1)
assert out is not target  # immutability: new object (recommended contract)
```

## Example 2 — Multiple injections in time order

```python
from gwmock_signal.injection import inject_strains_sequential

# target: long segment; inj1, inj2: non-overlapping or overlapping GWpy series
out = inject_strains_sequential(target, [inj1, inj2], interpolate_if_offset=True)
```

## Example 3 — Disable interpolation (strict grid)

If you know injections are **exactly aligned** to the target grid and want to
avoid cubic resampling at boundaries:

```python
out = inject_strain(target, h1, interpolate_if_offset=False)
```

## Pitfalls

- **Units:** Target and injection should use compatible strain units (typically
  dimensionless); mixed units should raise a clear error.
- **No overlap:** If the injection lies entirely outside the target span, the
  implementation should return the target unchanged (or document copy
  semantics).
- **Interpolation:** Cubic interpolation can ring at edges; prefer aligned
  waveforms from the same `sampling_frequency` and GPS grid when possible.
- **Performance:** Large segments are memory-bound; avoid unnecessary copies if
  the API documents mutability (default recommendation: return a **new**
  `TimeSeries`).

## Scientific notes

- Conventions follow common **GWpy** / **LIGO** injection practice: coherent
  addition of strain in the time domain on a fixed grid.
- For **colored noise** backgrounds, build `target` as noise first, then inject;
  stationary Gaussian noise can be added in a separate noise-focused package.

## See also

- [Waveform generation](waveform.md)
- [Detector strain projection](detector-projection.md)
- [Injection API](../api/injection/)
- [API overview](../api/index.md)
- [Documentation home](../index.md)
