# Wave1124 RepairPad Current-Risk Review

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1124-repairpad-current-risk-review`

Wave1124 accounts for `2 rows` from the Wave1108 current focused denominator as a score-23 RepairPadAI dock-candidate helper cluster, moving current focused accounting to `133/1179 = 11.28%` of current focused candidates: 1179. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

This is a fresh read-only Ghidra export of the existing RepairPadAI static evidence; no mutation was needed: no rename, no signature change, no function-boundary change, and no executable-byte change.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold` | Leaf helper called by `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` at `0x004d6e15`. The body scans six float slots starting at `this+0x52c`, uses owner/reference state through `this+0x4b0`, and returns true when a zero-gated slot is still below its referenced threshold. |
| `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` | Dock-candidate compatibility gate called by `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader` at `0x004d6d77`. The body calls `CRepairPadAI__IsWithinRepairBounds`, calls `CRepairPadAI__HasAnySlotBelowThreshold`, then compares candidate and repair-pad owner state fields at `+0x138`. |

Evidence:

- Fresh metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `73` / `2`.
- Existing tags remain anchored to `comment-hardened`, `repairpad-ai`, `repairpad-wave328`, and `static-reaudit`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`, `19` files, `175737735` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-052636_post_wave1123_airunit_plane_support_vfunc_review_verified`.
- Prior context: Wave328 normalized the RepairPadAI helper comments/tags, Wave924 re-read the four-row dock-candidate chain, and Wave1119 re-read the vtable-slot 11 caller.

Boundary:

This is static Ghidra evidence. It does not prove runtime repair-pad docking behavior, runtime repair behavior, exact source-body identity, concrete `CRepairPadAI`, candidate-unit, slot, bounds, state, or owner layouts, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
