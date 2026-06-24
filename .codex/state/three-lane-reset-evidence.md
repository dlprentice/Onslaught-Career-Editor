# Three-Lane Reset Evidence

Status: active
Last updated: 2026-05-04

## Baseline

- `git status --short`: clean at start of reset.
- Initial stale-direction search found active Electron-first wording in root docs, roadmap docs, release docs, roadmap lore-book mirrors, package metadata, and repo hygiene tests.

## Lane Inventory

| Lane | Current path(s) | Reset classification |
| --- | --- | --- |
| WinUI 3 product | `OnslaughtCareerEditor.WinUI/`, AppCore projects/tests | Primary user-facing Windows product lane |
| Electron workbench | `archive/electron-workbench/apps/electron/`, `archive/electron-workbench/packages/ui/`, `archive/electron-workbench/packages/contracts/`, `archive/electron-workbench/packages/cli/` | Active maintainer/agentic RE workbench and automation lane |
| Python lab | `tools/`, `archive/legacy-python/` | Active RE/tooling/lab support; not a shipping GUI/product lane |
| WPF archive | `archive/legacy-wpf/` | Archived/reference only |
| Public safety/export | `release/readiness/`, release tooling | Framework-neutral curated public safety/export boundary |

## Search Evidence

Repo-wide search rerun after edits:

| Search | Result summary | Disposition |
| --- | --- | --- |
| `Electron-first` | Remaining hits are intentional supersession wording, historical evidence reports, private operator directive text, stale-term hygiene fixtures, and this reset evidence. Active root/roadmap/release docs no longer present Electron-first as current product strategy. | Benign/deferred historical context |
| `active Electron product` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `Electron product direction` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `WinUI archived` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `WinUI non-expanding` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `Python archived` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `Python non-shipping` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `WPF active` | Only the search term inside `.codex/goals/three-lane-strategy-reset.md`. | Benign |
| `curated release` | Remaining hits describe the public-safety/export boundary, historical Ralph-loop goal/evidence, and release tooling. | Keep; not stale by itself |
| `public allowlist` | Remaining hits describe public-safety tooling and historical evidence. | Keep; not stale by itself |
| `repo-as-release` | Remaining hits are release-safety comparisons and historical Ralph-loop goal text. | Keep as safety discussion |

## Files Changed

Created:

- `.codex/goals/three-lane-strategy-reset.md`
- `.codex/goals/winui-lane-health.md`
- `.codex/state/three-lane-reset.md`
- `.codex/state/three-lane-reset-evidence.md`
- `roadmap/three-lane-product-strategy.md`
- `lore-book/roadmap/three-lane-product-strategy.md`

Updated:

- `AGENTS.md`
- `README.MD`
- `CURRENT_CAPABILITIES.md`
- `README.RELEASE.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md`
- `package.json`
- `developer_agent_state.json`
- `documentation_agent_state.json`
- `archive/electron-workbench/release/ELECTRON-BUNDLE-README.MD`
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md`
- `release/readiness/curated_release_manifest.json`
- `release/readiness/private_only_inventory.tsv`
- `release/readiness/public_candidate_allowlist.tsv`
- `release/readiness/release_lane_strategy_2026-05-01.md`
- `release/readiness/release_readiness_checklist.md`
- `roadmap/ROADMAP-INDEX.md`
- `roadmap/agent-workflow.md`
- `roadmap/app-delivery-phases.md`
- `roadmap/app-validation-checklist.md`
- `roadmap/electron-workbench-migration.md`
- `roadmap/release-allowlist-classification.tsv`
- `roadmap/release-allowlist-profile.md`
- `roadmap/repo-structure-and-archive-map.md`
- `roadmap/status-current.md`
- `roadmap/technical-debt.md`
- matching `lore-book/roadmap/` mirrors required by docsync policy
- release profile/allowlist generated mirrors under `lore-book/roadmap/`

## Validation Results

| Command | Result | Important output |
| --- | --- | --- |
| `git status --short` | PASS | Clean at baseline; final working tree contains only this docs/reset change set. |
| `git diff --check` | PASS/WARN | Exit 0. Windows line-ending warnings only for generated TSV/inventory files after release artifact regeneration. |
| `npm run test:doc-commands` | PASS | 293 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check wrote ignored audit output under `subagents/md-link-check/`. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene unit tests passed; repo text hygiene check passed with 19 text and 2 path rules. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed after updating required lore-book mirrors. |
| `py -3 tools\release_profile_snapshot.py --check` | FAIL, then PASS | Initial check found stale release profile artifacts after new strategy docs. Regenerated with `py -3 tools\release_profile_snapshot.py`; rerun passed with `R0=1173`, `R2=0`, `R3=2`, `R4=18132`. |
| `py -3 tools\release_curated_manifest.py --check` | FAIL, then PASS | Initial check found stale allowlist for the new strategy docs. Regenerated with `py -3 tools\release_curated_manifest.py`; rerun passed with 1162 selected files. |
| `npm run test:public-allowlist` | PASS | 1162 rows checked after regeneration. |

## Deferred Issues

| File or area | Issue | Reason deferred | Next action |
| --- | --- | --- | --- |
| WinUI build/test health | Not assessed in this docs-only phase | Next run is specifically scaffolded for WinUI health | Execute `.codex/goals/winui-lane-health.md` |
| Physical Python relocation | `archive/legacy-python/` may contain scripts worth reactivating | Directory moves are forbidden in this phase | Classify scripts in a Python lab/tooling goal |
| Public WinUI release scope | WinUI is product focus but not automatically public-shippable | Public scope expansion is forbidden in this phase | Review build/license/public-safety impact after WinUI health |
