# Three-Lane Strategy Reset Goal

## Metadata

| Field | Value |
| --- | --- |
| Title | Three-lane strategy reset |
| Status | active |
| Created | 2026-05-04 |
| Phase | Phase 1: docs-only strategy reset |
| Scope | Documentation, agent instructions, strategy state, and validation evidence only |
| Owner | Main/Codex agent operating in this repo |
| Allowed files | Active strategy docs, active release-safety docs, roadmap index docs, `.codex/state/three-lane-reset*.md`, `developer_agent_state.json`, `documentation_agent_state.json` |
| Forbidden files/actions | Product code, directory moves, release manifest include/exclude rules, broad UX redesign, public release expansion, commits |

## Strategic Decision

The repo is no longer Electron-first as the primary community product.

- WinUI 3 is the primary user-facing Windows product lane.
- Electron remains active as a maintainer/agentic reverse-engineering workbench lane.
- Active Python scripts are reverse-engineering/tooling/lab support; the historical Python GUI/CLI parity app is archived/reference, not a shipping product lane.
- WPF remains archived/reference only.
- AppCore remains shared correctness/core support for the Windows product lane.
- TypeScript CLI and typed job runner remain active automation and RE infrastructure.
- Curated public safety/export tooling remains intact and framework-neutral.

## Lane Definitions

### WinUI 3 Product Lane

WinUI 3 is the product lane normal users should see first. Work in this lane includes Windows desktop UX, AppCore-backed save/options behavior, player-facing patch workflows, media/lore access where appropriate, Windows packaging decisions, and build/run/test health.

### Electron Maintainer/Agentic RE Workbench Lane

Electron remains active for typed IPC/job boundaries, Browser Use/browser-verifiable checks, Ghidra/CDB/game harness work, release-policy inspection, diagnostics, automation, and agentic workflows. Halt broad Electron product polish and broad UX redesign unless required for maintainer workflow correctness, job-runner safety, security, IPC integrity, or test stability.

### Python Tooling And Archived Python App

Python remains useful for extraction, analysis, data transforms, fast experiments, validation helpers, and scripts under active tooling paths. The Python GUI/CLI parity app under `archive/legacy-python/` remains archived/reference and is not a shipping GUI/product lane.

### Archived WPF Lane

WPF remains archived/reference only. Do not grow WPF product work.

## Public/Private Safety Policy

Keep the curated public safety/export boundary. The private repo is not public-shaped and still contains mixed active code, archived code, private game/media/save/runtime evidence, agent/operator files, generated artifacts, and RE scratch.

Public release/export tooling must remain allowlist/curation based until a later public-shaped repo review proves otherwise. Do not treat `.gitignore` as a release boundary.

Hard-deny families remain private unless a later explicit review sanitizes and reclassifies a narrow subset:

- `game/**`
- `media/**`
- `save-attempts/**`
- `subagents/**`
- `.codex/**`
- `release/readiness/private_runtime_evidence/**`
- operator directives
- repo state files
- raw binaries, saves, runtime evidence, screenshots, frames, cache paths, and private absolute paths

## Active Docs To Update

At minimum, inspect and update active contradictions in:

- `AGENTS.md`
- `README.MD`
- `CURRENT_CAPABILITIES.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md`
- `roadmap/repo-structure-and-archive-map.md`
- `roadmap/electron-workbench-migration.md`
- `release/readiness/release_lane_strategy_2026-05-01.md`
- active roadmap/index docs that directly contradict the new lane policy

Create `roadmap/three-lane-product-strategy.md` as the canonical strategy doc.

## Stale Wording Searches

Run and summarize repo-wide searches for:

- `Electron-first`
- `active Electron product`
- `Electron product direction`
- `WinUI archived`
- `WinUI non-expanding`
- `Python archived`
- `Python non-shipping`
- `WPF active`
- `curated release`
- `public allowlist`
- `repo-as-release`

Record hits and disposition in `.codex/state/three-lane-reset-evidence.md`.

## Docs-Only Validation Commands

Attempt these commands and record exact pass/fail/warn/skipped status:

```powershell
git status --short
git diff --check
npm run test:doc-commands
npm run test:md-links
npm run test:repo-hygiene
py -3 tools\docsync_check.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

## Completion Criteria

This phase is complete only when:

1. `.codex/goals/three-lane-strategy-reset.md` exists and defines this operating contract.
2. `.codex/goals/winui-lane-health.md` exists and is ready for the next run.
3. `roadmap/three-lane-product-strategy.md` exists and is the canonical strategy doc.
4. Active docs no longer present Electron as the primary polished user-facing product lane.
5. Active docs no longer classify WinUI 3 as archived, reference-only, or non-expanding.
6. Active docs classify Electron as active maintainer/agentic RE workbench infrastructure.
7. Active docs classify Python as active RE/tooling/lab support, not a product GUI lane.
8. WPF remains archived/reference only.
9. Curated public safety/export tooling remains intact and framework-neutral.
10. Evidence is recorded in `.codex/state/three-lane-reset-evidence.md`.
11. Validation results are recorded.
12. Remaining contradictions or deferred issues are listed with exact files.

## Final Response Requirements

Report:

- strategy change summary
- files created
- files updated
- stale wording found and resolved
- validation commands and results
- remaining contradictions or deferred issues
- confirmation that no product code was modified
- exact next `/goal` prompt for WinUI lane health
