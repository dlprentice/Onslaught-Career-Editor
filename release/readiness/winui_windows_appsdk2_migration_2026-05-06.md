# WinUI Windows App SDK 2.x Migration - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records the focused Windows App SDK 2.x migration for the WinUI-first product lane. It upgrades the primary WinUI app from Windows App SDK `1.8.251106002` to `2.0.1` and validates build, tests, desktop launch, primary-screen visual smoke, disposable publish output, and published-output Media interaction.

This report is public-safe. It does not include private game paths, screenshots, copied executables, extracted assets, runtime proof JSON, local NuGet cache paths, or generated publish output contents.

## Package Update

| Package | Previous | Current | Reason |
| --- | ---: | ---: | --- |
| `Microsoft.WindowsAppSDK` | `1.8.251106002` | `2.0.1` | Current WinUI platform/runtime migration. |

After this update, `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --outdated` reports no direct package updates from the configured NuGet sources.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. | Confirms the WinUI app compiles on Windows App SDK `2.0.1`. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | 23/23 AppCore tests passed. | Confirms shared core behavior remains green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 31/31 active UiTests passed. | Confirms active WinUI/static/runtime automation remains green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests"` | PASS | 1/1 native Media interaction smoke passed against the current build. | Confirms debug-build audio/video interaction still works after the platform migration. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiLaunchSmokeTests.MainWindow_LaunchesAndShowsWinUiProductChrome"` | PASS | 1/1 launch smoke passed. | Confirms desktop shell startup and product chrome still work. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 visual smoke passed. | Confirms primary WinUI screens still render under automation; screenshots stay ignored/private. |
| `dotnet publish .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj -c Release -r win-x64 --self-contained true -o .\subagents\winui-appsdk2-publish-smoke\2026-05-06\publish --nologo` | PASS | Publish completed and the output contains the app PRI resource. | Confirms a disposable unpackaged publish folder can be produced on Windows App SDK `2.0.1`. |
| Published launch smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 launch smoke passed against the disposable published executable. | Confirms the published output launches and shows product chrome. |
| Published visual smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 visual smoke passed against the disposable published executable. | Confirms primary screens render from the published output. |
| Published Media interaction smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 native Media interaction smoke passed against the disposable published executable. | Confirms published-output audio/video interaction works for the focused proof row. |
| `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --outdated` | PASS | NuGet reported no direct package updates from the configured sources. | Confirms direct WinUI dependencies are current for the configured package feeds. |
| `py -3 tools\generate_winui_third_party_notices.py` | PASS | Regenerated `THIRD_PARTY_NOTICES.winui-draft.md` with 74 packages. | Updates notices for Windows App SDK 2.x transitive package changes. |
| `npm run test:winui-notices` | PASS | Third-party notices check passed for 74 packages. | Confirms the source-controlled notice draft is current after the platform migration. |

## What Is Proven

- WinUI builds and active automation passes on Windows App SDK `2.0.1`.
- Desktop launch and primary-screen visual smoke pass.
- Disposable unpackaged publish output launches and renders primary screens.
- Focused Media audio/video interaction passes from both current build and published output.
- Direct WinUI packages are current against the configured NuGet sources.
- Notice draft output has been regenerated for the updated Windows App SDK dependency graph.

## What Is Not Proven

- Signed installer/MSIX install/uninstall flow.
- SmartScreen, trust, or store-submission posture.
- Full media catalog coverage beyond focused smoke rows.
- Legal/compliance approval for binary redistribution.
- Public redistribution approval for any private game-origin assets.

## Current Decision

Keep the Windows App SDK `2.0.1` migration. The previous Windows App SDK 2.x blocker is closed at source/publish-smoke level, while signed installer-grade release work remains a separate release lane.
