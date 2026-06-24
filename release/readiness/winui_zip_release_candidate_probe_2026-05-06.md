# WinUI ZIP Release-Candidate Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `02882405`
Evidence-report commit: de45b5ed62bf4aa16a4f086a3a7f3b40573ca0d6

## Purpose

This pass tested the non-cert ZIP distribution lane with an explicit dated release-candidate package name. It does not create, sign, install, or uninstall an MSIX/AppInstaller package.

The probe uses the same public-safe ZIP packaging path as the local-probe ZIP proof, but writes to a separate ignored output root and uses the package name `OnslaughtCareerEditor.WinUI-2026-05-06-rc1-win-x64.zip`.

## Command

```powershell
npm run test:winui-zip-release-candidate-probe
```

Equivalent direct command:

```powershell
py -3 tools\winui_zip_package_probe.py --check --include-media-smoke --out-root subagents\winui-zip-release-candidate-probe\current --package-name OnslaughtCareerEditor.WinUI-2026-05-06-rc1-win-x64.zip
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
WinUI ZIP package probe
Status: pass
ZIP package: OnslaughtCareerEditor.WinUI-2026-05-06-rc1-win-x64.zip
ZIP byte size: 242329095
ZIP SHA-256: 1ae3be7fe270be2f16f2bb0ef55ae7784ab97d3fb1319e945f3ce8117d0e0fad
- PASS: public-safe ZIP README copied into publish root
- PASS: publish executable, PRI, THIRD_PARTY_NOTICES.md, and README.txt exist
- PASS: publish output contains no MSIX/AppX/AppInstaller artifacts
- PASS: ZIP package exists and is non-empty
- PASS: SHA-256 checksum sidecar exists
- PASS: ZIP contains executable, PRI, THIRD_PARTY_NOTICES.md, and README.txt
- PASS: ZIP contains no MSIX/AppX/AppInstaller artifacts
- PASS: extracted executable, PRI, THIRD_PARTY_NOTICES.md, and README.txt exist
- PASS: extracted launch smoke
- PASS: extracted representative Media smoke
- PASS: no WinUI process remains after ZIP probe
```

## What This Proves

- Current WinUI self-contained publish output can be packaged with a dated release-candidate ZIP filename.
- The ZIP package has a generated SHA-256 checksum sidecar.
- The ZIP package and extracted folder include the WinUI executable, PRI file, `THIRD_PARTY_NOTICES.md`, and public-safe `README.txt`.
- The ZIP package contains no MSIX/AppX/AppInstaller artifacts.
- The ZIP package can be extracted to a clean local folder.
- The extracted executable launches and renders primary WinUI product chrome through native UI Automation smoke.
- The extracted executable passes the representative Media playback smoke used for published-output proof.
- No WinUI process remains after the probe.

## What This Does Not Prove

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Windows package identity launch.
- Start menu shortcuts, uninstall entries, or installer UX.
- SmartScreen, Store, reputation, or malware-scanner posture.
- Legal/compliance approval for public binary redistribution.
- Row-by-row media playback coverage beyond the representative sample.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include generated ZIP contents, raw screenshots, private absolute paths, private game paths, media payloads, saves, certificates, package binaries, or raw UI Automation logs.

The generated publish folder, ZIP archive, checksum sidecar, extracted folder, and raw JSON report remain ignored local artifacts under `subagents/`.

## Recommended Next Step

Before publishing a public binary ZIP, complete final human release signoff:

1. Confirm the release version/tag and final artifact name.
2. Confirm `THIRD_PARTY_NOTICES.md` and the ZIP README are final for the candidate.
3. Confirm legal/compliance posture for public binary redistribution.
4. Document SmartScreen, malware-scanner, and reputation expectations honestly.
5. Publish checksum information beside the ZIP, not inside this repo.
