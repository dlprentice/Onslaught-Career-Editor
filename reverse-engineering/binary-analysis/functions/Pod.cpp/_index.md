# Pod.cpp Functions

> Source File: Pod.cpp | Binary: BEA.exe

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Current retail static evidence has a CPOD RTTI/vtable island, but the current Stuart source snapshot does not contain a `CPod` source body. Treat the saved names here as conservative retail-binary labels.

Wave1069 (`groundunit-vfunc-motion-effects-review-wave1069`) re-read `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` as part of the GroundUnit/vfunc motion-effects cluster with no mutation. Fresh evidence ties it to CPod vtable `0x005dff8c` slot `66`, `CUnit__UpdateMotionAttachmentsAndEffects`, a vfunc `+0xb4` dispatch, and scalar accumulation at `this+0x84`; runtime pod motion behavior, exact source identity, concrete layout, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1120 (`wave1120-mixed-score25-current-risk-review`) re-read `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` again from the current-risk queue with a fresh read-only Ghidra export and no mutation. Fresh DATA xref `0x005e0094` keeps the vtable slot assignment coherent, and decompile evidence still calls `CUnit__UpdateMotionAttachmentsAndEffects`, dispatches vfunc `+0xb4`, and accumulates into `this+0x84`. Current focused accounting moves to `118/1179 = 10.01%`; verified backup `G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`. Runtime pod motion behavior, exact source identity, concrete layout, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
| --- | --- | --- | --- |
| `0x004d3630` | [CPod__VFunc_66_UpdateMotionAndAccumulateScalar](CPod__VFunc_66_UpdateMotionAndAccumulateScalar.md) | CPOD vtable slot 66 override that forwards motion/effect update and accumulates a vfunc-returned scalar into `this+0x84` | ~32 bytes |

## Boundary

Static retail-binary evidence only. Exact CPOD source identity, slot contract, concrete layout, scalar meaning, runtime motion behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
