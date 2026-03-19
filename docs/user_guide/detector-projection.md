---
title: Detector strain projection
description:
    Examples for projecting GW polarizations onto ground-based detector
    networks.
---

After generating **plus** and **cross** polarizations (see
[Waveform generation](waveform.md)), the next step in many pipelines is to
compute the **strain in each interferometer** using the detector **antenna
patterns** \(F*+, F*\times\) and **geometric time delays** relative to the
geocenter. This is required for **injection into multi-detector data**,
**end-to-end simulations**, and cross-checks with **matched filtering** that use
the same sky location and polarization as the search.

This guide shows typical usage of the projection API. **Exact signatures, types,
and exceptions** are documented in the **[Projection API](../api/projection/)**
(generated from docstrings).

<!-- markdownlint-disable -->

!!! tip "API reference"

    See **API → Projection** for `project_polarizations_to_network` and full parameter
    documentation.

<!-- markdownlint-enable -->

## Public API

The package exposes:

```python
from collections.abc import Mapping, Sequence

from gwpy.timeseries import TimeSeries


def project_polarizations_to_network(
    polarizations: Mapping[str, TimeSeries],
    detector_names: Sequence[str],
    *,
    right_ascension: float,
    declination: float,
    polarization_angle: float,
    earth_rotation: bool = True,
) -> dict[str, TimeSeries]:
    """Project h_+, h_× onto named detectors; return one GWpy TimeSeries per detector."""
```

- **`polarizations`**: must include keys `plus` and `cross`, each a GWpy
  [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/)
  on a **common** time grid (same length, sample rate, and epoch up to the
  projection shifts).
- **`detector_names`**: IFO codes understood by PyCBC/LAL, e.g. `H1`, `L1`, `V1`
  (see [PyCBC detector](https://pycbc.org/pycbc/latest/html/detector.html)
  docs).
- **Sky and orientation** (all in **radians**): right ascension \(\alpha\),
  declination \(\delta\), polarization angle \(\psi\) (tensor modes).
- **`earth_rotation`**: if `True`, evaluate antenna patterns over time (and
  delays) consistently with the time series; if `False`, use a single reference
  time (faster, approximate for short waveforms).

**Return value:** mapping from detector name to **projected strain** as a GWpy
`TimeSeries` (same sample rate as input; time ordering follows the
implementation of delays and interpolation).

## Example 1 — Waveform then H1 / L1 / V1 projection

```python
from gwmock_signal.waveform import pycbc_waveform_wrapper
from gwmock_signal.projection import project_polarizations_to_network

tc = 1_400_000_000.0
pol = pycbc_waveform_wrapper(
    tc=tc,
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
    waveform_model="IMRPhenomD",
    mass1=36.0,
    mass2=29.0,
    spin1z=0.0,
    spin2z=0.0,
)

# Sky location and polarization (radians)
ra = 1.23
dec = -0.45
psi = 0.78

strains = project_polarizations_to_network(
    pol,
    ["H1", "L1", "V1"],
    right_ascension=ra,
    declination=dec,
    polarization_angle=psi,
    earth_rotation=True,
)
for name, h in strains.items():
    print(name, h.shape, h.t0)
```

## Example 2 — Short segment, fixed antenna pattern

For very short waveforms where Earth rotation over the segment is negligible:

```python
strains = project_polarizations_to_network(
    pol,
    ["H1", "L1"],
    right_ascension=0.5,
    declination=0.3,
    polarization_angle=1.0,
    earth_rotation=False,
)
```

## Example 3 — Custom detector list from configuration (advanced)

Some analyses use custom **interferometer geometry** from `.interferometer`
config files (e.g. Einstein Telescope configurations). The implementation may
accept optional paths or detector objects in addition to built-in names; see the
API reference when available.

```python
# Illustrative only — exact keyword names TBD in API reference.
# strains = project_polarizations_to_network(
#     pol,
#     detector_names=["E1_Triangle_Sardinia"],
#     ...
# )
```

## Parameter and units checklist

| Quantity                                               | Unit       | Notes                                                   |
| ------------------------------------------------------ | ---------- | ------------------------------------------------------- |
| `right_ascension`, `declination`, `polarization_angle` | radians    | Same convention as PyCBC `Detector.antenna_pattern`.    |
| GW polarizations                                       | strain     | Dimensionless \(h\); output strains are dimensionless.  |
| Time bases                                             | GPS / GWpy | Input `plus`/`cross` must share a compatible time axis. |

## Edge cases and pitfalls

- **Misaligned arrays:** If `plus` and `cross` differ in length, sample rate, or
  epoch, the implementation should raise a clear error before projecting.
- **Unknown detector:** Invalid IFO names should fail with an actionable message
  listing supported or loaded detectors.
- **Unconfigured custom sites:** Custom interferometer configs must be loaded
  successfully; otherwise projection is undefined.
- **Numerics:** Cubic interpolation (if used) can ring at edges; for production
  injections, prefer waveforms that are windowed or long enough that edge
  effects are negligible.

## Scientific notes

- Antenna patterns and delays follow **PyCBC/LAL** conventions, consistent with
  many **Bilby** and **PyCBC** analyses.
- For long signals or high precision, keep **`earth_rotation=True`** unless you
  have verified the approximation.

## See also

- [Waveform generation](waveform.md) — produce `plus` / `cross`
- [Projection API](../api/projection/) — `project_polarizations_to_network`
- [API overview](../api/index.md)
- [Documentation home](../index.md)
