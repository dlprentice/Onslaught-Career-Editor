# WinUI Published Representative Media Smoke - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `9ff1a1efc1b5`

Evidence-report commit: `fc0e1e5f8ee2c29a31c9e76ef241339673e9907f`

Recorded at: 2026-05-06T13:42:30-04:00

## Scope

This smoke proves the same representative WinUI Media playback sample against a disposable published WinUI output folder, not only the debug build output.

This is still not installer-grade proof. The app was launched from a local publish folder under ignored evidence storage, not installed through MSIX/AppX/AppInstaller.

## Private Evidence Policy

Ignored local output remains under `subagents/`. This report does not include private absolute paths, media paths, screenshots, media cache paths, media payloads, or publish-folder file listings beyond public-safe names.

## Publish Output Shape

Disposable publish output checks:

| Check | Result |
| --- | --- |
| `OnslaughtCareerEditor.WinUI.exe` exists | PASS |
| `OnslaughtCareerEditor.WinUI.pri` exists | PASS |
| `THIRD_PARTY_NOTICES.md` exists | PASS |
| MSIX/AppX/AppInstaller package exists | NO |

## Commands Run

### Disposable Publish

Command:

```powershell
dotnet publish .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj -c Release -r win-x64 --self-contained true -o <ignored publish output> --nologo
```

Result: PASS

Important output:

- `OnslaughtCareerEditor.WinUI` published successfully to ignored local output.
- The output includes the WinUI executable, PRI resource file, and third-party notices.
- No MSIX/AppX/AppInstaller package was produced by this publish command.

What it proves:

- Current WinUI source can produce a disposable self-contained win-x64 publish folder.

### Representative Playback Against Published Output

Command:

```powershell
$env:ONSLAUGHT_WINUI_TEST_EXE_PATH = "<ignored publish output>\OnslaughtCareerEditor.WinUI.exe"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests.MediaPage_PlaysRepresentativeAudioAndVideoRowsThroughUi"
```

Result: PASS

Important output:

- 1/1 focused UI test passed.
- The native UI test launched the published WinUI executable.
- The representative playback sample selected and played:
  - a Music row
  - a Tutorial row
  - a Main Videos row
  - a Cutscenes row
- Each row was stopped after playback activation, and video rows advanced playback time.

What it proves:

- The disposable published WinUI app can run the representative Media playback flow from packaged/published app assets.

### Process Cleanup

Command:

```powershell
Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue
```

Result: PASS

Important output:

- No `OnslaughtCareerEditor.WinUI` process remained after the smoke.

## What Is Proven

- Disposable published WinUI output launches through UI Automation.
- Published-output Media playback works for representative Music, Tutorial, Main Videos, and Cutscenes rows.
- Third-party notices are present in the publish output.
- No WinUI process is left running.

## What Is Not Proven

- This is not trusted MSIX/AppX/AppInstaller install proof.
- This is not signed installer-grade release proof.
- This is not all-row media playback proof.
- This is not public redistribution approval for private media.
- This does not mutate the installed game, saves, profiles, or executables.

## Release Posture

GREEN for disposable published-output representative Media playback.

Remaining release gaps are trusted install/launch/uninstall, installer-grade signing/trust/SmartScreen posture, legal/compliance approval, and row-by-row broader media playback coverage.
