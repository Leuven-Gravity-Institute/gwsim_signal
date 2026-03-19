---
title: Waveform generation
description:
    Examples for time-domain gravitational-wave polarizations with PyCBC and
    GWpy.
---

## Waveform generation

Generate **time-domain gravitational-wave polarizations** $h_{+}$ and
$h_{\times}$ for compact-binary and other sources supported by
[PyCBC](https://pycbc.org/) time-domain approximants, and return them as
[GWpy](https://gwpy.github.io)
[`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/)
objects. Typical uses include **injection studies**, **matched-filter sanity
checks**, and **mock data challenges** (e.g. O4/O5-style pipelines).

The helpers are **stateless at call time**: one invocation produces one
waveform. `WaveformFactory` adds a **registry** over PyCBC’s time-domain
approximants (plus any models you register yourself).

<!-- markdownlint-disable -->

!!! tip "Full API reference"

    For signatures, arguments, return types, and exceptions, see the
    **[Waveform API](../api/waveform/)** (generated from docstrings).

<!-- markdownlint-enable -->

### Examples

#### Example 1 — Direct wrapper call (BBH, IMRPhenomD)

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
)
hp, hx = pol["plus"], pol["cross"]
print(hp.t0, hp.duration)  # GWpy TimeSeries: start time includes tc shift
```

#### Example 2 — Factory with parameter dict (aligned spins)

```python
from gwmock_signal.waveform import WaveformFactory

factory = WaveformFactory()
params = {
    "tc": 1_400_000_000.0,
    "mass1": 40.0,
    "mass2": 30.0,
    "spin1z": 0.5,
    "spin2z": -0.3,
}
pol = factory.generate(
    "IMRPhenomD",
    params,
    sampling_frequency=4096.0,
    minimum_frequency=20.0,
)
```

#### Example 3 — Register your own waveform model (not PyCBC)

Use this when you already have a waveform generator—e.g. **numerical
relativity**, a **custom reduced-order model**, or a **research prototype**—and
only need it to plug into the same `dict["plus"/"cross"]` + GWpy contract as the
built-in PyCBC path.

The callable **does not** have to call `pycbc_waveform_wrapper`. It must accept
the merged keyword arguments (including `waveform_model`, `tc`,
`sampling_frequency`, `minimum_frequency`) and return `{"plus", "cross"}` as
GWpy `TimeSeries`. You may ignore arguments your model does not use (here
`waveform_model` and `minimum_frequency` are unused).

Below is a **toy Gaussian-windowed sinusoid**—illustrative only, not a physical
CBC waveform—so the example stays short and shows clearly that **you own the
numerics**:

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
    width_s = float(kwargs.get("width", 0.1))  # Gaussian width [s]
    f_hz = float(kwargs.get("f0", 150.0))  # carrier frequency [Hz]
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

#### Example 4 — List available built-in approximants

```python
from gwmock_signal.waveform import WaveformFactory

factory = WaveformFactory()
names = factory.list_models()
print(len(names), names[:5])
```

### Tips and pitfalls

- Unknown model names raise `ValueError`; use `list_models()` to inspect what is
  registered.
- Invalid masses, spins, or `f_lower` for an approximant usually surface as
  PyCBC/LAL errors—validate inputs for production runs.
- The PyCBC wrapper **offsets** series by `tc` but does **not** crop to a
  science segment; windowing is up to downstream code.
- **Reuse one `WaveformFactory`** in hot loops: construction walks all PyCBC TD
  approximants once and can be slow on cold import.

### Scientific notes

- Parameter conventions follow PyCBC’s `get_td_waveform`; see the
  [PyCBC waveform documentation](https://pycbc.org/pycbc/latest/html/waveform.html).
- GWpy `TimeSeries` outputs work with typical **GWpy**, **frame writing**, and
  **Bilby** workflows.

### See also

- [Waveform API reference](../api/waveform/) — auto-generated from docstrings
- [Documentation home](../index.md)
