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
"""Registry of waveform generators keyed by approximant or custom name.

See `docs/user_guide/waveform.md` (examples) and `docs/api/waveform/index.md` (API reference).
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from typing import Any

from gwpy.timeseries import TimeSeries
from pycbc.waveform import td_approximants

from gwmock_signal.waveform.pycbc_wrapper import pycbc_waveform_wrapper

logger = logging.getLogger("gwmock_signal.waveform")


class WaveformFactory:
    """Registry and dispatcher for time-domain waveform generators.

    On construction, every name returned by PyCBC
    [`td_approximants`](https://pycbc.org/pycbc/latest/html/waveform.html) is
    registered and mapped to ``pycbc_waveform_wrapper``.
    You may register additional names pointing at custom callables. See package docs for examples.
    """

    def __init__(self) -> None:
        """Build the registry of built-in PyCBC TD approximants.

        Note:
            Importing PyCBC and enumerating approximants can be slow; reuse one factory
            instance in tight loops instead of creating many factories.
        """
        self._models: dict[str, Callable[..., dict[str, TimeSeries]]] = dict.fromkeys(
            td_approximants(),
            pycbc_waveform_wrapper,
        )

    def register_model(self, name: str, factory_func: Callable[..., Any] | str) -> None:
        """Register or overwrite a waveform model under ``name``.

        Args:
            name: Key used with ``WaveformFactory.generate`` and ``WaveformFactory.get_model``.
            factory_func: Callable that accepts merged waveform kwargs (including
                ``waveform_model``, ``tc``, ``sampling_frequency``, ``minimum_frequency``)
                and returns a dict of GWpy ``plus``/``cross`` series, **or** an import
                string: either ``module.path:callable`` (colon before the name) or
                ``package.module.callable`` (split on the last ``.`` for attribute lookup).

        Raises:
            ImportError: If a string path does not refer to an importable module.
            AttributeError: If the imported module has no such callable attribute.
            ValueError: If factory_func string is neither 'module.path:callable' nor 'package.module.callable'.
            TypeError: Registered model is not callable.
        """
        if isinstance(factory_func, str):
            if ":" in factory_func:
                module_path, func_name = factory_func.split(":", 1)
            else:
                if "." not in factory_func:
                    raise ValueError("factory_func string must be 'module.path:callable' or 'package.module.callable'")
                module_path, func_name = factory_func.rsplit(".", 1)
            module = importlib.import_module(module_path)
            factory_func = getattr(module, func_name)

        if not callable(factory_func):
            raise TypeError(f"Registered model '{name}' is not callable")

        self._models[name] = factory_func
        logger.info("Registered waveform model: %s", name)

    def get_model(self, name: str) -> Callable[..., dict[str, TimeSeries]]:
        """Look up the generator function registered for ``name``.

        Args:
            name: Registered model name (built-in approximant or custom).

        Returns:
            The callable registered for this name.

        Raises:
            ValueError: If ``name`` is not registered.
        """
        if name in self._models:
            return self._models[name]
        raise ValueError(f"Waveform model '{name}' not found. Available: {list(self._models.keys())}.")

    def list_models(self) -> list[str]:
        """Return every registered waveform model name, in dict iteration order.

        Returns:
            List of keys (PyCBC TD approximants plus any custom registrations).
        """
        return list(self._models.keys())

    def generate(
        self,
        waveform_model: str,
        parameters: dict[str, Any],
        **extra_params: Any,
    ) -> dict[str, TimeSeries]:
        """Generate polarizations by calling the registered model with merged parameters.

        The callable is invoked with ``waveform_model``, then entries from ``parameters``,
        then ``extra_params`` (later keys override earlier ones).

        Args:
            waveform_model: Name of the registered model to run.
            parameters: Injection parameters (e.g. ``tc``, masses, spins) merged first.
            **extra_params: Additional fixed settings (e.g. ``sampling_frequency``,
                ``minimum_frequency``) merged after ``parameters``; later keys override.

        Returns:
            Dict whose keys are the strings ``plus`` and ``cross``, each mapping to a
            GWpy [`TimeSeries`](https://gwpy.github.io/docs/latest/api/gwpy.timeseries.TimeSeries/).

        Raises:
            ValueError: If ``waveform_model`` is not registered.
            TypeError: If the underlying generator is called with invalid arguments.
        """
        waveform_func = self.get_model(waveform_model)
        if "waveform_model" in parameters or "waveform_model" in extra_params:
            raise ValueError("Do not pass 'waveform_model' in parameters/extra_params.")
        all_params: dict[str, Any] = {**parameters, **extra_params, "waveform_model": waveform_model}
        return waveform_func(**all_params)
