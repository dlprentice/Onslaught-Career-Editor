# Wave1151 Mixed Score21 Current-Risk Readiness Note

Status: complete static tag-only normalization
Date: 2026-06-05
Scope: `wave1151-mixed-score21-current-risk-review`

Wave1151 re-read thirteen score21 current-risk rows with fresh Ghidra exports, then saved tag-only normalization with the `wave1151-mixed-score21-current-risk-review` and `wave1151-readback-verified` tags. The wave made no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and no Codex subagent.

Probe token anchor: Wave1151; wave1151-mixed-score21-current-risk-review; 368/1179 = 31.21%; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 811; current risk candidates: 6166; mixed score21 current-risk review; fresh Ghidra export; tag-only normalization; 81 tags; resource descriptor cleanup thunk, cockpit destructor thunk, primitive collision vfunc wrappers, building occupancy/static-shadow vfunc, DeviceObject destructor thunk, frontend multiplayer text helper, world occupancy rasterizer, menu-item destructor thunk, RTBuilding random linked entry, and CRT runtime thunk/path/float-dispatch helpers; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk; CDXCockpit__dtor_base_thunk; CCylinder__VFunc_01_004059a0; CLine__VFunc_01_004098c0; CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward; DeviceObject__dtor_thunk; FrontEndText__GetMultiplayerLevelDescriptionByType; CWorld__RasterizeFootprintIntoOccupancyBitplanes; CMenuItem__Destructor_Thunk; CRTBuilding__VFuncSlot10_PickRandomLinkedEntry; CRT__FpuIntrinsicDispatch2Thunk; CRT__SpawnSearchPathWithFallbackExtensions; CRT__FloatDispatchAmsgExitCode2Thunk; [maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv` / `post-metadata.tsv`: `13` rows, `targets=13 found=13 missing=0`.
- `pre-tags.tsv` / `post-tags.tsv`: `13` rows, `missing=0`.
- `pre-xrefs.tsv` / `post-xrefs.tsv`: `89` rows.
- `pre-instructions.tsv` / `post-instructions.tsv`: `593` instruction rows, `targets=13 missing=0`.
- `pre-decompile/index.tsv` / `post-decompile/index.tsv`: `13` rows, `targets=13 dumped=13 missing=0 failed=0`.
- Tag dry/apply/final dry: `tags_added=81` in dry/apply, then `tags_added=0` and `skipped=13` on final dry.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected, exported, mutated tags, read back, and audited the tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00403ff0 CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk` | Resource descriptor cleanup thunk calling `CRT__EhVectorDestructorIterator_WithUnwind` with `CResourceDescriptor__dtor`. |
| `0x00405990 CDXCockpit__dtor_base_thunk` | Cockpit destructor jump thunk into `CCockpit__dtor_base`. |
| `0x004059a0 CCylinder__VFunc_01_004059a0` | Primitive collision wrapper dispatching through target vfunc `+0x8`. |
| `0x004098c0 CLine__VFunc_01_004098c0` | Primitive collision wrapper dispatching through target vfunc `+0x10`. |
| `0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward` | Building slot 2 removes from world occupancy, updates static-shadow visibility, and forwards. |
| `0x004661c0 DeviceObject__dtor_thunk` | DeviceObject destructor thunk to `0x00512d50`. |
| `0x0046a220 FrontEndText__GetMultiplayerLevelDescriptionByType` | Multiplayer level-description text resolver with wide-string fallback. |
| `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes` | World occupancy rasterizer and optional static-shadow rebuild helper. |
| `0x004cf050 CMenuItem__Destructor_Thunk` | Menu-item destructor thunk reached from the mouse-sensitivity scalar-deleting destructor. |
| `0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry` | Random linked-entry selector over `this+0x54/+0x58`. |
| `0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk` | CRT/FPU intrinsic dispatch thunk with broad math/renderer/gameplay/UI xrefs. |
| `0x00564a0b CRT__SpawnSearchPathWithFallbackExtensions` | CRT spawn path/fallback-extension probe helper. |
| `0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk` | CRT float-conversion default-abort thunk that calls `__amsg_exit` with error code `2`. |

Accounting after Wave1151:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `368/1179 = 31.21%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 811.

This is static Ghidra evidence only. Runtime resource cleanup, runtime cockpit/collision/building/device/frontend/world/menu/CRT behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
