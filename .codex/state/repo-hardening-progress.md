# Repo Hardening Progress Ledger

Status: active
Last updated: 2026-05-03

## Current Phase

First Ralph-style hardening loop reached a review stop, but that stop must now be audited against the evidence-based completion gate in `.codex/goals/repo-hardening.md`. Treat the previous completion claim as untrusted until `.codex/state/repo-hardening-evidence.md` is filled in from git diff, validation output, coverage evidence, search evidence, and an allowed stop reason.

## Files Inspected

- `.codex/goals/repo-hardening.md`
- `.codex/state/repo-hardening-progress.md`
- `package.json`
- `README.MD`
- `README.RELEASE.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md`
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md`
- `release/readiness/release_readiness_checklist.md`
- `release/readiness/release_lane_strategy_2026-05-01.md`
- `release/readiness/curated_release_manifest.json`
- `release/readiness/redaction_notes.md`
- `roadmap/repo-structure-and-archive-map.md`
- `roadmap/technical-debt.md`
- `roadmap/agent-workflow.md`
- `lore-book/roadmap/technical-debt.md`
- `lore-book/roadmap/agent-workflow.md`
- `tools/release_profile_snapshot.py`
- `tools/public_allowlist_safety_check.py`
- `tools/docsync_policy.json`
- `tools/export_game_assets.py`
- `archive/electron-workbench/release/ElectronBundlePolicy.psm1`
- `archive/electron-workbench/release/Test-ElectronBundlePolicy.ps1`
- `archive/electron-workbench/release/Test-ElectronBundleSmoke.ps1`
- `archive/electron-workbench/apps/electron/src/main.ts`
- `archive/electron-workbench/apps/electron/src/preload.ts`
- `archive/electron-workbench/apps/electron/src/release-policy.ts`
- `archive/electron-workbench/apps/electron/src/content-browser.ts`
- `archive/electron-workbench/apps/electron/src/media-catalog.ts`
- `archive/electron-workbench/apps/electron/src/job-runner.ts`
- `archive/electron-workbench/packages/cli/src/index.ts`
- `archive/electron-workbench/packages/ui/src/lib/mock-data.ts`
- `tools/prepare_game_profile.ps1`
- `tools/start_game_profile.ps1`
- `tools/list_game_windows.ps1`
- `tools/send_game_window_input.ps1`
- `OnslaughtCareerEditor.Release.slnx`
- `OnslaughtCareerEditor.AppCore/`
- `OnslaughtCareerEditor.AppCore.Host/`
- `OnslaughtCareerEditor.AppCore.Tests/`
- `OnslaughtCareerEditor.Cli/`
- `OnslaughtCareerEditor.UiTests/`
- TypeScript and Vite config files under `tsconfig*.json`, `archive/electron-workbench/apps/electron`, `archive/electron-workbench/packages/ui`, `archive/electron-workbench/packages/contracts`, and `archive/electron-workbench/packages/cli`.

## Findings

- `.codex/` did not exist before setup and was not classified in release tooling.
- After adding `.codex/**` as release-excluded agent/operator material, several active release docs and safety descriptions still omitted it.
- `tools/public_allowlist_safety_check.py` did not reject `.codex/` paths if they ever appeared in the generated public allowlist.
- The live Electron release policy inventory and browser fixture did not include `.codex/` as a denied path.
- Electron `BrowserWindow` already used `contextIsolation: true`, `nodeIntegration: false`, and `sandbox: true`, but did not explicitly deny renderer-created windows, top-level navigations, or browser permission prompts.
- The `shell:openExternal` IPC accepted only strings beginning with `https://`; parsing through `URL` is stricter and avoids non-string/invalid URL ambiguity.
- Electron bundle policy denied `game/`, `media/`, `save-attempts/`, `subagents/`, state files, and operator docs, but did not deny `app/.codex`.
- `py -3 tools\docsync_check.py` failed after editing `roadmap/agent-workflow.md` because the lore-book mirror was stale.
- Asset extraction docs and `tools/export_game_assets.py` still described future WinUI integration even though Electron is now the active workbench direction.
- `roadmap/technical-debt.md` still listed moving legacy WinUI bundle scripts as open debt after those helpers had already been archived under `archive/legacy-winui-release/`.
- Updating the canonical asset extraction doc caused docsync to catch the mirrored lore-book copy, which needed the same wording correction.
- The hardened external-link helper correctly parsed and restricted URLs, but initially discarded the `shell.openExternal()` promise. IPC should preserve async error behavior and non-IPC background opens should catch rejections.
- Dependency audit found no high or higher npm vulnerabilities.
- Active TODO/stale-marker scan mostly surfaced intentional RE placeholders, archived/private materials, or explicit known gaps rather than a safe immediate code fix.
- CLI argument/input handling, Game Harness helper scripts, and managed-process selection were inspected. No safe patch was found beyond existing arm phrases, copied-profile checks, exact-target scoped input, and artifact-root containment.
- C# solution/project inspection found AppCore/AppCore.Host/C# CLI still limited to parity/reference. The release solution excludes WinUI, and legacy WPF tests are explicit/reference-only.
- The original completion gate was too subjective. The goal now requires `.codex/state/repo-hardening-evidence.md` before any completion claim.

## Fixes Completed

- Created `.codex/goals/repo-hardening.md` as the mostly immutable operating contract.
- Created `.codex/state/repo-hardening-progress.md` as the mutable progress ledger.
- Added an evidence-based completion gate to `.codex/goals/repo-hardening.md`.
- Created `.codex/state/repo-hardening-evidence.md` as an audit scaffold; it still needs to be populated by the next Codex audit run.
- Classified `.codex/**` as `R4_DENY` in `tools/release_profile_snapshot.py`.
- Added `.codex/**` to `release/readiness/curated_release_manifest.json` excludes.
- Added `.codex/**` to `release/readiness/redaction_notes.md` and the repo structure/archive map.
- Regenerated release profile/private inventory/allowlist artifacts.
- Updated active release docs and workflow docs so `.codex/` is named with the private/runtime deny families.
- Updated `tools/public_allowlist_safety_check.py` so `.codex/` is rejected if it appears in the public allowlist.
- Mirrored the `roadmap/agent-workflow.md` changes to `lore-book/roadmap/agent-workflow.md`.
- Added `.codex` to the live Electron release policy path rules and browser fixture release policy data.
- Hardened Electron external navigation:
  - added strict URL parsing for `shell:openExternal`;
  - preserved async IPC error behavior by awaiting `shell.openExternal()` in the IPC path;
  - caught rejected background shell opens from denied new-window/navigation attempts;
  - kept external opens HTTPS-only;
  - denied renderer-created windows inside the workbench;
  - blocked unexpected top-level renderer navigations;
  - denied renderer permission prompts by default.
- Added renderer smoke coverage proving the external-link bridge rejects non-HTTPS URLs.
- Added `app/.codex` to Electron bundle policy deny roots.
- Extended bundle policy smoke fixture and bundle smoke denied-path assertions to cover `.codex`.
- Updated asset extraction docs and the extraction summary note from future WinUI integration to Electron workbench integration.
- Marked the legacy WinUI bundle-script archive debt complete in both roadmap and lore-book mirrors.
- Mirrored canonical reverse-engineering and roadmap doc changes to lore-book copies until docsync passed.

## Validation Commands Run

- `node -e "JSON.parse(require('fs').readFileSync('developer_agent_state.json','utf8')); JSON.parse(require('fs').readFileSync('documentation_agent_state.json','utf8')); console.log('state json ok')"`: PASS.
- `py -3 tools\release_profile_snapshot.py`: PASS, regenerated profile artifacts with `.codex/**` classified as `R4_DENY`.
- `py -3 tools\release_curated_manifest.py`: PASS, regenerated public allowlist; selected file count remained 1160.
- `py -3 tools\release_profile_snapshot.py --check`: PASS.
- `py -3 tools\release_curated_manifest.py --check`: PASS.
- `py -3 tools\docsync_check.py`: initially FAIL for `roadmap_agent_workflow` mirror drift; PASS after syncing `lore-book/roadmap/agent-workflow.md`.
- `npm run test:public-allowlist`: PASS.
- `npm run test:repo-hygiene`: PASS.
- `npm run test:md-links`: PASS.
- `npm run test:doc-commands`: PASS; 295 documented npm commands checked.
- `npm audit --audit-level=high`: PASS; found 0 vulnerabilities.
- `npm run test:cli-smoke`: PASS.
- `npm run typecheck`: PASS.
- `npm run archive:electron:test:renderer-smoke`: PASS; renderer smoke returned `{"ok":true,"failures":[]}`. Electron logged the expected rejected non-HTTPS external-link error during the negative smoke assertion.
- `npm run archive:electron:test:bundle-policy`: PASS.
- `npm run archive:electron:test:parity`: PASS.
- `npm run archive:electron:test:bundle-smoke`: PASS; built disposable community bundle under ignored `release/artifacts/`.
- `dotnet build .\OnslaughtCareerEditor.Release.slnx --nologo`: PASS with .NET preview SDK informational messages.
- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo`: PASS, 19/19.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"`: PASS, 21/21.
- `git diff --check`: PASS with existing line-ending warnings on generated TSV/code files.

## Validation Failures

- `py -3 tools\docsync_check.py` failed once after editing `roadmap/agent-workflow.md`; the mirror file was updated and the rerun passed.
- `py -3 tools\docsync_check.py` failed once after editing `reverse-engineering/game-assets/extraction-pipeline.md`; the lore-book mirror file was updated and the rerun passed.

## Remaining Risks

- This pass was broad but not a proof that the repository has no bugs. Confidence is limited to the areas inspected and the gates run.
- Packaged portable-bundle runtime media/Game Harness proof remains a separate unproven release gap; this hardening loop did not run BEA or runtime proof.
- The active TODO/stale-marker scan contains many RE placeholders and known gaps that should not be bulk-edited without fresh RE evidence.
- C# parity-oracle retirement is still deferred until equivalent TypeScript golden fixtures exist.
- Generated Electron bundle smoke artifacts under ignored `release/artifacts/` were created during validation and remain intentionally untracked.

## Deferred Follow-Ups

- Packaged portable-bundle runtime proof remains the next substantive release-facing milestone, but it is outside this hardening goal and was not started.
- Continue job-runner mutation/path-boundary tests only when adding targeted negative coverage; no safe broad rewrite was identified in this pass.
- Continue replacing C# parity oracles with TypeScript golden fixtures when behavior coverage is ready.
- Keep the separate UI/UX redesign lane out of scope.
- Do not commit unless the user explicitly instructs it.

## Next Planned Inspection Target

Audit the previous completion claim first. Populate `.codex/state/repo-hardening-evidence.md`, verify the actual diff and validation claims, and only then choose between continuing repo hardening or starting the separate packaged portable-bundle runtime proof milestone.
