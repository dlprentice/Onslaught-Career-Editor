# Wave1128 GeneralVolume Current-Risk Review

Status: complete static comment/tag normalization evidence
Date: 2026-06-05
Scope: `wave1128-generalvolume-current-risk-review`

Wave1128 accounts for `6 rows` from the Wave1108 current focused continuity denominator as a score-22 `CGeneralVolume` current-risk cluster. This wave uses fresh Ghidra export evidence plus narrow comment/tag normalization. Current focused accounting moves to `150/1179 = 12.72%` of the continuity denominator. The live regenerated current focused candidates: 1178; remaining active focused work: 1029. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00402020 CGeneralVolume__ResetCooldownTimestamp` | Stores `DAT_00672fd0` into `this+0xd4`; fresh xrefs include caller `0x0040c73c CGeneralVolume__ResetAndSetActiveReader` plus vtable DATA refs. |
| `0x0040b100 CGeneralVolume__ctor_base` | Installs the `CGeneralVolume` vtable pointer `PTR_LAB_005d892c` and clears `+0x4/+0x8/+0xc`; fresh callers include world occupancy, BattleEngine crosshair, static-shadow, and launch-position helpers. |
| `0x0040c720 CGeneralVolume__ResetAndSetActiveReader` | Calls `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, binds `this+0x264` through `CGenericActiveReader__SetReader`, then calls `CGeneralVolume__ResetCooldownTimestamp`. |
| `0x00412830 CGeneralVolume__DisableLinkedEntriesByNameAndReselect` | Walks linked entries, byte-compares the entry-name pointer at `entry+0xa4`, clears `entry+0x9c`, and calls `CBattleEngineJetPart__ChangeWeapon` when the selected entry was disabled. |
| `0x00413660 CGeneralVolume__ApplyYawInputByWeaponClass` | `CPlayer__ReceiveButtonAction` caller evidence at `0x004d337b`; scales yaw input using `DAT_00889304` class tokens `0xb/0xc`, `DAT_005d8cd8`, and `CGeneralVolume__ToDoubleIdentity`, then writes owner yaw field `+0x278`. |
| `0x004136e0 CGeneralVolume__ApplyPitchInputByWeaponClass` | `CPlayer__ReceiveButtonAction` caller evidence at `0x004d3390`; scales pitch input using `DAT_00889304` class tokens `0xb/0xc`, `DAT_005d8c90`, and `CGeneralVolume__ToDoubleIdentity`, then writes owner pitch field `+0x280`. |

Mutation status:

- Comment/tag normalization.
- `51 tags` added.
- Three comments normalized to remove the old “tags unproven” wording after the tags were saved.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `6` / `6` / `54` / `170` / `6`.
- `ApplyGeneralVolumeCurrentRiskWave1128.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0`.
- `ApplyGeneralVolumeCurrentRiskWave1128.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyGeneralVolumeCurrentRiskWave1128.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `6` / `6` / `54` / `170` / `6`.
- Pre/post instruction exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`, `19` files, `175934343` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`.

What this proves:

- The six target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1128-generalvolume-current-risk-review`, `wave1128-readback-verified`, `current-risk-review`, `score-22-current-risk`, `general-volume`, and `tag-normalized`.
- The comments, xrefs, instruction windows, and decompile rows remain coherent with the bounded static evidence from prior GeneralVolume waves.
- The older Wave966 tag gap for `0x00402020`, `0x0040b100`, and `0x0040c720` is closed in the saved Ghidra project.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime active-reader behavior.
- Runtime linked-entry or weapon-selection behavior.
- Runtime yaw/pitch control behavior.
- Exact source-body identity.
- Concrete `CGeneralVolume`, linked-entry, owner, weapon-class, or BattleEngine layout semantics.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
