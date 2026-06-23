# WinUI MSIX Trusted Install Guarded Blocker - 2026-05-22

Status: public-safe installer blocker evidence
Date: 2026-05-22
Branch: `wip/sandbox`
Source head before pass: `966d0f10`

## Purpose

Refresh the trusted-install boundary for the current WinUI release posture without claiming installer readiness.

The probe creates a disposable MSIX candidate under ignored `subagents/`, signs it with a generated local PFX, exports the generated public certificate, temporarily adds that certificate to CurrentUser `TrustedPeople`, attempts package deployment, then removes any package/certificate/process residue.

## Commands

Red guard before implementation:

```powershell
dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.WinUiInstallerSigning_PreflightTracksPackageProofLayers"
```

Expected red result:

```text
Expected: String containing "winui_msix_trusted_install_guarded_blocker_2026-05-22.md"
```

Trusted-install probe:

```powershell
npm run test:winui-msix-trusted-install-probe
```

Result: PASS as `guarded-blocked`.

Important output summary:

```text
Status: guarded-blocked
- PASS: candidate_publish
- PASS: makeappx_pack
- PASS: signtool_sign
- PASS: appx_signature
- PASS: public_cert_export
- PASS: current_user_cert_trust
- FAIL: install_package: Add-AppxPackage failed with exit code 1.
- PASS: stop_process
- PASS: remove_package
- PASS: remove_certificate
- PASS: package_after
- PASS: certificate_after
- PASS: process_after
```

Observed deployment blocker:

```text
Deployment failed with HRESULT: 0x800B0109
The root certificate of the signature in the app package or bundle must be trusted.
```

## What Changed

- `tools\winui_msix_signing_probe.py` now emits a companion public `.cer` beside the generated PFX.
- `tools\winui_msix_trusted_install_probe.py` uses that public `.cer` for CurrentUser trust instead of reopening the generated PFX through Windows PowerShell.
- `tools\winui_msix_trusted_install_probe.py` uses .NET `X509Store` APIs for CurrentUser certificate add/find/remove so unattended runs do not depend on the `Cert:` provider.
- `tools\winui_installer_preflight.py` now requires this trusted-install guarded-blocker evidence file.
- `OnslaughtCareerEditor.UiTests\WinUiProductLaneTests.cs` now guards the preflight link to this evidence.

## What This Proves

- The current disposable WinUI MSIX candidate can be built, packaged, signed, and inspected.
- The generated public certificate can be temporarily trusted in CurrentUser `TrustedPeople`.
- TrustedPeople-only trust is still insufficient for Windows package deployment on this workstation.
- The probe removes the generated certificate after the blocked install attempt.
- No disposable local probe package remains installed after the attempt.
- No WinUI process remains running after cleanup.
- The installer preflight now tracks this trusted-install blocker layer explicitly.

## What This Does Not Prove

- Successful package installation.
- Launch from installed package identity.
- Successful uninstall after a successful install.
- A real public signing identity or certificate chain.
- SmartScreen, Store, reputation, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- End-user installer UX.
- Packaged BEA runtime launch or Game Harness proof.

## Privacy / Release Safety

This note is public-safe. It does not include generated PFX contents, generated package binaries, raw private paths, screenshots, game assets, save files, copied executables, certificate material, or raw deployment logs.

Generated package, certificate, package-root, and deployment artifacts remain ignored under `subagents/` and must not be committed.
