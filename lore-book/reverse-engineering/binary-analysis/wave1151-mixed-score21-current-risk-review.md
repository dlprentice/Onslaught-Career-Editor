# Wave1151 Mixed Score21 Current-Risk Review

Wave1151 (`wave1151-mixed-score21-current-risk-review`) accounts for `13 current-risk rows` from the Wave1108 current focused denominator as a mixed score21 current-risk review. It used fresh Ghidra exports, then saved tag-only normalization for all thirteen rows. It made no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and used no Codex subagent.

Probe token anchor: Wave1151; wave1151-mixed-score21-current-risk-review; 368/1179 = 31.21%; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 811; current risk candidates: 6166; mixed score21 current-risk review; fresh Ghidra export; tag-only normalization; 81 tags; resource descriptor cleanup thunk, cockpit destructor thunk, primitive collision vfunc wrappers, building occupancy/static-shadow vfunc, DeviceObject destructor thunk, frontend multiplayer text helper, world occupancy rasterizer, menu-item destructor thunk, RTBuilding random linked entry, and CRT runtime thunk/path/float-dispatch helpers; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk; CDXCockpit__dtor_base_thunk; CCylinder__VFunc_01_004059a0; CLine__VFunc_01_004098c0; CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward; DeviceObject__dtor_thunk; FrontEndText__GetMultiplayerLevelDescriptionByType; CWorld__RasterizeFootprintIntoOccupancyBitplanes; CMenuItem__Destructor_Thunk; CRTBuilding__VFuncSlot10_PickRandomLinkedEntry; CRT__FpuIntrinsicDispatch2Thunk; CRT__SpawnSearchPathWithFallbackExtensions; CRT__FloatDispatchAmsgExitCode2Thunk; [maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00403ff0` | `CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk` | Resource-descriptor cleanup thunk: advances `ECX` by `8`, passes element size `0x41c` and count `1`, and calls `CRT__EhVectorDestructorIterator_WithUnwind` with `CResourceDescriptor__dtor`. |
| `0x00405990` | `CDXCockpit__dtor_base_thunk` | Cockpit destructor jump thunk; forwards to `CCockpit__dtor_base` and is called by `CDXCockpit__scalar_deleting_dtor`. |
| `0x004059a0` | `CCylinder__VFunc_01_004059a0` | Primitive collision vfunc wrapper; forwards four stack arguments plus `this` into `dispatchObject` vfunc `+0x8`. |
| `0x004098c0` | `CLine__VFunc_01_004098c0` | Primitive collision vfunc wrapper; forwards the receiver plus four stack arguments into `dispatch_target` vfunc `+0x10`. |
| `0x00417870` | `CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward` | CBuilding/CSimpleBuilding slot 2 body; removes from world occupancy, updates static-shadow visibility, and forwards to `0x004f95d0`. |
| `0x004661c0` | `DeviceObject__dtor_thunk` | DeviceObject destructor thunk; jumps to `0x00512d50`, whose body unlinks from DeviceObject global lists rooted at `DAT_00889074` and `DAT_00889078`. |
| `0x0046a220` | `FrontEndText__GetMultiplayerLevelDescriptionByType` | Frontend multiplayer level description helper; maps level type to `CText__GetStringById` and falls back to `Unknown Multiplayer Level Description`. |
| `0x004bd5c0` | `CWorld__RasterizeFootprintIntoOccupancyBitplanes` | World occupancy rasterizer; clamps bounds to `0..511`, samples height/normal, sets/clears occupancy bits, and optionally rebuilds tracked-unit static shadows. |
| `0x004cf050` | `CMenuItem__Destructor_Thunk` | Menu-item destructor jump thunk; observed caller `CMouseSensitivityMenuItem__scalar_deleting_dtor` destroys the base menu-item subobject before optional free. |
| `0x004dba40` | `CRTBuilding__VFuncSlot10_PickRandomLinkedEntry` | RTBuilding vtable slot 10 helper; returns null for zero count, otherwise chooses `rand() % *(this+0x58)` and walks entries rooted at `this+0x54`. |
| `0x0055e3ea` | `CRT__FpuIntrinsicDispatch2Thunk` | CRT/FPU intrinsic dispatch thunk; tail-calls `__cintrindisp2` with broad math/renderer/gameplay/UI xrefs rather than a sprite-local owner. |
| `0x00564a0b` | `CRT__SpawnSearchPathWithFallbackExtensions` | CRT spawn path helper; probes slash/backslash/drive-colon markers, appends fallback extensions, validates candidates, and dispatches to `CRT__SpawnResolvedPathWithBuiltCommandEnv`. |
| `0x00569cb8` | `CRT__FloatDispatchAmsgExitCode2Thunk` | CRT float-conversion default-abort thunk; pushes runtime error code `2`, calls `__amsg_exit`, and returns. |

Fresh primary exports verified `13` metadata rows, `13` tag rows, `89` xref rows, `593` body-instruction rows, and `13` decompile rows before and after the tag write. The mutation logs reported:

- Dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=81 missing=0 bad=0`
- Apply: `updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=81 missing=0 bad=0`
- Final dry: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`

The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence and tag coverage for the selected current-risk rows only. Runtime resource cleanup, runtime cockpit/collision/building/device/frontend/world/menu/CRT behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
