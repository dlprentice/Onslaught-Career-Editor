# WinUI MSIX Signing Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `39dedaee`
Evidence-report commit: `d41edafc`

## Purpose

This pass tested whether the current disposable WinUI MSIX candidate can be signed locally without mutating Windows certificate trust stores.

The probe generated a throwaway PFX file under ignored local `subagents/` output with .NET certificate APIs, signed a copied local MSIX with Windows SDK `signtool.exe`, and inspected the signed package for `AppxSignature.p7x`.

The probe did not install the certificate, trust the certificate, install the package, uninstall the package, launch the app from an installed package identity, run the game, or commit generated package/certificate artifacts.

## Command

```powershell
npm run test:winui-msix-signing-probe
```

Working directory:

```text
repo root
```

Result: PASS.

Important output:

```text
WinUI MSIX signing probe
Status: pass
Release claim: Disposable local MSIX signing is proven only if status is pass; trust/install/uninstall remain separate release gates.
Output root: subagents\winui-msix-signing-probe\current
PFX exit code: 0
SignTool exit code: 0
- PASS: candidate_publish: dotnet publish exit code 0.
- PASS: makeappx_pack: makeappx.exe exit code 0.
- PASS: local_pfx: Local PFX file exists under ignored output.
- PASS: signtool_tool: signtool.exe is available from the Windows SDK.
- PASS: signtool_sign: signtool sign exit code 0.
- PASS: signed_msix_file: signed local probe package exists and is non-empty.
- PASS: appx_signature: Signed package contains AppxSignature.p7x.
```

## What The Helper Does

- Rebuilds the disposable local MSIX candidate from the current WinUI publish output.
- Generates a throwaway PFX certificate file under ignored `subagents/` output using .NET `CertificateRequest`.
- Copies the unsigned MSIX candidate to a signed candidate path.
- Runs Windows SDK `signtool.exe sign` with the generated PFX.
- Opens the signed MSIX as a ZIP container and verifies `AppxSignature.p7x` exists.

## What This Proves

- The local Windows SDK signing toolchain can sign the current disposable WinUI MSIX candidate.
- The signing probe does not require OpenSSL or external package-signing tooling.
- The signed package contains an AppX signature payload.
- The release blocker has moved past "can the local package be signed at all" to certificate trust, install, launch, uninstall, and distribution posture.

## What This Does Not Prove

- Certificate trust posture.
- Install through Windows package deployment.
- Launch from installed package identity.
- Uninstall behavior.
- SmartScreen, store, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- Runtime workflows against an installed package.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include private absolute paths, generated PFX contents, generated package binaries, raw screenshots, private game paths, raw media, saves, frame captures, or package output.

The generated PFX, unsigned package, signed package, package root, and scratch certificate generator remain local ignored artifacts under `subagents/`.

## Recommended Next Step

The next release-facing proof should be an explicit trust/install/uninstall slice:

1. Choose the real release signing identity and certificate chain.
2. Decide whether test-certificate trust-store mutation is acceptable for a local install proof; if so, perform it as a separately documented reversible step.
3. Install the signed candidate.
4. Launch and smoke the installed package.
5. Uninstall the package and verify no stale WinUI process remains.
6. Record only public-safe evidence.
