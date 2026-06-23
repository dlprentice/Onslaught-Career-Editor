# Three-Lane Product Strategy

Status: active canonical strategy
Last updated: 2026-06-19

This document supersedes the Electron-first product strategy. The repo now has a WinUI-first product lane with archived app detours and active script/tooling support.

Static-to-proof/rebuild transition planning is tracked in `static-to-proof-rebuild-transition-backlog.md`. It does not reactivate runtime, visual, patch, Godot, or rebuild proof by itself; it records which static contract slices are strong enough to become the next bounded proof candidates.

Player-facing patch/mod/runtime/rebuild proof accounting is tracked in `mod-patch-runtime-rebuild-register.md`. Keep those measurements separate from static RE percentages.

## Strategic Decision

WinUI 3 is the primary user-facing Windows product lane. Electron, WPF, and the old Python GUI/CLI parity app are archived/reference surfaces rather than competing community product apps. Active Python work is limited to focused scripts and lab utilities under `tools/`.

| Lane | Role | Product priority |
| --- | --- | ---: |
| WinUI 3 Windows app | Primary user-facing Windows desktop product | Active focus |
| Electron workbench | Archived maintainer/agentic RE workbench detour under `archive/electron-workbench/` | Archived/reference |
| Python tooling | Active `tools/` scripts and explicitly reactivated utilities | Support/lab |
| Legacy Python GUI/CLI | Historical parity app under `archive/legacy-python/` | Archived/reference |
| WPF | Archived/reference historical app | Archived |

## WinUI 3 Product Lane

WinUI 3 is the lane normal users should see first. It should own player-facing Windows UX, save/options editing, safe copied-target workflows, user-facing patch flows, and product polish.

Toolchain and QA direction for this lane is tracked in `roadmap/winui-toolchain-and-qa-direction.md`. In short: keep WinUI 3 / Windows App SDK as the native product shell, keep AppCore as shared correctness support, keep UI Automation/FlaUI for native automation, and escalate graphics work to Win2D or Direct3D planning only when a concrete product need exceeds the current XAML/wireframe approach.

Current scope:

- `OnslaughtCareerEditor.WinUI/`
- `OnslaughtCareerEditor.AppCore/`
- `OnslaughtCareerEditor.AppCore.Tests/`
- `OnslaughtCareerEditor.UiTests/` where tests apply to active Windows behavior
- C# solution/project files needed to build and validate the Windows lane

Reactivating WinUI means restoring build/run/test confidence and product focus. It does not mean immediately redesigning the UI, moving Electron features into WinUI, or expanding public release scope without review.

## Archived Electron Workbench Lane

Electron is archived as a reference/provenance app, not a product or active maintainer lane. Its code lives under `archive/electron-workbench/` with its React renderer, TypeScript contracts, TypeScript CLI, and Electron bundle helpers.

Allowed Electron archive work:

- read-only inspection
- restoring optional archive health checks
- porting a narrow, reviewed idea into the active WinUI/AppCore/tools lane
- fixing archive-only broken links or references when they confuse active docs

Halted Electron work:

- broad community-product polish
- broad visual redesign
- attempts to make Electron mimic the WinUI product app
- TypeScript job-runner/CLI expansion
- Electron packaged-runtime proof as a product milestone
- using Browser Use renderer success as product proof

If the archive is revived later, that should be a new explicit strategy decision with its own validation plan.

## Python Tooling And Archived Python App

Python remains useful for reverse engineering and tooling, but the active lane is script-level utility work, not a Python GUI or product CLI. The old Python GUI/CLI parity app under `archive/legacy-python/` was a historical attempt to track WPF/WinUI behavior visually and from the command line; it is now archived/reference.

Allowed Python work:

- extraction and analysis helpers
- asset/media/data transforms
- validation scripts
- fast experiments
- one-off RE inspection tools
- scripts under `tools/`
- narrow, deliberately ported ideas from `archive/legacy-python/` after review

Halted Python work:

- Python GUI/product app work
- Python CLI parity-app work from `archive/legacy-python/`
- attempts to maintain a third product UX
- broad packaging or parity work unless explicitly scoped

Do not describe `archive/legacy-python/` as an active lab lane. If a useful algorithm or fixture from that archive is needed, port or reclassify the narrow piece deliberately and validate it in the active lane.

## WPF Archived/Reference Lane

WPF remains archived/reference only under `archive/legacy-wpf/`. Do not grow WPF product work. Tests that inspect archived WPF resources may remain until replaced.

## Shared Core And Automation Roles

AppCore is shared correctness/core support for the Windows product lane and a useful oracle while the lane is stabilized. It should not be described merely as throwaway Electron parity while WinUI is active again.

The archived TypeScript CLI and Electron job runner remain preserved under `archive/electron-workbench/`. They are not active automation surfaces. Current automation should prefer C# AppCore/C# CLI or focused scripts under `tools/` unless a later prompt explicitly reactivates archived TypeScript pieces.

## Public/Private Safety Boundary

The private repo is not a public release shape. Keep curated public safety/export tooling intact and framework-neutral.

Public safety remains allowlist/curation based until a later public-shaped repo review proves otherwise. `.gitignore` is not a release boundary.

Hard-deny families remain excluded unless a future review sanitizes and reclassifies a narrow subset:

- `game/**`
- `media/**`
- `save-attempts/**`
- `subagents/**`
- `.codex/**`
- `release/readiness/private_runtime_evidence/**`
- operator directives
- repo state files
- raw binaries, saves, screenshots, frames, cache paths, and private runtime evidence

The curated source candidate can be WinUI-first when release policy explicitly includes reviewed WinUI/AppCore/CLI/docs/tooling source. Do not claim signed installer readiness until packaging, signing, install/uninstall, dependency, and public-safety impact are reviewed.

## Validation Gates

Use only the gates relevant to a change.

### Windows Lane

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

WinUI run command:

```powershell
dotnet run --project .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj
```

Do not require UI launch proof when the environment cannot display the app.

### Archived Electron Workbench Lane

```powershell
npm run archive:electron:build
npm run archive:electron:test:renderer-smoke
npm run archive:electron:test:cli-smoke
```

These are optional archive-reference checks only. They are not WinUI product gates.

### Python Lab Lane

Identify script-specific validation during Python work. Prefer existing `py -3 ...` checks and focused fixtures over inventing heavy packaging.

### Docs And Public Safety

```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools\docsync_check.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

## Next Recommended Work Sequence

1. Three-lane strategy reset: complete.
2. Static Ghidra closeout: complete at **6411/6411 = 100.00%** with `0 / 0 / 0` static debt and Wave1220 active current-risk closeout **1179/1179 = 100.00%**. Reopen static/Ghidra only when source, decompile, xref, runtime, or patch evidence contradicts the current contract.
3. Active runtime/mod/patch proof: continue safe-copy WinUI/AppCore work through bounded copied-profile artifacts. Current public front door is `roadmap/mod-patch-runtime-rebuild-register.md`; detailed online feasibility ledgers remain private until rewritten as public summaries.
4. Online multiplayer proof ladder: continue toward private multi-host proof when a second host/session is available; otherwise keep improving same-host authority/control evidence without claiming multi-host LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, or 4+ player runtime behavior.
5. WinUI 3 UX/product polish: keep dedicated UI/UX critique active after clean runtime/proof checkpoints. UI/UX and copy changes should receive helpful and skeptical review, but implementation, validation, and release acceptance stay with the maintainer lane.
6. Private/public repo cleanup: prepare tidy private and public repo surfaces with release denylist boundaries intact, but do not publish a public release without explicit operator approval.
7. Python tooling inventory: keep active work under script/tooling paths and leave the archived Python GUI/CLI parity app as reference unless a narrow piece is deliberately ported.
8. Archived Electron workbench: do not resume unless a later explicit strategy prompt reactivates it.
