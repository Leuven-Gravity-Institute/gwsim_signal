# PyCBC supports custom ground-based detectors via
# ``pycbc.detector.add_detector_on_earth(name, longitude, latitude,
# yangle, xangle, height, xaltitude, yaltitude)``.
# Confirmed present in PyCBC >= 2.x (pycbc.detector.ground module).
# This module wraps that API behind a validated dataclass.

"""User-defined ground-based detector geometry."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pycbc.detector

if TYPE_CHECKING:
    pass


@dataclass
class CustomDetector:
    """A user-defined ground-based gravitational-wave detector.

    All angular fields are in radians; elevation is in metres.

    Attributes:
        name: Short identifier used as the key in strain output dicts.
            Must be unique within a network.
        latitude_rad: Geodetic latitude of the vertex in radians.
            Must be in ``[-pi/2, pi/2]``.
        longitude_rad: Geodetic longitude of the vertex in radians.
            Must be in ``[-pi, pi]``.
        elevation_m: Vertex elevation above the WGS-84 ellipsoid in metres.
            Must be in ``[-1e4, 1e5]``.
        xarm_azimuth_rad: Azimuthal angle of the x-arm measured from
            geodetic North in radians.
        yarm_azimuth_rad: Azimuthal angle of the y-arm measured from
            geodetic North in radians.
        xarm_tilt_rad: Altitude angle of the x-arm above the local
            horizon in radians.  Defaults to ``0.0``.
        yarm_tilt_rad: Altitude angle of the y-arm above the local
            horizon in radians.  Defaults to ``0.0``.
    """

    name: str
    latitude_rad: float
    longitude_rad: float
    elevation_m: float
    xarm_azimuth_rad: float
    yarm_azimuth_rad: float
    xarm_tilt_rad: float = 0.0
    yarm_tilt_rad: float = 0.0

    # Cache for the PyCBC Detector object; not exposed as a public attribute.
    _pycbc_detector: pycbc.detector.Detector | None = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate geodetic parameters on construction."""
        _elev_min = -1e4
        _elev_max = 1e5
        half_pi = math.pi / 2.0
        if not (-half_pi <= self.latitude_rad <= half_pi):
            raise ValueError(f"latitude_rad must be in [-pi/2, pi/2]; got {self.latitude_rad!r}.")
        if not (-math.pi <= self.longitude_rad <= math.pi):
            raise ValueError(f"longitude_rad must be in [-pi, pi]; got {self.longitude_rad!r}.")
        if not (_elev_min <= self.elevation_m <= _elev_max):
            raise ValueError(f"elevation_m must be in [-1e4, 1e5] m; got {self.elevation_m!r}.")

    def to_pycbc(self) -> pycbc.detector.Detector:
        """Return a PyCBC :class:`~pycbc.detector.Detector` for this geometry.

        The first call registers the detector with PyCBC via
        :func:`pycbc.detector.add_detector_on_earth` and caches the result.
        Subsequent calls return the cached object.

        Returns:
            A :class:`pycbc.detector.Detector` instance configured with
            this detector's geodetic coordinates and arm orientations.
        """
        if self._pycbc_detector is None:
            pycbc.detector.add_detector_on_earth(
                self.name,
                self.longitude_rad,
                self.latitude_rad,
                yangle=self.yarm_azimuth_rad,
                xangle=self.xarm_azimuth_rad,
                height=self.elevation_m,
                xaltitude=self.xarm_tilt_rad,
                yaltitude=self.yarm_tilt_rad,
            )
            self._pycbc_detector = pycbc.detector.Detector(self.name)
        return self._pycbc_detector  # type: ignore[return-value]
