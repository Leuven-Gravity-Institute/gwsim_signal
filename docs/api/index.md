---
title: API Reference
description: Auto-generated reference for gwmock-signal public Python APIs.
icon: material/api
---

# API reference

This section documents the **public Python API** of **gwmock-signal**. Pages are
generated with **mkdocstrings** from **Google-style docstrings** in the source
tree (`src/gwmock_signal/`).

**How to use this site**

- For **workflow overview and example snippets**, use
  **[User guide → Examples](../user_guide/index.md)** (sidebar).
- For **exact signatures, types, and raised exceptions**, use the API sections
  below.
- For **`gwmock-signal` CLI** flags and JSON formats, use
  **[User guide → Command-line interface](../user_guide/cli.md)**.

## Sections

| Section                           | Contents                                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------- |
| **[Waveform](waveform/)**         | `pycbc_waveform_wrapper`, `WaveformFactory`                                               |
| **[Projection](projection/)**     | `project_polarizations_to_network`                                                        |
| **[Injection](injection/)**       | `inject_strain`, `inject_strains_sequential`                                              |
| **[Pipeline](pipeline/)**         | `inject_cbc_signal` (CBC orchestration)                                                   |
| **[Multichannel](multichannel/)** | `DetectorStrainStack`                                                                     |
| **[Network](network/)**           | `Network` (presets, `from_file`, detector lists)                                          |
| **[Simulator](simulator/)**       | `GWSimulator`, `TransientSimulator`, `CBCSimulator`                                       |
| **[Registry](registry/)**         | `resolve_simulator_backend`, `register_simulator_backend`, `list_registered_source_types` |
| **[Utility](utils/)**             | Logging and other helpers                                                                 |

## Main entry points (quick links)

- **[Waveform](waveform/)** — Time-domain polarizations via PyCBC
  (`pycbc_waveform_wrapper`, `WaveformFactory`).
- **[Projection](projection/)** — Strain per detector
  (`project_polarizations_to_network`).
- **[Injection](injection/)** — Strain into segments (`inject_strain`,
  `inject_strains_sequential`).
- **[Pipeline](pipeline/)** — One-call CBC injection (`inject_cbc_signal`).
- **[Multichannel](multichannel/)** — Stacked IFO strains
  (`DetectorStrainStack`).
- **[Network](network/)** — Named networks and YAML/JSON network configs.
- **[Simulator](simulator/)** — Simulator base class and CBC implementation.
- **[Registry](registry/)** — Lookup `GWSimulator` subclasses by `source_type`
  string (for example `bbh`).
- **[Utility](utils/)** — Utility functions.

## Top-level package exports

`import gwmock_signal` re-exports the main symbols from `gwmock_signal.__init__`
(including `CBCSimulator`, `Network`, `resolve_simulator_backend`, and
`__version__`). Prefer these imports in application code; submodule paths are
stable but longer.

## See also

- [User guide overview](../user_guide/index.md)
- [Documentation home](../index.md)
