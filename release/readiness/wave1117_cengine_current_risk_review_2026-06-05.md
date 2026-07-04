# Wave1117 CEngine Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1117-cengine-current-risk-review`

Wave1117 re-read `10 rows` from the next Wave1108 current focused candidates: 1179, the score-26 CEngine core head, with a fresh read-only Ghidra export and no mutation. Current focused accounting moves to `87/1179 = 7.38%`.

Representative anchors: `0x00449820 CEngine__ctor`, `0x00449890 CEngine__Shutdown`, `0x004499d0 CEngine__Init`, `0x0044a0d0 CEngine__SelectViewpoint`, `0x0044a130 CEngine__InitDamageSystem`, `0x0044a1f0 CEngine__LoadMixers`, `0x0044a2a0 CEngine__SetKempyCube`, `0x0044a2c0 CEngine__SetWater`, `0x0044a6e0 CEngine__Deserialize`, and `0x0044a830 VFuncSlot_03_0044a830`.

Evidence:

- Fresh metadata export: `10` rows, `targets=10 found=10 missing=0`.
- Fresh tag export: `10` rows, `missing=0`.
- Fresh xref export: `17` rows.
- Fresh instruction export: `1370` rows, `targets=10 missing=0`.
- Fresh decompile export: `10` rows, `targets=10 dumped=10 missing=0 failed=0`.
- Mutation status: no mutation, no rename, no signature change, no comment/tag write, no executable-byte change.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified`.

What this proves:

- The ten target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows are coherent with the existing bounded CEngine evidence.
- The `CEngine__SetWater` stack argument/`RET 0x4` evidence is instruction-backed despite a decompiler temporary-register artifact.
- `0x0044a830 VFuncSlot_03_0044a830` remains owner-deferred rather than force-renamed.

What remains separate:

- Runtime engine behavior.
- Runtime render behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
