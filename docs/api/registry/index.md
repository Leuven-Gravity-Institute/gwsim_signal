---
title: Registry
description: Public simulator backend lookup by source type (gwmock-pop).
icon: material/database-cog-outline
---

<!-- prettier-ignore-start -->

::: gwmock_signal.registry
    options:
        show_root_heading: true
        heading_level: 2
        inherited_members: true
        show_if_no_docstring: false
        docstring_style: google
        show_source: true

<!-- prettier-ignore-end -->

The built-in CBC backend is registered under the key `bbh`. For the simulator
classes returned by `resolve_simulator_backend`, see
**[Simulator](../simulator/)**.

For a short **Python example** of `resolve_simulator_backend`, see the
[README](https://github.com/Leuven-Gravity-Institute/gwmock-signal/blob/main/README.md)
on the project home page.
