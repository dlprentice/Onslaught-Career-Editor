# WinUI MSIX Trusted Install Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `093e6248`
Evidence-report commit: 18b2121909ed67b3c8fb58824654c16a5f47afeb

## Purpose

This pass added and exercised an explicit reversible trusted-install probe for the disposable WinUI MSIX candidate.

The probe creates a signed local MSIX candidate under ignored `subagents/`, exports the generated public certificate, temporarily imports that certificate into CurrentUser trust, attempts package install, stops any launched app process, removes the package if present, removes the generated certificate, and verifies no package, certificate, or WinUI process remains.

This is intentionally not a normal green release gate yet. It is a guarded probe for the final installer boundary.

## Commands

### Safe Root-Trust Refusal

```powershell
py -3 tools\winui_msix_trusted_install_probe.py --check --allow-current-user-cert-trust --trust-root-too
```

Working directory:

```text
repo root
```

Result: PASS as safe refusal.

Important output summary:

```text
Refusing CurrentUser Root trust probe without --allow-interactive-root-cert-prompt.
TrustedPeople-only probing is non-interactive; Root trust may prompt and is not safe for unattended runs.
```

### Non-Interactive TrustedPeople Probe

```powershell
py -3 tools\winui_msix_trusted_install_probe.py --check --allow-current-user-cert-trust
```

Working directory:

```text
repo root
```

Result: GUARDED-BLOCKED, with cleanup PASS.

Important output summary:

```text
WinUI MSIX trusted install probe
Status: guarded-blocked
Release claim: Disposable current-user trusted MSIX install, package launch, app stop, uninstall, and certificate cleanup are proven only if status is pass; real signing, SmartScreen/store/distribution posture, and legal approval remain separate gates.
- PASS: candidate_publish
- PASS: makeappx_pack
- PASS: signtool_sign
- PASS: appx_signature
- PASS: signed_package
- PASS: public_cert_export
- PASS: current_user_cert_trust
- FAIL: install_package
- PASS: stop_process
- PASS: remove_package
- PASS: remove_certificate
- PASS: package_after
- PASS: certificate_after
- PASS: process_after
```

Observed install blocker:

```text
HRESULT 0x800B0109: the package signature chain terminates in a root certificate that is not trusted.
```

### Cleanup Audit

```powershell
Get-AppxPackage -Name 'OnslaughtCareerEditor.WinUI.LocalProbe'
Get-ChildItem Cert:\CurrentUser\TrustedPeople
Get-ChildItem Cert:\CurrentUser\Root
Get-Process -Name OnslaughtCareerEditor.WinUI,MSBuild,vstest.console,testhost,certutil -ErrorAction SilentlyContinue
```

Result: PASS.

Important output summary:

```text
No disposable local probe package remained installed.
No generated local-probe certificate remained in CurrentUser TrustedPeople or Root.
No WinUI, MSBuild, vstest, testhost, or certutil process remained.
```

## What This Proves

- The trusted-install probe refuses unattended Root-store mutation unless explicitly allowed.
- The probe can build, package, sign, and inspect the disposable WinUI MSIX candidate.
- The probe can export the generated public certificate before attempting trust-store mutation.
- TrustedPeople-only current-user trust is insufficient for Windows package deployment on this machine.
- The npm diagnostic exits successfully for the expected guarded blocker only when cleanup is also proven.
- The probe leaves no disposable package installed after the blocked attempt.
- The probe leaves no generated local-probe certificate in CurrentUser trust stores after cleanup.
- The probe leaves no WinUI package process behind after cleanup.

## What This Does Not Prove

- Successful trusted package installation.
- Launch from installed package identity.
- Successful uninstall after a successful install.
- A real public signing identity or certificate chain.
- SmartScreen, Store, reputation, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- End-user installer UX.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include private absolute paths, generated PFX contents, generated package binaries, raw screenshots, private game paths, raw media, saves, frame captures, or package output.

The generated signed package, PFX, exported certificate, package roots, and raw deployment report remain ignored local artifacts under `subagents/`.

## Recommended Next Step

The next installer proof requires one of these decisions:

1. Use a real release signing certificate and verify the package installs without local test-root trust prompts.
2. Run an explicitly interactive CurrentUser Root trust proof and record the prompt/manual approval plus cleanup.
3. Choose a different distribution shape, such as a ZIP plus launcher, and create a separate install/launch/uninstall smoke for that shape.

Do not claim installer-grade release readiness until successful install, launch, uninstall, certificate/trust cleanup, process cleanup, legal review, and public-safe evidence are all complete.
