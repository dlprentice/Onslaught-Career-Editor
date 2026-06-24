# DiveBomber.cpp Functions

> Source File: DiveBomber.cpp | Binary: BEA.exe
> Debug Path: 0x006289c0

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Dive bomber aircraft AI implementation. Contains target selection logic for dive bombing runs. CDiveBomber likely inherits from CAirUnit. Wave800 corrected the saved `CDiveBomber__SelectTarget` signature to the static output-pointer form used by `CCannon__SelectTarget`; Wave959 re-read the DiveBomber/Dropship/AirUnit aircraft slice after static export-contract closure.

Wave1215 static read-back (`wave1215-unit-targeting-combat-residual-current-risk-review`) re-read `CDiveBomber__SelectTarget` in the unit-targeting residual cluster. CALL xref `0x004fd4e1` from `CCannon__SelectTarget` passes the output pointer; the body walks the owner/controller target list at `+0x15c/+0x160`, resolves candidate records through `this+4` and `candidate+0x88`, selects the highest priority `record+0x40`, or falls back through `CThing__GetCentrePos`. Verified backup: `G:\GhidraBackups\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`. Runtime dive-bomber targeting behavior, concrete target-record layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x00445380 | CDiveBomberAI__scalar_deleting_dtor | DiveBomber AI scalar-deleting destructor wrapper; retains `RET 0x4` | SAVED |
| 0x004453a0 | CDiveBomberAI__dtor_base | DiveBomber AI cleanup body | SAVED |
| 0x00445440 | CDiveBomberGuide__scalar_deleting_dtor | DiveBomber guide scalar-deleting destructor wrapper; retains `RET 0x4` | SAVED |
| 0x00445460 | CDiveBomberGuide__dtor_base | DiveBomber guide cleanup body | SAVED |
| 0x00445070 | [CDiveBomber__SelectTarget](./CDiveBomber__SelectTarget.md) | Wave800 target-output helper; selects candidate target data or writes fallback center position through `out_target_position` | SAVED |
| 0x0050eed0 | CDiveBomber__scalar_deleting_dtor | Wave557 primary CDiveBomber vtable slot-1 wrapper; calls `CDiveBomber__Destructor_VFunc01` and optionally frees `this` | SAVED |
| 0x0050f2d0 | CDiveBomber__Destructor_VFunc01 | Wave557 primary CDiveBomber destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base` | SAVED |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2250 | Unwind@005d2250 | 0x16 | Wave749 `unwind-continuation-wave749` cleanup callback; `OID__FreeObject_Callback` on `EBP+4`, debug path `0x006289c0`, allocation/type `0x12`. |
| 0x005d2266 | Unwind@005d2266 | 0x17 | Wave749 `unwind-continuation-wave749` cleanup callback; `OID__FreeObject_Callback` on `EBP+4`, debug path `0x006289c0`, allocation/type `0x13`. |

## Key Observations

- **Target selection AI** - Iterates through vehicles, checks state, selects highest priority
- **Distance filtering** - Uses offset 0x10 for health/distance calculations
- **Entity validation** - Checks dive bomber entities at offset 0x88
- **Debug assertions** - Lines 18, 19, 22, 23 contain runtime checks
- **No direct constructor found** - May be inlined or in assertion-only code
- **Wave557 lifecycle correction** - The primary `CDiveBomber__scalar_deleting_dtor` and `CDiveBomber__Destructor_VFunc01` names are static retail-binary evidence from vtable slot 1, direct xrefs, and read-back exports. Exact class layout, source virtual names, runtime teardown behavior, and rebuild parity remain unproven.
- **Wave749 unwind continuation** - `0x005d2250 Unwind@005d2250` and `0x005d2266 Unwind@005d2266` now have saved `void __cdecl Unwind@...(void)` signatures/comments/tags from static retail Ghidra read-back. Verified backup: `G:\GhidraBackups\BEA_20260522-190133_post_wave749_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.
- **Wave800 gameplay object helpers** - `0x00445070 CDiveBomber__SelectTarget` is now saved as `void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)` with `gameplay-object-helpers-wave800` and `wave800-readback-verified` tags. Direct caller `0x004fd4d0 CCannon__SelectTarget` passes the stack output pointer; the older no-argument return-pointer signature was incomplete. Verified backup: `G:\GhidraBackups\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified`. Runtime targeting behavior and rebuild parity remain deferred.
- **Wave959 aircraft re-audit** - `dive-dropship-aircraft-review-wave959` re-read the DiveBomber AI/Guide cleanup rows, `0x00445070 CDiveBomber__SelectTarget`, `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits`, `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`, `0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`, and the Wave557 aircraft lifecycle wrappers/bodies with fresh metadata/tags/xref/instruction/body-instruction/decompile/vtable/string exports. Wave911 focused re-audit progress is `303/1408 = 21.52%`; static closure remains `6151/6151 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified`; no mutation. Runtime dive-bomber targeting, runtime dropship door/thruster behavior, exact source method identity, concrete aircraft layouts, BEA patching, and rebuild parity remain separate proof.
- **Wave1130 current-risk tag normalization** - `wave1130-dive-dropship-current-risk-review` re-read and tag-normalized `6 rows` from the score-22 DiveBomber/Dropship aircraft current-risk cluster with fresh Ghidra export evidence: `0x00445380 CDiveBomberAI__scalar_deleting_dtor`, `0x00445440 CDiveBomberGuide__scalar_deleting_dtor`, `0x00446d70 CDropship__Init`, `0x00447040 CDropshipAI__scalar_deleting_dtor`, `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits`, and `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`. Current focused accounting is `161/1179 = 13.66%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018; static debt remains `0 / 0 / 0`; dry/apply/final-dry added `42 tags` with tag-only normalization and no rename, signature, comment, function-boundary, or executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`. Runtime dive-bomber AI behavior, runtime dropship door/thruster/child-unit behavior, exact layouts, BEA patching, visual QA, and rebuild parity remain separate proof.

Probe anchor: Wave959; dive-dropship-aircraft-review-wave959; 0x00447120 CDropship__ProcessDoorThrustersAndChildUnits; 0x00448170 CDropship__TraceGroundAndSpawnThrusterDust; 0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight; 0x00445070 CDiveBomber__SelectTarget; 303/1408 = 21.52%; 6151/6151 = 100.00%; G:\GhidraBackups\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified; no mutation.

Probe anchor: Wave1130; wave1130-dive-dropship-current-risk-review; 161/1179 = 13.66%; 6 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018; score-22 DiveBomber/Dropship aircraft current-risk cluster; fresh Ghidra export; tag-only normalization; 42 tags; 0 / 0 / 0; 0x00445380 CDiveBomberAI__scalar_deleting_dtor; 0x00445440 CDiveBomberGuide__scalar_deleting_dtor; 0x00446d70 CDropship__Init; 0x00447040 CDropshipAI__scalar_deleting_dtor; 0x00447120 CDropship__ProcessDoorThrustersAndChildUnits; 0x00448170 CDropship__TraceGroundAndSpawnThrusterDust; G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified.

## Related Files

- AirUnit.cpp - CAirUnit base class
- Bomber.cpp - Related bomber class
- BattleEngine.cpp - Combat system integration

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
