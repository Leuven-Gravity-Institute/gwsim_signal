#
# Copyright (C) 2026 Leuven Gravity Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
"""Main entry point for the gwmock_signal CLI application."""

from __future__ import annotations

import enum
from typing import Annotated

import typer


class LoggingLevel(enum.StrEnum):
    """Logging levels for the CLI."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Create the main Typer app
app = typer.Typer(
    name="gwmock_signal",
    help="Main CLI for gwmock_signal.",
    rich_markup_mode="rich",
)


def setup_logging(level: LoggingLevel = LoggingLevel.INFO) -> None:
    """Set up logging with Rich handler.

    Args:
        level: Logging level.
    """
    import logging  # noqa: PLC0415

    from rich.console import Console  # noqa: PLC0415
    from rich.logging import RichHandler  # noqa: PLC0415

    logger = logging.getLogger("gwmock_signal")

    logger.setLevel(level.value)

    console = Console(stderr=True)

    # Remove any existing handlers to ensure RichHandler is used
    for h in logger.handlers[:]:  # Use slice copy to avoid modification during iteration
        logger.removeHandler(h)
    # Add the RichHandler

    handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_time=True,
        show_level=True,  # Keep level (e.g., DEBUG, INFO) for clarity
        markup=True,  # Enable Rich markup in messages for styling
        level=level.value,  # Ensure handler respects the level
        omit_repeated_times=False,
        log_time_format="%H:%M",
    )
    handler.setLevel(level.value)
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate output
    logger.propagate = False


@app.callback()
def main(
    verbose: Annotated[
        LoggingLevel,
        typer.Option("--verbose", "-v", help="Set verbosity level."),
    ] = LoggingLevel.INFO,
) -> None:
    """Main entry point for the CLI application.

    Args:
        verbose: Verbosity level for logging.
    """
    setup_logging(verbose)


def register_commands() -> None:
    """Register CLI commands."""
    from gwmock_signal.cli.inject import inject_app  # noqa: PLC0415

    app.add_typer(inject_app, name="inject")


register_commands()
