# Phase 1 Audit Findings (2026-03-01)

## Scope
- Program: `BEA Static RE Completion Program` Phase 1 (docs/state hygiene)
- Lanes: all 10 explorer lanes completed
- Artifacts: lane outputs + direct repo verification

## Critical Findings

1. Coverage/stat totals are stale/contradictory across canonical docs.
- `reverse-engineering/binary-analysis/functions/_index.md` still shows legacy `~5700/874/153` block.
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` top metadata says `5861` but bottom stats table still says `~5700`.
- `FUNCTION_COVERAGE_STATE.md` and `function_coverage_master.json` had stale Stuart-corpus counters (`159/1067`) vs current index-derived (`158/1059`).

2. Runbook “Current Known Gaps” contains resolved recovery targets and stale create-function framing.
- `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md` listed multiple already-landed manual-create targets as pending.

3. Lore-book mirror parity drift exists in key function index docs.
- Missing mirror files for Platform wrappers.
- Stale mirror indexes for `FEPLevelSelect.cpp`, `DXImposter.cpp`, `DestructableSegmentsController.cpp`.

## High Findings

1. Widescreen analysis wording drift.
- `widescreen-patch-analysis.md` described the JZ patch as always setting windowed, which is inaccurate without additional forcing patches.
- Region grouping text incorrectly bundled region 12 with the `0x001D7***` cave cluster.

2. Capture/menu docs lacked explicit command-by-command mapping.
- `Go/stop` and `Single step` are visible but handler cases are commented out.
- `About...` path is explicit no-op/defer behavior.

3. Root process docs drift.
- `MCP_LIMITATIONS.md` still used old FE ownership wording at `0x0051bfa0` (`CFEPMultiplayerStart`) despite corrected `CFEPLanguageTest` mapping.

## Medium Findings

1. State files had excessive/duplicated `next_steps` tails and stale queue semantics.
2. Scratch archive opportunities existed but required reference-risk triage before moving high-link folders.
3. `string-locations-index.md` historical debug-path totals (`196`) needed explicit historical framing to avoid collision with current canonical tracking totals.

## Completed in This Pass

- Canonical metric/coverage contradictions corrected.
- Runbook known-gaps section pruned to live unresolved items.
- Widescreen and capture/menu docs corrected.
- Lore-book parity repaired for identified missing/stale files.
- Phase 2 archive execution performed for low-risk `archive_now` scratch folders with manifest/index.
- State files compacted to short actionable queues.

## Remaining (Post-Phase1)

- Continue deep ownership/type/behavior contract validation (Phase 5) by subsystem priority.
- Keep `archive_after_rewrite` and `keep_now` scratch folders until references are rewritten or no longer active.
