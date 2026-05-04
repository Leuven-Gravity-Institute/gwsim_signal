---
title: Simulator
description: GWSimulator, TransientSimulator, and CBCSimulator APIs.
icon: material/function-variant
---

<!-- prettier-ignore-start -->

::: gwmock_signal.simulator
    options:
        show_root_heading: true
        heading_level: 2
        inherited_members: true
        show_if_no_docstring: false
        docstring_style: google
        show_source: true

<!-- prettier-ignore-end -->

For **registry-based construction** (gwmock-pop `source_type` strings), see
**[Registry](../registry/)**. For **one-shot CBC injection** without
instantiating a simulator, see **[Pipeline](../pipeline/)**
(`inject_cbc_signal`).

`TransientSimulator` also exposes `register_waveform_model(name, factory)` for
per-instance waveform registration. Use this when downstream orchestration needs
to inject a custom callable waveform without reaching into private
`_waveform_factory` state.

For **narrative examples** (waveforms → projection → injection), see the
[user guide overview](../../user_guide/index.md).
