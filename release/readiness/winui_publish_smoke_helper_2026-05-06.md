# WinUI Publish Smoke Helper - 2026-05-06

Status: PASS
Branch: `wip/sandbox`
Source commit before this evidence: `17ab0391`

## Purpose

Record the release-system improvement that turns the current disposable unpackaged WinUI publish smoke into a repeatable `npm` gate.

This does not create an installer, sign a package, install the app, or prove MSIX readiness. It strengthens the current release lane by making the known-good unpackaged publish smoke easier to rerun and harder to misdescribe.

## What Changed

- Added `tools/winui_publish_smoke.py`.
- Added `npm run test:winui-publish-smoke`.
- Updated release docs to use the repeatable smoke command instead of an inline one-off `dotnet publish` command.
- The helper writes only under ignored `subagents/winui-publish-smoke/current/`.
- The helper refuses output roots outside `subagents/`.
- The helper checks for:
  - `OnslaughtCareerEditor.WinUI.exe`
  - `OnslaughtCareerEditor.WinUI.pri`
  - `THIRD_PARTY_NOTICES.md`
  - absence of MSIX/AppX/AppInstaller package artifacts, because this smoke is intentionally unpackaged

## Command

```powershell
npm run test:winui-publish-smoke
```

Result: PASS.

Important output:

```text
WinUI publish smoke
Status: pass
Release claim: Disposable unpackaged WinUI publish output is buildable and inspectable; signed/MSIX installer release remains unproven.
Publish directory: subagents\winui-publish-smoke\current\publish
Publish exit code: 0
- PASS: exe: subagents\winui-publish-smoke\current\publish\OnslaughtCareerEditor.WinUI.exe exists and is non-empty.
- PASS: pri: subagents\winui-publish-smoke\current\publish\OnslaughtCareerEditor.WinUI.pri exists and is non-empty.
- PASS: notices: subagents\winui-publish-smoke\current\publish\THIRD_PARTY_NOTICES.md exists and is non-empty.
- PASS: package_files: No MSIX/AppX/AppInstaller artifacts were produced; this remains an unpackaged publish smoke.
```

## What This Proves

- The current WinUI project can produce disposable unpackaged publish output through a repeatable repo command.
- The output includes the executable, WinUI PRI resource, and third-party notices.
- The smoke command preserves the current truth that signed/MSIX installer readiness is still unproven.

## What This Does Not Prove

- MSIX packaging.
- Installer-grade release.
- Code signing.
- Install/uninstall behavior.
- Trust or SmartScreen posture.
- Legal/compliance approval for binary redistribution.

## Privacy And Release Safety

- Generated publish output remains under ignored `subagents/`.
- This report does not include private game assets, private install paths, save files, raw proof JSON, screenshots, data URLs, base64 payloads, or local binary artifacts.
