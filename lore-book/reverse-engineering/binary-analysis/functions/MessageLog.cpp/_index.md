# MessageLog.cpp

> Retail static evidence bucket for `CMessageLog` helpers in `BEA.exe`.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CMessageLog` sits next to the MessageBox overlay cluster and owns the queued-message log panel, message-card rendering, scroll/back input, texture loading, and basic lifecycle helpers. Wave451 corrected the main saved MessageLog tranche after Wave450 separated the neighboring MessageBox portrait/queue/reveal helpers.

## Functions

| Address | Name | Status | Notes |
| --- | --- | --- | --- |
| `0x004b82a0` | `CMessageLog__GetEntryField3CByIndex` | SAVED | Wave450 hardened the adjacent MessageLog accessor signature. `ret 0x4` confirms one stack `entry_index` argument; it returns `this + entry_index*0x18 + 0x3c`. |
| `0x004b8dd0` | `CMessageLog__ctor_base` | SAVED | Wave451 corrected the former `CGameMenu__ctor_like_004b8dd0` label. The function initializes the pointer-set queue at `+0x18`, clears queue/render counters and texture slots, clears shared arrow texture global `DAT_00807418`, installs the MessageLog vtable, and returns `this`. |
| `0x004b8e50` | `CMessageLog__scalar_deleting_dtor` | SAVED | Wave451 corrected the vfunc-style label to a scalar-deleting destructor wrapper. It calls `CMessageLog__dtor_base`, conditionally frees through `CDXMemoryManager__Free` when `flags & 1` is set, and `ret 0x4` confirms one stack `flags` argument. |
| `0x004b8e70` | `CMessageLog__LoadTextures` | SAVED | Wave451 hardened the texture-load signature/comment. The function loads MessageLog end-curve, arrow, blank, head-frame, and mask textures into slots `+0x08..+0x14` and shared arrow texture global `DAT_00807418`. |
| `0x004b8ef0` | `CMessageLog__EnqueueMessageNode` | SAVED | Wave451 hardened the queue insert signature/comment. `ret 0x4` confirms one stack `message_node` argument; the function adds the node to the head of the pointer-set queue at `this+0x18`. |
| `0x004b8f00` | `CMessageLog__dtor_base` | SAVED | Wave451 corrected the former ctor-like label to the base destructor. It releases queued message nodes through their vtable slot, clears the pointer-set queue, releases MessageLog textures and the shared arrow texture global, then calls `CMonitor__Shutdown`. |
| `0x004b9010` | `CMessageLog__RenderPanelFrame` | SAVED | Wave451 hardened the panel-frame signature. `ret 0x14` confirms five stack arguments after `this`: `screen_x`, `screen_y`, `width`, `height`, and `alpha`; the body draws corners, stretched edges, and center fill from the end-curve/blank textures. |
| `0x004b93f0` | `CMessageLog__Render` | SAVED | Wave451 hardened the main log-render signature. The `CDXEngine__PostRender` callsite passes `DAT_008a9d88` in ECX and one stack render context; the body renders the title, empty-log panel, queued cards, scroll arrows, click regions, close/back affordance, and cursor. |
| `0x004b9a80` | `CMessageLog__RenderMessageCard` | SAVED | Wave451 hardened the message-card renderer signature. `ret 0x14` confirms `message_node`, `screen_x`, `screen_y`, `alpha`, and `measure_only`; the body word-wraps/measures a queued message node and optionally renders the card frame, portrait, timestamp, and wrapped lines. |
| `0x004b9ea0` | `CMessageLog__ResetRenderState` | SAVED | Wave451 hardened the state-reset helper. It enables the overlay and clears scroll/render interpolation fields at `+0x2c`, `+0x30`, `+0x38`, and `+0x3c`. |
| `0x004b9ec0` | `CMessageLog__HandleInputCommand` | SAVED | Wave451 corrected the vfunc-style label to the input-command handler. Button `0x2a` scrolls up, `0x2b` scrolls down when more rows are available, and `0x2e` closes the log, initializes pause state, relinquishes controller ownership, and plays frontend sounds. |

## Wave451 Evidence Boundary

Wave451 saved names/signatures/comments/tags for `11` MessageLog and overlay-adjacent targets. Dry/apply/verify-dry and post-export probes passed, with read-back artifacts under `subagents/ghidra-static-reaudit/wave451-messagelog-overlay-current/` and public-safe readiness evidence at `release/readiness/ghidra_messagelog_wave451_2026-05-16.md`.

Static evidence supports these owner/signature corrections, but runtime message-log display, scroll/back input behavior, exact overlay layout, concrete MessageLog/MessageBox layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven by this wave.
