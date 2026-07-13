# ParticleSet.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1150 current-risk update: Wave1150 (`wave1150-particle-set-render-tail-current-risk-review`) accounts for `11 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle set/render tail current-risk review. It uses fresh Ghidra export evidence for particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `355/1179 = 30.11%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; focused threshold `15`; not Wave911 reconstruction. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1150; wave1150-particle-set-render-tail-current-risk-review; 355/1179 = 30.11%; 11 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; current risk candidates: 6166; particle set/render tail current-risk review; fresh Ghidra export; particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CParticle__ApplyParentTransformOrStoreLink; CPDSimpleSprite__VFunc_10_004c14f0; CPDSimpleSprite__VFunc_23_004c8040; CParticleSet__shared_scalar_deleting_dtor; CPDSelector__DispatchChildVFunc20; CParticleSet__InitType11; CParticleSet__InitType12; CParticleSet__InitType13; CParticleSet__FindByNameAndTrackLinkSlot; CParticleSet__LoadParticleSetFile; CParticleManager__UnlinkNodeByOffset3C40; [maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1149 current-risk update: Wave1149 (`wave1149-particle-effects-score20-current-risk-review`) accounts for `15 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle/effects score20 current-risk review. It uses fresh Ghidra export evidence for particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `344/1179 = 29.18%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; focused threshold `15`; not Wave911 reconstruction. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1149; wave1149-particle-effects-score20-current-risk-review; 344/1179 = 29.18%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; current risk candidates: 6166; particle/effects score20 current-risk review; fresh Ghidra export; particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CEngine__ConfigureParticleBurstForDistance; CParticleDescriptor__Update; CParticleDescriptor__Load; CEngine__ComputeSpriteTintByDistance; CParticleManager__SetParticleResource; CParticleManager__CleanupHandles; ParticleEffectLink__SetHandleStateAndClear; CParticleManager__InterpolatePositions; CParticleManager__CreateEffect; CParticleManager__UpdateParticleAndRecycleIfDead; CParticleManager__ProjectPointToTerrainWithRadiusClamp; CParticleManager__ComputeMinCameraDistanceSqForParticle; CParticleManager__DestroyParticleList; CParticleSet__CreateByType; CParticleSet__Init; [maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: ParticleSet.cpp | Binary: BEA.exe
> Debug Path: 0x00630fb0 (`[maintainer-local-source-export-root]\ParticleSet.cpp`)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

ParticleSet manages collections of related particles that form visual effects (explosions, smoke trails, sparks, etc.). Each particle set contains multiple particle descriptors and handles their lifecycle. The system uses a factory pattern with 13 different particle set types, each with distinct vtables and initialization parameters.

Key data files referenced:
- `data/ParticleSets/MainSet.par` - Main game particle sets
- `data/ParticleSets/Frontend.par` - Frontend/menu particle sets

Wave1118 (`wave1118-particle-message-current-risk-review`) re-read `0x004cc870 CParticleSet__dtor_base` and `0x004cd7f0 CParticleSet__LoadFromArchive` from the current score-26 focused queue with a fresh read-only Ghidra export and no mutation. Static evidence still confirms the base destructor restoring `PTR_LAB_005ddad4` and the archive loader's `0x1388c` workspace, token ids `0/1/2/3/4`, created-set vfunc `+0x18`, and reference-resolution path. Current focused accounting moves to `100/1179 = 8.48%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`. Runtime particle loading/visual behavior, exact archive/object layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x004cc020 | CParticleSet__CreateByType | ~2000 bytes | Factory method - sorted name lookup, type-specific allocation/vtable/default setup, name copy, and `DAT_0082b450` update (Wave463 hardened) |
| 0x004cc850 | CParticleSet__Init | ~40 bytes | Base class initialization - clears observed fields and installs the base particle-set vtable (Wave463 hardened) |
| 0x004cc870 | CParticleSet__dtor_base | ~16 bytes | Base destructor body - restores the base particle-set vtable pointer (Wave464 corrected from constructor-like label) |
| 0x004ccb40 | CParticleSet__shared_scalar_deleting_dtor | ~48 bytes | Shared scalar-deleting destructor wrapper - calls base dtor and conditionally frees `this` when flags bit 0 is set (Wave464 corrected) |
| 0x004cd290 | CParticleSet__InitType11 | ~64 bytes | Type 11 particle set init - installs CPDMesh-flavored vtable/defaults including `+0x64=100` and `+0x74=1` (Wave464 hardened) |
| 0x004cd2d0 | CParticleSet__InitType12 | ~48 bytes | Type 12 particle set init - clears shared fields and zeroes observed `+0x5c/+0x60/+0x64` defaults (Wave464 hardened) |
| 0x004cd3c0 | CParticleSet__InitType13 | ~260 bytes | Type 13 particle set init - clears extended fields and seeds scalar defaults including 1.0, 0.5, 5.0, 10, 180.0, and 360.0 (Wave464 hardened) |
| 0x004cd7a0 | CParticleSet__FindByNameAndTrackLinkSlot | ~80 bytes | Sorted particle-set/effect name lookup - callers pass `&DAT_0082b400`; stores cursor slot in `DAT_0082b3f8`, walks `+0x38`, compares name `+0x4` by `stricmp`, and returns with `RET 0x4` (Wave823 corrected from `CWorldPhysicsManager__FindNodeByNameGE`) |
| 0x004cd7f0 | CParticleSet__LoadFromArchive | ~624 bytes | Loads particle sets from tokenized archive format using a 0x1388c workspace and token ids 0/1/2/3/4 (Wave464 hardened) |
| 0x004cda60 | CParticleSet__LoadParticleSetFile | ~352 bytes | High-level loader - selects `MainSet.par` or `Frontend.par`, opens a `CDXMemBuffer`, and triggers archive load (Wave464 hardened) |
| 0x004cdb90 | CDXMemBuffer__dtor_base_Thunk | 5 bytes | Single-instruction jump thunk to `0x00547d90 CDXMemBuffer__dtor_base` used by `0x005d4230 Unwind@005d4230` for the ParticleSet.cpp stack-local `CDXMemBuffer` cleanup at `EBP-0x140` (Wave823 corrected) |

**Total: 11 functions**

## Particle Set Types

The factory method `CreateByType` supports 13 particle set types with different allocation sizes:

| Type ID | Alloc Size | Vtable | Notes |
|---------|------------|--------|-------|
| 1 | 0xD0 (208) | PTR_FUN_005ddf60 | Standard particles |
| 2 | 0xB4 (180) | PTR_FUN_005ddef8 | Velocity-based particles |
| 3 | 0x5C (92) | PTR_FUN_005dde90 | Minimal particle set |
| 4 | 0x7C (124) | PTR_FUN_005dde28 | With 4-element array |
| 5 | 0xB0 (176) | PTR_FUN_005dddc0 | RGB color particles |
| 6 | 0xD8 (216) | PTR_FUN_005ddd58 | Array-based (10 elements) |
| 7 | 0x84 (132) | PTR_FUN_005ddcf0 | Timed particles |
| 8 | 0xD0 (208) | PTR_FUN_005ddc88 | Complex with scale |
| 9 | 0x7C (124) | PTR_FUN_005ddc20 | Simple clearing type |
| 10 | 0x94 (148) | PTR_FUN_005ddbb8 | Position-based |
| 11 | 0x7C (124) | PTR_CPDMesh__scalar_deleting_dtor_005ddb3c | Via InitType11 helper |
| 12 | 0x68 (104) | PTR_CParticleSet__shared_scalar_deleting_dtor_005ddfc8 | Via InitType12 helper |
| 13 | 0xE4 (228) | PTR_CParticleSet__shared_scalar_deleting_dtor_005de030 | Via InitType13 helper (largest) |

## Key Constants (Float Hex Values)

Common float constants found in initialization:
- `0x3f800000` = 1.0f
- `0x3f000000` = 0.5f
- `0x41200000` = 10.0f
- `0x41a00000` = 20.0f
- `0x40a00000` = 5.0f
- `0x43340000` = 180.0f
- `0x43b40000` = 360.0f
- `0xbdcccccd` = -0.1f
- `0x3dcccccd` = 0.1f

## CParticleSet Base Class Layout

Based on common initialization patterns:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | vtable | Virtual function table pointer |
| 0x04 | 0x31 | name | Particle set name (strncpy, null-terminated at +0x35) |
| 0x38 | 4 | next | Linked list pointer to next particle set |
| 0x3C | 4 | [field_0xf] | Cleared during init |
| 0x40 | 4 | [field_0x10] | Cleared during init |
| 0x48 | 4 | [field_0x12] | Cleared during init |
| 0x50 | 4 | [field_0x14] | Cleared during init |
| 0x54 | 4 | [field_0x15] | Cleared during init |
| 0x5C+ | varies | type-specific | Type-specific particle parameters |

## Global Variables

| Address | Type | Name | Purpose |
|---------|------|------|---------|
| 0x0082b450 | CParticleSet* | g_pLastParticleSet | Most recently created/accessed particle set |
| 0x0082b3f8 | int* | g_pParticleSetListPtr | Pointer into particle set linked list |

## Wave1014 ParticleSet Load Lifecycle Read-Back

Wave1014 static re-audit (`particle-set-load-lifecycle-review-wave1014`) re-read the ParticleSet load/factory/lifecycle spine and found the saved Wave463/Wave464/Wave823 names, signatures, comments, and tags still coherent. Primary anchors include `0x004cc020 CParticleSet__CreateByType`, `0x004cc850 CParticleSet__Init`, `0x004ccb40 CParticleSet__shared_scalar_deleting_dtor`, `0x004ccc50 CPDSelector__DispatchChildVFunc20`, `0x004cd290 CParticleSet__InitType11`, `0x004cd2d0 CParticleSet__InitType12`, `0x004cd3c0 CParticleSet__InitType13`, `0x004cd7f0 CParticleSet__LoadFromArchive`, and `0x004cda60 CParticleSet__LoadParticleSetFile`.

Fresh target exports verified `13` metadata rows, `13` tag rows, `79` xref rows, `997` body-instruction rows, and `13` decompile rows. Context exports verified `16` metadata rows, `54` xref rows, `1206` body-instruction rows, and `16` decompile rows for adjacent Particle/ParticleManager/ParticleDescriptor/CDXMemBuffer support rows. `CParticleSet__LoadParticleSetFile` remains the high-level `MainSet.par` / `Frontend.par` loader and calls `CParticleSet__LoadFromArchive`, which calls `CParticleSet__CreateByType`; the observed stack-local `CDXMemBuffer` path remains bounded through `CDXMemBuffer__ctor`, `CDXMemBuffer__OpenReadMode11`, `CDXMemBuffer__Close_Thunk`, and `CDXMemBuffer__dtor_base_Thunk`.

No mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed. Export-contract closure remains `6238/6238 = 100.00%`; Wave911 focused progress remains `505/1408 = 35.87%`; expanded static surface progress is `729/1493 = 48.83%`; Wave911 top-500 risk-ranked coverage is `431/500 = 86.20%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified`. Probe token anchor: Wave1014; particle-set-load-lifecycle-review-wave1014; 0x004cc020 CParticleSet__CreateByType; 0x004cc850 CParticleSet__Init; 0x004ccb40 CParticleSet__shared_scalar_deleting_dtor; 0x004ccc50 CPDSelector__DispatchChildVFunc20; 0x004cd290 CParticleSet__InitType11; 0x004cd2d0 CParticleSet__InitType12; 0x004cd3c0 CParticleSet__InitType13; 0x004cd7f0 CParticleSet__LoadFromArchive; 0x004cda60 CParticleSet__LoadParticleSetFile; 0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40; 505/1408 = 35.87%; 729/1493 = 48.83%; 431/500 = 86.20%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified; no mutation.

This is static retail Ghidra evidence only. Runtime particle/effect loading, `.par` schema behavior, runtime render/effect behavior, exact source-body identity, concrete ParticleSet/CDXMemBuffer layouts, BEA patching, and rebuild parity remain separate proof.

## Wave761 Unwind Continuation Read-Back

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved ParticleSet.cpp-adjacent cleanup callbacks from `0x005d4100 Unwind@005d4100` through `0x005d41ce Unwind@005d41ce` as `void __cdecl Unwind@...(void)` compiler-generated SEH unwind rows. DATA scope-table refs `0x0061cc84` through `0x0061ccd4` point at `OID__FreeObject_Callback(*(EBP+0xc))` rows using debug path `0x00630fb0`, line token `0x10`, and allocation/type values `0x5f` through `0x68`; `0x005d4184 Unwind@005d4184` loads `ECX` from `*(EBP+0xc)` and jumps to `CParticleSet__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave762 Unwind Continuation Read-Back

Wave762 static read-back (`unwind-continuation-wave762`, `wave762-readback-verified`) continued the ParticleSet.cpp cleanup tranche and saved `0x005d41e4 Unwind@005d41e4`, `0x005d41fa Unwind@005d41fa`, `0x005d4210 Unwind@005d4210`, and `0x005d4230 Unwind@005d4230` as `void __cdecl Unwind@...(void)` compiler-generated SEH unwind rows. DATA scope-table refs `0x0061ccdc` through `0x0061cd14` point at three `OID__FreeObject_Callback(*(EBP+0xc))` rows using debug path `0x00630fb0`, line token `0x10`, and allocation/type values `0x69` through `0x6b`, followed by `CDXMemBuffer__dtor_base(EBP-0x140)` at `0x005d4230 Unwind@005d4230`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-143913_post_wave762_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave823 Particle Archive Buffer Cleanup Read-Back

Wave823 static read-back (`particle-archive-buffer-cleanup-wave823`, `wave823-readback-verified`) corrected two adjacent raw-commentless ParticleSet/CDXMemBuffer rows. `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot` supersedes the older `CWorldPhysicsManager__FindNodeByNameGE` label: callers pass `&DAT_0082b400`, the body stores the current link slot in `DAT_0082b3f8`, walks particle-set/effect nodes through `+0x38`, compares the caller `set_name` against node name `+0x4` with `stricmp`, and returns with `RET 0x4`, proving the old `unused_ctx` parameter was phantom. `0x004cdb90 CDXMemBuffer__dtor_base_Thunk` is a single-instruction jump thunk to `0x00547d90 CDXMemBuffer__dtor_base` and is referenced by `0x005d4230 Unwind@005d4230` for the ParticleSet.cpp stack-local buffer at `EBP-0x140`.

Queue after Wave823: `6098` total, `5628` commented, `470` commentless, strict proxy `5628/6098 = 92.29%`, next raw commentless row `0x004cf050 CMenuItem__Destructor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified`. This is saved static retail Ghidra evidence only; exact particle-set node layout, link-slot ownership beyond observed static cursor/global evidence, exact unwind parent/source-body identity, runtime particle/effect lookup behavior, runtime stack-local buffer lifetime, runtime particle archive behavior, BEA patching, and rebuild parity remain deferred.

## Loading Process

1. `LoadParticleSetFile(mode)` is called with mode:
   - 0 = Load MainSet.par
   - 1 = Load Frontend.par
   - 2 = Load MainSet.par (alternate path)

2. Allocates 200-byte filename buffer

3. Opens a stack `CDXMemBuffer` through the adjacent Wave420-corrected helper `CDXMemBuffer__OpenReadMode11` at `0x0048ddd0`

4. Calls `LoadFromArchive` which:
   - Destroys existing particle sets via vtable destructor calls
   - Allocates 0x1388C (80,012) bytes for particle data pool
   - Parses tokenized archive format (tokens 0-4 for structure)
   - For each particle set entry:
     - Allocates 1000-byte name buffer
     - Reads name and type from archive
     - Calls `CreateByType` to instantiate
     - Calls virtual method at vtable+0x18 to complete loading

## Exception Handlers

17 saved/static-readback Unwind handlers from `0x005d4100` through `0x005d4230` reference this source file for structured exception handling cleanup during particle set operations; Wave761 and Wave762 document the currently bounded evidence.

## Key Observations

1. **Factory Pattern**: Single `CreateByType` function handles all 13 particle types via switch statement, each with unique vtable and struct size.

2. **Linked List Management**: Particle sets form a linked list (next pointer at offset 0x38), managed via global pointers.

3. **Name Storage**: Each particle set stores its name at offset 0x04, max 49 chars (0x31) plus null terminator.

4. **Memory Pools**: Loading allocates large pools (80KB for particle data, 1KB per name) suggesting pre-allocation strategy.

5. **Two-Phase Init**: Types 11-13 use separate init functions rather than inline initialization in the switch.

6. **Archive Format**: Uses tokenized archive with 5 token types (0-4) for structured particle set data.

## Wave 420 Static Re-Audit Note (2026-05-14)

Wave420 corrected the old caller-owned `CParticleSet__OpenRead` label at `0x0048ddd0` to `CDXMemBuffer__OpenReadMode11`. The checked body receives the `CDXMemBuffer` instance in ECX, takes one filename stack argument, and forwards to `CDXMemBuffer__InitFromFile` with mode/context `0x11, 1, 0`. Its observed caller in this tranche is `CParticleSet__LoadParticleSetFile`, but the saved Ghidra owner is the mem-buffer helper, not ParticleSet itself.

This is static retail-binary evidence only. Runtime particle archive loading and complete ParticleSet/TokenArchive layouts remain unproven.

## Wave 463 Static Re-Audit Note (2026-05-16)

Wave463 refreshed the saved Ghidra signatures/comments/tags for `CParticleSet__CreateByType` and `CParticleSet__Init` alongside the adjacent ParticleManager tranche. Read-back evidence verified the factory sorted-name lookup, type-id dispatch/allocation, type-specific vtable/default setup, name copy, and `DAT_0082b450` update for `0x004cc020`, plus base-field clearing and base vtable installation for `0x004cc850`.

Evidence artifacts live under `subagents/ghidra-static-reaudit/wave463-particle-manager-current/`; the public-safe release note is `release/readiness/ghidra_particle_manager_wave463_2026-05-16.md`.

This is static retail-binary evidence only. Runtime particle-set loading/render behavior, exact ParticleSet layouts, exact source identities, and rebuild parity remain unproven.

## Wave 464 Static Re-Audit Note (2026-05-16)

Wave464 refreshed the saved Ghidra names/signatures/comments/tags for the ParticleSet tail helpers and adjacent loader tranche. Read-back evidence verified `CParticleSet__dtor_base` at `0x004cc870`, `CParticleSet__shared_scalar_deleting_dtor` at `0x004ccb40`, type-11/12/13 init helpers at `0x004cd290`, `0x004cd2d0`, and `0x004cd3c0`, `CParticleSet__LoadFromArchive` at `0x004cd7f0`, and `CParticleSet__LoadParticleSetFile` at `0x004cda60`.

Evidence artifacts live under `subagents/ghidra-static-reaudit/wave464-particleset-tail-current/`; the public-safe release note is `release/readiness/ghidra_particleset_tail_wave464_2026-05-16.md`.

This is static retail-binary evidence only. Runtime particle-set loading/render behavior, exact ParticleSet layouts, exact source identities, and rebuild parity remain unproven.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
