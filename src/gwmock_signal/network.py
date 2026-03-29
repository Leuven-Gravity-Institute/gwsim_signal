"""Named detector network catalog for ground-based GW observatories."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pycbc.detector

if TYPE_CHECKING:
    from gwmock_signal.detector import CustomDetector

# Convenience presets for common multi-detector networks.  These are *not* the
# source of truth for which detector codes exist — PyCBC is.  Any code returned
# by ``pycbc.detector.get_available_detectors()`` is valid independently of
# what is listed here.  New PyCBC detectors are automatically usable via
# :meth:`Network.from_detectors` without touching this file.
_NETWORK_PRESETS: dict[str, tuple[str, ...]] = {
    # LIGO Hanford + LIGO Livingston
    "H1L1": ("H1", "L1"),
    # LIGO Hanford + LIGO Livingston + Virgo
    "H1L1V1": ("H1", "L1", "V1"),
    # LIGO Hanford + LIGO Livingston + Virgo + KAGRA
    "HLVK": ("H1", "L1", "V1", "K1"),
    # Einstein Telescope triangle configuration (three 60° arms)
    "ET-triangle": ("E1", "E2", "E3"),
    # Einstein Telescope L-shaped configuration
    "ET-L": ("E0",),
}

# Required geometry keys that trigger CustomDetector construction in from_file.
_geometry_keys: frozenset[str] = frozenset(
    {"latitude_deg", "longitude_deg", "elevation_m", "xarm_azimuth_deg", "yarm_azimuth_deg"}
)


def _load_data(path: Path) -> object:
    """Load YAML or JSON from *path*; raise ``ValueError`` for other extensions."""
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        import yaml  # noqa: PLC0415

        with path.open() as fh:
            return yaml.safe_load(fh)
    if suffix == ".json":
        with path.open() as fh:
            return json.load(fh)
    raise ValueError(f"Unsupported file extension {path.suffix!r}. Supported extensions: .yaml, .yml, .json")


def _detector_from_entry(entry: dict) -> str | CustomDetector:
    """Convert one detector dict entry to a str alias or :class:`CustomDetector`.

    Args:
        entry: Detector config mapping (must include ``"name"``).

    Returns:
        The PyCBC detector code string when no geometry keys are present,
        or a :class:`CustomDetector` instance.

    Raises:
        ValueError: If a required geometry field is absent.
    """
    from gwmock_signal.detector import CustomDetector  # noqa: PLC0415

    det_name: str = entry["name"]
    if not _geometry_keys & set(entry.keys()):
        return det_name
    for key in _geometry_keys:
        if key not in entry:
            raise ValueError(f"Missing required geometry field: '{key}' for detector {det_name!r}.")
    return CustomDetector(
        name=det_name,
        latitude_rad=math.radians(entry["latitude_deg"]),
        longitude_rad=math.radians(entry["longitude_deg"]),
        elevation_m=float(entry["elevation_m"]),
        xarm_azimuth_rad=math.radians(entry["xarm_azimuth_deg"]),
        yarm_azimuth_rad=math.radians(entry["yarm_azimuth_deg"]),
        xarm_tilt_rad=float(entry.get("xarm_tilt_rad", 0.0)),
        yarm_tilt_rad=float(entry.get("yarm_tilt_rad", 0.0)),
    )


@dataclass(frozen=True)
class Network:
    """A detector network: a named, ordered collection of detector specs.

    Attributes:
        name: Human-readable label for the network.
        detector_names: Ordered tuple of PyCBC/LAL detector prefix strings
            (e.g. ``"H1"``) or
            :class:`~gwmock_signal.detector.CustomDetector` instances.
    """

    name: str
    detector_names: tuple[str | CustomDetector, ...]

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_detectors(
        cls,
        detectors: Sequence[str | CustomDetector],
        *,
        name: str = "",
    ) -> Network:
        """Construct a :class:`Network` from any sequence of detector specs.

        String entries are validated against PyCBC's runtime detector list
        (``pycbc.detector.get_available_detectors()``), so any detector code
        that PyCBC knows about works here without any hard-coding.
        :class:`~gwmock_signal.detector.CustomDetector` instances are accepted
        as-is for non-standard geometries.

        Args:
            detectors: Sequence of PyCBC detector code strings (e.g. ``"H1"``)
                or :class:`~gwmock_signal.detector.CustomDetector` instances.
            name: Optional human-readable label.  Defaults to the
                comma-joined detector names.

        Returns:
            A :class:`Network` containing exactly the specified detectors.

        Raises:
            ValueError: If any string entry is not in PyCBC's available
                detector set, or if *detectors* is empty.
        """
        from gwmock_signal.detector import CustomDetector  # noqa: PLC0415

        if not detectors:
            raise ValueError("detectors must be a non-empty sequence.")

        pycbc_codes: set[str] = set(pycbc.detector.get_available_detectors())
        validated: list[str | CustomDetector] = []
        for det in detectors:
            if isinstance(det, CustomDetector):
                validated.append(det)
            else:
                code = str(det)
                if code not in pycbc_codes:
                    raise ValueError(
                        f"Unknown PyCBC detector code {code!r}. "
                        f"Run Network.list_pycbc_detectors() to see available codes, "
                        "or use a CustomDetector for non-standard geometries."
                    )
                validated.append(code)

        auto_name = name or ",".join(d if isinstance(d, str) else d.name for d in validated)
        return cls(name=auto_name, detector_names=tuple(validated))

    @classmethod
    def from_name(cls, alias: str) -> Network:
        """Construct a :class:`Network` from a named preset.

        Args:
            alias: One of the pre-defined network names returned by
                :meth:`list_names`.

        Returns:
            A :class:`Network` whose ``detector_names`` are the PyCBC codes
            for that preset.

        Raises:
            ValueError: If *alias* is not in the named presets.
        """
        if alias not in _NETWORK_PRESETS:
            raise ValueError(f"Unknown network {alias!r}. Known networks: {sorted(_NETWORK_PRESETS)}")
        return cls(name=alias, detector_names=_NETWORK_PRESETS[alias])

    @classmethod
    def from_file(cls, path: str | Path) -> Network:
        """Load a :class:`Network` from a YAML or JSON config file.

        The file must have a top-level ``name`` key (str) and a ``detectors``
        key containing a non-empty list of detector entries.  Each entry must
        have a ``name`` field.  If any geometry keys are present
        (``latitude_deg``, ``longitude_deg``, ``elevation_m``,
        ``xarm_azimuth_deg``, ``yarm_azimuth_deg``), a
        :class:`~gwmock_signal.detector.CustomDetector` is constructed;
        otherwise the name is treated as a PyCBC alias string.

        Args:
            path: Path to a ``.yaml``, ``.yml``, or ``.json`` file.

        Returns:
            A :class:`Network` whose ``detector_names`` contains str entries
            for PyCBC aliases and
            :class:`~gwmock_signal.detector.CustomDetector` entries for
            user-defined geometries.

        Raises:
            ValueError: If the file extension is unsupported, any required
                field is missing, or a field value is out of range.
        """
        path = Path(path)
        data = _load_data(path)

        if not isinstance(data, dict):
            raise ValueError("Network config must be a YAML/JSON mapping at the top level.")
        if "name" not in data:
            raise ValueError("Missing required field: 'name'")
        if "detectors" not in data:
            raise ValueError("Missing required field: 'detectors'")

        detectors_raw = data["detectors"]
        if not isinstance(detectors_raw, list) or len(detectors_raw) == 0:
            raise ValueError("'detectors' must be a non-empty list.")

        detectors: list[str | CustomDetector] = []
        for entry in detectors_raw:
            if not isinstance(entry, dict) or "name" not in entry:
                raise ValueError("Each detector entry must be a mapping with a 'name' field.")
            detectors.append(_detector_from_entry(entry))

        return cls(name=data["name"], detector_names=tuple(detectors))

    # ------------------------------------------------------------------
    # Listing helpers
    # ------------------------------------------------------------------

    @classmethod
    def list_names(cls) -> list[str]:
        """Return a sorted list of all named network preset aliases."""
        return sorted(_NETWORK_PRESETS.keys())

    @classmethod
    def list_pycbc_detectors(cls) -> list[str]:
        """Return every detector code available in the installed PyCBC, sorted.

        This list is computed at call time from
        ``pycbc.detector.get_available_detectors()``, so it automatically
        reflects whatever PyCBC version is installed — no hard-coding required.

        Returns:
            Sorted list of PyCBC/LAL detector prefix strings
            (e.g. ``['E0', 'E1', 'H1', 'L1', 'V1', ...]``).
        """
        return sorted(pycbc.detector.get_available_detectors())
