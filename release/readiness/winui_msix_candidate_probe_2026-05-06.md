# WinUI MSIX Candidate Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `a845fd60`
Evidence-report commit: `13b982f6`

## Purpose

This pass tested whether the current WinUI publish output can be assembled into a disposable unsigned MSIX package with the local Windows SDK `makeappx.exe` toolchain.

The probe did not change WinUI source packaging properties, did not add a source `Package.appxmanifest`, did not sign the package, did not install it, and did not run the game. All generated package files stayed under ignored local `subagents/` output.

## Toolchain Decision

WinUI 3 / Windows App SDK remains the primary Windows desktop app lane. The release path now has three distinct layers:

1. Disposable unpackaged publish output: proven by `npm run test:winui-publish-smoke`.
2. Disposable unsigned MSIX assembly: proven by this probe.
3. Signed installer-grade install/launch/uninstall release: still unproven.

This keeps the current product shell native while avoiding a premature claim that the app has a signed or installable release package.

## Command

```powershell
npm run test:winui-msix-candidate-probe
```

Working directory:

```text
repo root
```

Result: PASS.

Important output:

```text
WinUI MSIX candidate probe
Status: pass
Release claim: Unsigned disposable MSIX assembly is proven only if status is pass; signing/install/uninstall remain separate release gates.
Output root: subagents\winui-msix-candidate\current
Publish exit code: 0
MakeAppx exit code: 0
- PASS: OnslaughtCareerEditor.WinUI.exe: package copy exists and is non-empty.
- PASS: OnslaughtCareerEditor.WinUI.pri: package copy exists and is non-empty.
- PASS: THIRD_PARTY_NOTICES.md: package copy exists and is non-empty.
- PASS: AppxManifest.xml: scratch package manifest exists and is non-empty.
- PASS: msix_file: unsigned local probe package exists and is non-empty.
- PASS: contains_AppxManifest.xml: Package contains AppxManifest.xml.
- PASS: contains_OnslaughtCareerEditor.WinUI.exe: Package contains OnslaughtCareerEditor.WinUI.exe.
- PASS: contains_OnslaughtCareerEditor.WinUI.pri: Package contains OnslaughtCareerEditor.WinUI.pri.
- PASS: contains_THIRD_PARTY_NOTICES.md: Package contains THIRD_PARTY_NOTICES.md.
- PASS: unsigned_posture: Package is intentionally unsigned; install/signing proof remains a separate gate.
- PASS: makeappx_tool: Using makeappx.exe from Windows SDK.
```

## What The Helper Does

- Publishes the current WinUI project as a self-contained `win-x64` output into ignored local `subagents/` output.
- Stages a disposable package root from that publish output.
- Writes a scratch package manifest and placeholder logo assets into the ignored package root.
- Runs Windows SDK `makeappx.exe pack`.
- Opens the produced package as a ZIP container and verifies it contains:
  - `AppxManifest.xml`
  - `OnslaughtCareerEditor.WinUI.exe`
  - `OnslaughtCareerEditor.WinUI.pri`
  - `THIRD_PARTY_NOTICES.md`
- Verifies the package remains intentionally unsigned by checking that `AppxSignature.p7x` is absent.

## What This Proves

- The local Windows SDK package toolchain can assemble a disposable unsigned MSIX candidate from the current WinUI publish output.
- The package contains the WinUI executable, PRI resources, and current third-party notices.
- The release blocker has moved past "no package artifact can be assembled" to the remaining signing, trust, install, launch, uninstall, and distribution checks.

## What This Does Not Prove

- Package signing.
- Certificate trust posture.
- Installation through Windows package deployment.
- Launch from installed package identity.
- Uninstall behavior.
- SmartScreen or store/distribution posture.
- Legal/compliance approval for public binary redistribution.
- Runtime workflows against an installed package.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include private absolute paths, screenshots, raw generated package contents, private game paths, raw media, saves, frame captures, or package binaries.

The generated candidate package and package root remain local ignored artifacts under `subagents/`.

## Recommended Next Step

Choose and implement the signed-package proof slice deliberately:

1. Decide whether the release shape should be MSIX, another installer, or ZIP plus launcher.
2. If MSIX remains the path, add a real source package identity/manifest or packaging project instead of relying on a scratch probe manifest.
3. Produce a signed candidate with an intentional certificate strategy.
4. Install, launch, smoke, uninstall, and verify no stale WinUI process remains.
5. Record only public-safe evidence.
