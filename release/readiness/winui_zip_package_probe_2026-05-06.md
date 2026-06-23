# WinUI ZIP Package Probe

Status: public-safe release readiness evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `42a4bc33`
Evidence-report commit: 9c83ad59d00ef40aad169aa6b3038d6355931190
Checksum enhancement commit: 48f65e50e0f65de006f23339140f72cfaf442558
ZIP README enhancement commit: d4c7eb9b0470f7b11383ecc08836f2b875c943c6

## Purpose

This pass tested a non-cert distribution lane for the WinUI app while MSIX trusted install remains blocked by Windows certificate trust.

The probe publishes the WinUI app to ignored output, copies a public-safe ZIP `README.txt` into the package root, creates a disposable ZIP archive with a stable local-probe filename, writes a SHA-256 checksum sidecar, extracts the archive to a fresh ignored folder, runs existing native UI Automation launch smoke against the extracted executable, runs representative Media playback smoke against the extracted executable, and verifies no WinUI process remains.

This is not an installer/MSIX proof. It is a ZIP-plus-extracted-exe proof for the current self-contained WinUI output.

## Command

```powershell
py -3 tools\winui_zip_package_probe.py --check --include-media-smoke
```

Equivalent npm wrapper:

```powershell
npm run test:winui-zip-package-probe
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
ZIP package: OnslaughtCareerEditor.WinUI-local-probe-win-x64.zip
ZIP byte size: 242329093
ZIP SHA-256: ee9062195ca3c49b4d028cda63726dc6a1944d3ea7650102b3d60f2b3124f7c6
- PASS: public-safe ZIP README copied into publish root
- PASS: publish executable, PRI, and THIRD_PARTY_NOTICES.md exist
- PASS: publish README.txt exists and is non-empty
- PASS: publish output contains no MSIX/AppX/AppInstaller artifacts
- PASS: ZIP package exists and is non-empty
- PASS: SHA-256 checksum sidecar exists
- PASS: ZIP contains executable, PRI, and THIRD_PARTY_NOTICES.md
- PASS: ZIP contains README.txt
- PASS: ZIP contains no MSIX/AppX/AppInstaller artifacts
- PASS: extracted executable, PRI, and THIRD_PARTY_NOTICES.md exist
- PASS: extracted README.txt exists and is non-empty
- PASS: extracted launch smoke
- PASS: extracted representative Media smoke
- PASS: no WinUI process remains after ZIP probe
```

## What This Proves

- Current WinUI self-contained publish output can be packaged as a ZIP archive.
- The ZIP archive has a stable local-probe filename and a generated SHA-256 checksum sidecar.
- The ZIP archive and extracted folder include a public-safe `README.txt` with quick-start instructions and scoped release claims.
- The ZIP archive contains the WinUI executable, PRI file, and `THIRD_PARTY_NOTICES.md`.
- The ZIP archive does not contain MSIX/AppX/AppInstaller artifacts.
- The ZIP archive can be extracted to a clean local folder.
- The extracted executable launches and renders primary WinUI product chrome through native UI Automation smoke.
- The extracted executable passes the representative Media playback smoke used for published-output proof.
- No WinUI process remains after the probe.

## What This Does Not Prove

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Windows package identity launch.
- Start menu shortcuts, uninstall entries, or installer UX.
- SmartScreen, Store, reputation, or distribution posture.
- Legal/compliance approval for public binary redistribution.
- Row-by-row media playback coverage beyond the representative sample.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include generated ZIP contents, raw screenshots, private absolute paths, private game paths, media payloads, saves, certificates, package binaries, or raw UI Automation logs.

The generated publish folder, ZIP archive, checksum sidecar, extracted folder, and raw JSON report remain ignored local artifacts under `subagents/`.

## Recommended Next Step

Choose the release distribution lane:

1. If ZIP is acceptable, add a final release-candidate ZIP packaging/signoff pass with release-version naming, notice/license review, malware/SmartScreen expectations, and manual extraction/launch instructions.
2. If MSIX is required, resolve the certificate trust/signing chain and rerun a successful install/launch/uninstall probe.
3. Do not claim installer-grade readiness until the selected lane has public-safe evidence for build, distribution artifact, launch, cleanup/uninstall expectations, notices, and legal/compliance review.
