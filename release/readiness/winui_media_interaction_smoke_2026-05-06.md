# WinUI Media Interaction Smoke Evidence - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records a focused native WinUI Media interaction smoke. It proves that the WinUI app can use the configured local game install as read-only source material, select real catalog rows through the desktop UI, start inline audio playback, start inline video playback, and keep full local source paths collapsed by default.

This report is public-safe. It does not include private absolute Windows paths, raw game media paths, screenshots, frame captures, copied files, media payloads, data URLs, base64, save contents, executable bytes, or proof JSON. Local screenshots stayed ignored under `subagents/`; only screenshot filenames are listed here.

## What Changed

- Added stable WinUI automation IDs for the Media page controls that matter to real interaction smoke: tabs, search boxes, catalog trees, selected item summaries, transport buttons, progress controls, and source summaries.
- Added an explicit desktop-only FlaUI smoke test, `WinUiMediaInteractionSmokeTests.MediaPage_SelectsRealInstallAudioAndVideoThroughUi`.
- The smoke starts from an ignored isolated app config root and points the app at a locally detected/read-only game install.
- The smoke searches the catalog, selects a real audio row, starts and stops inline audio playback, selects a real video row, starts inline video playback, verifies time advances, and stops playback.
- The smoke asserts selected source summaries do not expose the configured install path or a full Windows path in the primary UI.
- A later Windows App SDK 2.x pass reran the same focused Media interaction smoke against a disposable published executable; see `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md`.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors; preview SDK informational output only. | Confirms the Media automation IDs compile in the WinUI product app. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests"` | PASS | 1/1 explicit runtime UI test passed. | Confirms native UI automation can select real Media rows, start inline audio playback, start inline video playback, verify video time advances, and stop playback. |

## Private Screenshot Review

Screenshots remained local/ignored and are not release artifacts.

| Filename | Status | Public-safe review |
| --- | --- | --- |
| `01-audio-playing.png` | PASS | Shows a selected music row, active Now Playing state, enabled transport, and collapsed path details. |
| `02-video-playing.png` | PASS/YELLOW | Shows selected video playback with timer advancement and visible decoded frame content. The player works, but the selected sample is strongly letterboxed; broader video visual polish remains useful. |

## What Is Proven

- WinUI Media can scan a configured read-only game install.
- Audio catalog search and selection work through the desktop UI.
- Inline audio playback starts and stops from the WinUI page.
- Video catalog search and selection work through the desktop UI.
- Inline video playback starts from the WinUI page and the playback timer advances.
- Default selected audio/video source summaries do not expose full local install paths.
- The smoke leaves no private screenshot or media payload in tracked files.

## What Is Not Proven

- Signed installer-grade release readiness.
- MSIX install/uninstall behavior.
- Broader catalog coverage across many audio and video rows.
- Texture/model extraction or preview coverage in the WinUI product lane.
- Game runtime launch/capture/input proof from the WinUI app.

## Privacy And Release Boundary

The local game install, generated app config, screenshots, and runtime smoke artifacts remain private local evidence under ignored locations. Public release accounting should continue to exclude `subagents/**`, private game/media/save content, executable payloads, raw proof images, media caches, and runtime proof JSON.
