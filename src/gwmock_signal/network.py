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

# Keys whose presence in an entry signals a full custom geometry rather than a
# plain PyCBC alias string.  Both *_deg and *_rad variants are included so that
# either convention triggers CustomDetector construction.
_geometry_keys: frozenset[str] = frozenset(
    {
        "latitude_deg",
        "latitude_rad",
        "longitude_deg",
        "longitude_rad",
        "elevation_m",
        "xarm_azimuth_deg",
        "xarm_azimuth_rad",
        "yarm_azimuth_deg",
        "yarm_azimuth_rad",
    }
)

# Required angle base-names (elevation is handled separately as it is not an angle).
_required_angles: tuple[str, ...] = ("latitude", "longitude", "xarm_azimuth", "yarm_azimuth")
_optional_angles: tuple[str, ...] = ("xarm_tilt", "yarm_tilt")


def _parse_angle(entry: dict, base: str, *, required: bool, default: float = 0.0) -> float:
    """Return an angle in radians from *entry*, accepting ``{base}_deg`` or ``{base}_rad``.

    Args:
        entry: Detector config mapping.
        base: Angle parameter base name (e.g. ``"latitude"``).
        required: If ``True`` raise :class:`ValueError` when neither key is present.
        default: Value returned when both keys are absent and ``required`` is ``False``.

    Raises:
        ValueError: If both ``{base}_deg`` and ``{base}_rad`` are present simultaneously.
        ValueError: If ``required`` is ``True`` and neither key is present.
    """
    deg_key = f"{base}_deg"
    rad_key = f"{base}_rad"
    has_deg = deg_key in entry
    has_rad = rad_key in entry
    if has_deg and has_rad:
        raise ValueError(
            f"Conflicting angle specification for '{base}': provide either '{deg_key}' or '{rad_key}', not both."
        )
    if has_deg:
        return math.radians(float(entry[deg_key]))
    if has_rad:
        return float(entry[rad_key])
    if required:
        raise ValueError(f"Missing required angle '{base}': provide either '{deg_key}' or '{rad_key}'.")
    return default


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
        ValueError: If a required angle is absent or if both ``*_deg`` and
            ``*_rad`` variants of the same angle are present simultaneously.
    """
    from gwmock_signal.detector import CustomDetector  # noqa: PLC0415

    det_name: str = entry["name"]
    if not _geometry_keys & set(entry.keys()):
        return det_name

    if "elevation_m" not in entry:
        raise ValueError(f"Missing required geometry field: 'elevation_m' for detector {det_name!r}.")

    try:
        return CustomDetector(
            name=det_name,
            latitude_rad=_parse_angle(entry, "latitude", required=True),
            longitude_rad=_parse_angle(entry, "longitude", required=True),
            elevation_m=float(entry["elevation_m"]),
            xarm_azimuth_rad=_parse_angle(entry, "xarm_azimuth", required=True),
            yarm_azimuth_rad=_parse_angle(entry, "yarm_azimuth", required=True),
            xarm_tilt_rad=_parse_angle(entry, "xarm_tilt", required=False, default=0.0),
            yarm_tilt_rad=_parse_angle(entry, "yarm_tilt", required=False, default=0.0),
        )
    except ValueError as exc:
        raise ValueError(f"Detector {det_name!r}: {exc}") from exc


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
        have a ``name`` field.  If any geometry key is present a
        :class:`~gwmock_signal.detector.CustomDetector` is constructed;
        otherwise the name is treated as a plain PyCBC detector code string.

        **Angle conventions** — every angle parameter accepts either a degrees
        variant (``*_deg``) or a radians variant (``*_rad``), but *not both* for
        the same parameter:

        +-----------------------+-------------------+-----------+
        | Parameter             | Degrees key       | Radians key |
        +=======================+===================+=============+
        | Geodetic latitude     | ``latitude_deg``  | ``latitude_rad`` |
        | Geodetic longitude    | ``longitude_deg`` | ``longitude_rad`` |
        | x-arm azimuth         | ``xarm_azimuth_deg`` | ``xarm_azimuth_rad`` |
        | y-arm azimuth         | ``yarm_azimuth_deg`` | ``yarm_azimuth_rad`` |
        | x-arm tilt (optional) | ``xarm_tilt_deg`` | ``xarm_tilt_rad`` |
        | y-arm tilt (optional) | ``yarm_tilt_deg`` | ``yarm_tilt_rad`` |
        +-----------------------+-------------------+-----------+

        ``elevation_m`` is always in metres.  Tilt fields default to ``0.0``
        when absent.

        Args:
            path: Path to a ``.yaml``, ``.yml``, or ``.json`` file.

        Returns:
            A :class:`Network` whose ``detector_names`` contains str entries
            for PyCBC aliases and
            :class:`~gwmock_signal.detector.CustomDetector` entries for
            user-defined geometries.

        Raises:
            ValueError: If the file extension is unsupported, a required
                angle is absent, both ``*_deg`` and ``*_rad`` are given for
                the same angle, or a geometry value is out of range.
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

        return cls.from_detectors(detectors, name=data["name"])

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
