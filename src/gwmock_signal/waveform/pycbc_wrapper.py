"""PyCBC time-domain waveforms as GWpy `TimeSeries` polarizations.

See `docs/user_guide/waveform.md` (examples) and `docs/api/waveform/index.md` (API reference).
"""

from __future__ import annotations

from typing import Any

from gwpy.timeseries import TimeSeries
from pycbc.waveform import get_td_waveform


def pycbc_waveform_wrapper(
    tc: float,
    sampling_frequency: float,
    minimum_frequency: float,
    waveform_model: str,
    **kwargs: Any,
) -> dict[str, TimeSeries]:
    """Generate plus and cross polarizations with PyCBC and return GWpy time series.

    Calls :func:`pycbc.waveform.get_td_waveform` with ``delta_t = 1/sampling_frequency``,
    ``f_lower = minimum_frequency``, and ``approximant=waveform_model``, then shifts both
    polarizations by ``tc`` in GPS seconds and converts them to GWpy.

    Args:
        tc: GPS time of coalescence (seconds); added to each series' ``start_time``.
        sampling_frequency: Sample rate in Hz for ``delta_t``.
        minimum_frequency: Low-frequency cutoff in Hz, passed to PyCBC as ``f_lower``.
        waveform_model: PyCBC time-domain approximant name (e.g. ``IMRPhenomD``).
        **kwargs: Additional arguments for ``get_td_waveform`` (masses, spins, distance,
            etc., depending on the approximant).

    Returns:
        Mapping whose keys are the strings ``plus`` and ``cross``; each value is a
        GWpy :class:`gwpy.timeseries.TimeSeries`.

    Note:
        Invalid parameters may raise exceptions from PyCBC/LAL; see PyCBC waveform docs.
    """
    hp, hc = get_td_waveform(
        approximant=waveform_model,
        delta_t=1 / sampling_frequency,
        f_lower=minimum_frequency,
        **kwargs,
    )
    hp.start_time += tc
    hc.start_time += tc
    return {
        "plus": TimeSeries.from_pycbc(hp, copy=True),
        "cross": TimeSeries.from_pycbc(hc, copy=True),
    }
