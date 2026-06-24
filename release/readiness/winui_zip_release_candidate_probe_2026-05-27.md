# WinUI ZIP Release-Candidate Probe — Home Navigation Expansion

Status: public-safe release readiness evidence
Date: 2026-05-27
Branch: captured on `wip/sandbox` pre-merge; **revalidated on `main` era** (`ca95a9d7`, 2026-05-27).
Source head before initial pass: `c7275c5e` (home navigation probe expansion)
Package name: `OnslaughtCareerEditor.WinUI-2026-05-27-rc1-win-x64.zip` (npm `test:winui-zip-release-candidate-probe`)

## Purpose

This pass extends the 2026-05-06 release-candidate ZIP probe to include extracted `WinUiHomeNavigationSmokeTests` on the extracted Release executable. The May 6 evidence at `release/readiness/winui_zip_release_candidate_probe_2026-05-06.md` remains the historical record for launch and representative Media smoke only.

The probe uses the same `tools/winui_zip_package_probe.py` path as the local-probe ZIP proof, with a separate ignored output root and the dated RC package filename above.

## Command

```powershell
npm run test:winui-zip-release-candidate-probe
```

Equivalent:

```powershell
py -3 tools\winui_zip_package_probe.py --check --include-media-smoke --out-root subagents\winui-zip-release-candidate-probe\current --package-name OnslaughtCareerEditor.WinUI-2026-05-27-rc1-win-x64.zip
```

Working directory: repo root.

Result: **PASS** (2026-05-27; initial + post-`main` revalidation).

| Pass | Tree | Package filename |
| --- | --- | --- |
| Initial | `c7275c5e` | dated RC naming validated |
| Revalidation | `ca95a9d7` (`main` era) | `OnslaughtCareerEditor.WinUI-2026-05-27-rc1-win-x64.zip` |

Important output summary (revalidation, 2026-05-27):

```text
WinUI ZIP package probe
Status: pass
ZIP byte size: 242396914
ZIP SHA-256: 2880951756fa83784b09b6d3453d83387c95e885dea87d47877835b242a9e36c
- PASS: extracted_launch_smoke
- PASS: extracted_home_navigation_smoke (exit code 0)
- PASS: extracted_media_smoke
- PASS: process_after
```

Initial pass SHA-256: `9954d6ee749e940b820f2249e0e4931f22e5138fb064688331fec098f8feecfc` (byte size 242397014).

Report JSON (ignored): `subagents/winui-zip-release-candidate-probe/current/zip-package-report.json` with `homeNavigationSmokeExitCode: 0`.

## What This Proves (additive to 2026-05-06 RC)

- Dated RC ZIP packaging with checksum sidecar, public-safe README, clean extract, launch smoke, full explicit Home navigation on the extracted executable, and representative Media smoke (Media gated on successful home navigation).
- Same publish bytes as the 2026-05-27 local-probe pass (SHA `9954d6ee…`) for this workstation run; filename differs from local-probe ZIP name only.

## What This Does Not Prove

- MSIX/AppInstaller packaging, signing, trust, SmartScreen, or installer UX (unchanged from 2026-05-06 RC).
- Full Home/page workflows beyond automation-marker reachability.
- That future RC runs must reuse the `2026-05-06-rc1` filename (npm script may be updated to a newer dated name).

## Privacy / Release Safety

Committed evidence is public-safe. Generated ZIP, extract tree, and raw JSON remain under ignored `subagents/`.

## Related Historical Evidence

- `release/readiness/winui_zip_release_candidate_probe_2026-05-06.md` — RC launch + Media (SHA `1ae3be7f…`); no home navigation.
