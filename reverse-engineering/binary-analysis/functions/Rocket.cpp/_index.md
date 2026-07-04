# Rocket.cpp Functions

Wave1196 current-risk update: Wave1196 (`wave1196-round-rocket-projectile-vfunc-residual-current-risk-review`) accounts for `4 Round/Rocket projectile vfunc residual score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `VFuncSlot_39_004d8ae0`, `VFuncSlot_66_004d8e40`, `VFuncSlot_00_004d9910`, and `CRocket__VFunc_22_CreateBigRocketEngineEffects`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`, then `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`, then final dry updated=0 skipped=4. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `881/1179 = 74.72%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `7 xref rows`, `1386 instruction rows`, and `4 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact source virtual names, exact hit/collision/event/effect layouts, concrete CRound/CMissile/CRocket/particle-handle layouts, runtime projectile behavior, runtime engine-effect behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1196; wave1196-round-rocket-projectile-vfunc-residual-current-risk-review; 881/1179 = 74.72%; 4 Round/Rocket projectile vfunc residual score17 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=47; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; VFuncSlot_39_004d8ae0; VFuncSlot_66_004d8e40; VFuncSlot_00_004d9910; CRocket__VFunc_22_CreateBigRocketEngineEffects; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 1386 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

> Source family: CRocket object lifecycle/render/effect helpers | Binary: `BEA.exe` (Steam build)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This page tracks saved Ghidra evidence for the CRocket object family. The current public-safe evidence is static retail-binary read-back only; the current Stuart source snapshot does not prove exact source file or virtual method names for these two entries.

## Wave1170 Actor-Derived Lifecycle Cleanup Review

Wave1170 (`wave1170-actor-derived-lifecycle-cleanup-current-risk-review`) re-read `CRocket__scalar_deleting_dtor` and `CRocket__dtor_base` inside `6 actor-derived lifecycle cleanup current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra export evidence verified the scalar-deleting wrapper DATA vtable xref and the base destructor path that destroys the `+0xec` particle/global-list array before delegating to `CActor__dtor_base`. This was a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified`.

Runtime rocket cleanup behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1170; wave1170-actor-derived-lifecycle-cleanup-current-risk-review; 666/1179 = 56.49%; 6 actor-derived lifecycle cleanup current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 513; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 100 instruction rows; CRocket__scalar_deleting_dtor; CSphereTrigger__scalar_deleting_dtor; CEscapePod__scalar_deleting_dtor; CRocket__dtor_base; CSphereTrigger__dtor_base; CEscapePod__dtor_base; Wave459; Wave460; Wave1022; [maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Wave1022 Object-Lifecycle Destructor Review

Wave1022 (`object-lifecycle-dtor-review-wave1022`) re-read `0x004bfe10 CRocket__dtor_base` as part of the adjacent destructor strip. The row still reads back as `void __fastcall CRocket__dtor_base(void * this)`; static evidence keeps it as the body called by `CRocket__scalar_deleting_dtor`, destroying the `+0xec` particle/global-list array through `CDXLandscape__DestroyArrayWithCallback` and `CParticleManager__RemoveFromGlobalList_Thunk` before delegating to `CActor__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bfe10 CRocket__dtor_base; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified.

Runtime rocket cleanup behavior, exact array element layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x004d7b10` | `CRocket__Init` | Init-style vtable slot 9 entry that adjusts init flags, loads `m_rocket.msh`, creates/stores the render object, copies init state, seeds rocket fields, and delegates to `CActor__Init`. | Wave492 |
| `0x004d8040` | `CRocket__VFunc_22_CreateBigRocketEngineEffects` | Vtable slot 22 helper that resolves `Big Rocket Engine Effect` and creates four particle effects using handle slots beginning at `this+0xec`. | Wave492 |

## Wave492 Read-Back

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave492-rocket-round-004d7b10/`
- Apply script: `tools/ApplyRocketWave492.java`
- Probe: `tools/ghidra_rocket_wave492_probe.py`
- Test alias: `npm run test:ghidra-rocket-wave492`
- Dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
- Apply summary: `updated=2 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back verified CRocket vtable `0x005dd458` slot 9 and slot 22, metadata/comments/signatures, tags, decompile exports, DATA xrefs from `0x005dd47c` and `0x005dd4b0`, instruction rows including `CRocket__Init` `RET 0x4`, focused probe status `PASS`, npm probe status `PASS`, and queue refresh status `PASS`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-084058_post_wave492_rocket_verified` (`19` files, `157584263` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

Wave492 is saved static Ghidra refinement only. Exact source virtual names, concrete `CRocket` / init / particle-handle layouts, runtime rocket launch/render/effect behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
