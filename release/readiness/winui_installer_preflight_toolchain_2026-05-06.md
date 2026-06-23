# WinUI Installer Preflight Toolchain Check - 2026-05-06

Status: PASS / guarded-not-ready
Branch: `wip/sandbox`
Source commit before this evidence: `695fd1ed`

## Purpose

Record a small release-preflight improvement: the WinUI installer/signing preflight now checks whether the local Windows SDK packaging/signing tools are available.

This does not create, sign, install, or prove an MSIX/installer candidate. It only improves the blocker report so the next packaging slice can distinguish missing tooling from missing package identity/signing/install evidence.

## What Changed

- Updated `tools/winui_installer_preflight.py`.
- The preflight now reports:
  - `makeappx_tool`
  - `signtool_tool`
- Tool lookup checks `PATH` first and then the standard Windows Kits 10 x64 tool path.
- Missing tools are reported as `WARN`, not as a repo regression, because the current accepted posture is still guarded-not-ready rather than installer-ready.

## Command

```powershell
npm run test:winui-installer-preflight
```

Result: PASS / guarded-not-ready.

Important output:

```text
Status: guarded-not-ready
Release claim: Disposable unpackaged publish is proven; signed installer/MSIX release is not proven.
- PASS: makeappx_tool: makeappx.exe is available from the Windows SDK toolchain.
- PASS: signtool_tool: signtool.exe is available from the Windows SDK toolchain.
```

## What This Proves

- The local workstation has the Windows SDK packaging/signing toolchain needed for a future MSIX/signing experiment.
- The repo preflight now records that toolchain fact instead of leaving it implicit.
- Signed/MSIX installer readiness is still explicitly blocked on package identity, manifest/project setup, signing identity, install/launch/uninstall smoke, and release approval.

## What This Does Not Prove

- MSIX package creation.
- Package signing.
- Install/uninstall behavior.
- Trust/SmartScreen posture.
- Public binary release readiness.

## Privacy And Release Safety

- No private game assets, saves, executable copies, screenshots, raw proof JSON, data URLs, or base64 payloads are included.
