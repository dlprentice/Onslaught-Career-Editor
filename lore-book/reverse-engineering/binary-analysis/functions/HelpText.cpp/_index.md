# HelpText.cpp Functions

> Source family: `CHelpTextDisplay` helpers | Binary: `BEA.exe` (Steam build)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This folder tracks the saved static Ghidra evidence for the retail HelpTextDisplay object. Stuart's current source snapshot references `HelpText.h` from `game.cpp`, and `CGame` allocates a `CHelpTextDisplay` during restart/init setup, but the matching HelpText source body is not present in the snapshot used for this pass.

## Functions

Wave1175 current-risk review (`wave1175-helptext-display-current-risk-review`) re-read the three active HelpTextDisplay current-risk rows with fresh Ghidra export evidence and no mutation. It accounts for `3 HelpTextDisplay current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; Wave1108 current focused accounting is `683/1179 = 57.93%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 496; current risk candidates: 6166; focused threshold `15`; not Wave911 reconstruction. Fresh Ghidra export evidence verified `3 xref rows` and `169 instruction rows`. Anchors include `CHelpTextDisplay__ctor`, `CHelpTextDisplay__QueueMessageWithTimestamp`, `CHelpTextDisplay__RenderQueuedMessages`, `CGame__InitRestartLoop`, `CHud__RenderOverlayForViewpoint`, `TextLayout__WrapWideTextToFixedLines`, and `CDXFont__DrawTextDynamic`. Prior context remains Wave397 `help-hive-wave397` and Wave1005 `help-text-display-review-wave1005`. Verified backup: `G:\GhidraBackups\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified`. This was a read-only review with no mutation and Codex root final judgment; runtime HelpText behavior, runtime HUD/text rendering behavior, exact HelpTextDisplay/HUD/font/text-layout layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Wave1005 static re-audit (`help-text-display-review-wave1005`) re-read all four HelpTextDisplay rows with fresh metadata, tags, xrefs, body instructions, and decompile. The saved project state remained coherent, so no mutation was justified. Current anchors include `0x0047fab0 CHelpTextDisplay__ctor`, `0x0047fad0 CHelpTextDisplay__scalar_deleting_dtor`, `0x0047fb00 CHelpTextDisplay__QueueMessageWithTimestamp`, and `0x0047fb50 CHelpTextDisplay__RenderQueuedMessages`. The render row is called from `0x00487b83 CHud__RenderOverlayForViewpoint`, wraps text through `0x00465a20 TextLayout__WrapWideTextToFixedLines`, and dispatches through `0x00465710 CDXFont__DrawTextDynamic`. Verified backup: `G:\GhidraBackups\BEA_20260531-132023_post_wave1005_help_text_display_review_verified`. Runtime help-text behavior, runtime text rendering, exact source-body identity, concrete HelpTextDisplay/HUD/text-layout/font layouts, BEA patching, and rebuild parity remain separate proof.

| Address | Name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x0047fab0` | `CHelpTextDisplay__ctor` | Clears two queued-message slots, installs the HelpTextDisplay vtable, and returns the receiver. | `ghidra_help_hive_wave397_2026-05-14.md` |
| `0x0047fad0` | `CHelpTextDisplay__scalar_deleting_dtor` | Scalar deleting destructor wrapper; restores the vtable and conditionally frees the object when the delete flag is set. | `ghidra_help_hive_wave397_2026-05-14.md` |
| `0x0047fb00` | `CHelpTextDisplay__QueueMessageWithTimestamp` | Queues a message pointer into one of two slots, stamps the global time, marks the slot active, and logs an overflow message when both slots are occupied. | `ghidra_help_hive_wave397_2026-05-14.md` |
| `0x0047fb50` | `CHelpTextDisplay__RenderQueuedMessages` | Renders up to two queued messages with age/fade handling, text wrapping, optional controller-config font state, draw dispatch, and old-slot expiry. | `ghidra_help_hive_wave397_2026-05-14.md` |

## Boundaries

- These are saved static Ghidra names/signatures/comments/tags only.
- Wave397 corrected older `CUnitAI` and `CExplosionInitThing` owner labels where the current HelpTextDisplay layout and caller evidence support HelpText ownership.
- Runtime HelpText behavior, exact source identity, concrete layout fields, local variables, and rebuild parity remain unproven.
- This documentation does not launch, patch, or mutate `BEA.exe`.
