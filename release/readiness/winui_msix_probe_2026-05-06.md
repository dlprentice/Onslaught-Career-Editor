# WinUI MSIX Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `2d3738a3785bd42b691dad386a57eebf89e9d5cd`

## Purpose

This pass tested whether the current WinUI project can produce an MSIX/AppX/AppInstaller package by command-line property override alone. It was a disposable local probe under `subagents/`; no install, signing, game launch, private asset copy, or runtime proof was performed.

## Project Inputs

- `OnslaughtCareerEditor.WinUI.csproj` is still configured with `WindowsPackageType=None`.
- The source tree does not contain a source `Package.appxmanifest`.
- The source tree does not contain a Windows packaging project (`.wapproj`).
- The WinUI project has no package certificate properties.

## Commands

```powershell
dotnet publish ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" -c Release -r win-x64 --self-contained true -p:WindowsPackageType=MSIX -p:AppxPackageSigningEnabled=false -o ".\subagents\winui-msix-probe\2026-05-06\publish" --nologo
```

Result: PASS as a publish command.

Important output:

```text
OnslaughtCareerEditor.WinUI -> subagents\winui-msix-probe\2026-05-06\publish\
```

Output inspection:

```powershell
Get-ChildItem ".\subagents\winui-msix-probe\2026-05-06\publish" -Recurse -File -Include *.msix,*.appx,*.appinstaller,*.msixbundle,*.appxbundle
```

Result:

```text
No MSIX/AppX/AppInstaller package files produced.
```

Positive output checks:

```text
OnslaughtCareerEditor.WinUI.exe: present
OnslaughtCareerEditor.WinUI.pri: present
THIRD_PARTY_NOTICES.md: present
```

## Conclusion

The property override generated another unpackaged publish folder, not an MSIX/AppX/AppInstaller package. Current signed/MSIX release readiness is blocked on deliberate package identity and packaging setup, not just another `dotnet publish` invocation.

## What This Proves

- The current WinUI project can still publish to a disposable unpackaged folder after the preflight changes.
- The current project does not produce an MSIX package from `WindowsPackageType=MSIX` override alone.
- Signed/MSIX proof should require a real package manifest/project/signing pass, followed by install/launch/uninstall smoke.

## What This Does Not Prove

- MSIX packaging works.
- Installer-grade release works.
- Signing works.
- Install/uninstall behavior works.
- Trust/SmartScreen posture is acceptable.
- Final public binary notices and LGPL redistribution are legally approved.

## Required Follow-Up

1. Choose the package shape deliberately.
2. Add or generate the package identity inputs needed for that shape.
3. Produce a candidate package under ignored local output.
4. Sign or document signing preconditions.
5. Install, launch, smoke, uninstall, and verify no stale process remains.
6. Record only public-safe evidence; keep raw artifacts and local paths private.
