# WinUI Installer/Signing Preflight

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `841e46873a9db00135d58745e0009c41fc1a7737`

## Purpose

This pass makes the WinUI installer/signing posture machine-checkable without claiming a signed installer is ready. The current release lane has proven disposable unpackaged WinUI publish output, launch smoke, visual smoke, Media interaction smoke, Windows App SDK 2.x compatibility, and published notice inclusion. It has not proven a signed installer, MSIX package, install/uninstall flow, trust chain, SmartScreen posture, or legal redistribution approval.

## Added Guard

`tools/winui_installer_preflight.py` now checks the current WinUI project and release evidence posture:

- `EnableMsixTooling=false`
- `AppxPackage=false`
- `WindowsPackageType=None`
- `WindowsAppSDKSelfContained=true`
- no package certificate properties are configured in the WinUI project
- no source `Package.appxmanifest` or Windows packaging project is present
- WinUI third-party notice draft exists
- unpackaged publish, Windows App SDK 2.x, published notice, dependency/license, and LGPL review evidence files exist
- release readiness docs still state signed installer/MSIX/install-uninstall proof remains unproven

The root npm wrapper is:

```powershell
npm run test:winui-installer-preflight
```

## Command Result

Command:

```powershell
npm run test:winui-installer-preflight
```

Result: PASS

Important output:

```text
WinUI installer/signing preflight
Status: guarded-not-ready
Release claim: Disposable unpackaged publish is proven; signed installer/MSIX release is not proven.
PASS: EnableMsixTooling is false.
PASS: AppxPackage is false.
PASS: WindowsPackageType is None.
PASS: WindowsAppSDKSelfContained is true.
PASS: No package certificate properties are configured in the WinUI project.
PASS: No source Package.appxmanifest is present; current WinUI project is not configured as an MSIX package.
PASS: No Windows packaging project is present at the repo root.
PASS: WinUI third-party notice draft exists.
PASS: required public-safe release evidence files exist.
PASS: Release checklist clearly marks signed installer/MSIX/install-uninstall proof as unproven.
```

## What This Proves

- The repo has a repeatable local check for the current WinUI packaging truth.
- The active WinUI project is still configured for disposable unpackaged publish, not MSIX/signing.
- Release docs and evidence are internally consistent with that posture.
- Future signed/MSIX work should require a new proof pass instead of silently inheriting unpackaged-publish claims.

## What This Does Not Prove

- A signed installer exists.
- An MSIX package installs and launches.
- Install/uninstall behavior is correct.
- The app has a trusted certificate chain.
- SmartScreen posture is acceptable.
- LGPL redistribution has legal approval.
- A final public binary contains every required license/notice file.

## Validation

The implementation and release accounting were validated with:

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-installer-preflight
npm run test:winui-notices
py -3 tools\release_profile_snapshot.py
py -3 tools\release_curated_manifest.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
py -3 tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
node -e "<parse developer_agent_state.json, documentation_agent_state.json, curated_release_manifest.json>"
git diff --check
```

Result: PASS after regenerating release profile and curated allowlist artifacts for the new public-safe tool/evidence.

## Required Before Installer Release

1. Choose the installer shape: MSIX, installer, or ZIP plus launcher.
2. Create a disposable candidate from a clean checkout.
3. Apply or document the signing identity and certificate chain.
4. Install, launch, smoke, uninstall, and verify no stale app process remains.
5. Verify `THIRD_PARTY_NOTICES.md` and required package license files are present in the final output.
6. Complete LGPL redistribution review for LibVLC-related runtime components.
7. Keep private game assets, generated exports, screenshots, and local proof artifacts out of public output.
