---
title: Detector projection examples
description:
    Example workflows for projecting GW polarizations onto ground-based detector
    networks.
---

# Detector projection examples

After generating **plus** and **cross** polarizations (see
[Waveforms](waveform.md)), the next step in many pipelines is to compute the
**strain in each interferometer** using the detector **antenna patterns**
$F_{+}$, $F_{\times}$ and **geometric time delays** relative to the geocenter.
This is required for **injection into multi-detector data**, **end-to-end
simulations**, and cross-checks with **matched filtering** that use the same sky
location and polarization as the search.

This page is **examples only**. **Signatures, parameter semantics, return types,
and exceptions** for `project_polarizations_to_network` live exclusively in the
**[Projection API](../api/projection/)** (generated from docstrings).

<!-- markdownlint-disable -->

!!! tip "API reference"

    Use **API → Projection** for the full contract; the sections below are
    narrative + runnable snippets.

<!-- markdownlint-enable -->

## Example 1 — Waveform then H1 / L1 / V1 projection

```python
from gwmock_signal.waveform import WaveformFactory
from gwmock_signal.projection import project_polarizations_to_network

tc = 1_400_000_000.0
factory = WaveformFactory()
pol = factory.generate(
    "IMRPhenomD",
    {
        "tc": tc,
        "detector_frame_mass_1": 36.0,
        "detector_frame_mass_2": 29.0,
        "spin_1z": 0.0,
        "spin_2z": 0.0,
        "distance": 410.0,
        "inclination": 0.0,
        "coa_phase": 0.0,
    },
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
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

## Example 3 — Custom detectors (advanced)

For observatories not in the built-in LAL cache, pass
`gwmock_signal.detector.CustomDetector` instances (or load a YAML/JSON network
with [`Network.from_file`](../api/network/) or a bundled ET preset such as
`Network.from_preset("ET-Triangle-Sardinia")`) and use the same
`project_polarizations_to_network` call pattern as for `H1` / `L1` strings. See
the **[Projection API](../api/projection/)** for the supported `detector_names`
types.

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

- [User guide overview](index.md)
- [Waveforms](waveform.md) — produce `plus` / `cross`
- [Strain injection](strain-injection.md) — embed projected strain in a segment
- [Projection API](../api/projection/)
- [API overview](../api/index.md)
- [Documentation home](../index.md)
