# WinUI Dependency Compatibility Update - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records a focused dependency compatibility update for the WinUI-first product lane. It upgraded non-major runtime/media packages before the later Windows App SDK 2.x migration was attempted and proven separately.

This report is public-safe. It does not include private game paths, screenshots, copied executables, extracted assets, runtime proof JSON, or local NuGet cache paths.

## Package Updates

| Package | Previous | Current | Reason |
| --- | ---: | ---: | --- |
| `LibVLCSharp` | `3.9.6` | `3.9.7.1` | Runtime/media compatibility refresh. |
| `Microsoft.Web.WebView2` | `1.0.3179.45` | `1.0.3912.50` | Current WebView2 SDK refresh for Lore/document rendering support. |
| `NAudio` | `2.2.1` | `2.3.0` | Runtime/audio compatibility refresh. |
| `VideoLAN.LibVLC.Windows` | `3.0.21` | `3.0.23.1` | Native LibVLC Windows runtime refresh for video playback. |

Deferred at the time of this report:

| Package | Current | Latest | Reason deferred |
| --- | ---: | ---: | --- |
| `Microsoft.WindowsAppSDK` | `1.8.251106002` | `2.0.1` | Major platform migration; should be planned separately with publish, launch, media, and installer checks. |

Follow-up: `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md` records the subsequent Windows App SDK `2.0.1` migration and its source/publish-smoke validation.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors after restore. | Confirms the upgraded runtime/media packages compile in the WinUI app. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | 23/23 AppCore tests passed. | Confirms core behavior remains green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 31/31 active UiTests passed. | Confirms active WinUI/static/runtime test coverage remains green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests"` | PASS | 1/1 explicit native Media interaction smoke passed. | Confirms real WinUI audio/video UI automation still works after NAudio/LibVLC/WebView2 refresh. |
| `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --outdated` | PASS/WARN | Only `Microsoft.WindowsAppSDK` remains outdated, with latest `2.0.1`. | Confirms the non-major updates were applied and the remaining update is a major platform migration. |
| `py -3 tools\generate_winui_third_party_notices.py` | PASS | Regenerated `THIRD_PARTY_NOTICES.winui-draft.md` with 73 packages. | Updates notice draft package versions after dependency refresh. |
| `npm run test:winui-notices` | PASS | Third-party notices check passed for 73 packages. | Confirms the notice draft is current after dependency refresh. |

## What Is Proven

- Non-major WinUI runtime/media packages restore, build, and pass current AppCore/WinUI automation gates.
- Native Media interaction still works after the NAudio/LibVLC package refresh.
- Third-party notice draft versions are updated and checked.
- At the time of this report, Windows App SDK 2.x was the only remaining direct outdated WinUI package reported by NuGet. The follow-up migration report records its later validation.

## What Is Not Proven

- Signed installer/MSIX/ZIP packaging after the dependency refresh.
- Store submission readiness.
- Legal approval for binary redistribution.
- Public redistribution approval for any private game-origin assets.

## Current Decision

Keep the non-major dependency refresh. Windows App SDK 2.x was correctly treated as a separate migration slice and is now recorded in `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md`.
