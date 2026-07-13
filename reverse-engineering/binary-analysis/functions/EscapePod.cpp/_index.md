# EscapePod.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source family: escape-pod lifecycle/render-resource helpers | Binary: `BEA.exe` (Steam build)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This page tracks saved Ghidra evidence for escape-pod functions. The current public-safe evidence is static retail-binary read-back only; runtime escape-pod behavior and exact source method identity remain open.

## Wave1170 Actor-Derived Lifecycle Cleanup Review

Wave1170 (`wave1170-actor-derived-lifecycle-cleanup-current-risk-review`) re-read `CEscapePod__scalar_deleting_dtor` and `CEscapePod__dtor_base` inside `6 actor-derived lifecycle cleanup current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra export evidence verified the scalar-deleting wrapper DATA vtable xref and the base destructor path that removes the `+0xe0` particle/global-list node before delegating to `CActor__dtor_base`. This was a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified`.

Runtime escape-pod cleanup behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1170; wave1170-actor-derived-lifecycle-cleanup-current-risk-review; 666/1179 = 56.49%; 6 actor-derived lifecycle cleanup current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 513; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 100 instruction rows; CRocket__scalar_deleting_dtor; CSphereTrigger__scalar_deleting_dtor; CEscapePod__scalar_deleting_dtor; CRocket__dtor_base; CSphereTrigger__dtor_base; CEscapePod__dtor_base; Wave459; Wave460; Wave1022; [maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Wave1022 Object-Lifecycle Destructor Review

Wave1022 (`object-lifecycle-dtor-review-wave1022`) re-read `0x004c0000 CEscapePod__dtor_base` as part of the adjacent destructor strip. The row still reads back as `void __fastcall CEscapePod__dtor_base(void * this)`; static evidence keeps it as the body called by `CEscapePod__scalar_deleting_dtor`, removing the `+0xe0` particle/global-list node through `CParticleManager__RemoveFromGlobalList` before delegating to `CActor__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004c0000 CEscapePod__dtor_base; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified.

Runtime escape-pod cleanup behavior, exact node layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x0044aab0` | `CEscapePod__InitRocketMeshAndEngineEffect` | Init-style helper that adjusts init flags, builds a `CResourceDescriptor` for `m_rocket.msh`, creates the render/resource object, calls `CActor__Init`, and attaches `Muspell_Engine_Small_Effect` when the node is found | `ghidra_attachment_escape_pause_signature_2026-05-13.md` |

## Boundaries

- Wave 365 corrected the older `CEscapePod__VFunc_09_0044aab0` label to the behavior-bounded saved name above.
- This is saved static Ghidra metadata, decompile, xref, instruction, and tag evidence only.
- Exact source method name, concrete `CEscapePod` / init layouts, local variables, runtime escape-pod behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
