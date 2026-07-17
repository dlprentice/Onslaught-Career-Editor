# MCTentacle.cpp Functions

> Source File: MCTentacle.cpp | Binary: BEA.exe
> Debug Path: `[maintainer-local-source-export-root]\MCTentacle.cpp` at `0x0062e06c`
> Current evidence: Wave435 saved Ghidra read-back on 2026-05-16; Wave515 follow-up saved the adjacent `0x004f0c50` matrix helper on 2026-05-17

## Overview

`CMCTentacle` is the tentacle boss motion-controller cluster. The recovered functions animate a multi-segment tentacle by caching bone transforms, evaluating cubic Bezier spline positions, and writing interpolated mesh-part transforms through a `CMotionController` vtable.

Wave435 corrected a stale interpretation at `0x0049eca0`: it is not an all-required-bones validator. It is a `CMeshPart` optimization filter that returns false for protected tentacle names and true for parts that can avoid the tentacle-specific optimization path.

Wave1021 (`motion-controller-constructor-review-wave1021`) re-read the adjacent `0x0049cad0 CMCTentacle__Constructor` and `0x0049ef80 CMCWarspiteDome__Constructor` rows with no mutation. Fresh evidence keeps `CMCTentacle__Constructor` tied to `CTentacle__CreateTentacleGuide`, vtable `0x005dc450`, owner storage at `+0x08`, setup/cache clears, and `+0x28 = 0xbf800000`; it keeps `CMCWarspiteDome__Constructor` tied to `CWarspiteDome__Init`, vtable `0x005dc484`, and owner storage at `+0x08`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`. Runtime tentacle/dome motion behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Wave755 MCTentacle Unwind Continuation (2026-05-23)

Wave755 static read-back (`unwind-continuation-wave755`, `wave755-readback-verified`) hardened `0x005d3360 Unwind@005d3360` and `0x005d3379 Unwind@005d3379` as compiler-generated SEH unwind allocation-cleanup callbacks. DATA scope-table xrefs `0x0061c09c` and `0x0061c0a4` point at the bodies; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP-0x174)` with MCTentacle.cpp debug path `0x0062e06c`, line token `0x1b`, and allocation/type values `0x45` and `0x49`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-105815_post_wave755_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave756 MCTentacle Unwind Continuation (2026-05-23)

Wave756 static read-back (`unwind-continuation-wave756`, `wave756-readback-verified`) hardened `0x005d3392 Unwind@005d3392` as the next MCTentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. DATA scope-table xref `0x0061c0ac` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP-0x174)` with MCTentacle.cpp debug path `0x0062e06c`, line token `0x1b`, and allocation/type value `0x6d`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose |
| --- | --- | --- |
| `0x0049cad0` | `CMCTentacle__Constructor` | Calls the base motion-controller constructor, installs vtable `0x005dc450`, stores owner tentacle at `+0x08`, and clears setup state. |
| `0x0049cb20` | `CMCTentacle__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCTentacle__Destructor`; frees through `OID__FreeObject` when flag bit 0 is set. |
| `0x0049cb40` | `CMCTentacle__Destructor` | Restores vtable `0x005dc450`, releases owned buffers, clears owner/setup fields, and tails into the base motion-controller destructor. |
| `0x0049cc40` | `CMCTentacle__Init` | Initializes tentacle controller state from a mesh model, allocates bone/spline buffers, and finds the special tentacle control bones. |
| `0x0049d280` | `CMCTentacle__UpdateBone` | Recursively updates per-bone transforms and cached interpolation state for the tentacle bone hierarchy. |
| `0x0049dc90` | `CMCTentacle__Factorial` | Iterative factorial helper used by the Bezier coefficient path. |
| `0x0049dcb0` | `CMCTentacle__Power` | Iterative float power helper used by the Bezier polynomial path. |
| `0x0049dcd0` | `CMCTentacle__UpdateSpline` | Evaluates cubic Bezier spline positions and orientation matrices for spline-driven tentacle bones. |
| `0x004f0c50` | `CMCTentacle__BuildOrientationMatrixFromEuler` | Wave515 follow-up helper called by `CMCTentacle__UpdateSpline`; builds a basis from global Euler constants and copies 12 dwords to an output matrix. |
| `0x0049e4b0` | `CMCTentacle__BuildOrientationMatrix` | Builds a 3x4 orientation matrix from direction/up vectors; the Ghidra `this` parameter is the output matrix pointer. |
| `0x0049e660` | `CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660` | Vtable slot 4; writes an interpolated bone transform for a mesh part and refreshes cached update timing. |
| `0x0049ead0` | `CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0` | Vtable slot 5; writes interpolated per-bone float output for a mesh part. |
| `0x0049ec80` | `CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80` | Vtable slot 8; compact cached-update predicate. |
| `0x0049eca0` | `CMeshPart__NameAvoidsTentacleOptimizationTokens` | Mesh-part token filter; returns false for protected tentacle tokens and true for names that avoid this special path. |
| `0x0049ed30` | `CMesh__HasTentacleBone` | Mesh-level scan for a `tentacle` bone name. |
| `0x0049ef80` | `CMCWarspiteDome__Constructor` | Adjacent dome motion-controller constructor; installs vtable `0x005dc484` and stores owner dome at `+0x08`. |
| `0x0049efa0` | `CMCWarspiteDome__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCWarspiteDome__Destructor`. |
| `0x0049efc0` | `CMCWarspiteDome__Destructor` | Restores vtable `0x005dc484`, clears owner/cached fields, and tails into the base motion-controller destructor. |
| `0x0049efe0` | `CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0` | Dome motion-controller slot 4; updates dome mesh-part transforms and cached owner-driven state. |

## Vtable Evidence

| Vtable | Owner | Confirmed slots |
| --- | --- | --- |
| `0x005dc450` | `CMCTentacle` | Slot 1 scalar deleting destructor; slot 4 transform update; slot 5 float output; slot 8 cached-update predicate. |
| `0x005dc484` | `CMCWarspiteDome` | Slot 1 scalar deleting destructor; slot 4 dome transform update; shared no-op/default slots around it. |

The vtable export intentionally includes adjacent data/function pointers beyond the confirmed slots. Treat only the confirmed slots above as semantic evidence from this wave.

## Function Details

### CMCTentacle__Init (`0x0049cc40`)

Initializes the controller from the mesh model. It allocates per-bone position arrays, matrix arrays, timing arrays, previous-state arrays, spline positions, spline matrices, and spline bone-index storage. It scans bone names for tentacle control tokens and seeds timing values with `-1.0f` (`0xbf800000`) before marking the controller initialized at `this+0x2c`.

Observed member offsets include:

| Offset | Meaning |
| --- | --- |
| `+0x08` | Owner tentacle pointer |
| `+0x0c` / `+0x10` / `+0x14` | Current matrix, position, and timing buffers |
| `+0x18` / `+0x1c` / `+0x20` | Previous matrix, position, and timing buffers |
| `+0x2c` | Initialized flag |
| `+0xa0` / `+0xa4` / `+0xb0` | Important control-bone indices, including tether/control/head paths |
| `+0xdc` / `+0xe0` / `+0xe4` / `+0xe8` | Spline positions, matrices, bone-index array, and spline bone count |

### CMCTentacle__UpdateBone (`0x0049d280`)

Performs recursive bone hierarchy updates. The static evidence shows lazy init, parent transform use, special handling for control bones, rotation/transform math, state copy into previous arrays, and child recursion. The saved signature preserves the long retail stack shape rather than overfitting friendly local names.

### CMCTentacle__UpdateSpline (`0x0049dcd0`)

Computes cubic Bezier spline values from four control points. The implementation uses the recovered `Factorial` and `Power` helpers for Bernstein coefficients, iterates over the spline-bone count at `this+0xe8`, builds an orientation matrix for each spline segment, and stores position/matrix outputs in the spline buffers.

### CMCTentacle__BuildOrientationMatrix (`0x0049e4b0`)

Builds right/up/direction axes from direction and up vectors, normalizes them, and writes a 3x4 matrix. Ghidra read-back represents the output matrix pointer as the hidden `this` parameter; that is intentional for the saved signature.

### CMCTentacle__BuildOrientationMatrixFromEuler (`0x004f0c50`)

Wave515 saved this adjacent helper as:

```cpp
void __thiscall CMCTentacle__BuildOrientationMatrixFromEuler(void * this, void * out_matrix);
```

The current xref is `CMCTentacle__UpdateSpline` at `0x0049dd79`. `RET 0x4` confirms one explicit output-matrix argument after `ECX`. The body builds yaw/pitch-derived basis values from global angle constants, combines them with `CSquadNormal__BuildOrientationMatrixFromEuler` and two `Mat34__MultiplyBasisToOut` calls, then copies 12 dwords to `out_matrix`.

This remains static evidence only; exact math names, concrete layout, runtime spline motion behavior, and rebuild parity remain unproven.

### CMeshPart__NameAvoidsTentacleOptimizationTokens (`0x0049eca0`)

This helper is the corrected Wave435 interpretation of the old `CMCTentacle__ValidateBoneStructure` label. It checks a mesh part name against protected tentacle tokens and returns false for names that must stay in the tentacle-specific path:

- `tether`
- `head`
- `tethercp`
- `headcp`
- `tentacle`
- names with the `bone` prefix

Current xrefs place this in mesh-part optimization checks, including `CMeshPart__CanOptimizePart_Strict` and `CMeshPart__CanMergeInOptimizePass`.

### CMesh__HasTentacleBone (`0x0049ed30`)

Scans the mesh bone array for a `tentacle` name and returns true on the first match. This is a mesh-level predicate, not a `CMCTentacle` instance method.

## String References

| Address | String | Usage |
| --- | --- | --- |
| `0x0062e02c` | `tentacle` | Bone/token search |
| `0x0062e040` | `tether` | Anchor/control token |
| `0x0062e00c` | `tethercp` | Tether control-point token |
| `0x0062e004` | `headcp` | Head control-point token |
| `0x0062e090` | `bone` | Prefix rejected by the mesh-part optimization filter |
| `0x0062e048` | `Got %d bones in tentacle\n` | Debug print string |
| `0x0062e018` | `TPos at %f %f %f` | Debug position print string |

## Validation

Wave435 saved the Ghidra create/name/signature/comment/tag correction with `ApplyCmcTentacleWarspiteDomeWave435.java`. Headless apply reported `updated=18 skipped=0 created=4 would_create=0 renamed=8 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`; the corrective signature apply reported `updated=18 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; and verify dry reported `updated=0 skipped=18 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.

Read-back verified `18` metadata rows, `18` tag rows, `28` xref rows, `32` vtable-slot rows, `4338` instruction rows, and `18` decompile exports. The retired focused probe passed after the saved-project read-back; its implementation remains available in Git history.

## Not Proven

These static waves do not prove runtime tentacle or dome motion behavior, exact concrete class layouts beyond observed offsets, exact local variable names/types, exact source-body identity, BEA launch behavior, game patching, or source-to-retail rebuild parity.
