# Animal.cpp Functions

> Source File: Animal.cpp owner group | Binary: BEA.exe
> Debug Path: not confirmed in the tracked Stuart-source corpus

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CAnimal` is currently documented as a Ghidra RTTI/vtable-backed owner group. No dedicated tracked Stuart-source `CAnimal` file has been located in this repo, so the names below are conservative saved-Ghidra labels based on vtable, decompile, xref, and instruction evidence rather than exact source method names. Wave946 (`animal-lifecycle-boundary-wave946`) recovered the remaining real CAnimal vtable function boundaries through slot 68 and kept exact layout/runtime claims separate. Wave1016 (`animal-init-dtor-review-wave1016`) re-read the init/destructor head rows and adjacent vtable/data context with no mutation.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00403d30 | CAnimal__Init | Initialize animal instance state from an init object, create model/resource state, link the animal list, and schedule event 3000 when active | ~520 bytes |
| 0x00404010 | CAnimal__dtor_base | Destructor-base body that resets the CAnimal vtable, clears animal-list references, and delegates to CComplexThing cleanup | ~320 bytes |
| 0x004041f0 | CAnimal__scalar_deleting_dtor | Scalar-deleting destructor wrapper that calls CAnimal__dtor_base and optionally frees the object | ~32 bytes |
| 0x0044c140 | CAnimal__HandleEvent3000Dispatch | Wave946 vtable slot 0 event handler; event `0xbb8`/3000 dispatches vtable byte offset `+0x108`, otherwise forwards to `CComplexThing__HandleEvent` | recovered boundary |
| 0x004040f0 | CAnimal__GetClassNameString | Wave946 vtable slot 7 constant string getter returning `0x00622d70` (`CAnimal`) | recovered boundary |
| 0x00404100 | CAnimal__GetTypeId1D | Wave946 vtable slot 8 constant id getter returning `0x1d` | recovered boundary |
| 0x00404110 | CAnimal__SetThingTypeMask80000001 | Wave946 vtable slot 38 type-mask setter: ORs caller value with `0x80000001` and stores `this+0x34` | recovered boundary |
| 0x00404120 | CAnimal__CopyVector7CToOut | Wave946 vtable slot 27 copies four dwords from `this+0x7c` to caller output | recovered boundary |
| 0x00404150 | CAnimal__SetVector7CFromInput | Wave946 vtable slot 67 copies four dwords from caller input into `this+0x7c` | recovered boundary |
| 0x00404170 | CAnimal__AddVectorTo7C | Wave946 vtable slot 68 adds a three-float vector into `this+0x7c..0x84` | recovered boundary |
| 0x004041a0 | CAnimal__CopyVector8CToOut | Wave946 vtable slot 30 copies four dwords from `this+0x8c` to caller output | recovered boundary |
| 0x004041d0 | CAnimal__CopyMatrix9CToOut | Wave946 vtable slot 31 copies `0x30` bytes from `this+0x9c` to caller output | recovered boundary |
| 0x004045d0 | CAnimal__RenderViaCThingRender | Wave946 vtable slot 36 forwards `renderFlags` to `CThing__Render` | recovered boundary |

## Key Observations

- **RTTI/vtable owner** - Vtable `0x005d8698` resolves to `CAnimal`; slot refs point at `0x00403d30` and `0x004041f0`.
- **Init behavior** - `CAnimal__Init` copies init transform/vector state, reads a type value at init offset `+0x3bc`, references `bird_msh`, creates model/resource state, delegates to `CComplexThing__Init`, links the animal list, and schedules event `3000` when active.
- **Destructor correction** - `0x00404010` is now saved as `CAnimal__dtor_base`; the old `CAtmospheric__Destructor` label is superseded by CAnimal vtable/list evidence.
- **Wave946 boundary recovery** - `0x005d8698` was re-exported through the real 69-slot table span; after creating 23 function boundaries, all slots through 68 read back with `status=OK`. Representative anchors: `0x0044c140 CAnimal__HandleEvent3000Dispatch`, `0x00401440 CThing__GetRenderRadiusFromRenderThing`, `0x00401460 CThing__MakeVisible`, `0x004041d0 CAnimal__CopyMatrix9CToOut`, and `0x004f3d30 CThing__DrawDebugStuff3d`. Queue closure after refresh is `6139/6139 = 100.00%`; Wave911 progress is `232/1408 = 16.48%`; verified backup `G:\GhidraBackups\BEA_20260528-062816_post_wave946_animal_lifecycle_boundary_review_verified`.
- **Proof boundary** - Exact source virtual names, concrete layouts, tags, local variables, runtime behavior, and rebuild parity remain open.

## 2026-05-31 Wave1016 CAnimal Init/Destructor Review

Wave1016 re-read the CAnimal init/destructor rows with no mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation. Target exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `195` body-instruction rows, and `3` decompile rows. Context exports verified `32` metadata rows, `637` xref rows, `1292` body-instruction rows, and `32` decompile rows. Additional evidence verified `69` CAnimal vtable slots from `0x005d8698`, `14` data-xref rows, `3` scalar-reference rows, and direct strings `0x00622d48 bird.msh`, `0x00622d1c Warning! Unknown animal type %d generated!\x0a`, and `0x00622d70 CAnimal`.

Wave1112 (`wave1112-animal-wave1016-current-risk-supersession`) accounts these same `3 rows` in the Wave1108 current focused denominator using the Wave1016 static evidence, moving current focused accounting to `28/1179 = 2.37%` of current focused candidates: 1179. It performs no new Ghidra export and no mutation; latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x00403d30 CAnimal__Init` | DATA/vtable slot 9 xref `0x005d86bc`; constructs local resource-descriptor state, reads init type at `init+0x3bc`, uses `bird.msh` for type 1, creates a render object through `PCRTID__CreateObject`, delegates to `CComplexThing__Init`, links `DAT_00660130`/`DAT_00660134`, and schedules event `3000` through `CEventManager__AddEvent_AtTime` when active. |
| `0x00404010 CAnimal__dtor_base` | Called by `0x004041f0 CAnimal__scalar_deleting_dtor`; resets CAnimal vtables, walks and clears animal-list references through `DAT_00660130`/`DAT_00660134`, unlinks this node when present, then jumps to `CComplexThing__dtor_base`. |
| `0x004041f0 CAnimal__scalar_deleting_dtor` | DATA/vtable slot 1 xref `0x005d869c`; calls `CAnimal__dtor_base`, frees through `CDXMemoryManager__Free` when `flags&1`, returns `this`, and `RET 0x4` confirms one stack `flags` argument. |

Queue closure remains `6238/6238 = 100.00%`. Wave911 focused re-audit progress advances to `513/1408 = 36.43%`; expanded static surface progress is `739/1493 = 49.50%`; Wave911 top-500 risk-ranked coverage is `439/500 = 87.80%`. Verified backup: `G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified`. Probe token anchor: Wave1016; animal-init-dtor-review-wave1016; 0x00403d30 CAnimal__Init; 0x00404010 CAnimal__dtor_base; 0x004041f0 CAnimal__scalar_deleting_dtor; 0x005d8698; 0x00622d48 bird.msh; 0x00622d1c Warning! Unknown animal type; 0x00622d70 CAnimal; 513/1408 = 36.43%; 739/1493 = 49.50%; 439/500 = 87.80%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified; no mutation.

Boundary: exact source virtual names, concrete `CAnimal`/`CAnimalInitThing`/resource-descriptor/list layouts, runtime animal behavior, runtime event scheduling, BEA patching, and rebuild parity remain separate proof.

## Related Files

- `thing.cpp` - CThing base class.
- `Actor.cpp` - CActor/CComplexThing owner groups with adjacent init/destructor patterns.
- `Atmospherics.cpp` - Environmental effects; older docs had misattributed `0x00404010` to this owner before the 2026-05-09 CAnimal correction.

---
*Updated by Wave1016 CAnimal init/destructor review (2026-05-31); prior boundary recovery wave was Wave946 and earlier owner correction wave was 2026-05-09.*
