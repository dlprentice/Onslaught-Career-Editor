# Ghidra Post–Wave909 Queue Contract Re-Export (Read-Only)

Status: complete read-only verification
Date: 2026-05-26
Scope: single `ExportFunctionQualitySnapshot.java` pass on the loaded `BEA.exe` program (not a repeat of post-100 subsystem reviews)

After Wave909 closeout was pushed, a read-only headless export re-validated the loaded Steam retail `BEA.exe` Ghidra program.

## Command shape

```text
analyzeHeadless.bat [maintainer-local-ghidra-project-root] BEA -process BEA.exe
  -scriptPath <repo>\tools
  -postScript ExportFunctionQualitySnapshot.java <output.tsv>
  -noanalysis
```

Log: `subagents/ghidra-static-reaudit/queue/current/headless_export_20260526.log`

## Results

| Metric | Value |
| --- | ---: |
| Total functions | 6113 |
| Commented functions | 6113 |
| Commentless functions | 0 |
| `FUN_` names | 0 |
| Exact-undefined signatures (export) | 0 |
| Name/signature drift vs prior `functions_quality.tsv` | 0 |

Output TSV: `subagents/ghidra-static-reaudit/queue/current/functions_quality_headless_refresh_20260526.tsv`

Ghidra reported: `REPORT: Save succeeded for processed file: /BEA.exe`

## Project backup (post-closeout push)

`[maintainer-local-ghidra-backup-root]\BEA_20260526-234159_post_wave909_closeout_pushed_verified` (robocopy of `[maintainer-local-ghidra-project-root]`, 19 files, matches prior backup shape)

## Boundary

This verifies the **current loaded Ghidra database** still matches the closed queue contract. It does not prove runtime gameplay behavior, layout identity, or that no future rename/signature polish is desirable—only that the export contract remains **6113/6113 commented** with no weak-name regression detected in this pass.
