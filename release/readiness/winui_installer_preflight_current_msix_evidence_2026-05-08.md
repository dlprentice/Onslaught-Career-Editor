# WinUI Installer Preflight Current MSIX Evidence - 2026-05-08

Status: public-safe installer preflight freshness evidence
Date: 2026-05-08
Branch: `wip/sandbox`
Source head before pass: `5a1058b3`

## Purpose

Refresh the WinUI installer/signing preflight guard so it requires the current 2026-05-08 MSIX evidence chain instead of only older 2026-05-06 reports.

This is a guardrail update. It does not install the package, trust a certificate, launch under package identity, uninstall anything, or run the game.

## TDD Guard

Red command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.WinUiInstallerSigning_PreflightTracksPackageProofLayers"
```

Expected red result:

```text
Failed WinUiInstallerSigning_PreflightTracksPackageProofLayers
Expected: String containing "winui_msix_current_candidate_probe_2026-05-08.md"
```

Green command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.WinUiInstallerSigning_PreflightTracksPackageProofLayers"
```

Green result:

```text
Passed: 1
Failed: 0
```

## Preflight Command

```powershell
npm run test:winui-installer-preflight
```

Result: PASS with guarded-not-ready status.

Important output summary:

```text
WinUI installer/signing preflight
Status: guarded-not-ready
Release claim: Disposable unpackaged publish, unsigned MSIX assembly, local signing, and untrusted install blocking are proven; install is blocked without certificate trust; trusted install/launch/uninstall remains unproven.
- PASS: unsigned_msix_candidate_probe: release\readiness\winui_msix_current_candidate_probe_2026-05-08.md exists.
- PASS: local_msix_signing_probe: release\readiness\winui_msix_current_signing_probe_2026-05-08.md exists.
- PASS: untrusted_install_probe: release\readiness\winui_msix_current_untrusted_install_probe_2026-05-08.md exists.
- PASS: release_checklist: Release checklist clearly marks installer/install-uninstall proof as unproven.
```

## What Changed

- `tools\winui_installer_preflight.py` now requires the current unsigned MSIX candidate proof.
- `tools\winui_installer_preflight.py` now requires the current local MSIX signing proof.
- `tools\winui_installer_preflight.py` now requires the current untrusted-install blocker proof.
- `OnslaughtCareerEditor.UiTests\WinUiProductLaneTests.cs` now guards those current evidence filenames.

## What This Proves

- The installer preflight tool is anchored to the latest public-safe MSIX evidence chain.
- The tool still reports `guarded-not-ready`, not installer-grade readiness.
- The release checklist still preserves successful install, launch, uninstall, and trust as unproven blockers.

## What This Does Not Prove

- Certificate trust.
- Successful package installation.
- Launch from installed package identity.
- Successful uninstall after a successful install.
- SmartScreen, Store, reputation, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- Packaged BEA runtime launch or Game Harness proof.

## Privacy / Release Safety

This note is public-safe. It does not include generated package binaries, generated certificate material, private absolute paths, screenshots, game assets, save files, copied executables, or raw deployment logs.
