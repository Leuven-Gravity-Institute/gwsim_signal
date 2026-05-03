---
title: Waveforms and backends
description:
    Waveform backends (LAL vs PyCBC), WaveformFactory registry, supported
    approximant names, and GWpy time-domain examples.
---

# Waveforms and backends

## Overview

This page explains how **time-domain** gravitational-wave polarizations $h_{+}$
and $h_{\times}$ are produced and how they surface as
[GWpy](https://gwpy.github.io)
[`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/)
values (`dict` keys `"plus"` and `"cross"`). Typical uses include **injection
studies**, **matched-filter sanity checks**, and **mock data challenges**.

The helpers are **stateless at call time** for a single generation: one call
returns one waveform pair. [`WaveformFactory`](../api/waveform/) adds a
**registry**: every built-in name from the active **waveform backend** is
pre-registered, and you may add more with `WaveformFactory.register_model`.

!!! tip "API reference"

    Exact signatures, types, and exceptions live under **[Waveform API](../api/waveform/)**;
    the sections below are narrative and copy-paste examples.

## Backend architecture

Waveform generation is split into three layers:

1. **`WaveformBackend`** (abstract interface; see
   [Waveform API](../api/waveform/)) Implementations expose
   `available_approximants()` and
   `generate_td_waveform(approximant, tc, sampling_frequency, minimum_frequency, **params)`.

2. **Concrete backends**
    - **`LALSimulationBackend`** (default) — uses **LALSimulation**
      (`SimInspiralChooseTDWaveform`). Shipped with the core dependency
      **`lalsuite`**; no optional extra is required. Parameter handling is
      **strict**: only documented mass, spin, distance, inclination, and
      coalescence-phase aliases are accepted; unknown keys raise `ValueError`.

    - **`PyCBCBackend`** (optional) — delegates to PyCBC’s time-domain waveform
      path via the internal `pycbc_waveform_wrapper`. Requires installing
      **`gwmock-signal[pycbc]`** (see [Installation](installation.md)). Extra
      parameters are forwarded to PyCBC like a direct `get_td_waveform` call.

3. **`WaveformFactory`** — on construction, takes
   `backend: WaveformBackend | None` (default `LALSimulationBackend()`),
   registers **one callable per** name returned by
   `backend.available_approximants()`, and dispatches
   `generate(waveform_model, parameters, **extra)` to the right callable.

[`CBCSimulator`](../api/simulator/) and [`inject_cbc_signal`](../api/pipeline/)
accept an optional `waveform_backend` and build a `WaveformFactory(backend=…)`
internally. The CLI `inject cbc` exposes **`--backend lal`** (default) or
**`--backend pycbc`**.

## Supported waveform model names

Built-in model names are **not hard-coded in this documentation**: they depend
on your installed **`lalsuite`** / **PyCBC** versions.

| Backend           | Where names come from                                                                                           | Install                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------ |
| **LAL** (default) | Every approximant for which LAL marks a **time-domain** implementation (`SimInspiralImplementedTDApproximants`) | Core (`lalsuite`)        |
| **PyCBC**         | `pycbc.waveform.td_approximants()`                                                                              | Optional extra `[pycbc]` |

**List every name in your environment**

```bash
python -c "from gwmock_signal.waveform import WaveformFactory; print('\n'.join(WaveformFactory().list_models()))"
```

With PyCBC installed:

```bash
python -c "from gwmock_signal.waveform import WaveformFactory, PyCBCBackend; print('\n'.join(WaveformFactory(backend=PyCBCBackend()).list_models()))"
```

The two lists **overlap in spirit** (many IMR models exist in both stacks) but
are **not identical** string-for-string. If a name fails, use the listing above
or check upstream tables (LALSimulation approximant documentation;
[PyCBC waveforms](https://pycbc.org/pycbc/latest/html/waveform.html)).

**Illustrative examples** (always confirm with `list_models()` on your machine):
`IMRPhenomD`, `IMRPhenomPv2`, `SEOBNRv4`, `SEOBNRv4PHM`, `TaylorF2`,
`SpinTaylorT4`, …

## Examples

### Example 1 — `WaveformFactory` with default LAL backend (BBH, IMRPhenomD)

```python
from gwmock_signal.waveform import WaveformFactory

factory = WaveformFactory()
pol = factory.generate(
    "IMRPhenomD",
    {
        "tc": 1_400_000_000.0,
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
hp, hx = pol["plus"], pol["cross"]
print(hp.t0, hp.duration)
```

### Example 2 — Explicit PyCBC backend (requires optional install)

```python
from gwmock_signal.waveform import PyCBCBackend, WaveformFactory

factory = WaveformFactory(backend=PyCBCBackend())
params = {
    "tc": 1_400_000_000.0,
    "mass1": 40.0,
    "mass2": 30.0,
    "spin1z": 0.5,
    "spin2z": -0.3,
    "distance": 400.0,
    "inclination": 0.0,
    "coa_phase": 0.0,
}
pol = factory.generate(
    "IMRPhenomD",
    params,
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
)
```

### Example 3 — Direct PyCBC wrapper (lazy import)

`pycbc_waveform_wrapper` is still available for **direct** PyCBC calls without
going through `WaveformFactory`. Importing it triggers a PyCBC import; install
**`gwmock-signal[pycbc]`** first.

```python
from gwmock_signal.waveform import pycbc_waveform_wrapper

pol = pycbc_waveform_wrapper(
    tc=1_400_000_000.0,
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
    waveform_model="IMRPhenomD",
    mass1=36.0,
    mass2=29.0,
    spin1z=0.0,
    spin2z=0.0,
    distance=410.0,
    inclination=0.0,
    coa_phase=0.0,
)
hp, hx = pol["plus"], pol["cross"]
```

### Example 4 — Register your own waveform model

Use this when you have a custom generator (e.g. **numerical relativity** or a
**ROM**) and want the same `{"plus", "cross"}` GWpy contract as the built-in
backends. The callable does **not** have to call PyCBC or LAL.

```python
import numpy as np
from astropy import units as u
from gwpy.timeseries import TimeSeries

from gwmock_signal.waveform import WaveformFactory


def toy_gaussian_sine_burst(
    *,
    waveform_model: str,
    tc: float,
    sampling_frequency: float,
    minimum_frequency: float,
    **kwargs,
) -> dict[str, TimeSeries]:
    width_s = float(kwargs.get("width", 0.1))
    f_hz = float(kwargs.get("f0", 150.0))
    dt = 1.0 / sampling_frequency
    n_half = max(8, int(width_s * sampling_frequency))
    t = (np.arange(-n_half, n_half + 1) * dt) + tc
    env = np.exp(-0.5 * ((t - tc) / (width_s / 3)) ** 2)
    phase = 2 * np.pi * f_hz * (t - tc)
    hp = env * np.cos(phase)
    hc = env * np.sin(phase)
    return {
        "plus": TimeSeries(hp, t0=float(t[0]), dt=dt, unit=u.dimensionless_unscaled),
        "cross": TimeSeries(hc, t0=float(t[0]), dt=dt, unit=u.dimensionless_unscaled),
    }


factory = WaveformFactory()
factory.register_model("toy_burst", toy_gaussian_sine_burst)
out = factory.generate(
    "toy_burst",
    {"tc": 1_400_000_000.0, "f0": 120.0, "width": 0.05},
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
)
```

### Example 5 — Inspect registered names

```python
from gwmock_signal.waveform import WaveformFactory

factory = WaveformFactory()
names = factory.list_models()
print(len(names), names[:5])
```

## Tips and pitfalls

- Unknown model names raise `ValueError`; use `list_models()` after install.
- **LAL** surfaces invalid physics or unsupported parameter combinations as
  LAL/LALSimulation errors; **PyCBC** behaves like PyCBC’s `get_td_waveform`.
- Series are **offset by `tc`** in the sense documented for each backend; they
  are **not** cropped to a science segment — windowing is downstream.
- **Reuse one `WaveformFactory`** in hot loops: construction calls
  `available_approximants()` once and can be slow on cold import.

## Scientific notes

- Default **LAL** path follows `SimInspiralChooseTDWaveform` conventions; see
  LIGO Algorithm Library / LALSimulation documentation for parameter meanings.
- **PyCBC** wrapper path follows PyCBC’s `get_td_waveform` keyword conventions.
- GWpy `TimeSeries` outputs interoperate with typical **GWpy**, **frame**, and
  **Bilby** workflows.

## See also

- [User guide overview](index.md)
- [Installation](installation.md) — core vs `[pycbc]` optional extra
- [Command-line interface](cli.md) — `inject cbc --backend` / `--approximant`
- [Detector projection](detector-projection.md)
- [Waveform API reference](../api/waveform/)
- [Documentation home](../index.md)
