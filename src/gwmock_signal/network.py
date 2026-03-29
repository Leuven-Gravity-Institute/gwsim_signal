"""Named detector network catalog for ground-based GW observatories."""

from __future__ import annotations

from dataclasses import dataclass

# Module-level catalog mapping alias → tuple of PyCBC/LAL detector prefix codes.
# Sources:
#   LIGO/Virgo codes: https://pycbc.org/pycbc/latest/html/detector.html
#   KAGRA code K1: lal.KAGRA_DETECTOR_PREFIX == "K1"
#   ET codes E0-E3: lal.ET0/ET1/ET2/ET3_DETECTOR_PREFIX (confirmed via PyCBC
#     get_available_detectors() and lal.ET*_DETECTOR_PREFIX attributes)
_CATALOG: dict[str, tuple[str, ...]] = {
    # LIGO Hanford + LIGO Livingston
    "H1L1": ("H1", "L1"),
    # LIGO Hanford + LIGO Livingston + Virgo
    "H1L1V1": ("H1", "L1", "V1"),
    # LIGO Hanford + LIGO Livingston + Virgo + KAGRA (K1: lal.KAGRA_DETECTOR_PREFIX)
    "HLVK": ("H1", "L1", "V1", "K1"),
    # Einstein Telescope triangle configuration: three 60° arms (E1, E2, E3 —
    # lal.ET1/ET2/ET3_DETECTOR_PREFIX)
    "ET-triangle": ("E1", "E2", "E3"),
    # Einstein Telescope L-shaped configuration: single L-shaped interferometer
    # (E0 — lal.ET0_DETECTOR_PREFIX)
    "ET-L": ("E0",),
}


@dataclass(frozen=True)
class Network:
    """A named detector network with an ordered tuple of PyCBC detector codes.

    Attributes:s
        name: The alias identifying this network (e.g. ``"H1L1V1"``).
        detector_names: Ordered tuple of PyCBC/LAL detector prefix codes
            (e.g. ``("H1", "L1", "V1")``).
    """

    name: str
    detector_names: tuple[str, ...]

    @classmethod
    def from_name(cls, alias: str) -> Network:
        """Construct a :class:`Network` from a catalog alias.

        Args:
            alias: One of the pre-defined network names returned by
                :meth:`list_names`.

        Returns:
            A :class:`Network` whose ``detector_names`` are the PyCBC codes
            for that network.

        Raises:
            ValueError: If *alias* is not in the catalog.
        """
        if alias not in _CATALOG:
            raise ValueError(f"Unknown network {alias!r}. Known networks: {sorted(_CATALOG)}")
        return cls(name=alias, detector_names=_CATALOG[alias])

    @classmethod
    def list_names(cls) -> list[str]:
        """Return a sorted list of all catalog alias names."""
        return sorted(_CATALOG.keys())
