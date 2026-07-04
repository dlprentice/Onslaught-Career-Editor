# Wave1180 CInfantryUnit Lifecycle / VFunc Current-Risk Review

Status: complete read-only static current-risk review
Date: 2026-06-06
Scope: `wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review`

Wave1180 accounts for `8 CInfantryUnit lifecycle/vfunc current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It is a read-only review: no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Codex read-only consults used; one adversarial consult recommended already-counted CUnitAI door-wing rows, while Codex root rejected duplicate Wave1116 accounting and kept the CInfantryUnit slice. A second infantry-focused consult recommended the exact eight-row CInfantryUnit lifecycle/vfunc slice. Codex root final judgment checked the live metadata/tags/xrefs/decompile before counting the wave. No Cursor/Composer consults were used.

Current accounting after Wave1180:

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused | `812/1408 = 57.67%`, historical-retired/non-reconstructable |
| Wave911 top-500 risk-ranked | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `729/1179 = 61.83%` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `450` |
| Current risk candidates | `6166` |

Fresh export evidence:

| Artifact | Rows |
| --- | ---: |
| Metadata | `8` |
| Tags | `8` |
| Xrefs | `8` |
| Function-body instructions | `1150` |
| Decompile rows | `8` |

Reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x00488f10` | `CInfantryUnit__VFunc38_HandleHitOrDispatchHit` | DATA xref `0x005e27c8` from the CInfantryUnit primary vtable; slot-38 hit/collision dispatch boundary from Wave1076. |
| `0x00488f60` | `CInfantryUnit__VFunc02_ClearParticleLinkAndForward` | DATA xref `0x005e2734`; Wave805 cleanup extension clears the `this+0x270` particle/effect owner-link cell and forwards to CUnit slot-2 cleanup. |
| `0x00488f80` | `CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius` | DATA xref `0x005e27b8`; slot-34 collision-sphere helper with Infantry.cpp debug allocation evidence. |
| `0x00489090` | `CInfantryUnit__VFunc59_SelectAnimationMode` | DATA xref `0x005e281c`; slot-59 animation-mode selector using mesh-animation lookups before `CComplexThing__SetAnimMode`. |
| `0x004892c0` | `CInfantryUnit__VFunc65_UpdateMotionAnimationState` | DATA xref `0x005e2834`; slot-65 motion/effects/shadow animation-state update boundary. |
| `0x00489650` | `CInfantryUnit__VFunc39_HandleCollisionDamageReaction` | DATA xref `0x005e27cc`; slot-39 collision-damage/reaction path that reaches damage, random, distance/vector, animation, and effect helpers. |
| `0x00489b40` | `CInfantryUnit__VFunc49_HandleDeathPickupAndEffects` | DATA xref `0x005e27f4`; slot-49 destroyed-state, pickup, particle-effect, and linked-flag cleanup completion path. |
| `0x0050f1a0` | `CInfantryUnit__Destructor_VFunc01` | Call xref `0x0050ee33` from `CInfantryUnit__scalar_deleting_dtor`; destructor body removes the `this+0x270` global-list node and forwards to `CUnit__dtor_base`. |

Prior context:

- Wave557 corrected the CInfantryUnit destructor wrapper/body signatures.
- Wave805 hardened `CInfantryUnit__VFunc02_ClearParticleLinkAndForward`.
- Wave1076 recovered the six adjacent CInfantryUnit primary-vtable function boundaries and tied them to CInfantryUnit primary vtable `0x005e2730`.
- Wave1116 already counted the CUnitAI door-wing rows, so those rows were rejected for Wave1180 duplicate accounting despite adversarial consult interest.

Backup:

`[maintainer-local-ghidra-backup-root]\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified`

Backup verification: `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference from the original game. Actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

What this proves:

- The eight target function rows exist in the saved Ghidra project and match the saved names/signatures/comments.
- Fresh DATA/call xrefs still tie the seven CInfantryUnit vfunc rows to the CInfantryUnit primary vtable or scalar-deleting destructor path.
- Fresh instruction and decompile exports still support the prior Wave557/Wave805/Wave1076 CInfantryUnit static contract.
- The rows are now explicitly counted against the active Wave1108 current-risk denominator.

What remains unproven:

- Runtime infantry behavior.
- Runtime hit/collision/damage/death/pickup/effect behavior.
- Exact concrete CInfantryUnit/CUnit/CUnitAI/layout semantics.
- Exact source virtual names.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1180; wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review; 729/1179 = 61.83%; 8 CInfantryUnit lifecycle/vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 450; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; adversarial consult recommended already-counted CUnitAI door-wing rows; root rejected duplicate Wave1116 accounting; infantry consult recommended exact eight-row CInfantryUnit slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 1150 instruction rows; CInfantryUnit__VFunc38_HandleHitOrDispatchHit; CInfantryUnit__VFunc02_ClearParticleLinkAndForward; CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius; CInfantryUnit__VFunc59_SelectAnimationMode; CInfantryUnit__VFunc65_UpdateMotionAnimationState; CInfantryUnit__VFunc39_HandleCollisionDamageReaction; CInfantryUnit__VFunc49_HandleDeathPickupAndEffects; CInfantryUnit__Destructor_VFunc01; [maintainer-local-ghidra-backup-root]\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
