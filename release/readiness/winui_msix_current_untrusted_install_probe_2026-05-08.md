# WinUI Current MSIX Untrusted Install Probe - 2026-05-08

Status: public-safe installer blocker evidence
Date: 2026-05-08
Branch: `wip/sandbox`
Source head before pass: `2480d6e8`

## Purpose

Refresh the untrusted-install blocker proof against the current WinUI branch head after the current unsigned-candidate and local-signing proofs.

This probe does not trust the generated certificate. It builds and signs a disposable local MSIX candidate under ignored output, attempts Windows package deployment, expects Windows to reject the untrusted generated certificate, then verifies no local probe package and no WinUI process remain.

## Command

```powershell
npm run test:winui-msix-install-probe
```

Equivalent direct command:

```powershell
py -3 tools\winui_msix_install_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS as a safe blocked install probe.

Important output summary:

```text
WinUI MSIX install probe
Status: pass
Release claim: Install is safely blocked without certificate trust; installer-grade trust/install-uninstall remains unproven.
Output root: subagents\winui-msix-install-probe\current
Install exit code: 1
- PASS: signing_probe: Signing probe exit code 0.
- PASS: signed_package: signed local probe package exists and is non-empty.
- PASS: install_attempt: Add-AppxPackage was blocked by untrusted generated certificate as expected.
- PASS: cleanup: No installed local probe package remained after cleanup.
- PASS: package_after: No local probe package is installed.
- PASS: process_after: No WinUI process remains running after install probe.
```

Observed deployment blocker:

```text
HRESULT 0x800B0109: the package signature chain terminates in a root certificate that is not trusted.
```

Signed local probe MSIX SHA-256:

```text
6c915d9b570607214d9465c5f033ce2e538086105eb05156cee6b710ea62c8e6
```

## What This Proves

- The current signed local MSIX candidate reaches Windows package deployment.
- Windows blocks installation until the generated signing certificate is trusted.
- The probe does not silently install an untrusted package.
- No local probe package remains installed after the blocked attempt.
- No WinUI process remains running after the blocked attempt.

## What This Does Not Prove

- Trusting a signing certificate.
- Successful package installation.
- Launch from installed package identity.
- Successful uninstall after a successful install.
- SmartScreen, store, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- Packaged BEA runtime launch or Game Harness proof.

## Privacy / Release Safety

This note is public-safe. It does not include generated PFX contents, generated package binaries, private absolute paths, screenshots, game assets, save files, copied executables, certificate material, or raw deployment logs.

Generated package, certificate, package-root, and deployment artifacts remain ignored under `subagents/` and must not be committed.

## Recommended Next Step

The next installer proof requires an explicit certificate trust strategy:

1. Choose a real release signing identity or a temporary test-certificate trust strategy.
2. If using a test certificate, trust it only through a reversible user-scoped cleanup plan.
3. Install the signed package.
4. Launch and smoke the installed package identity.
5. Uninstall the package.
6. Remove any temporary trusted certificate.
7. Verify no package, certificate, or WinUI process remains.
8. Record only public-safe evidence.
