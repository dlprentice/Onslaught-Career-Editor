# WinUI Visual QA Refresh - 2026-05-06

Status: pass with scoped yellow notes

Source commit: 61f0d0b0
Evidence-report commit: ce845eed9791a1965fc692dee3743a803c3d63b9
Latest validation refresh: 2026-05-06
Latest source commit: b5ddc56b43f0e46d0109cb5c1f9e5edac871f772
Latest evidence-update commit: 8d7113539abf79b07f919024a3b47f4faa80f7c1
Latest capture-harness hardening: 2026-05-07, recorded in `winui_visual_capture_harness_guard_2026-05-07.md`

## Objective

Refresh native WinUI visual evidence after the current product-lane hardening waves. This review uses ignored local screenshots from the WinUI desktop app and records only public-safe screenshot summaries.

## Command

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

Latest rerun result at `b5ddc56b43f0e46d0109cb5c1f9e5edac871f772`: pass.

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1, Duration: 47 s
```

Process cleanup check after the rerun reported no lingering `OnslaughtCareerEditor.WinUI`, `dotnet`, `MSBuild`, `vstest.console`, `testhost`, `java`, or `javaw` processes.

Runner hygiene note: an initial attempt from the Node REPL used an incomplete child-process environment and failed during NuGet restore before launching the app. The successful rerun used PowerShell's normal environment with only `MSBUILDDISABLENODEREUSE=1` set.

What it proves:

- the current WinUI app can launch repeatedly in the desktop session
- primary screens render without blank-window failures
- screenshots are captured for Home, Save Lab, Media audio, Media video, Asset Library texture, Asset Library model, Lore, Patch Bench, Settings, and About
- Asset Library model preview visual evidence reflects the current bounded wireframe copy and no longer carries stale "planned native preview" language
- the app closes after each capture
- the 2026-05-07 capture-harness guard normalizes the screenshot window bounds so lower-right OS notifications are less likely to contaminate broad visual evidence

## Private Screenshot Set

Screenshots were captured under ignored local evidence storage. The inherited directory name is:

```text
ignored local visual QA artifact folder
```

The files were refreshed on 2026-05-06. They remain private/ignored and are not release artifacts.

## Screen Review

| Screen | Screenshot | Verdict | Top visible issue | Reference intent |
| --- | --- | --- | --- | --- |
| Home | `01-home.png` | PASS | First viewport is card-heavy but clear. | Meets the native task-router intent. |
| Save Lab | `02-save-lab.png` | PASS | Workflow is dense, but the three-step editor structure is visible. | Meets safe save/options workflow intent. |
| Media audio | `03-media-audio.png` | YELLOW | First viewport is an empty/default selected-track state; playback proof comes from focused Media interaction smoke, not this screenshot. | Meets library layout intent, but not playback-state proof. |
| Media video | `04-media-video.png` | YELLOW | First viewport is an empty/default video state; playback proof comes from focused Media interaction smoke, not this screenshot. | Meets selected-player layout intent at a default state, but not playback-state proof. |
| Asset Library texture | `05-asset-library-texture.png` | PASS | Fixture texture is a simple solid-color generated preview. | Meets texture-preview proof intent for generated catalog fixtures. |
| Asset Library model | `06-asset-library-model.png` | PASS | Wireframe preview is intentionally lightweight rather than full 3D rendering. | Meets current bounded wireframe intent. |
| Lore | `07-lore.png` | PASS | Document starts on Start Here rather than a deep article in this broad smoke. | Meets readable in-app document reader intent. |
| Patch Bench | `08-patch-bench.png` | PASS | Workflow is still information-dense, but original/copy safety is visible. | Meets safe copied-executable workflow intent. |
| Settings | `09-settings.png` | PASS | First viewport does not expand path details; that is intentional. | Meets path-safe setup summary intent. |
| About | `10-about.png` | PASS | Dense capability cards, but readable. | Meets public-safe product/about intent. |

## Public-Safe Summary

- Current WinUI primary surfaces render coherently in the native desktop app.
- The shell remains WinUI-first and no archived Electron/WPF/Python app surface appears as a product lane.
- Settings, Lore, Patch Bench, Asset Library, Save Lab, and Home are visually aligned with the current native product direction.
- Media first-viewport visual smoke is useful for layout, but actual playback proof remains covered by focused Media interaction smokes.
- Full native 3D rendering remains unproven; current visual evidence is bounded wireframe/metadata preview.
- The Asset Library model screen now states the current in-app wireframe preview boundary rather than implying native 3D preview is unavailable.

## What Did Not Change

- No game files were launched or mutated.
- No installed `BEA.exe` was patched.
- No private screenshots were committed.
- No archived app lane was reactivated.
- No release scope was expanded beyond public-safe source/evidence accounting.
