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
  below only.

## Sections

| Section                           | Contents                                     |
| --------------------------------- | -------------------------------------------- |
| **[Waveform](waveform/)**         | `pycbc_waveform_wrapper`, `WaveformFactory`  |
| **[Projection](projection/)**     | `project_polarizations_to_network`           |
| **[Injection](injection/)**       | `inject_strain`, `inject_strains_sequential` |
| **[Multichannel](multichannel/)** | `DetectorStrainStack`                        |
| **[Utility](utils/)**             | Logging and other helpers                    |

## Main entry points (quick links)

- **[Waveform](waveform/)** — Time-domain polarizations via PyCBC
  (`pycbc_waveform_wrapper`, `WaveformFactory`).
- **[Projection](projection/)** — Strain per detector
  (`project_polarizations_to_network`).
- **[Injection](injection/)** — Strain into segments (`inject_strain`,
  `inject_strains_sequential`).
- **[Multichannel](multichannel/)** — Stacked IFO strains
  (`DetectorStrainStack`).
- **[Utility](utils/)** — Utility functions.

## See also

- [User guide overview](../user_guide/index.md)
- [Documentation home](../index.md)
