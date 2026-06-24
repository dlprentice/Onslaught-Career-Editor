# WinUI Current MSIX Candidate Probe - 2026-05-08

Status: public-safe unsigned MSIX candidate evidence
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

Refresh the unsigned MSIX candidate proof against the current WinUI branch head after the WinUI product and RE campaign waves.

This probe assembles a disposable local package candidate only. It does not sign the package, install it, alter certificate stores, launch under package identity, uninstall anything, or run the game.

## Command

```powershell
npm run test:winui-msix-candidate-probe
```

Equivalent direct command:

```powershell
py -3 tools\winui_msix_candidate_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
WinUI MSIX candidate probe
Status: pass
Output root: subagents\winui-msix-candidate\current
Publish exit code: 0
MakeAppx exit code: 0
MSIX byte size: 240829825
MSIX SHA-256: 3ea8afdc96a4740dbf299e608bd24b809c9bc827f932580934c36fcfce309e53
```

The probe verified:

- `OnslaughtCareerEditor.WinUI.exe` exists in the staged package root.
- `OnslaughtCareerEditor.WinUI.pri` exists in the staged package root.
- `THIRD_PARTY_NOTICES.md` exists in the staged package root.
- `AppxManifest.xml` exists in the staged package root.
- `OnslaughtCareerEditor.WinUI.LocalProbe.msix` exists and is non-empty.
- The package contains `AppxManifest.xml`, the WinUI executable, the PRI file, and third-party notices.
- The package is intentionally unsigned; `AppxSignature.p7x` is absent.
- `makeappx.exe` was resolved from the local Windows SDK toolchain.

## What This Proves

- The current WinUI publish output can still be assembled into a disposable unsigned MSIX package candidate.
- The package contains the key app executable/resources and notices.
- The local Windows SDK `makeappx` path remains usable for this repo.
- The release lane is past "cannot assemble an MSIX-like package artifact" for current head.

## What This Does Not Prove

- Package signing.
- Certificate trust.
- Installation through Windows package deployment.
- Launch from installed package identity.
- Uninstall behavior.
- SmartScreen/reputation/store posture.
- Legal/compliance approval for public binary redistribution.
- Packaged BEA runtime launch or Game Harness proof.

## Privacy / Release Safety

This note is public-safe. It does not include generated package contents, private absolute paths, screenshots, game assets, save files, copied executables, certificate material, or raw package binaries.

Generated package artifacts remain ignored under `subagents/` and must not be committed.
