# Ghidra CRTBuilding/CRTMesh Lifecycle Review Wave1068 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `rtbuilding-rtmesh-lifecycle-review-wave1068`

Wave1068 re-read the existing Wave496 CRTBuilding/CRTMesh lifecycle, pose-data, effect-cleanup, and mesh-LOD quality cluster with fresh metadata, tags, xrefs, instructions, decompile, context, and vtable exports. The saved names, signatures, comments, tags, and vtable anchors remain coherent with the static retail Ghidra evidence, so this wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Primary anchors:

| Address | Static evidence |
| --- | --- |
| `0x004db850 CRTBuilding__Destructor` | Resets CRTBuilding vtable `0x005de9c0`, decrements the referenced mesh/resource counter at `this+0x54 -> +0x170`, clears `this+0x54`, then chains into `CRTMesh__Destructor`. |
| `0x004db8d0 CRTBuilding__ScalarDeletingDestructor` | CRTBuilding vtable slot 0 wrapper; calls `CRTBuilding__Destructor`, frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)` when `flags & 1`, and returns `this`. |
| `0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry` | CRTBuilding vtable slot 10 helper; returns null for zero count, otherwise uses `_rand() % *(this+0x58)` and walks linked entries rooted at `this+0x54` through `entry+0x08`. |
| `0x004dc370 CRTMesh__Init` | CRTMesh vtable slot 1 init; initializes render-thing state, registers RTMesh console variables, resolves/falls back to a `CMesh`, allocates meshpose/effect arrays, and optionally creates an imposter. |
| `0x004dc950 CRTMesh__Destructor` | Resets CRTMesh vtable `0x005deb1c`, unlinks from global list anchors `DAT_0083cd5c/DAT_0083cd60`, clears particle effects, frees pose/imposter/effect resources, decrements mesh refcount, and restores base render-thing vtable. |
| `0x004dcb00 CRTMesh__FreePoseData` | Frees and nulls the four pose-data pointer fields at `+0x00/+0x04/+0x08/+0x0c`. |
| `0x004dcb70 CRTMesh__ScalarDeletingDestructor` | CRTMesh vtable slot 0 scalar-deleting destructor wrapper; calls `CRTMesh__Destructor`, frees on `flags & 1`, and returns `this`. |
| `0x004dd0c0 CRTMesh__CleanupAllEffects` | Static cleanup called from `0x0053e2e0 CDXEngine__Render`; walks the global RTMesh list and clears/removes active effect handles. |
| `0x004dd6b0 CRTMesh__SetQualityLevel` | Static quality setter called from `0x004cef50 CTreeDetail__SetQualityLevel`; writes mesh distance/LOD globals including `g_MeshQualityDistance`, `g_MeshLodBias`, and `_g_MeshQualityScaleFactor`. |
| `0x004dd770 CRTMesh__GetQualityLevel` | Static getter called from PauseMenu/CPauseMenu quality UI paths; maps `g_MeshQualityDistance` thresholds back to quality levels `0/1/2`. |

Context anchors:

- CRTBuilding vtable `0x005de9c0`: slot 0 `0x004db8d0`, slot 10 `0x004dba40`, shared slot 9 `0x004de070`, and several raw no-function slot pointers.
- CRTMesh vtable `0x005deb1c`: slot 0 `0x004dcb70`, slot 1 `0x004dc370`, slot 4 `0x004de060`, shared slot 9 `0x004de070`, slot 10 `0x00405930`, and several raw no-function slot pointers.
- Caller/context rows include `0x004dbc00 SharedVFunc__ReturnFalseRet4_004dbc00`, `0x004dbc30 CRTCutscene__scalar_deleting_dtor`, `0x004dbd50 CRenderThing__scalar_deleting_dtor`, `0x004cef50 CTreeDetail__SetQualityLevel`, `0x004cde60 PauseMenu__Init`, and `0x0053e2e0 CDXEngine__Render`.
- The seven context `MISSING` rows (`0x004dabb0`, `0x004dabc0`, `0x004dac10`, `0x004dc0d0`, `0x004dc2c0`, `0x004dc560`, `0x004dd810`) are intentional raw vtable-slot pointers with no function starts, not failed primary evidence.

Read-back evidence:

- Primary exports: `10` metadata rows, `10` tag rows, `14` xref rows, `788` function-body instruction rows, and `10` decompile rows.
- Context exports: `23` metadata rows, `23` tag rows, `60` xref rows, `2661` function-body instruction rows, and `23` decompile rows, including seven intentional no-function context rows.
- Vtable export: `48` rows from `0x005de9c0` and `0x005deb1c`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1258/1560 = 80.64%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The ten primary CRTBuilding/CRTMesh rows exist in the saved Ghidra project with expected Wave496 names, signatures, comments, and tags.
- The exported decompile, instructions, xrefs, and vtable slots remain coherent with the saved Wave496 mapping and the later Wave1046 render-object context.
- The review records this render-object lifecycle/LOD/effect-cleanup cluster in the Wave900+ continuation evidence set without adding new Ghidra mutations.

What remains unproven:

- Runtime RTMesh/building render behavior.
- Runtime mesh LOD / imposter / particle-effect cleanup behavior.
- Exact concrete `CRTBuilding`, `CRTMesh`, `CRenderThing`, meshpose, imposter, effect-array, and linked-list layouts.
- Exact source-body identity; `rtmesh.cpp` remains absent from the available Stuart source set.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1068; rtbuilding-rtmesh-lifecycle-review-wave1068; 0x004db850 CRTBuilding__Destructor; 0x004db8d0 CRTBuilding__ScalarDeletingDestructor; 0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry; 0x004dc370 CRTMesh__Init; 0x004dc950 CRTMesh__Destructor; 0x004dd0c0 CRTMesh__CleanupAllEffects; 0x004dd6b0 CRTMesh__SetQualityLevel; 0x004dd770 CRTMesh__GetQualityLevel; 812/1408 = 57.67%; 1258/1560 = 80.64%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified; read-only review.
