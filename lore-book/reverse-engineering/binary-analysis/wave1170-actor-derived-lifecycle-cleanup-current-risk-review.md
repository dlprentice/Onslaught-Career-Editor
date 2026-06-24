# Wave1170 Actor-Derived Lifecycle Cleanup Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1170-actor-derived-lifecycle-cleanup-current-risk-review`

Wave1170 accounts for six actor-derived lifecycle cleanup current-risk rows from the `wave1108-current-risk-rank` denominator with fresh Ghidra export evidence. The pass is read-only: no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

| Address | Saved function | Static read-back evidence |
| --- | --- | --- |
| `0x004bfd40` | `CRocket__scalar_deleting_dtor` | DATA vtable xref `0x005dd45c`; calls `CRocket__dtor_base`, conditionally frees `this` through `CDXMemoryManager__Free` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfda0` | `CSphereTrigger__scalar_deleting_dtor` | DATA vtable xref `0x005dce68`; calls `CSphereTrigger__dtor_base`, conditionally frees `this` through `CDXMemoryManager__Free` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfde0` | `CEscapePod__scalar_deleting_dtor` | DATA vtable xref `0x005dc834`; calls `CEscapePod__dtor_base`, conditionally frees `this` through `CDXMemoryManager__Free` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfe10` | `CRocket__dtor_base` | Called by the scalar-deleting wrapper; destroys the `+0xec` particle/global-list array through `CRT__EhVectorDestructorIterator_WithUnwind` and `CParticleManager__RemoveFromGlobalList_Thunk`, then delegates to `CActor__dtor_base`. |
| `0x004bff40` | `CSphereTrigger__dtor_base` | Called by the scalar-deleting wrapper; clears `CSPtrSet` at `+0x8c`, removes the `+0x7c` particle/global-list node through `CParticleManager__RemoveFromGlobalList`, then delegates to `CComplexThing__dtor_base`. |
| `0x004c0000` | `CEscapePod__dtor_base` | Called by the scalar-deleting wrapper; removes the `+0xe0` particle/global-list node through `CParticleManager__RemoveFromGlobalList`, then delegates to `CActor__dtor_base`. |

Evidence counts:

- Fresh Ghidra exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `100` instruction rows, and `6` decompile rows.
- Queue/static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting advances to `666/1179 = 56.49%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 513.
- Verified backup: `G:\GhidraBackups\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The six selected lifecycle cleanup rows still read back with the saved Wave459/Wave460 static names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The scalar-deleting wrappers remain tied to their DATA vtable slots and base destructor calls.
- The base destructor bodies remain bounded to particle/global-list cleanup and base-class teardown paths.

What remains unproven:

- Runtime rocket, sphere-trigger, or escape-pod cleanup behavior.
- Exact concrete object layouts beyond observed static offsets.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1170; wave1170-actor-derived-lifecycle-cleanup-current-risk-review; 666/1179 = 56.49%; 6 actor-derived lifecycle cleanup current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 513; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 100 instruction rows; CRocket__scalar_deleting_dtor; CSphereTrigger__scalar_deleting_dtor; CEscapePod__scalar_deleting_dtor; CRocket__dtor_base; CSphereTrigger__dtor_base; CEscapePod__dtor_base; Wave459; Wave460; Wave1022; G:\GhidraBackups\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
