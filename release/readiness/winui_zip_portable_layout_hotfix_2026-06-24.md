# WinUI ZIP Portable Layout Hotfix

Status: public-safe release readiness evidence
Date: 2026-06-24
Package: `OnslaughtToolkit-winui-v1.0.2-win-x64.zip`

## Purpose

The v1.0.2 ZIP release candidate had proven that the extracted WinUI app could
launch, navigate Home, and run representative Media smoke from the raw
self-contained publish root. That was functionally useful but poor release UX:
extracting the ZIP exposed runtime DLLs, executables, and locale folders at the
top level instead of a small portable-app entry point.

This hotfix makes the friendly portable layout the active package contract.

## Required Layout

The ZIP root must contain only:

- `Launch Onslaught Toolkit.cmd`
- `README.MD`
- `LICENSE`
- `app/`

The raw self-contained WinUI payload, including `OnslaughtCareerEditor.WinUI.exe`,
support DLLs, locale folders, notices, and patch catalogs, lives under `app/`.

The updated package probe rejects root-level `.exe` and `.dll` files and rejects
unexpected top-level folders such as raw publish locale directories.

## Validation

Command:

```powershell
npm run test:winui-zip-release-candidate-probe
```

Result: **PASS**

Evidence:

```text
ZIP package: subagents\winui-zip-release-candidate-probe\current\OnslaughtToolkit-winui-v1.0.2-win-x64.zip
ZIP byte size: 242786394
ZIP SHA-256: 7bbf43f69ff9f73a61e9afcced10c7f4f69b7c7b5e0e9713eb7be6a64d4c2091
PASS: zip_contains_Launch Onslaught Toolkit.cmd
PASS: zip_contains_README.MD
PASS: zip_contains_LICENSE
PASS: zip_contains_app_OnslaughtCareerEditor.WinUI.exe
PASS: zip_friendly_root_shape
PASS: zip_no_root_executables
PASS: zip_no_root_dlls
PASS: extracted_launch_smoke
PASS: extracted_home_navigation_smoke
PASS: extracted_media_smoke (exit code 0 after 1 attempt)
PASS: process_after
```

## Boundaries

This proves only the unsigned portable ZIP layout, extraction, extracted app
launch smoke, Home navigation smoke, representative Media smoke, checksum
sidecar generation, and process cleanup. It does not prove MSIX/AppInstaller
packaging, signing/trust, SmartScreen reputation, Store readiness, installer UX,
or legal/compliance approval for public binary redistribution.

## Publication Verification

GitHub release `v1.0.2` was updated after the hotfix:

```text
Release URL: https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2
Uploaded asset digest: sha256:7bbf43f69ff9f73a61e9afcced10c7f4f69b7c7b5e0e9713eb7be6a64d4c2091
Uploaded asset size: 242786394
Checksum sidecar: OnslaughtToolkit-v1.0.2-SHA256SUMS.txt
Public source doc hotfix: e0ec5b8 Docs: clarify portable ZIP launch layout
Private source probe hotfix: 7249f7e39 Release: restore WinUI portable ZIP layout
```

Downloaded-release verification also passed: the downloaded ZIP hash matched
`7bbf43f69ff9f73a61e9afcced10c7f4f69b7c7b5e0e9713eb7be6a64d4c2091`, the
checksum sidecar matched that digest, and the downloaded ZIP root contained
only `LICENSE`, `Launch Onslaught Toolkit.cmd`, `README.MD`, and `app/`.
