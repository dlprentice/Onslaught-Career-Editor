# WinUI Toolchain And QA Direction

Status: active
Last updated: 2026-05-26

This note records the current WinUI 3 product-lane tooling decision so future work can move quickly without reopening the Electron detour or adding speculative desktop frameworks.

## Decision

WinUI 3 on the Windows App SDK remains the primary user-facing Windows desktop app stack for this repository.

That does not mean every graphics, media, automation, or reverse-engineering concern must be solved by XAML controls alone. It means the app shell and normal player-facing workflows stay native Windows, while lower-level needs use focused Windows-native or repo-local tooling.

Current direction:

- User-facing app: `OnslaughtCareerEditor.WinUI/` with WinUI 3, Windows App SDK, C#, XAML, and AppCore.
- Core logic: `OnslaughtCareerEditor.AppCore/` for save/options parsing, patch plans, asset catalog summaries, and shared correctness.
- Native UI automation: `OnslaughtCareerEditor.UiTests/` using UI Automation through FlaUI plus static product-lane guards.
- Visual evidence: WinUI launch/visual smokes that capture ignored screenshots under `subagents/`, with public-safe summaries in `release/readiness/`.
- 2D rendering escalation: Win2D only when XAML Canvas becomes the limiting factor for texture/model previews, charts, overlays, or other immediate-mode 2D drawing.
- 3D rendering escalation: deliberate Direct3D/SwapChainPanel or conversion-viewer planning only after the repo has a concrete model-preview requirement that exceeds the current lightweight wireframe preview.
- RE/tooling support: Python scripts under `tools/`, C# support CLIs, Ghidra/CDB helpers, and copied artifact roots.

Do not reintroduce Electron, WPF, the old Python GUI, or a browser shell as the community product surface unless a later strategy prompt explicitly reverses the current lane decision.

## Why This Is The Right Stack

Current Microsoft documentation describes the Windows App SDK as the unified API/tooling set for modern Windows apps, with WinUI as the modern native UI framework for Windows apps. The WinUI 3 documentation describes it as Microsoft's modern native UI framework for Windows desktop applications and part of the Windows App SDK.

For this repository, that maps well to the real problem:

- Battle Engine Aquila is a Windows game with Windows filesystem, media, executable, DirectX-era, controller, debugger, and launcher concerns.
- The primary app needs to feel native and stable for normal Windows users.
- The app must interoperate with local files, copied executables, copied saves/options, local media, and app-owned artifact roots.
- Native UI Automation can test offscreen and scrolled controls through automation IDs and scroll patterns, which matches the current WinUI smoke strategy.

Electron, WPF, and the old Python GUI remain useful historical references, but they are no longer the product path.

## Current QA Stack

Use the strongest relevant checks for the work being changed:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

For focused WinUI visual or interaction work, add the relevant filtered UI test:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests"
```

For release/docs changes, use the release safety gates:

```powershell
py -3 tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

UI claims should distinguish:

- first-viewport visual proof
- scrolled workflow visual proof
- accessibility-tree automation proof
- static XAML/code guard proof
- real copied-file/runtime proof

Do not treat one category as proof of another.

## Rendering Escalation Rules

The current Asset Library model view is intentionally a lightweight wireframe preview over parsed FBX geometry facts. It is useful, bounded, and already validated across the current private generated model catalog.

Do not add a renderer just because the preview could be prettier.

Escalate only when a concrete product need exists:

| Need | Preferred path | Notes |
| --- | --- | --- |
| Larger/faster 2D preview, overlays, texture transforms, charts, simple immediate-mode drawing | Win2D in WinUI | Microsoft documents Win2D as a GPU-accelerated WinRT 2D API usable in WinUI Windows App SDK apps. |
| Real model inspection with camera, lighting, materials, UVs, normals, or animation | Direct3D/SwapChainPanel planning or external converted preview workflow | Treat this as a deliberate mini-architecture slice. Do not add speculative dependencies. |
| Offline conversion/export | Existing `tools/`, AppCore, or narrow C# utility | Keep private game assets and generated outputs out of public release scope. |
| Full game-rebuild rendering research | RE docs and scratch evidence first | Do not turn product UI into an engine before the reverse-engineering evidence supports it. |

## Dependency Rules

Before adding any new UI, rendering, test, or packaging dependency:

1. Prove the current stack cannot solve the concrete problem cleanly.
2. Prefer Windows-native dependencies that work with WinUI 3 and AppCore.
3. Add the smallest dependency that solves the problem.
4. Update third-party notice generation and release evidence.
5. Validate WinUI build, active UI tests, release policy, and docs.

Current likely candidates:

- Win2D for richer 2D native previews.
- A deliberate Direct3D/SwapChainPanel path for true 3D preview only after a focused proof plan.
- Accessibility Insights for Windows or equivalent manual accessibility review tooling as release-candidate QA evidence, not as a repo dependency.

## What Not To Do

- Do not revive Electron because screenshots are easier in a browser.
- Do not migrate WinUI to a cross-platform UI framework unless Windows is no longer the product target.
- Do not replace UI Automation/FlaUI solely because native UI testing is more work than browser testing.
- Do not add a full 3D/game-engine dependency before a focused model-preview proof plan.
- Do not claim installer, signed release, accessibility certification, full 3D rendering, or semantic gameplay interpretation until those things are actually proven.

## Source References Checked

Official Microsoft references consulted on 2026-05-06:

- [Windows App SDK](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/)
- [WinUI 3](https://learn.microsoft.com/en-us/windows/apps/winui/winui3/)
- [Win2D overview](https://learn.microsoft.com/en-us/windows/apps/develop/win2d/)
- [UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32)
