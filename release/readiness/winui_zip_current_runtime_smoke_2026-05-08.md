# WinUI Current ZIP Runtime Smoke - 2026-05-08

Status: public-safe ZIP package runtime evidence
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

Refresh the WinUI ZIP package proof against the current branch head after the WinUI product and RE campaign waves. This verifies the primary WinUI lane as a disposable ZIP-deliverable app, not only as a dev build.

This does not create, sign, install, or uninstall an MSIX/AppInstaller package.

## Command

```powershell
py -3 tools\winui_zip_package_probe.py --check --include-media-smoke --out-root subagents\winui-zip-current-proof\2026-05-08 --package-name OnslaughtCareerEditor.WinUI-2026-05-08-current-win-x64.zip
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
WinUI ZIP package probe
Status: pass
ZIP package: subagents\winui-zip-current-proof\2026-05-08\OnslaughtCareerEditor.WinUI-2026-05-08-current-win-x64.zip
ZIP byte size: 242396510
ZIP SHA-256: a04c283e519d0107926f98a8b51bf1096bd4d4f4fbb584a757822c71f32f1216
extracted_launch_smoke: PASS
extracted_media_smoke: PASS
process_after: PASS
```

The raw generated ZIP package, checksum sidecar, publish folder, extracted folder, UI Automation logs, and JSON report remain ignored under `subagents/`.

## What This Proves

- The current WinUI app can publish as a self-contained `win-x64` output.
- The publish output includes `OnslaughtCareerEditor.WinUI.exe`, `OnslaughtCareerEditor.WinUI.pri`, `THIRD_PARTY_NOTICES.md`, and the public-safe ZIP `README.txt`.
- The publish output and ZIP contain no MSIX/AppX/AppInstaller artifacts.
- The ZIP can be extracted to a clean ignored folder.
- The extracted executable launches and passes the native WinUI launch smoke.
- The extracted executable passes the representative Media interaction smoke.
- No WinUI process remains after the probe.

## What This Does Not Prove

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Installer install/uninstall behavior.
- Start menu shortcuts, uninstall entries, SmartScreen reputation, or Store posture.
- Packaged Game Harness/runtime BEA launch proof.
- Legal/compliance approval for public binary redistribution.
- Exhaustive media row coverage beyond the representative sample.

## Privacy / Release Safety

This note is public-safe. It does not include generated package contents, raw UI Automation logs, screenshots, private absolute paths, game assets, save files, copied executables, or raw proof JSON.

Generated package artifacts remain ignored and must not be committed.
