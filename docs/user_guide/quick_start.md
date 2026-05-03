---
title: Quick Start
description: Orient yourself and run a minimal import check for gwmock-signal.
icon: material/rocket-launch
---

# Quick Start

Welcome to the **gwmock-signal** documentation.

## Before you begin

1. Follow **[Installation](installation.md)** to create an environment and
   install the package.
2. Read the **[User guide overview](index.md)** for the recommended workflow
   (waveforms → projection → injection → multichannel).

## Verify the install

```bash
gwmock-signal --help
gwmock-signal inject --help
```

```bash
python -c "import gwmock_signal; print(gwmock_signal.__version__)"
python -c "from gwmock_signal import list_registered_source_types; print(list_registered_source_types())"
```

## Next steps

- Read **[Command-line interface](cli.md)** if you plan to use
  `gwmock-signal inject`.
- Work through **User guide → Examples** (start with [Waveforms](waveform.md)).
- Browse the **[API overview](../api/index.md)** for full function and class
  reference.
