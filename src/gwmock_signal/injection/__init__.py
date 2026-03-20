"""Time-domain strain injection into GWpy segments.

See ``docs/user_guide/strain-injection.md`` (examples) and ``docs/api/injection/index.md`` (API).
"""

from __future__ import annotations

from gwmock_signal.injection.core import inject_strain, inject_strains_sequential

__all__ = ["inject_strain", "inject_strains_sequential"]
