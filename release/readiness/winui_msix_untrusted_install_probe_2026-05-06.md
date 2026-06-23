# WinUI MSIX Untrusted Install Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `e7d377ca`
Evidence-report commit: `09879fb4`

## Purpose

This pass tested the next installer boundary without mutating Windows certificate trust stores.

The probe rebuilt a signed disposable WinUI MSIX candidate under ignored `subagents/`, attempted `Add-AppxPackage`, expected Windows to reject the generated self-signed certificate, then verified no local probe package and no WinUI process remained.

## Command

```powershell
npm run test:winui-msix-install-probe
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

## What This Proves

- The signed local MSIX candidate reaches Windows package deployment.
- Windows blocks installation until the generated signing certificate is trusted.
- The current probe does not silently install an untrusted package.
- No local probe package remains installed after the blocked attempt.
- No WinUI process remains running after the blocked attempt.

## What This Does Not Prove

- Trusting a signing certificate.
- Successful package installation.
- Launch from installed package identity.
- Successful uninstall after a successful install.
- SmartScreen, store, or distribution posture.
- Legal/compliance approval for public binary redistribution.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include private absolute paths, generated PFX contents, generated package binaries, raw screenshots, private game paths, raw media, saves, frame captures, or package output.

The generated signed package, PFX, package roots, and PowerShell deployment outputs remain ignored local artifacts under `subagents/`.

## Recommended Next Step

The next installer proof should be explicitly permissioned because it requires certificate trust-store work:

1. Choose the real release signing identity or a temporary test certificate trust strategy.
2. If using a test certificate, add it to a user-scoped trusted store only with an explicit reversible cleanup plan.
3. Install the signed package.
4. Launch and smoke the installed app.
5. Uninstall the package.
6. Remove any temporary trusted certificate.
7. Verify no package, certificate, or WinUI process remains.
8. Record only public-safe evidence.
