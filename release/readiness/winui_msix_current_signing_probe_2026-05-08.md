# WinUI Current MSIX Signing Probe - 2026-05-08

Status: public-safe local MSIX signing evidence
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

Refresh the local MSIX signing proof against the current WinUI branch head after the current unsigned-candidate proof.

This probe signs a disposable local package only. It does not install a certificate, add trust-store entries, install the app, launch under package identity, uninstall anything, or run the game.

## Command

```powershell
npm run test:winui-msix-signing-probe
```

Equivalent direct command:

```powershell
py -3 tools\winui_msix_signing_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
WinUI MSIX signing probe
Status: pass
Output root: subagents\winui-msix-signing-probe\current
PFX exit code: 0
SignTool exit code: 0
Unsigned candidate byte size: 240829879
Signed MSIX byte size: 240874912
Signed MSIX SHA-256: fc4203520149fbbbdf7ed948be5a918788a997789a9a5ab462a22343f1a9763f
```

The probe verified:

- WinUI publish succeeded.
- Scratch package root contains the WinUI executable, PRI file, third-party notices, and `AppxManifest.xml`.
- `makeappx.exe` assembled the unsigned candidate.
- A local PFX file was generated under ignored output.
- `signtool.exe` was available from the Windows SDK.
- `signtool sign` exited `0`.
- The signed local probe package exists and is non-empty.
- The signed package contains `AppxSignature.p7x`.

## What This Proves

- The current WinUI publish output can still be assembled into an unsigned local MSIX candidate and signed with a generated local PFX.
- The local Windows SDK `signtool` path remains usable for this repo.
- Signing is no longer the current blocker for a disposable local candidate.

## What This Does Not Prove

- Certificate trust.
- Installation through Windows package deployment.
- Launch from installed package identity.
- Uninstall behavior.
- SmartScreen/reputation/store posture.
- Legal/compliance approval for public binary redistribution.
- Packaged BEA runtime launch or Game Harness proof.

## Privacy / Release Safety

This note is public-safe. It does not include generated PFX contents, generated package contents, private absolute paths, screenshots, game assets, save files, copied executables, certificate material, or raw package binaries.

Generated package and certificate artifacts remain ignored under `subagents/` and must not be committed.
