# WinUI Publish Smoke Evidence - 2026-05-05

Status: public-safe release readiness evidence

## Scope

This note records a focused WinUI publish/signoff wave. It proves that the active WinUI 3 app can be published into a disposable unpackaged output folder and launched by the native desktop smoke tests. It does not claim signed installer, MSIX, install/uninstall, SmartScreen, or runtime game proof readiness.

Private generated output stayed under ignored `subagents/`. This report does not embed screenshots, local absolute paths, raw game paths, private media, copied executables, crash dumps, WER payloads, data URLs, or base64.

## What Changed

- Added a narrow WinUI project publish target that copies the app PRI resource file into the publish directory.
- Updated WinUI desktop smoke tests so maintainers can set `ONSLAUGHT_WINUI_TEST_EXE_PATH` and validate a published executable instead of only the debug build.
- Isolated launch-smoke app config under ignored `subagents/` so packaged/published smoke does not depend on the real user config.
- Updated Patch Bench default UI so the configured source executable is summarized as a folder/source label, with full paths collapsed under details.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet publish .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj -c Release -r win-x64 --self-contained true -o .\subagents\winui-publish-smoke\2026-05-05\publish --nologo` | PASS, then exposed blocker | Publish emitted files, but the initial disposable output omitted `OnslaughtCareerEditor.WinUI.pri`. | A naive publish path was not enough for a runnable unpackaged WinUI output. |
| Published launch smoke before the fix | WARN/BLOCKED | The published process exited before a main window appeared; local Application Error evidence showed `Microsoft.UI.Xaml.dll` crash code `0xc000027b`. | Confirmed the issue was a real published-output launch blocker, not a test-only assertion. |
| App PRI comparison | PASS | Release build output contained `OnslaughtCareerEditor.WinUI.pri`; disposable publish output did not. | Identified the concrete publish-output gap. |
| `dotnet publish .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj -c Release -r win-x64 --self-contained true -o .\subagents\winui-publish-smoke\2026-05-05\publish --nologo` after the project fix | PASS | Publish succeeded and the disposable output included `OnslaughtCareerEditor.WinUI.pri`. | Confirms the targeted publish fix populates the required WinUI resource file. |
| Published launch smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 `WinUiLaunchSmokeTests` passed against the disposable published executable. | Proves the published output launches and shows product chrome in an interactive Windows session. |
| Published visual smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 `WinUiVisualSmokeTests` passed and refreshed ignored screenshots for Home, Save Lab, Media audio, Media video, Lore, Patch Bench, Settings, and About. | Proves primary WinUI screens can be captured from the disposable published executable. |

## What Is Proven

- The WinUI project can produce a disposable unpackaged self-contained `win-x64` publish folder.
- The publish folder includes the required app PRI resource file.
- The published executable launches through automated native smoke.
- The published executable renders the primary product screens through automated native visual smoke.
- A later Windows App SDK 2.x pass records focused published-output Media interaction proof in `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md`.
- Patch Bench no longer exposes the configured retail executable's full path in the default source field.

## What Is Not Proven

- Signed installer-grade release readiness.
- MSIX packaging.
- Installer install/uninstall behavior.
- Windows trust, signing, or SmartScreen posture.
- Game runtime launch/capture/input proof from the WinUI app.
- Any mutation of the installed game or original `BEA.exe`.

## Privacy And Release Boundary

The disposable publish output and screenshots remain ignored local evidence under `subagents/`. Public release accounting should continue to exclude generated build output, private game/media/save content, screenshots, crash dumps, and runtime proof assets unless a later prompt explicitly sanitizes and reclassifies a narrow subset.
