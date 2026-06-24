# Wave1129 Lifecycle / Init Current-Risk Review

Status: complete static comment/tag normalization evidence
Date: 2026-06-05
Scope: `wave1129-lifecycle-init-current-risk-review`

Wave1129 accounts for `5 rows` from the Wave1108 current focused continuity denominator as a score-22 lifecycle/init current-risk cluster. This wave uses fresh Ghidra export evidence plus narrow comment/tag normalization. Current focused accounting moves to `155/1179 = 13.15%` of the continuity denominator. The live regenerated current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00405970 CDXCockpit__scalar_deleting_dtor` | `CDXCockpit` vtable `0x005d88b0[1]` DATA xref `0x005d88b4`; scalar-deleting destructor shape calls `CDXCockpit__dtor_base_thunk`, tests the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |
| `0x00421a80 CCarrier__Init` | `0x005e203c[8]` DATA xref `0x005e205c`; caller xref `0x0044dfcc FenrirEffects__InitBurningAndEngineHandles_0044dfb0`; calls `CAirUnit__Init`, allocates Carrier.cpp child helpers at `+0x208` and `+0x13c`, and preserves source-absence boundary. |
| `0x00422440 CCarver__Init` | `0x005e0d90[8]` DATA xref `0x005e0db0`; calls `CAirUnit__Init`, allocates `CCarverGuide` at `+0x208` and a CCarverAI/Warspite-adjacent helper at `+0x13c`, starts launch-animation context, and seeds wing/attack fields. |
| `0x00422970 CCarverAI__CanStartAttack` | `0x005e0d90[103]` DATA xref `0x005e0f2c`; returns true only when the wing/blend threshold and longer `+0x288` attack cooldown allow it. |
| `0x00424710 CCockpit__scalar_deleting_dtor` | `CCockpit` vtable `0x005d9524[1]` DATA xref `0x005d9528`; scalar-deleting destructor shape calls `CCockpit__dtor_base`, tests the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |

Mutation status:

- Comment/tag normalization.
- `69 tags` added.
- Two cockpit destructor comments normalized to remove old “tags unproven” wording after the tags were saved.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `5` / `5` / `6` / `113` / `5`.
- Pre vtable slot/type exports: `416` / `4`.
- `ApplyLifecycleInitCurrentRiskWave1129.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=69 missing=0 bad=0`.
- `ApplyLifecycleInitCurrentRiskWave1129.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=69 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyLifecycleInitCurrentRiskWave1129.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `5` / `5` / `6` / `113` / `5`.
- Post vtable slot/type exports: `416` / `4`.
- Pre/post instruction, xref, and vtable-slot exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`.

What this proves:

- The five target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1129-lifecycle-init-current-risk-review`, `wave1129-readback-verified`, `current-risk-review`, `score-22-current-risk`, `lifecycle-init-review`, `tag-normalized`, and `vtable`.
- The comments, xrefs, vtable slots, instruction windows, and decompile rows remain coherent with prior cockpit, carrier, and Carver lifecycle/init evidence.
- The older cockpit destructor tag-gap wording is closed in the saved Ghidra project.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime cockpit behavior.
- Runtime carrier behavior.
- Runtime Carver/CarverAI attack behavior.
- Exact source-body identity.
- Concrete `CCockpit`, `CDXCockpit`, `CCarrier`, `CCarver`, `CCarverAI`, helper, or vtable layout semantics.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
