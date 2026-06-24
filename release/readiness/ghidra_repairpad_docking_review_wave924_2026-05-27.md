# Ghidra RepairPadAI Docking Review Wave924 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `repairpad-docking-review-wave924`

Wave924 re-reviewed a narrow RepairPadAI dock-candidate chain from the Wave911 focused queue plus one context helper. The pass exported fresh metadata, tags, xrefs, instructions, and decompile for four targets, made no Ghidra mutations, and made no executable-byte changes.

Targets:

| Address | Saved name | Wave924 read-back evidence |
| --- | --- | --- |
| `0x004d6d10` | `CRepairPadAI__VFunc_11_UpdateDockCandidateReader` | CRepairPadAI vtable DATA xref `0x005d8e34`; body clears active-reader state, scans `CMapWho` radius entries, calls the compatibility gate, and stores an accepted candidate reader. |
| `0x004d6e00` | `CRepairPadAI__IsCompatibleDockCandidate` | Called only by `0x004d6d10`; calls the repair-bounds and slot-threshold leaf helpers, then compares candidate/owner state fields at `+0x138`. |
| `0x0040c5b0` | `CRepairPadAI__IsWithinRepairBounds` | Called by `0x004d6e00`; compares candidate-unit float thresholds at `+0xf8/+0xfc` against the referenced bounds record at `*(this+0x4b0)+0x1c/+0x20`. |
| `0x0040c5e0` | `CRepairPadAI__HasAnySlotBelowThreshold` | Context helper called by `0x004d6e00`; scans six float slots starting at `+0x52c` against referenced thresholds. |

Read-back evidence:

- Metadata rows: `4`, all `OK`.
- Tag rows: `4`, all `OK`.
- Xref rows: `4`; the observed chain is vtable slot -> update reader -> compatibility gate -> two leaf helpers.
- Instruction rows: `174`.
- Decompile rows: `4`, all `OK`.
- Mutation status: read-only review; no mutation warranted.
- Wave911 focused re-audit progress: `89/1408 = 6.32%` after Wave924 (`3` focused candidates plus `1` context helper reviewed in this wave).
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260527-213142_post_wave924_repairpad_docking_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The four saved Ghidra function rows still exist with the expected names, signatures, comments, and tags.
- The prior Wave328/Wave491 RepairPadAI chain remains static-coherent after fresh read-back.
- No stronger source-backed rename or signature change is justified by this tranche.

What remains unproven:

- Exact source virtual name for slot 11.
- Concrete `CRepairPadAI`, candidate-unit, bounds, slot, and state layouts.
- Runtime repair-pad docking behavior.
- BEA patch behavior.
- Rebuild parity.
