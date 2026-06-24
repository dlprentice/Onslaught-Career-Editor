# Reverse-Engineering Docs Inventory (Lane 05)

## Summary

- Scope inventoried: canonical reverse-engineering docs under `reverse-engineering/`, excluding deep `binary-analysis/scratch/**` tranche contents.
- Canonical navigation chain is stable and index-first:
  - Root: `reverse-engineering/RE-INDEX.md`
  - Folder indexes: `save-file/_index.md`, `game-mechanics/_index.md`, `game-assets/_index.md`, `source-code/_index.md`, `project-meta/_index.md`, `binary-analysis/_index.md`
  - Binary function corpus index: `binary-analysis/functions/_index.md`
- README parity posture is mostly clean: most subfolder `README.md` files now redirect to `_index.md`; `binary-analysis/README.md` remains a full narrative doc (not just a redirect).
- Fast-changing authority files are concentrated in binary-analysis coverage/mutation tracking artifacts and should be treated as operational source-of-truth for current RE state.

## Canonical Sources

### Major Indexes

| Path | Canonical Role |
|---|---|
| `reverse-engineering/RE-INDEX.md` | Master RE landing page and cross-folder map |
| `reverse-engineering/save-file/_index.md` | Save-format docs index |
| `reverse-engineering/game-mechanics/_index.md` | Runtime mechanics + cheats index |
| `reverse-engineering/game-assets/_index.md` | Assets/MSL/modding index |
| `reverse-engineering/source-code/_index.md` | Source-analysis top index |
| `reverse-engineering/source-code/core/_index.md` | Core systems sub-index |
| `reverse-engineering/source-code/gameplay/_index.md` | Gameplay systems sub-index |
| `reverse-engineering/source-code/frontend/_index.md` | Front-end systems sub-index |
| `reverse-engineering/source-code/io/_index.md` | I/O systems sub-index |
| `reverse-engineering/project-meta/_index.md` | Attribution/community/bugs index |
| `reverse-engineering/binary-analysis/_index.md` | Binary-analysis navigation + authoritative links |
| `reverse-engineering/binary-analysis/functions/_index.md` | Master source-file-to-function mapping index |

### Authoritative Operational/State Files

| Path | Authority Type | Use |
|---|---|---|
| `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md` | Coverage authority | Canonical `% mapped`, named/unnamed counts, source-corpus counters |
| `reverse-engineering/binary-analysis/functions/function_coverage_master.json` | Machine snapshot | Coverage snapshot companion for tooling |
| `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md` | Work backlog | Pending/failed mutation retries and status |
| `reverse-engineering/binary-analysis/function_mutation_ledger.jsonl` | Append-only journal | Per-function mutation outcomes |
| `reverse-engineering/binary-analysis/function_mutation_attempt_log.jsonl` | Attempt log authority | Per-attempt transport/op/read-back history |
| `reverse-engineering/binary-analysis/function_mutation_tracking_state.json` | Resume state | Counters/pending set/resume metadata |
| `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md` | Runbook authority | MCP/headless operational guardrails |
| `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` | Workspace authority | Ghidra project/reference context |

### Canonical Data/Inventory Artifacts

| Path | Dataset Purpose |
|---|---|
| `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv` | Full Onslaught reference corpus inventory |
| `reverse-engineering/source-code/aya-resourceextractor-file-manifest-2026-02-11.tsv` | AYA extractor source corpus inventory |
| `reverse-engineering/game-assets/mission-text-map.tsv` | Mission token-to-text map |
| `reverse-engineering/binary-analysis/widescreen-diff-regions-28.tsv` | Canonical BEA vs widescreen diff region map |

## Topic Coverage

| Topic | Primary Canonical Docs | Coverage Notes |
|---|---|---|
| `.bes` file format + true dword view | `save-file/save-format.md`, `save-file/struct-layouts.md`, `save-file/_index.md` | Strong, with explicit offset map and encoding rules |
| Career graph/unlock semantics | `save-file/career-graph.md`, `save-file/career-links.md`, `save-file/career-unlock-recipes.md` | Strong, split into structure/link/recipe layers |
| Ranks, goodies, kills | `save-file/grade-system.md`, `save-file/goodies-system.md`, `save-file/kill-tracking.md` | Strong, retail-aligned and patcher-relevant |
| Cheats/god mode runtime behavior | `game-mechanics/cheat-codes.md`, `game-mechanics/god-mode.md`, `game-mechanics/_index.md` | Strong, includes source-vs-retail caveats |
| Binary executable behavior | `binary-analysis/executable-analysis.md`, `binary-analysis/_index.md` | Strong baseline for PE/runtime evidence |
| Windowed/widescreen/capture behavior | `binary-analysis/windowed-mode-analysis.md`, `binary-analysis/widescreen-*.md`, `binary-analysis/capture-menu-behavior.md`, `widescreen-diff-regions-28.tsv` | Strong, with canonical diff-map dataset |
| Function-level symbol mapping | `binary-analysis/functions/_index.md`, `binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`, per-source `_index.md` files | Very strong; broad per-source corpus coverage |
| Mutation workflow + reproducibility | `binary-analysis/ghydra-mcp-runbook.md`, `MCP-MUTATION-BACKLOG.md`, mutation ledger/log/state files | Strong operational traceability |
| Asset formats + mission scripting | `game-assets/aya-asset-format.md`, `game-assets/msl-scripting.md`, mission index docs + TSV map | Strong for documented/decoded lanes |
| Source architecture parity context | `source-code/_index.md` + `core/gameplay/frontend/io` sub-indexes + manifests | Strong internal-source context with retail caveats |
| Attribution/community/meta | `project-meta/_index.md`, `project-meta/attribution.md`, `project-meta/community-resources.md`, `project-meta/known-bugs.md` | Supportive/project-level reference |

## Potential Drift Areas

| Drift Risk | Evidence | Potential Impact |
|---|---|---|
| Dual authority between `_index.md` and `binary-analysis/README.md` | Most folders moved README -> `_index.md`, but `binary-analysis/README.md` still carries substantive independent content and archived stats | Narrative or metrics can diverge across two entry points |
| Coverage metrics split across multiple files | `FUNCTION_COVERAGE_STATE.md`, `function_coverage_master.json`, and `functions/_index.md` all carry related counters/state | Inconsistent totals if not updated in same change window |
| Snapshot/audit docs are date-stamped | `semantic-audit-2026-02-12*`, `md-link-check-2026-02-12*`, `mirror-check-2026-02-12*`, `repo-quality-audit-2026-02-11.md` | Older snapshot conclusions may be mistaken for live state |
| Missing referenced evidence path in coverage file | `FUNCTION_COVERAGE_STATE.md` cites `pass2_semantic_wave217/all_after_wave217.tsv`, but that path is not present under `binary-analysis/` or `binary-analysis/scratch/` | Citation trail for some helper-placeholder metrics is not directly reproducible from current tree |
| Orphan-risk standalone file outside subfolder indexes | `reverse-engineering/stuart-request-list.md` sits at RE root and is not a subfolder-indexed topic lane | Can be missed during routine index-driven updates |
