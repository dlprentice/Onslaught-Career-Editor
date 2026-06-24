# Repo Quality Audit (2026-02-11)

> Deep consistency and duplication audit across code, docs, tooling, and reference sources.
> Scope requested by user before continuing pure binary RE.

## Scope

Audited areas:

- Root-level files (docs, configs, binaries, state files)
- `references/Onslaught` (Stuart source)
- `references/AYAResourceExtractor`
- `patches`
- `reverse-engineering`
- `roadmap`
- `save-attempts`
- `tests_pyqt`
- `tools`
- `Views`
- `.pytest_cache`
- `.venv`
- `__pycache__`
- `bin`
- `discord_channel_dumps`
- `game`
- `lore`
- `lore-book`
- `media`
- `obj`
- `onslaught`
- `OnslaughtCareerEditor.UiTests`

## Actions Already Applied

1. Removed repo-local GhydraMCP copy from active repo path to avoid runtime confusion.
2. Moved it to reversible trash/staging path:
   - `%USERPROFILE%\.codex-trash\GhydraMCP_2026-02-11_removed_from_repo`
3. Updated docs that incorrectly implied `tools/GhydraMCP` was still present.

## Folder Inventory (Quantitative)

| Folder | Files | Dirs | Size (MB) | Practical Status |
|--------|------:|-----:|----------:|------------------|
| `patches` | 7 | 3 | 0.05 | Active RE patch scripts + stale `__pycache__` |
| `reverse-engineering` | 318 | 135 | 1.87 | Canonical technical docs |
| `roadmap` | 14 | 0 | 0.07 | Canonical planning docs |
| `save-attempts` | 16 | 0 | 0.15 | Real/test `.bes` corpus; includes `_tmp_*` scratch saves |
| `tests_pyqt` | 2 | 1 | 0.01 | Minimal smoke test + cache |
| `tools` | 8 | 2 | 0.30 | Active utility scripts; cache present |
| `Views` | 17 | 0 | 0.26 | Active WPF UI sources |
| `.pytest_cache` | 4 | 2 | <0.01 | Generated cache |
| `.venv` | 6960 | 568 | 257.10 | Local environment; generated dependency tree |
| `__pycache__` | 2 | 0 | 0.09 | Generated cache |
| `bin` | 2244 | 334 | 592.06 | Build output; generated |
| `discord_channel_dumps` | 11 | 0 | 0.20 | Source research notes |
| `game` | 5507 | 133 | 667.65 | Private game install/resources (RE input corpus) |
| `lore` | 14 | 0 | 0.07 | Canonical lore docs |
| `lore-book` | 348 | 138 | 2.02 | Mirror/curated doc tree for in-app browsing |
| `media` | 19 | 8 | 44.28 | Large static assets (images/pdf/archives) |
| `obj` | 381 | 10 | 3.09 | Build intermediates; generated |
| `onslaught` | 51 | 9 | 0.72 | Active Python package |
| `OnslaughtCareerEditor.UiTests` | 341 | 48 | 16.69 | Test project + generated output |
| `references/Onslaught` | 111 | 0 | 1.33 | Stuart source corpus (primary RE reference) |
| `references/AYAResourceExtractor` | 75 | 8 | 1.30 | AYA extractor reference corpus |

## Root-Level File Assessment

High-value canonical:

- `AGENTS.md`
- `README.MD`
- `reverse-engineering/**`
- `roadmap/**`
- `lore/**`
- `re_orchestrator_state.json`
- `documentation_agent_state.json`

Useful but potentially duplicative summary layers:

- `CURRENT_CAPABILITIES.md`
- `MAPPED_SYSTEMS.md`
- `WHAT_WE_CAN_DO_NOW.md`
- `MCP_DEBUGGING_OPTIONS.md`
- `MCP_LIMITATIONS.md`

Low-value/generated/noise:

- `NUL` (zero-byte artifact)
- Root caches or generated binaries under `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`

## Duplication and Staleness Findings

### A) Summary-doc duplication at repo root

Overlap is meaningful across:

- `CURRENT_CAPABILITIES.md`
- `MAPPED_SYSTEMS.md`
- `WHAT_WE_CAN_DO_NOW.md`
- `README.MD`
- Parts of `AGENTS.md`

Risk:

- Drift between tactical snapshots and canonical RE docs.

Recommendation:

- Keep one canonical operational summary at root (`CURRENT_CAPABILITIES.md`).
- Convert `MAPPED_SYSTEMS.md` and `WHAT_WE_CAN_DO_NOW.md` to short pointer docs or archive snapshots.
- Keep deep details in `reverse-engineering/**`.

### B) MCP docs overlap

Overlap across:

- `MCP_DEBUGGING_OPTIONS.md`
- `MCP_LIMITATIONS.md`
- `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`
- `AGENTS.md` operational guardrails

Recommendation:

- Canonicalize runtime procedure in `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`.
- Keep `MCP_LIMITATIONS.md` as capability-gap + workaround ledger.
- Keep `MCP_DEBUGGING_OPTIONS.md` as debugger-stack comparison doc only.

### C) Mirror duplication (`lore-book`)

`lore-book/**` duplicates large parts of `reverse-engineering/**`, `roadmap/**`, `lore/**` by design.

Status:

- This duplication is intentional and useful for in-app browsing.
- Current mirror is in sync at audit time (`rsync -ani --delete` reported no deltas).

### D) Generated directories tracked in repo

Notably large generated content:

- `.venv` (~257 MB)
- `bin` (~592 MB)
- `obj` (~3 MB)
- `__pycache__`, `.pytest_cache`

Risk:

- Noise in diffs, large sync churn, stale runtime artifacts.

Recommendation:

- Continue allowing on private branch if required by workflow.
- Treat these as non-authoritative/generated; avoid documentation references to generated artifacts.

## Source Corpus Parse Status (100% inventory-level parse)

### `references/Onslaught`

- Files parsed/inventoried: `111`
- `.cpp`: `52`
- `.h`: `53`
- Unique classes (declarations found): `145`
- Unique scoped methods (`Class::Method`): `1097`

Artifacts produced:

- `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv`

### `references/AYAResourceExtractor`

- Files parsed/inventoried: `75`
- Source files (`.cs/.cpp/.c/.h`) parsed: `54`
- C# classes found: `22`
- C# method candidates found: `57`

Artifacts produced:

- `reverse-engineering/source-code/aya-resourceextractor-file-manifest-2026-02-11.tsv`

## Canonical Documentation Roles (post-audit)

| Need | Canonical File |
|------|----------------|
| RE operating constraints | `AGENTS.md` |
| Binary workflow/runbook | `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md` |
| MCP gaps and retries | `MCP_LIMITATIONS.md`, `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md` |
| Function mapping corpus | `reverse-engineering/binary-analysis/functions/_index.md` |
| Binary-wide progress metrics | `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md` |
| Machine-readable coverage metrics | `reverse-engineering/binary-analysis/functions/function_coverage_master.json` |
| Stuart source inventory ground truth | `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv` |
| AYA extractor inventory ground truth | `reverse-engineering/source-code/aya-resourceextractor-file-manifest-2026-02-11.tsv` |

## Immediate Follow-up (recommended)

1. Keep root summary docs but add explicit “canonical source” links at top to reduce drift.
2. Remove or quarantine root `NUL` artifact via a user-local trash folder such as `%USERPROFILE%\.codex-trash\`.
3. Continue binary RE using current mutate/read-back/save discipline and update coverage state after each symbol batch.

---

*Generated: 2026-02-11*
