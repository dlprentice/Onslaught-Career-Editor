# Wave1180 CInfantryUnit Lifecycle / VFunc Current-Risk Review Readiness Note

Status: complete read-only static current-risk review
Date: 2026-06-06
Scope: `wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review`

Wave1180 accounts for `8 CInfantryUnit lifecycle/vfunc current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It made no mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit` | DATA xref `0x005e27c8`; CInfantryUnit primary vtable slot-38 hit/collision dispatch boundary. |
| `0x00488f60 CInfantryUnit__VFunc02_ClearParticleLinkAndForward` | DATA xref `0x005e2734`; clears `this+0x270` particle/effect owner-link cell and forwards to CUnit slot-2 cleanup. |
| `0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius` | DATA xref `0x005e27b8`; collision-sphere helper with Infantry.cpp allocation-token evidence. |
| `0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode` | DATA xref `0x005e281c`; animation-mode selector using mesh-animation lookup evidence. |
| `0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState` | DATA xref `0x005e2834`; motion/effects/shadow animation-state update boundary. |
| `0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction` | DATA xref `0x005e27cc`; collision-damage/reaction path with damage/vector/random/effect helper evidence. |
| `0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects` | DATA xref `0x005e27f4`; destroyed-state, pickup, particle-effect, and linked-flag cleanup path. |
| `0x0050f1a0 CInfantryUnit__Destructor_VFunc01` | Call xref `0x0050ee33` from `CInfantryUnit__scalar_deleting_dtor`; removes `this+0x270` global-list node and forwards to `CUnit__dtor_base`. |

Read-back evidence:

- Post exports: `8` metadata rows, `8` tag rows, `8` xref rows, `1150` instruction rows, and `8` decompile rows.
- Queue/accounting after Wave1180: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, `729/1179 = 61.83%` current focused accounting, and `450` remaining active focused rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.

Consult note:

- Codex read-only consults were used. One adversarial consult recommended already-counted CUnitAI door-wing rows; Codex root rejected duplicate Wave1116 accounting. The infantry-focused consult recommended the exact eight-row CInfantryUnit slice. Codex root final judgment checked live metadata/tags/xrefs/decompile. No Cursor/Composer consults were used.

What this proves:

- The eight target function rows exist in the saved Ghidra project and match the saved names/signatures/comments.
- Fresh vtable DATA xrefs and the destructor call xref still support the prior CInfantryUnit static contract.
- The rows are now explicitly counted against the active Wave1108 current-risk denominator.

What remains unproven:

- Runtime infantry behavior, runtime hit/collision/damage/death/pickup/effect behavior, exact concrete CInfantryUnit/CUnit/CUnitAI/layout semantics, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference from the original game. Actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

Probe token anchor: Wave1180; wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review; 729/1179 = 61.83%; 8 CInfantryUnit lifecycle/vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 450; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; adversarial consult recommended already-counted CUnitAI door-wing rows; root rejected duplicate Wave1116 accounting; infantry consult recommended exact eight-row CInfantryUnit slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 1150 instruction rows; CInfantryUnit__VFunc38_HandleHitOrDispatchHit; CInfantryUnit__VFunc02_ClearParticleLinkAndForward; CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius; CInfantryUnit__VFunc59_SelectAnimationMode; CInfantryUnit__VFunc65_UpdateMotionAnimationState; CInfantryUnit__VFunc39_HandleCollisionDamageReaction; CInfantryUnit__VFunc49_HandleDeathPickupAndEffects; CInfantryUnit__Destructor_VFunc01; [maintainer-local-ghidra-backup-root]\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
