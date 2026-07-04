# FEPDebriefing.cpp - Function Index

> Source File: FEPDebriefing.cpp | Category: Frontend/Mission Debriefing

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Frontend mission debriefing screen implementation. Displays mission results after completion, including rank achieved, kills by category, and unlocked content.

## Wave801 Frontend/Render Helper Read-Back

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved a current comment/tag on `0x00456780 CFEPDebriefing__Initialize`. DATA xref `0x005db9c0` reaches the row; static evidence ties the body to FEPDebriefing.cpp debug path `0x0062913c`, allocation/type values `0x324` and `0x640`, and debriefing initialization state clears. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This remains static retail Ghidra evidence only. Exact source-body identity, runtime debriefing/frontend behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00456780 | [CFEPDebriefing__Initialize](./CFEPDebriefing__Initialize.md) | Named | Initialize mission debriefing screen |

Live signature (normalized, 2026-02-24):
- `int CFEPDebriefing__Initialize(void * this)`

## Wave 376 Debriefing-Adjacent Corrections (2026-05-13)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| `0x00456830` | `GlobalListNode__ClearField4AndPushGlobalList` | Shared callback | Corrected from old `CFEPDebriefing__ResetStateAndVector`; xrefs also include object creation and equipment construction paths, so it is not debriefing-owned. |
| `0x00456850` | `CFEPDebriefing__Shutdown` | Named/signature hardened | Corrected from old generic vfunc label; vtable data and cleanup behavior support a debriefing shutdown slot. |

These are saved static Ghidra corrections only. Runtime debriefing behavior, exact layout, concrete locals/types, and rebuild parity remain unproven.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) corrected the saved `0x00456830 GlobalListNode__ClearField4AndPushGlobalList` comment/tag evidence: fresh read-back shows this shared callback clears field `+0x4`, calls `0x004cb040 ParticleEffectLink__PushGlobalList`, and returns `this`; older CWorldPhysicsManager-only callee wording was too narrow. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

## Wave981 CFEPDebriefing Boundary Recovery (2026-05-29)

Wave981 recovered the missing CFEPDebriefing vtable slot boundaries after fresh vtable and instruction review:

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00456930` | `CFEPDebriefing__Process` | Created vtable slot-2 boundary; updates debriefing timers/state and node/particle positions. |
| `0x004568a0` | `CFEPDebriefing__ButtonPressed` | Created vtable slot-3 boundary; handles button routing and frontend sound/page dispatch. |
| `0x00456d40` | `CFEPDebriefing__RenderPreCommon` | Created vtable slot-4 boundary; updates camera and draws the video/pre-common layer. |
| `0x00456dd0` | `CFEPDebriefing__Render` | Created vtable slot-5 boundary; renders debriefing text, rank/goodie/stat output, and shared frontend UI. |
| `0x00457cf0` | `CFEPDebriefing__TransitionNotification` | Created vtable slot-6 boundary; bridges CAREER goodie counters into debriefing state. |

The CFEPDebriefing vtable at `0x005db9c0` now resolves through slot 8: slot 0 initialize, slot 1 shutdown, slots 2-6 recovered by Wave981, slot 7 shared active-notification no-op, and slot 8 `CFrontEndPage__DeActiveNotification`.

Runtime debriefing/front-end behavior, exact debriefing-page/career bridge layouts, BEA patching, and rebuild parity remain separate proof.

Caller-anchor update (2026-03-01):
- Dedicated xref export for `0x00456780` produced `from_addr=0x005db9c0`, `ref_type=DATA`, indicating indirect vtable/dispatch-table invocation (`scratch/program_2026-03-01/phase5_fepdebriefing_xrefs/xrefs.tsv`).

## Debriefing Screen Contents

After completing a mission, the debriefing screen displays:

1. **Mission Rank** (S, A, B, C, D, E)
   - Calculated from performance metrics
   - Uses `GetGradeFromRanking()` to convert float to letter grade

2. **Kill Statistics**
   - Aircraft destroyed
   - Vehicles destroyed
   - Emplacements destroyed
   - Infantry eliminated
   - Mechs destroyed

3. **Unlocked Content**
   - New goodies unlocked by this mission
   - Based on kill thresholds and grade achieved

4. **Mission Time**
   - Time taken to complete the mission

## Grade Calculation

From Career.cpp source:
```cpp
if (f == 1.f) c = 'S';
else if (f <= 0.f) c = 'E';
else c = 'D' - floor(f * 4);
```

| Float Range | Grade |
|-------------|-------|
| 1.0 | S |
| 0.75-0.99 | A |
| 0.50-0.74 | B |
| 0.25-0.49 | C |
| 0.01-0.24 | D |
| <= 0.0 | E |

## Kill Thresholds for Goodies

| Kill Type | Thresholds | Goodies Unlocked |
|-----------|------------|------------------|
| Aircraft | 25, 50, 75, 100 | 4 goodies |
| Vehicles | 100, 200, 300, 400 | 4 goodies |
| Emplacements | 25, 50 (75 only in combined unlocks) | 2 standalone (+ combined unlocks) |
| Infantry | 40, 80, 160 | 3 goodies |
| Mechs | 20, 40, 80 | 4 goodies (40 unlocks 2 goodies) |

## Wave750 Unwind Cleanup Evidence (2026-05-22)

Wave750 saved two FEPDebriefing/FrontEnd-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave750` and `wave750-readback-verified` tags. Both are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2630 Unwind@005d2630` | DATA scope-table xref `0x0061b4b4`; calls `OID__FreeObject_Callback` for FEPDebriefing.cpp debug path `0x0062913c`, line `0x80`, allocation/type value `0x30`. |
| `0x005d2660 Unwind@005d2660` | DATA scope-table xref `0x0061b4dc`; calls `CSPtrSet__Clear` on the stack-local set at `EBP-0x1c`. |

Read-back backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-193422_post_wave750_unwind_continuation_verified`. Exact parent source-body identity, runtime debriefing/frontend cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Cross-References

- Related: [Career.cpp](../Career.cpp/_index.md) - grade calculation and kill tracking
- Related: [FEPGoodies.cpp](../FEPGoodies.cpp/_index.md) - goodie unlock display

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
