# Local Sign-Off Commands

Status: active lane sign-off gate
Last updated: 2026-06-22

Use this runbook for public-primary local lane validation. It does not publish anything. Some commands write ignored validation reports or regenerated release-policy artifacts when explicitly listed. WinUI 3 is the primary product lane. Electron, WPF, and the old Python GUI/CLI app are archived/reference.

**Default branch:** `main` (WinUI lane promotion, 2026-05-27). **Release profile source:** run `py -3 tools\release_profile_snapshot.py --check` and `py -3 tools\release_curated_manifest.py --check`; do not copy release-count totals from old prose because the generated artifacts are the source of truth. **Evidence index:** `release/readiness/winui_main_lane_gate_index_2026-05-27.md` (maps local gates, ZIP probes, visual/Home smoke docs, and re-run rules). **MSIX strategy (not selected):** `release/readiness/msix_trust_strategy_next_steps_2026-05-27.md`. Re-run ZIP probes only when WinUI publish output or probe scripts change.

## 0. Start In Repo Root

```powershell
cd <repo-root>
```

## 1. Private WinUI Product Lane Gates

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI.slnx" --nologo
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-installer-preflight
npm run test:winui-zip-package-probe
npm run test:winui-zip-release-candidate-probe
npm run test:winui-msix-trusted-install-probe
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-safe-copy-runtime
npm run test:winui-safe-copy-music-replacement
npm run test:winui-safe-copy-music-swap-presets
npm run test:winui-safe-copy-music-swap-runtime-artifact-checker
npm run test:winui-patch-engine-safety
```

`npm run test:winui-safe-copy-runtime` is a local maintainer/runtime aggregate. It can require ignored local overlays such as a copied executable, CDB, or proof root, so it is not a default public PR gate.

Second-host online contract/self-test gates are private maintainer checks, not proof that Host/Join can be enabled:

```powershell
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-runtime-causality
npm run test:winui-original-binary-second-host-runtime-causality-builder
npm run test:winui-original-binary-dual-safe-copy-topology
npm run test:winui-original-binary-host-join-enablement
npm run test:winui-original-binary-second-host-live-candidate-gate
```

`test:winui-original-binary-second-host-runtime-causality-builder` is a public-safe preflight/materializer gate. It writes only a file-backed self-test candidate accepted in explicit fixture mode and rejects the current compatibility executor; it is not live runtime causality or Host/Join readiness.

Real second-host candidate validation is intentionally env-gated and should use private placeholder paths in docs:

```powershell
$env:SECOND_HOST_COMMAND_SOURCE_BUNDLE = "<private-proof-root>\command-source-bundle.json"
$env:SECOND_HOST_RUNTIME_CAUSALITY_CANDIDATE = "<private-proof-root>\runtime-causality-candidate.json"
npm run test:winui-original-binary-second-host-command-source-live
npm run test:winui-original-binary-second-host-runtime-causality-candidate
npm run test:winui-original-binary-host-join-candidate-gate
```

Those candidate gates intentionally fail without private inputs. Passing them would validate candidate inputs only; it would not by itself enable Host/Join, public matchmaking, native BEA netcode, or player-ready netplay.

Optional explicit desktop smokes (not in default primary-lane filter; interactive Windows session):

```powershell
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo `
  --filter "FullyQualifiedName~MainWindow_CapturesPrimaryProductScreens|FullyQualifiedName~MainWindow_CapturesScrolledWorkflowSections|FullyQualifiedName~WinUiHomeNavigationSmokeTests" `
  -- NUnit.IncludeExplicit=true NUnit.NumberOfTestWorkers=1
```

Public-safe summaries: `release/readiness/winui_home_visual_smoke_2026-05-27.md`. Private PNGs under `subagents/` (R4 deny).

Expected:

- WinUI project builds.
- AppCore tests pass.
- Applicable UI/static tests pass or report exact blockers.
- Installer/signing preflight reports the current packaging posture without claiming a signed release.
- ZIP package probe proves publish, public-safe ZIP README inclusion, ZIP creation, SHA-256 sidecar generation, extraction, extracted launch, extracted Home navigation smoke (full `WinUiHomeNavigationSmokeTests` on the extracted executable), representative Media smoke, and process cleanup for the non-cert distribution lane.
- ZIP release-candidate probe proves the same non-cert distribution lane with an explicit dated RC package filename.
- Trusted install probe may report the current certificate trust blocker; successful install/launch/uninstall remains unproven until that probe passes.

## 2. C# Support/CLI Gates

Run serially while AppCore/CLI remain support/reference:

```powershell
dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo
dotnet run --project ".\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj" -- --help
```

Expected:

- C# support/parity solution builds.
- CLI help works as a support-lane health check.

## 3. Release Policy Diagnostics

Use the non-check commands only when intentionally refreshing generated release-policy artifacts. For read-only verification, use the `--check` commands in section 4.

```powershell
py -3 tools\release_profile_snapshot.py
py -3 tools\release_curated_manifest.py
py -3 tools\release_curated_manifest.py --check
```

Expected:

- release profile artifacts are regenerated or already current
- curated public-safety/export allowlist is current
- public/private/archive exclusions remain explicit

## 4. Public-Safe Evidence

Before release-candidate review, confirm:

```powershell
py -3 tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:public-allowlist
npm run test:repo-hygiene
bash tools/release_package.sh --dry-run
```

These checks validate tracked docs, documented npm commands, local markdown links, public allowlist safety, stale-public-text hygiene, and release packaging gates (dry-run only; no archive written). They do not publish anything.

`npm run test:md-links` writes ignored JSON/Markdown reports under `subagents/md-link-check`; the report directory must remain excluded from public release output.

The public allowlist gate is content-aware: generated candidate rows that contain local proof/backup-root payloads are excluded, and `npm run test:public-allowlist` remains the fail-closed payload scanner before export.

## 5. Optional Archived Electron Checks

Only run these when intentionally inspecting the archived Electron workbench:

```powershell
npm run archive:electron:build
npm run archive:electron:test:renderer-smoke
npm run archive:electron:test:cli-smoke
```

Expected:

- Archived Electron/React/TypeScript code still builds or reports exact archive-health blockers.
- Failures here are archive-health issues unless a later prompt explicitly reactivates Electron.

## 6. Optional Legacy WinUI Bundle Checks

Only run the archived bundle helper when intentionally validating historical packaging reference material:

```powershell
powershell -ExecutionPolicy Bypass -File .\archive\legacy-winui-release\Build-PortableBundle.ps1 -ForceClean
```
