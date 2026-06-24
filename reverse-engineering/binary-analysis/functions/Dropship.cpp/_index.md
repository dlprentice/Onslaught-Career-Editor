# Dropship.cpp Functions

> Source File: Dropship.cpp | Binary: BEA.exe
> Debug Path: 0x00628a54

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Dropship transport unit implementation. CDropship handles transport aircraft with thruster effects, landing states, and deployment mechanics. Wave959 re-verified the current saved Dropship/DiveBomber/AirUnit aircraft slice read-only after the static export-contract queue closed.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00446d70 | CDropship__Init | Initialize dropship with thrusters/state; calls `0x00496090 CMCDropship__Ctor` and references `wingflat`, `doorclosed`, and `Thruster Dust Effect` | ~700 bytes |
| 0x00447040 | CDropshipAI__scalar_deleting_dtor | Dropship AI scalar-deleting destructor wrapper; retains `RET 0x4` | ~32 bytes |
| 0x00447060 | CDropshipAI__dtor_base | Dropship AI cleanup body | ~160 bytes |
| 0x00447100 | CDropship__dtor_base | Dropship cleanup body; calls `CAirUnit__dtor_base` after occupancy-grid cleanup | ~32 bytes |
| 0x00447120 | CDropship__ProcessDoorThrustersAndChildUnits | Current saved door/thruster/child-unit processing vtable body; supersedes historical `VFuncSlot_1c_00447120` boundary-only label | ~2320 bytes |
| 0x00448170 | CDropship__TraceGroundAndSpawnThrusterDust | Stdcall helper used by dropship door/thruster processing to trace ground and spawn thruster dust | ~496 bytes |
| 0x004b7ab0 | CMessageBox__SelectPortraitIndex | Superseded historical Dropship owner label; Wave450 places this in MessageBox portrait selection | ~180 bytes |
| 0x004b7b60 | CMessageBox__RequestQueueAdvance | Superseded historical Dropship owner label; Wave450 places this in MessageBox queue-advance control | ~20 bytes |
| 0x004b7b80 | CMessageBox__TryAdvanceQueuedMessage | Superseded historical Dropship owner label; Wave450 places this in MessageBox queued-message promotion | ~380 bytes |
| 0x0050ee70 | CDropship__scalar_deleting_dtor | Wave557 primary CDropship vtable slot-1 wrapper; calls `CDropship__Destructor_VFunc01` and optionally frees `this` | ~32 bytes |
| 0x0050f1f0 | CDropship__Destructor_VFunc01 | Wave557 primary CDropship destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base` | ~112 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d22e0 | Unwind@005d22e0 | 0x1b | Wave749 `unwind-continuation-wave749` cleanup callback; `OID__FreeObject_Callback`, debug path `0x00628a54`, allocation/type `0x2c`. |
| 0x005d22f6 | Unwind@005d22f6 | 0x17 | Wave749 cleanup callback; `OID__FreeObject_Callback`, debug path `0x00628a54`, allocation/type `0x2d`. |
| 0x005d230c | Unwind@005d230c | 0x16 | Wave749 cleanup callback; `OID__FreeObject_Callback`, debug path `0x00628a54`, allocation/type `0x2e`. |
| 0x005d2322 | Unwind@005d2322 | 0x10 | Wave749 cleanup callback; `OID__FreeObject_Callback`, debug path `0x00628a54`, allocation/type `0x37`. |
| 0x005d2350 | Unwind@005d2350 | n/a | Wave749 cleanup callback; jumps through `CMonitor__Shutdown`. |
| 0x005d2358 | Unwind@005d2358 | n/a | Wave749 cleanup callback; calls `CGenericActiveReader__dtor` on embedded field `+0xc`. |
| 0x005d2363 | Unwind@005d2363 | n/a | Wave749 cleanup callback; calls `CGenericActiveReader__dtor` on embedded field `+0x24`. |
| 0x005d2380 | Unwind@005d2380 | n/a | Wave749 cleanup callback; calls `CParticleManager__RemoveFromGlobalList_Thunk` on `EBP-0x68`. |
| 0x005d2388 | Unwind@005d2388 | n/a | Wave749 cleanup callback; calls `CLine__SetBaseVtable_00426360` on `EBP-0x40`. |

## Key Observations

- **Inherits CAirUnit** - Calls CAirUnit__Init during initialization
- **Thruster system** - Dynamically creates thrusters from "Thruster" attachment points
- **Two animation states** - "wingflat" (landed) and "doorclosed" (flying)
- **"Thruster Dust Effect"** - Loads particle effect for thruster visuals
- **VTable at 0x005e1dfc** - CDropship virtual function table
- **Wave450 owner correction** - The old `0x004b7ab0`, `0x004b7b60`, and `0x004b7b80` Dropship portrait/queue labels were moved to `CMessageBox` after saved Ghidra read-back showed they operate on the MessageBox portrait table and queue state.
- **Wave557 lifecycle correction** - `CDropship__scalar_deleting_dtor` and `CDropship__Destructor_VFunc01` are saved static Ghidra facts from primary vtable slot-1 read-back and direct xrefs. Exact source virtual names, concrete dropship layout, runtime destruction behavior, and rebuild parity remain unproven.
- **Wave749 unwind continuation** - `0x005d22e0 Unwind@005d22e0` through `0x005d2388 Unwind@005d2388` now have saved `void __cdecl Unwind@...(void)` signatures/comments/tags from static retail Ghidra read-back under `unwind-continuation-wave749`; representative anchor `0x005d2350 Unwind@005d2350` covers the monitor-shutdown cleanup row. Verified backup: `G:\GhidraBackups\BEA_20260522-190133_post_wave749_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.
- **Wave959 aircraft re-audit** - `dive-dropship-aircraft-review-wave959` re-read `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits`, `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`, `0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`, `0x00445070 CDiveBomber__SelectTarget`, the Dropship AI/destructor rows, and CMCDropship context (`0x00496090`, `0x00496100`, `0x00496200`) with fresh metadata/tags/xref/instruction/body-instruction/decompile/vtable/string exports. Wave911 focused re-audit progress is `303/1408 = 21.52%`; static closure remains `6151/6151 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified`; no mutation. Runtime dropship door behavior, runtime thruster dust behavior, child-unit deployment behavior, exact source method identity, concrete aircraft layouts, BEA patching, and rebuild parity remain separate proof.
- **Wave1009 static-shadow boundary recovery** - `geometry-guide-heightfield-spine-review-wave1009` recovered `0x00448580 CDropshipAI__VFunc_09_00448580` and `0x00448930 CDropshipGuide__VFunc_03_00448930` as DATA-backed static-shadow caller boundaries tied to `CStaticShadows__SampleShadowHeightBilinear`. Queue closure is `6233/6233 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime dropship or guide behavior, exact source method identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.
- **Wave1130 current-risk tag normalization** - `wave1130-dive-dropship-current-risk-review` re-read and tag-normalized `6 rows` from the score-22 DiveBomber/Dropship aircraft current-risk cluster with fresh Ghidra export evidence: `0x00445380 CDiveBomberAI__scalar_deleting_dtor`, `0x00445440 CDiveBomberGuide__scalar_deleting_dtor`, `0x00446d70 CDropship__Init`, `0x00447040 CDropshipAI__scalar_deleting_dtor`, `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits`, and `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`. Current focused accounting is `161/1179 = 13.66%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018; static debt remains `0 / 0 / 0`; dry/apply/final-dry added `42 tags` with tag-only normalization and no rename, signature, comment, function-boundary, or executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`. Runtime dive-bomber AI behavior, runtime dropship door/thruster/child-unit behavior, exact layouts, BEA patching, visual QA, and rebuild parity remain separate proof.

Probe anchor: Wave959; dive-dropship-aircraft-review-wave959; 0x00447120 CDropship__ProcessDoorThrustersAndChildUnits; 0x00448170 CDropship__TraceGroundAndSpawnThrusterDust; 0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight; 0x00445070 CDiveBomber__SelectTarget; 303/1408 = 21.52%; 6151/6151 = 100.00%; G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified; no mutation.

Probe anchor: Wave1130; wave1130-dive-dropship-current-risk-review; 161/1179 = 13.66%; 6 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018; score-22 DiveBomber/Dropship aircraft current-risk cluster; fresh Ghidra export; tag-only normalization; 42 tags; 0 / 0 / 0; 0x00445380 CDiveBomberAI__scalar_deleting_dtor; 0x00445440 CDiveBomberGuide__scalar_deleting_dtor; 0x00446d70 CDropship__Init; 0x00447040 CDropshipAI__scalar_deleting_dtor; 0x00447120 CDropship__ProcessDoorThrustersAndChildUnits; 0x00448170 CDropship__TraceGroundAndSpawnThrusterDust; G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified.

## Memory Allocations in Init

| Line | Size | Type ID | Purpose |
|------|------|---------|---------|
| 44 | 20 bytes | 0x1b | Component at this[0x1c] |
| 45 | 32 bytes | 0x17 | Component at this[0x82], vtable 0x005db228 |
| 46 | 100 bytes | 0x16 | Component at this[0x4f], vtable 0x005db1f4 |
| 55 | 8 bytes | 0x10 | Thruster objects (multiple) |

## Animation States

| State | Animation | Condition |
|-------|-----------|-----------|
| 0 | "wingflat" | Below height threshold |
| 6 | "doorclosed" | Above height threshold |

## String References

| Address | String | Purpose |
|---------|--------|---------|
| 0x00628a74 | "wingflat" | Wings-down animation |
| 0x00628a80 | "doorclosed" | Doors-closed animation |
| 0x00623080 | "Thruster" | Attachment point name |
| 0x00628a3c | "Thruster Dust Effect" | Particle effect name |

## Class Hierarchy

```
CUnit
  └── CAirUnit
        └── CDropship
```

## Related RTTI Classes

| Address | Class Name |
|---------|------------|
| 0x0063d618 | .?AVCDropship@@ |
| 0x00628a28 | .?AVCDropshipAI@@ |
| 0x00628a08 | .?AVCDropshipGuide@@ |
| 0x00627eb0 | .?AVCDropshipBehaviourType@@ |
| 0x0062dd58 | .?AVCMCDropship@@ |

## Related Files

- AirUnit.cpp - CAirUnit parent class
- Unit.cpp - CUnit base class
- ParticleManager.cpp - Thruster dust effects

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
