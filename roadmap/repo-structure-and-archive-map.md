# Repo Structure And Archive Map

Status: active
Last updated: 2026-06-24
Doc version: 3.0

This map classifies the public-primary repo layout so cleanup can proceed
without breaking the WinUI product lane, active Python utility/tooling scripts,
archived Electron/Python/WPF app references, public collaboration posture, or
local runtime evidence overlays. Do not move or delete a surface from this map
unless a later prompt proves all build, test, solution, and release references
are updated.

## Cleanup Rule

- Active product source, validation tooling, and maintainer-run scripts stay in
  place. This does not authorize or imply active standing automations.
- Shared correctness/reference surfaces stay in place until their lane role is
  explicitly retired.
- Archived surfaces may remain tracked for provenance and tests, but they are
  not product targets.
- Public source should include useful source, docs, tools, RE contracts, state
  batons, readiness notes, compact proof summaries, and text agent reports.
- Local/runtime hard payloads stay ignored: game files, copied executables,
  private media/input payloads, arbitrary saves, full Ghidra databases/backups,
  raw frame dumps, raw CDB logs, secrets, and generated build output.
- Public release ZIP contents are intentional package artifacts; they are not
  the same thing as the public source repo.

## Active Shipping/Product Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `OnslaughtCareerEditor.WinUI/` | Primary WinUI 3 product lane | Tracked public source | Primary user-facing Windows product lane. Build/test health has been proven locally; signed/installer packaging remains a future proof. |
| `OnslaughtCareerEditor.AppCore/` | Shared correctness/core support | Tracked public source | Core C# behavior support for the Windows lane and parity/reference checks. |
| `lore/`, `lore-book/` | Active curated content | Tracked public docs/content | Lore and user-facing/reference content. Keep hard runtime payloads out. |
| `patches/catalog/patches.v2.json` | Active patch catalog | Included | Byte-verified copied-executable patch catalog. |

## Active Automation/Tooling Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `tools/` | Mixed active tooling | Tracked public source where not hard payload | Contains release scripts, AYA/media/export tooling, Ghidra helpers, CDB helpers, and game-harness helpers. Tools may require user-supplied local overlays. |
| `tools/public_primary_migration_inventory.py` | Public-primary migration guard | Tracked | Verifies remaining private-only tracked delta is limited to hard payload or volatile scratch classes. |
| `release/readiness/curated_release_manifest.json` | Historical/source release accounting input | Tracked public source | Retained for provenance and release-safety checks, but no longer means the public repo is a tiny curated export. |
| `release/readiness/public_candidate_allowlist.tsv` | Generated public candidate allowlist | Tracked public source | Manifest-derived allowlist used by legacy release checks; not the full public-primary source boundary. |
| `release/readiness/public_package.json` | Public package template | Tracked public source | Reference for reviewed npm command surfaces and package-shape checks. |
| `release/readiness/public_AGENTS.md` | Public candidate agent guide | Tracked public source | Historical/materialized guide; root `AGENTS.md` is now the public-primary contributor guide. |
| `release/readiness/public_gitignore.txt` | Public candidate ignore template | Tracked public source | Historical/materialized ignore template; root `.gitignore` is now the public-primary working ignore file. |
| `reverse-engineering/binary-analysis/mapped-systems.md` | Active RE pointer index | Tracked public RE docs | The public repo now carries the RE pointer forest and static accounting docs, while full Ghidra databases/backups remain local. |
| `reverse-engineering/source-code/stuart-source-requirements.md` | Active source-code RE planning note | Included by curated docs policy | Moved from the repo root after reference checks; source/build/symbol/tooling requirements now live beside source-code analysis docs. |

## Shared Correctness/Reference Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `OnslaughtCareerEditor.AppCore.Host/` | Temporary parity bridge | Included while parity gates remain | JSON/stdio AppCore bridge used by Electron diagnostics/parity. |
| `OnslaughtCareerEditor.AppCore.Tests/` | Temporary parity tests | Included | C# regression tests for the current oracle lane. |
| `OnslaughtCareerEditor.Cli/` | Active C# support CLI | Included while public-safe and needed | C# analyzer/patcher CLI retained for Windows/AppCore workflows and comparison/reference. |
| `OnslaughtCareerEditor.UiTests/` | Parity/static tests | Included | Some tests intentionally inspect archived WPF files, so archive paths must not move casually. |
| `OnslaughtCareerEditor.WinUI.slnx` | Primary WinUI lane solution | Included | References the WinUI app, AppCore, AppCore.Tests, UiTests, and C# CLI for normal Windows-lane development. |
| `OnslaughtCareerEditor.Release.slnx` | Active C# parity/support solution | Included | References AppCore, AppCore.Host, AppCore.Tests, C# CLI, and UiTests as support/parity coverage. The primary app solution is `OnslaughtCareerEditor.WinUI.slnx`. |
| `references/` | Source/reference corpus | Tracked gitlinks | Contains submodule gitlinks to Stuart source and AYAResourceExtractor references. Submodule contents keep their own provenance/licensing; full game payloads do not belong here. |

## Archived Or Non-Shipping Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `archive/electron-workbench/` | Archived Electron/React/TypeScript workbench detour | Tracked reference source; not shipped app payload | Former Electron main process, React renderer, TypeScript contracts, TypeScript CLI, and Electron bundle helpers. Optional `archive:electron:*` npm scripts exist for reference checks only. |
| `archive/legacy-winui-release/` | Archived WinUI portable-bundle helpers | Tracked reference source; not shipped app payload | Retained only as historical reference for the WinUI bundle; Electron release helpers are `archive/electron-workbench/release/Build-ElectronBundle.ps1`, `archive/electron-workbench/release/ELECTRON-BUNDLE-LAUNCHER.cmd`, and `archive/electron-workbench/release/ELECTRON-BUNDLE-README.MD`. |
| `archive/legacy-wpf/` | Archived WPF app | Tracked reference source; not active product | Historical WPF surface. `OnslaughtCareerEditor.UiTests` still reads archived XAML resources, so do not move in cleanup-only passes. |
| `archive/legacy-python/` | Archived Python GUI/CLI parity app | Tracked reference source; not active product | Historical PyQt GUI and Python CLI parity attempt. Active Python tooling should live under `tools/` or be deliberately reclassified one narrow piece at a time. |
| Top-level legacy C#/WPF files | Archived elsewhere or absent at root | Excluded if reintroduced | The legacy WPF `App.xaml`, `MainWindow.xaml`, `Onslaught - Career Editor.csproj`, and `Onslaught - Career Editor.sln` live under `archive/legacy-wpf/`; release policy also excludes those root filenames if they reappear. |
| `archive/historical-docs/WHAT_WE_CAN_DO_NOW.md` | Deprecated historical priority snapshot | Tracked historical docs | Archived after reference checks; current app direction is README, current capabilities, roadmap, and this map. |
| `archive/historical-docs/USER_SANITY_CHECK.md` | Deprecated C#/WPF sanity checklist | Tracked historical docs | Archived after reference checks; use WinUI/AppCore `dotnet build` / `dotnet test` and `npm run test:winui-primary-lane` in active docs instead. Optional `npm run archive:electron:build` applies only when archived workbench health is deliberately in scope. |
| `archive/historical-docs/winui-migration-plan.md` | Superseded WinUI migration record | Tracked historical docs | Archived after reference checks; active roadmap index points readers to the three-lane strategy instead. |
| `wave_online_audit/`, `wave_online_audit2/` | Historical audit notes | Tracked if text/non-payload | Useful for audit provenance; raw runtime payloads still stay local. |
| `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | Documentation-only collaboration templates | Included where public-safe | Allowed public-primary collaboration templates. Do not add workflows, hosted CI, release automation, or Actions scaffolding. |

## Private Local/Runtime-Only Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `game/` | Local game mirror overlay | Ignored local payload | Read-only input for local proof only. Never patch repo-local `game/BEA.exe`. |
| `media/` | Local media/input overlay | Ignored local payload | Must not be tracked unless a future public-safe subset is explicitly classified. |
| `save-attempts/` | Local saves/options overlay | Ignored local payload | Useful for local tests and fixtures. The only tracked save-shaped exception is `tests_shared/fixtures/gold_career_save.bin`. |
| `subagents/` | Agent/proof reports | Tracked when text/non-payload; generated payload reports ignored by path | Text reports and compact summaries may be tracked. Screenshots, raw CDB logs, frame dumps, copied-game proof payloads, and generated md-link reports stay ignored/local. |
| `BEA.exe.gzf`, `BEA_Widescreen.exe`, `setuphistory.txt`, `winui-build.log` | Historical/private local artifacts | Excluded unless explicitly reviewed | Leave in place until a later inventory proves whether to archive, regenerate, or remove from private history. |

## Release-Excluded Evidence And Operator Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `release/readiness/private_runtime_evidence/` | Historical runtime proof reports | Track compact text summaries only; portable app ZIP excluded | Raw screenshots/frame PNGs/proof JSON remain local/ignored. Folder name is historical; tracked files are compact proof summaries, not raw payloads. |
| `.codex/` | Historical project goal/state notes where tracked; runtime cache local where untracked | Tracked only when compact and non-secret; portable app ZIP excluded | Do not publish runtime cache/session material. Compact historical project-goal notes may be tracked as public-primary source when useful. |
| `release/artifacts/`, `release/out/` | Generated release/build output | Ignored local output | Regenerated as needed and never treated as source content. |
| `reverse-engineering/binary-analysis/scratch/`, `lore-book/reverse-engineering/binary-analysis/scratch/` | RE scratch evidence and generated read-back archives | Track promoted summaries/checkers; keep volatile payload scratch local | Public-safe summaries should be promoted into canonical docs instead of shipping raw scratch trees. |
| `onslaught_codex_directive.md` | Operator/development directive | Local/operator-only unless explicitly public-reviewed | Prompt-order contract when activated; do not publish secrets or authority-bearing local runtime material. |
| `developer_agent_state.json` | Repo implementation state | Tracked state baton | Main-agent handoff state. Keep concise and non-secret. |
| `documentation_agent_state.json` | Repo docs/review state | Tracked state baton | Main-agent handoff state. Keep concise and non-secret. |
| `re_orchestrator_state.json` | RE orchestration state | Tracked state baton when active | RE coordination state. Keep concise and non-secret. |
| `AGENTS.md` | Public-primary contributor agent guide | Tracked root guide | Required for public repo operation. |
| `COLLABORATION.md` | Public-safe collaboration guide | Included | Handoff/PR/review expectations for collaborators working from the public-primary repo. |
| `CONTRIBUTING.md`, `SECURITY.md`, `README.RELEASE.md`, `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` | Public-safe contributor/release guides | Included where public-safe | Local validation, private-data reporting, and public-source sign-off guidance. |
| `CURRENT_CAPABILITIES.md` | Public-primary capability summary | Tracked public source | Current capability surface for contributors and users; raw local proof payload paths and generated runtime evidence remain excluded. |

## Move Decisions

Prompt 8 moved no files. The 2026-05-05 WinUI consolidation pass then archived the Electron/React/TypeScript detour.

- `OnslaughtCareerEditor.WinUI/` remains in place as the primary Windows product lane; no physical move occurs in the consolidation reset.
- `archive/electron-workbench/` now contains the former Electron app, React renderer, TypeScript contracts, TypeScript CLI, and Electron bundle helpers. This is reference/provenance code, not an active product or release lane.
- `archive/legacy-wpf/` remains in place because tests still reference its XAML.
- `archive/legacy-python/` remains in place as archived historical Python GUI/CLI parity code. It is reference material, not the active Python tooling lane.
- `game/`, `media/`, `save-attempts/`, and bulky runtime evidence remain local
  overlays. `subagents/` may carry tracked text reports, but not raw game
  payload, screenshots, frame dumps, raw CDB logs, or copied executable output.
- Deprecated top-level guidance files are archived only after reference checks prove the move is safe; `WHAT_WE_CAN_DO_NOW.md` and `USER_SANITY_CHECK.md` moved to `archive/historical-docs/` because only historical audits and release-deny accounting referenced their root paths.
- `MAPPED_SYSTEMS.md` moved to `reverse-engineering/binary-analysis/mapped-systems.md` after reference checks showed it was an active private RE pointer index, not a product root or public-candidate entrypoint.
- `STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md` moved to `reverse-engineering/source-code/stuart-source-requirements.md` after reference checks showed it was an active source-code RE planning note, not a product root entrypoint.
- Legacy WinUI portable-bundle helpers moved from `release/` to `archive/legacy-winui-release/`; this historical archive does not decide the current WinUI 3 product lane.
- `roadmap/winui-migration-plan.md` moved to `archive/historical-docs/winui-migration-plan.md` because it was superseded and no longer belongs in public roadmap output.

## Current Hard-Payload Excludes To Preserve

The public source repo can carry source/docs/tools/history broadly. Git must
exclude hard payloads, while app ZIP releases additionally exclude
package-irrelevant project-history/accounting surfaces:

- `game/**`
- `media/**`
- `save-attempts/**`
- `subagents/md-link-check/**` and any generated/raw proof payload below
  `subagents/**`
- runtime `.codex` cache/session/auth/log material; compact non-secret
  `.codex/goals/**` and `.codex/state/**` markdown may be tracked in source
  when useful, but app ZIPs and legacy exports omit them
- `release/artifacts/**`
- `release/out/**`
- full Ghidra project databases/backups
- copied executables, DLLs, archives, extracted audio/video/model/texture
  payloads, raw saves/options files, screenshots, frame captures, and raw CDB
  logs
- secrets, `.env*`, credentials, local config, and build/test output

## Next Cleanup Candidates

- Continue replacing stale curated-export wording with public-primary wording
  when encountered.
- Decide whether any narrow algorithm, fixture, or script from `archive/legacy-python/` should be ported into active tooling after script-level inventory and validation.
- Keep Ghidra rename-map Java/name preflight and read-back proof as a focused future hardening task.
- Keep Electron archive health checks optional and separate from WinUI product packaging proof.
- Keep release, UX, and Ralph-loop evidence reports traceable while hard
  runtime payloads stay ignored/local.
