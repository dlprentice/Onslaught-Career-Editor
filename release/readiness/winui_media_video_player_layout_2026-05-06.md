# WinUI Media Video Player Layout Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused WinUI Media video-player layout fix. It does not embed screenshots, frame captures, raw media paths, private absolute paths, copied files, media payloads, data URLs, or base64.

## What Changed

- The video player surface now keeps more vertical space for decoded frames.
- Video source-folder controls moved behind a collapsed `Source folder` expander in the Now Playing card instead of competing with playback as a third primary card.
- The standard Video tab empty state still presents a large, clear player surface.
- The focused real media interaction smoke still starts inline video playback and verifies the timer advances.

## Private Visual Evidence

Ignored screenshots remain under `subagents/` and are not committed:

- `subagents/winui-media-interaction/2026-05-06/02-video-playing.png`
- `ignored local visual QA screenshot (04-media-video.png)`

The playback screenshot shows the selected real video frame larger and readable, with source-folder details available but collapsed.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests"` | PASS | 1/1 explicit native Media interaction smoke passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.MediaPage_HidesSourcePathsInDefaultPlaybackSummaries"` | PASS | 1/1 focused Media product-lane static guard passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 standard visual smoke passed. |

## Proven

- The WinUI Media video page still loads and captures in desktop visual smoke.
- Real inline video playback still starts and advances in the focused Media interaction smoke.
- The visible video playback layout gives the frame more space than the previous shallow strip.
- Full source paths remain collapsed by default.

## Not Proven

- This does not prove every video row plays.
- This does not prove packaged installer/MSIX behavior.
- This does not prove signed release readiness.
- This does not replace broader media-row coverage.
