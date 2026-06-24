# WinUI Product Consolidation State

Status: active
Last updated: 2026-05-04

## Current Phase

Phase 1: WinUI-first release/docs policy consolidation validated; final diff review in progress.

## Baseline

- Branch: `wip/sandbox`
- Current pushed HEAD at goal start: `ace94b5b1d1f89812363fbd241d3cc30d96f572c`
- Working tree at goal start: dirty with uncommitted WinUI lane health and first WinUI product sprint changes.
- User direction: WinUI 3 is the main GUI/product lane; Electron product-app work, WPF, and the historical Python GUI/CLI parity app should be shelved/out of the way without destructive deletion. Active Python work is limited to narrow utility/lab scripts, not the archived app.

## Completed Inherited Work

- WinUI lane health evidence created.
- WinUI shell/About/Save Lab/Patch Bench first product sprint batch completed.
- Patch Bench now requires an app-owned working copy before executable verify/apply/restore.
- WinUI product-lane static tests were added.

## Current Batch

- Created `.codex/goals/winui-product-consolidation.md` as the long-horizon operating contract.
- Reclassified release policy so `OnslaughtCareerEditor.WinUI/**` is eligible in the curated public source candidate.
- Reclassified `archive/electron-workbench/apps/electron/**`, `archive/electron-workbench/packages/ui/**`, and Electron bundle helper scripts as excluded shelved-workbench surfaces for the default WinUI-first public candidate.
- Updated active release docs, roadmap docs, lore-book mirrors, and hygiene checks away from Electron-as-product wording.
- Looked back at pre-Electron history and `archive/legacy-python/`; clarified that the Python GUI/CLI was a historical parity attempt with WPF/WinUI and is now archived/reference, while active Python work should live as narrow utility/tooling scripts.
- Removed Markdown-style backticks from primary WinUI XAML copy so file names render naturally in the Windows app.
- Tightened Patch Bench working-copy creation so only BEA.exe/bea.exe sources can be copied into the app-owned workspace, lower-case `bea.exe` is found from Settings, and repeated copy creation uses a unique folder instead of colliding within the same second.
- Added and ran an explicit WinUI desktop launch smoke that verifies the current app opens, shows the WinUI product shell/navigation, then closes without leaving an app process behind.
- Re-ran WinUI, AppCore, UI static, CLI smoke, docs, release, allowlist, and JSON validation gates after the consolidation batch.

## Files Inspected

- `AGENTS.md`
- `roadmap/three-lane-product-strategy.md`
- `.codex/state/winui-lane-health.md`
- `.codex/state/winui-lane-health-evidence.md`
- WinUI shell/pages and UiTests from the previous batch
- `release/readiness/curated_release_manifest.json`
- `tools/release_profile_snapshot.py`
- `tools/release_curated_manifest.py`
- `tools/public_allowlist_safety_check.py`
- `tools/repo_text_hygiene_check.py`
- `README.RELEASE.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md`
- `release/readiness/release_lane_strategy_2026-05-01.md`
- `release/readiness/release_readiness_checklist.md`
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md`
- `roadmap/status-current.md`
- `roadmap/technical-debt.md`
- `roadmap/electron-workbench-migration.md`
- `roadmap/gui-expansion.md`
- `roadmap/repo-structure-and-archive-map.md`
- `roadmap/ROADMAP-INDEX.md`
- `roadmap/agent-workflow.md`
- `roadmap/csharp-python-parity.md`
- lore-book roadmap mirrors
- `archive/legacy-python/README.md`

## Findings

- Release manifest/profile was inverted for current strategy: Electron/UI were public candidate surfaces while WinUI was hard-denied.
- Several active docs still treated packaged Electron proof as the next primary release blocker.
- Historical Electron evidence reports needed supersession notes so they remain useful without defining current product release direction.
- Several docs incorrectly described `archive/legacy-python/` as an active lab lane. The correct distinction is active Python scripts under tooling paths versus the archived historical Python GUI/CLI parity app.
- Existing pending WinUI changes are preserved and will be validated as part of this goal.

## Validation

See `.codex/state/winui-product-consolidation-evidence.md`.

## Remaining Risks

- Electron, WPF, and the historical Python GUI/CLI app are still present; remaining references must clearly keep them out of product-lane release scope.
- Manual screenshot/visual design review is not yet performed, but an explicit desktop launch smoke now passes.
- Archive/reclassification moves are not yet inspected deeply enough to perform safely.
- Physical moves of Electron/Python trees were not attempted in this batch because package scripts, workspaces, tests, and reference docs still need a separate safe-move inventory.

## Next Target

Run final diff/whitespace checks, then classify the next slice as manual WinUI visual smoke or focused WinUI product hardening rather than more Electron/Python cleanup.
