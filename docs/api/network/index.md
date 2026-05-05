---
title: Network
description: Detector network presets and file-based network definitions.
icon: material/transit-connection-variant
---

<!-- prettier-ignore-start -->

::: gwmock_signal.network
    options:
        show_root_heading: true
        heading_level: 2
        inherited_members: true
        show_if_no_docstring: false
        docstring_style: google
        show_source: true

<!-- prettier-ignore-end -->

Used by the **[command-line interface](../../user_guide/cli.md)** (`--network`)
and by library workflows that need named IFO sets. For antenna-pattern
projection of $h_{+}$, $h_{\times}$, see **[Projection](../projection/)**.

Bundled detector-geometry presets currently include:

- `ET-Triangle-Sardinia` (compatibility alias: `ET-Sardinia`)
- `ET-Triangle-EMR` (compatibility alias: `ET-EMR`)
- `ET-2L-Aligned`
- `ET-2L-Misaligned`
