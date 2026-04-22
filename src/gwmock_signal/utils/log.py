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
"""Utility functions for logging."""

from __future__ import annotations

import logging
from pathlib import Path

from gwmock_signal.version import __version__


def get_version_information() -> str:
    """Get the version information.

    Returns:
        Version information.

    """
    return __version__


def setup_logger(
    outdir: str = ".", label: str | None = None, log_level: str | int = "INFO", print_version: bool = False
) -> None:
    """Set up logging output: call at the start of the script to use.

    Args:
        outdir: Output directory for log file.
        label: Label for log file name. If None, no log file is created.
        log_level: Logging level as string or integer.
        print_version: Whether to print version information to the log.

    """
    if isinstance(log_level, str):
        try:
            level = getattr(logging, log_level.upper())
        except AttributeError as e:
            raise ValueError(f"log_level {log_level} not understood") from e
    else:
        level = int(log_level)

    logger = logging.getLogger("gwmock_signal")
    logger.propagate = False
    logger.setLevel(level)

    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in logger.handlers
    ):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s %(name)s %(levelname)-8s: %(message)s", datefmt="%H:%M")
        )
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers) and label:
        outdir_path = Path(outdir)
        outdir_path.mkdir(parents=True, exist_ok=True)
        log_file = outdir_path / f"{label}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s", datefmt="%H:%M"))

        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    for handler in logger.handlers:
        handler.setLevel(level)

    if print_version:
        version = get_version_information()
        logger.info("Running gwmock_signal version: %s", version)
