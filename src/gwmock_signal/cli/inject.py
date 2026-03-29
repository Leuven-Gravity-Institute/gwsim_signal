"""CLI sub-app for gravitational-wave signal injection commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import numpy as np
import typer
from gwpy.timeseries import TimeSeries, TimeSeriesDict

from gwmock_signal.network import Network
from gwmock_signal.pipeline import inject_cbc_signal

inject_app = typer.Typer(
    name="inject",
    help="Inject gravitational-wave signals into detector data. "
    "See https://gwmock-signal.readthedocs.io for full documentation.",
)


@inject_app.command("cbc")
def cbc(  # noqa: PLR0913
    params: Annotated[
        Path,
        typer.Option("--params", help="Path to JSON file with CBC injection parameters.", show_default=False),
    ],
    network: Annotated[
        str,
        typer.Option(
            "--network",
            help="Named network catalog entry (e.g. H1L1V1). Run `gwmock-signal network list` for available names.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="HDF5 output file path. If omitted, a one-line summary per detector is printed to stdout.",
        ),
    ] = None,
    sample_rate: Annotated[
        int,
        typer.Option("--sample-rate", help="Sample rate in Hz."),
    ] = 4096,
    f_min: Annotated[
        float,
        typer.Option("--f-min", help="Minimum frequency cutoff in Hz passed to the waveform generator."),
    ] = 20.0,
    duration: Annotated[
        float,
        typer.Option("--duration", help="Length of the zero-noise background segment in seconds."),
    ] = 16.0,
    approximant: Annotated[
        str,
        typer.Option("--approximant", help="PyCBC time-domain waveform approximant name."),
    ] = "IMRPhenomD",
    seed: Annotated[
        int | None,
        typer.Option("--seed", help="Optional integer random seed for reproducibility."),
    ] = None,
) -> None:
    """Inject a single CBC event into zero-noise detector data.

    Loads CBC parameters from a JSON file, resolves the detector network,
    generates a zero-noise background, runs the injection pipeline, and
    either writes the result to an HDF5 file or prints a per-detector summary.

    See https://gwmock-signal.readthedocs.io for full documentation.
    """
    # Load CBC parameters from JSON
    try:
        with params.open() as fh:
            cbc_params = json.load(fh)
    except FileNotFoundError:
        raise typer.BadParameter(f"Parameter file not found: {params}", param_hint="--params") from None
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid JSON in {params}: {exc}", param_hint="--params") from exc

    # Resolve network: file path takes priority over catalog name
    network_path = Path(network)
    if network_path.exists():
        raise typer.BadParameter(
            f"File-based network definitions are not yet supported (planned in ISS-007). "
            f"Use a named catalog entry instead. Available names: {Network.list_names()}",
            param_hint="--network",
        )
    try:
        net = Network.from_name(network)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--network") from exc

    if seed is not None:
        np.random.seed(seed)

    if sample_rate <= 0:
        raise typer.BadParameter("--sample-rate must be > 0", param_hint="--sample-rate")
    if duration <= 0:
        raise typer.BadParameter("--duration must be > 0", param_hint="--duration")
    if f_min <= 0:
        raise typer.BadParameter("--f-min must be > 0", param_hint="--f-min")

    # Build zero-noise background centred on tc
    tc = float(cbc_params["tc"])
    n_samples = int(duration * sample_rate)
    background = {
        name: TimeSeries(
            np.zeros(n_samples),
            t0=tc - duration / 2,
            sample_rate=sample_rate,
        )
        for name in net.detector_names
    }

    # Run the injection pipeline
    result = inject_cbc_signal(
        waveform_model=approximant,
        params=cbc_params,
        detector_names=net.detector_names,
        background=background,
        sampling_frequency=float(sample_rate),
        minimum_frequency=f_min,
    )

    if output is not None:
        tsd = TimeSeriesDict(result.to_dict())
        tsd.write(str(output), format="hdf5")
    else:
        for name in net.detector_names:
            ts = result[name]
            rms = float(np.sqrt(np.mean(ts.value**2)))
            typer.echo(f"{name}  rms={rms:.4e}  duration={ts.duration.value:.1f}s")
