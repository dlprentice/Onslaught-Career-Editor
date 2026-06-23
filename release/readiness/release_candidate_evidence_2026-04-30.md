# Release Candidate Evidence 2026-04-30

Status: historical public-safe Electron workbench evidence; superseded for product direction
Branch: `wip/sandbox`
Source HEAD verified before Prompt 9 work: `6a596ea0ba58c6ba4a1d98ae3b82f48ffb439027`
Evidence-report commit: `7f2f3f49334767060e5ece6dbfcae75771a7c957`
Report date: 2026-04-30
Local shell timestamp observed during the gate run: `2026-04-29 21:27:33 -04:00`

This report summarizes the April 2026 Electron-first release candidate posture without copying private runtime evidence. It remains useful historical evidence for the archived Electron workbench, but it no longer defines the primary product release lane. Current product release work is WinUI-first. Private runtime proof is recorded in excluded private evidence reports, and those reports remain outside public/community release scope.

## Public-Safety Boundary

This report does not include private absolute Windows paths, raw screenshot paths, raw frame PNG paths, raw proof JSON paths, raw media cache paths, data URLs, base64 payloads, or private game asset paths.

Excluded private proof filenames summarized by this report:

- `2026-04-29-media-proof.md`
- `2026-04-29-game-harness-proof.md`
- `2026-04-29-agentic-re-loop-proof.md`

## Historical Active Product Surfaces At The Time

- `apps/electron`: Electron desktop shell, typed native job runner, preload boundary, native adapters, packaging helpers.
- `packages/ui`: React/Vite renderer for the Workbench, Save Lab, Patch Bench, Media, Lore, RE Lab, Game Harness, and Release surfaces.
- `packages/contracts`: shared typed IPC/job/artifact contracts.
- `packages/cli`: then-active TypeScript automation/API lane over the same job runner; now archived/reference with the Electron workbench.
- `patches/catalog/patches.v2.json`: curated copied-executable patch catalog.
- `release/Build-ElectronBundle.ps1` and bundle policy scripts: portable Electron community-bundle path and policy checks.

## Parity And Reference Surfaces

- `OnslaughtCareerEditor.AppCore`: temporary C# behavior oracle.
- `OnslaughtCareerEditor.AppCore.Host`: temporary JSON/stdio bridge for AppCore diagnostics.
- `OnslaughtCareerEditor.AppCore.Tests`: C# parity regression tests.
- `OnslaughtCareerEditor.Cli`: legacy C# CLI retained for comparison/reference.
- `OnslaughtCareerEditor.UiTests`: parity/static tests, including checks that still reference archived WPF resources.
- `OnslaughtCareerEditor.WinUI`: the current primary user-facing product lane.
- `archive/legacy-wpf` and `archive/legacy-python`: historical/non-shipping archived reference surfaces.

## Release-Excluded Private/Runtime Surfaces

Public/community release outputs must continue to exclude:

- `game/**`
- `media/**`
- `save-attempts/**`
- `subagents/**`
- `release/readiness/private_runtime_evidence/**`
- `onslaught_codex_directive.md`
- repo state files
- executable/binary/save/runtime payload families covered by the curated manifest deny rules
- archived/non-shipping app surfaces unless explicitly reclassified

## Command Results

Final automated gate state for this Prompt 9 pass:

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Clean at Prompt 9 start. |
| `git rev-parse HEAD` | PASS | Returned `6a596ea0ba58c6ba4a1d98ae3b82f48ffb439027` before Prompt 9 edits. |
| `npm run build` | PASS | Build completed; Vite emitted the existing non-fatal chunk-size warning. |
| `npm run typecheck` | PASS | Contracts, Electron, CLI, and UI typechecks passed. |
| `npm run test:cli-smoke` | PASS | TypeScript CLI catalog/run/list smoke passed. |
| `npm run test:renderer-smoke` | PASS | Electron renderer smoke returned `ok:true`. |
| `npm run test:electron-parity` | PASS | Electron parity passed across the current fixture/job-runner surface. |
| `npm run test:bundle-policy` | PASS | Electron bundle policy smoke passed. |
| `npm run test:bundle-smoke` | PASS | Disposable community portable bundle smoke passed. |
| `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo` | PASS | Build succeeded with 0 warnings and 0 errors; .NET preview SDK informational messages were emitted. |
| `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo` | PASS | 19 passed, 0 failed. |
| `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo` | PASS | 21 passed, 0 failed. |
| `py -3 tools\docsync_check.py` | PASS after correction | Initial run found strict mirror drift for quick-reference docs; mirrored those public-safe docs and reran successfully. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS after regeneration | Initial run found stale generated profile artifacts; regenerated snapshots and reran successfully. |
| `py -3 tools\release_curated_manifest.py --check` | PASS after regeneration | Initial run found the public allowlist stale after mirror sync and report inclusion; regenerated the allowlist and reran successfully. |
| Direct public allowlist scan for forbidden families | PASS | No private/runtime families or binary/save payload suffixes were present in the public candidate allowlist. |
| `node -e "<parse developer_agent_state.json and documentation_agent_state.json>"` | PASS | State JSON parsed successfully after final Prompt 9 updates. |
| `git diff --check` | PASS | Whitespace check passed; Git reported line-ending normalization warnings for generated release-profile TSV files only. |

## Runtime Proof Summary

Private runtime proof remains excluded from public release scope. The public-safe summary is:

- Texture PNG preview is proven in Electron desktop dev mode for one catalog-constrained texture preview row.
- In-app Bink playback is proven in Electron desktop dev mode for one catalog-constrained video row using VLC as backend transcode infrastructure and an app-owned MP4 cache.
- Game Harness copied-profile runtime loop is proven in Electron desktop dev mode: prepare copied profile, apply only `force_windowed` to the copied executable, launch as managed process, capture frame, plan/send one bounded scoped input, capture again, stop, and confirm no managed process remains.
- Direct scoped-input helper hardening is proven: real sends require exact process/window identity, while planning remains safe.
- One bounded observe/decide/act/observe/stop loop is proven in Electron desktop dev mode through typed workbench boundaries.

## What Is Proven For This Candidate

- Electron app builds.
- Electron app typechecks.
- Renderer smoke passes.
- TypeScript CLI smoke passes.
- Electron parity passes.
- Bundle policy passes.
- Disposable portable community bundle smoke passes.
- C# parity solution builds.
- C# AppCore tests pass.
- C# UiTests pass.
- Release doc mirror check passes after correction.
- Release profile snapshot check passes after regeneration.
- Public allowlist and curated manifest checks pass after adding this public-safe report.
- Private runtime evidence remains excluded from public/community release scope.

## What Is Not Proven

- Signed or installer-grade release readiness is not proven.
- Packaged portable-bundle runtime media playback has not been separately clicked/proven.
- Packaged portable-bundle Game Harness runtime behavior has not been separately proven.
- Continuous frame streaming is not implemented or proven.
- Semantic gameplay-state interpretation is not proven.
- Open-ended autonomy is not proven.
- Broader media row coverage beyond the focused proof rows is not proven.
- Ghidra rename-map Java/name preflight and read-back hardening remains future work.
- C# parity oracles are not fully retired.

## Release Posture

At the time, the Electron-first release candidate was testable and policy-accounted as a public-safe source/bundle candidate, with private game/media/save/runtime evidence excluded by manifest policy. Current release posture is WinUI-first; this report remains historical archived-workbench evidence and does not support a signed installer claim.

## Exact Next Recommended Action

For current product work, continue WinUI hardening and packaging/signoff planning. Packaged Electron runtime proof is archived workbench validation only.
