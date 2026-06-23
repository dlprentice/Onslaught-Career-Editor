# Repo Structure And Archive Map

Status: active
Last updated: 2026-06-22
Doc version: 2.0

This map classifies the current private repo layout so cleanup can proceed without breaking the WinUI product lane, active Python utility/tooling scripts, archived Electron/Python/WPF app references, release policy, or private runtime evidence. Do not move or delete a surface from this map unless a later prompt proves all build, test, solution, and release references are updated.

## Cleanup Rule

- Active product and automation surfaces stay in place.
- Shared correctness/reference surfaces stay in place until their lane role is explicitly retired.
- Archived surfaces may remain tracked for tests or history, but they are not product targets.
- Private local/runtime evidence stays private and release-excluded.
- Public/community release contents come from the curated release manifest, not from a broad repo copy.

## Active Shipping/Product Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `OnslaughtCareerEditor.WinUI/` | Primary WinUI 3 product lane | Included in curated source candidate where public-safe | Primary user-facing Windows product lane. Build/test health has been proven locally; signed/installer packaging remains a future proof. |
| `OnslaughtCareerEditor.AppCore/` | Shared correctness/core support | Included while public-safe and needed | Core C# behavior support for the Windows lane and parity/reference checks. |
| `lore/`, `lore-book/` | Active curated content | Included where public-safe | Lore and user-facing/reference content. Keep private runtime evidence out. |
| `patches/catalog/patches.v2.json` | Active patch catalog | Included | Byte-verified copied-executable patch catalog. |

## Active Automation/Tooling Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `tools/` | Mixed active tooling | Partly included by curated policy | Contains release scripts, AYA/media/export tooling, Ghidra helpers, CDB helpers, and game-harness helpers. Public inclusion is allowlist-controlled. |
| `release/readiness/curated_release_manifest.json` | Private-side release policy | Excluded from public candidate | Source-tree release inclusion/exclusion input used by private maintainer gates. Public candidates consume the materialized allowlist/output, not this private policy file. |
| `release/readiness/public_candidate_allowlist.tsv` | Generated public candidate allowlist | Included | Manifest-derived public candidate allowlist; do not add private evidence here. |
| `release/readiness/public_package.json` | Public candidate package template | Materialized as public root `package.json` | Public contributors use the smaller reviewed npm command surface, not the private root package manifest. |
| `release/readiness/public_AGENTS.md` | Public candidate agent guide | Materialized as public root `AGENTS.md` | Sanitized instructions for external developers and their agents. |
| `release/readiness/public_gitignore.txt` | Public candidate ignore template | Materialized as public root `.gitignore` | Public-source ignore rules; the private root `.gitignore` is intentionally permissive for private sync. |
| `reverse-engineering/binary-analysis/mapped-systems.md` | Private active RE pointer index | Private tree; summarized publicly through curated RE entrypoints | Moved from the repo root after reference checks; public candidates use `reverse-engineering/RE-INDEX.md` and `reverse-engineering/public-static-contracts.md` as link-closed entrypoints instead of exporting the private proof pointer forest. |
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
| `references/` | Internal reference corpus | Conditional/review | Contains Stuart source and extractor references. Public release inclusion requires scope/license review. |

## Archived Or Non-Shipping Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `archive/electron-workbench/` | Archived Electron/React/TypeScript workbench detour | Excluded | Former Electron main process, React renderer, TypeScript contracts, TypeScript CLI, and Electron bundle helpers. Optional `archive:electron:*` npm scripts exist for reference checks only. |
| `archive/legacy-winui-release/` | Archived WinUI portable-bundle helpers | Excluded | Retained only as historical reference for the WinUI bundle; Electron release helpers are `archive/electron-workbench/release/Build-ElectronBundle.ps1`, `archive/electron-workbench/release/ELECTRON-BUNDLE-LAUNCHER.cmd`, and `archive/electron-workbench/release/ELECTRON-BUNDLE-README.MD`. |
| `archive/legacy-wpf/` | Archived WPF app | Excluded | Historical WPF surface. `OnslaughtCareerEditor.UiTests` still reads archived XAML resources, so do not move in cleanup-only passes. |
| `archive/legacy-python/` | Archived Python GUI/CLI parity app | Excluded by current policy | Historical PyQt GUI and Python CLI parity attempt. Active Python tooling should live under `tools/` or be deliberately reclassified one narrow piece at a time. |
| Top-level legacy C#/WPF files | Archived elsewhere or absent at root | Excluded if reintroduced | The legacy WPF `App.xaml`, `MainWindow.xaml`, `Onslaught - Career Editor.csproj`, and `Onslaught - Career Editor.sln` live under `archive/legacy-wpf/`; release policy also excludes those root filenames if they reappear. |
| `archive/historical-docs/WHAT_WE_CAN_DO_NOW.md` | Deprecated historical priority snapshot | Excluded | Archived after reference checks; current app direction is README, current capabilities, roadmap, and this map. |
| `archive/historical-docs/USER_SANITY_CHECK.md` | Deprecated C#/WPF sanity checklist | Excluded | Archived after reference checks; use WinUI/AppCore `dotnet build` / `dotnet test` and `npm run test:winui-primary-lane` in active docs instead. Optional `npm run archive:electron:build` (and related `archive:electron:*` scripts in `package.json`) apply only when archived workbench health is deliberately in scope. |
| `archive/historical-docs/winui-migration-plan.md` | Superseded WinUI migration record | Excluded | Archived after reference checks; active roadmap index points readers to the three-lane strategy instead. |
| `wave_online_audit/`, `wave_online_audit2/` | Historical audit notes | Excluded unless explicitly allowed | Useful for audit provenance, not active release content. |
| `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | Documentation-only collaboration templates | Included where public-safe | Allowed public candidate issue/PR templates. Do not add workflows, hosted CI, release automation, or Actions scaffolding. |

## Private Local/Runtime-Only Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `game/` | Private local game mirror | Excluded | Read-only input for local proof only. Never patch repo-local `game/BEA.exe`. |
| `media/` | Private/reference media | Excluded | Must not enter public/community bundles unless a future public-safe subset is explicitly classified. |
| `save-attempts/` | Private/local saves | Excluded | Useful for local tests and fixtures, but public release requires sanitized fixtures only. |
| `subagents/` | Temporary agent/proof artifacts | Excluded | May contain screenshots, proof JSON, generated catalogs, local paths, or private game evidence. |
| `BEA.exe.gzf`, `BEA_Widescreen.exe`, `setuphistory.txt`, `winui-build.log` | Historical/private local artifacts | Excluded unless explicitly reviewed | Leave in place until a later inventory proves whether to archive, regenerate, or remove from private history. |

## Release-Excluded Evidence And Operator Surfaces

| Path | Classification | Release posture | Notes |
| --- | --- | --- | --- |
| `release/readiness/private_runtime_evidence/` | Sanitized private runtime proof reports | Excluded | Text reports are durable private evidence; raw screenshots/frame PNGs/proof JSON remain local/private. |
| `.codex/` | Agent goal contracts and progress ledgers | Excluded | Local/repo agent operating material. Keep goal contracts mostly immutable and progress ledgers mutable; do not publish as community release content. |
| `release/artifacts/`, `release/out/` | Generated release/build output | Excluded | Local generated bundle outputs; regenerated as needed and never treated as curated source content. |
| `reverse-engineering/binary-analysis/scratch/`, `lore-book/reverse-engineering/binary-analysis/scratch/` | RE scratch evidence and generated read-back archives | Excluded | Tracked on the private branch for maintainer provenance, but volatile/private by default. Public-safe summaries must be promoted into curated docs instead of shipping scratch trees. |
| `onslaught_codex_directive.md` | Private operator/development directive | Excluded | Prompt-order contract when activated; not public/community release content. |
| `developer_agent_state.json` | Repo implementation state | Excluded | Main-agent handoff state, not release content. |
| `documentation_agent_state.json` | Repo docs/review state | Excluded | Main-agent handoff state, not release content. |
| `re_orchestrator_state.json` | RE orchestration state | Excluded | Internal coordination state. |
| `AGENTS.md` | Private agent operating contract | Excluded from public bundle | Required for private repo operation, not a community runtime artifact. Public exports materialize `release/readiness/public_AGENTS.md` as root `AGENTS.md`. |
| `COLLABORATION.md` | Public-safe collaboration guide | Included | Handoff/PR/review expectations for private approved collaborators and public candidates. |
| `CONTRIBUTING.md`, `SECURITY.md`, `README.RELEASE.md`, `PUBLIC_SIGNOFF_COMMANDS.md` | Public-safe contributor/release guides | Included where public-safe | Local validation, private-data reporting, and public-source sign-off guidance. |
| `CURRENT_CAPABILITIES.md` | Public/private capability summary | Included as public materialized summary | Public candidates use the sanitized current-capabilities surface; private proof paths and raw evidence remain excluded. |

## Move Decisions

Prompt 8 moved no files. The 2026-05-05 WinUI consolidation pass then archived the Electron/React/TypeScript detour.

- `OnslaughtCareerEditor.WinUI/` remains in place as the primary Windows product lane; no physical move occurs in the consolidation reset.
- `archive/electron-workbench/` now contains the former Electron app, React renderer, TypeScript contracts, TypeScript CLI, and Electron bundle helpers. This is reference/provenance code, not an active product or release lane.
- `archive/legacy-wpf/` remains in place because tests still reference its XAML.
- `archive/legacy-python/` remains in place as archived historical Python GUI/CLI parity code. It is reference material, not the active Python tooling lane.
- `game/`, `media/`, `save-attempts/`, `subagents/`, and private runtime evidence remain in place and release-excluded.
- Deprecated top-level guidance files are archived only after reference checks prove the move is safe; `WHAT_WE_CAN_DO_NOW.md` and `USER_SANITY_CHECK.md` moved to `archive/historical-docs/` because only historical audits and release-deny accounting referenced their root paths.
- `MAPPED_SYSTEMS.md` moved to `reverse-engineering/binary-analysis/mapped-systems.md` after reference checks showed it was an active private RE pointer index, not a product root or public-candidate entrypoint.
- `STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md` moved to `reverse-engineering/source-code/stuart-source-requirements.md` after reference checks showed it was an active source-code RE planning note, not a product root entrypoint.
- Legacy WinUI portable-bundle helpers moved from `release/` to `archive/legacy-winui-release/`; this historical archive does not decide the current WinUI 3 product lane.
- `roadmap/winui-migration-plan.md` moved to `archive/historical-docs/winui-migration-plan.md` because it was superseded and no longer belongs in public roadmap output.

## Current Release Excludes To Preserve

The curated release manifest must continue to exclude:

- `game/**`
- `media/**`
- `save-attempts/**`
- `subagents/**`
- `.codex/**`
- `archive/**`
- `release/readiness/private_runtime_evidence/**`
- `release/artifacts/**`
- `release/out/**`
- `onslaught_codex_directive.md`
- repo state files
- archived WPF/non-shipping app surfaces

## Next Cleanup Candidates

- Continue deciding whether any remaining stale top-level historical notes should move under `archive/` after reference checks.
- Decide whether any narrow algorithm, fixture, or script from `archive/legacy-python/` should be ported into active tooling after script-level inventory and validation.
- Keep Ghidra rename-map Java/name preflight and read-back proof as a focused future hardening task.
- Keep Electron archive health checks optional and separate from WinUI product packaging proof.
- Keep public-safe release, UX, and Ralph-loop evidence reports traceable while private runtime proof stays excluded.
