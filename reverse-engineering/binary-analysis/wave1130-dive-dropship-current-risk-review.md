# Wave1130 Dive/Dropship Current-Risk Review

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1130-dive-dropship-current-risk-review`

Wave1130 accounts for `6 rows` from the Wave1108 current focused continuity denominator as a score-22 DiveBomber/Dropship aircraft current-risk cluster. This wave uses fresh Ghidra export evidence plus narrow tag-only normalization. Current focused accounting moves to `161/1179 = 13.66%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00445380 CDiveBomberAI__scalar_deleting_dtor` | `0x005db1b0` DATA xref; scalar-deleting destructor wrapper calls `CDiveBomberAI__dtor_base`, conditionally frees via `OID__FreeObject`, and returns `this`. |
| `0x00445440 CDiveBomberGuide__scalar_deleting_dtor` | `0x005db184` DATA xref; scalar-deleting destructor wrapper calls `CDiveBomberGuide__dtor_base`, conditionally frees via `OID__FreeObject`, and returns `this`. |
| `0x00446d70 CDropship__Init` | `0x005e1dfc` DATA xref; initializes `CAirUnit`, selects `wingflat` / `doorclosed`, creates `CMCDropship`, and resolves thruster context. |
| `0x00447040 CDropshipAI__scalar_deleting_dtor` | `0x005db1f8` DATA xref; scalar-deleting destructor wrapper calls `CDropshipAI__dtor_base`, conditionally frees via `OID__FreeObject`, and returns `this`. |
| `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits` | `0x005e1ee0` DATA xref; door/thruster/child-unit vtable body calls the dust helper at `0x004472b2` and `0x004473f9`. |
| `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust` | Direct calls from `CDropship__ProcessDoorThrustersAndChildUnits`; stdcall helper builds a stack-local line, samples/traces heightfield context, and spawns thruster dust. |

Mutation status:

- Tag-only normalization.
- `42 tags` added.
- No rename.
- No signature change.
- No comment change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `6` / `6` / `7` / `1049` / `6`.
- Pre vtable slot exports: `512`.
- `ApplyDiveDropshipCurrentRiskWave1130.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0`.
- `ApplyDiveDropshipCurrentRiskWave1130.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyDiveDropshipCurrentRiskWave1130.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `6` / `6` / `7` / `1049` / `6`.
- Post vtable slot exports: `512`.
- Pre/post metadata, instruction, xref, and vtable-slot exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`.

What this proves:

- The six target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1130-dive-dropship-current-risk-review`, `wave1130-readback-verified`, `current-risk-review`, `score-22-current-risk`, and `aircraft-current-risk-review`.
- The comments, xrefs, instruction windows, decompile rows, and vtable slots remain coherent with prior DiveBomber/Dropship aircraft evidence.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime dive-bomber AI behavior.
- Runtime dropship door behavior.
- Runtime thruster dust behavior.
- Runtime child-unit deployment.
- Exact source-body identity.
- Concrete `CDiveBomberAI`, `CDiveBomberGuide`, `CDropship`, `CDropshipAI`, helper, or vtable layout semantics.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
