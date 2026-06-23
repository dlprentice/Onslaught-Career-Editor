# WinUI Packaging Test Guard

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `53d3c5fb`
Evidence-report commit: `8d587740`

## Purpose

This pass updated the active WinUI product-lane static guard so it matches the current package proof layers:

- disposable unpackaged publish
- disposable unsigned MSIX assembly
- disposable local MSIX signing
- blocked untrusted install proof
- still-unproven certificate trust, successful install, launch, and uninstall

The previous guard still expected the older broad phrase that signed/MSIX release was unproven. That was stale after the unsigned assembly and local signing probes were added.

## Changed Guard

`OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

- Renamed the installer/signing static guard to `WinUiInstallerSigning_PreflightTracksPackageProofLayers`.
- Added checks for:
  - `test:winui-msix-candidate-probe`
  - `test:winui-msix-signing-probe`
  - `test:winui-msix-install-probe`
  - `unsigned_msix_candidate_probe`
  - `local_msix_signing_probe`
  - `untrusted_install_probe`
  - `install is blocked without certificate trust`
- Added a regression check that the stale phrase `signed installer/MSIX release is not proven` does not return.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"
```

Result: PASS.

```text
Passed: 12, Failed: 0, Skipped: 0
```

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

Result: PASS.

```text
Passed: 39, Failed: 0, Skipped: 0
```

## What This Proves

- Active WinUI product-lane static tests now guard the current package proof posture.
- The active UI test suite passes after the package proof wording changes.

## What This Does Not Prove

- Successful trusted package install.
- Launch from installed package identity.
- Uninstall after a successful install.
- Public binary release readiness.
