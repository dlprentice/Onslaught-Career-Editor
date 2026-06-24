# WinUI ZIP Package Probe — Home Navigation Expansion

Status: public-safe release readiness evidence
Date: 2026-05-27
Branch: captured on `wip/sandbox` pre-merge; **still valid on `main`** after PR #1 (`df6ed5a1`+) until publish/probe scripts change.
Source head before pass: `d191a333` (includes home navigation probe, evidence docs, and primary-lane test audit fix)
Probe tooling: `tools/winui_zip_package_probe.py` with `HOME_NAVIGATION_FILTER` and `HOME_NAVIGATION_TEST_TIMEOUT_SECONDS=600`

## Purpose

This pass extends the 2026-05-06 ZIP package probe lane to rerun the full explicit `WinUiHomeNavigationSmokeTests` class on the **extracted Release publish executable** after launch smoke. The May 6 evidence at `release/readiness/winui_zip_package_probe_2026-05-06.md` remains the historical record for launch and representative Media smoke only; it does not prove extracted Home navigation.

The probe still publishes WinUI output to ignored storage, copies a public-safe ZIP `README.txt`, creates a disposable ZIP with a SHA-256 sidecar, extracts to a fresh folder, runs launch smoke, runs all eight `WinUiHomeNavigationSmokeTests` (seven Home task routes plus Configuration Editor deep-link) with `NUnit.NumberOfTestWorkers=1`, runs representative Media smoke when requested, and verifies no WinUI process remains.

This is not installer/MSIX proof. Home navigation coverage is automation-marker reachability from Home, not full page workflows.

## Command

```powershell
npm run test:winui-zip-package-probe
```

Equivalent:

```powershell
py -3 tools\winui_zip_package_probe.py --check --include-media-smoke
```

Working directory: repo root.

Result: **PASS** (2026-05-27 local runs; validated pre-merge and post-`main`).

| Pass | Tree | Notes |
| --- | --- | --- |
| Initial | `d191a333` on `wip/sandbox` | First Home-navigation ZIP expansion |
| Revalidation | `6eebbe44` on `main` era (post PR #1) | Same probe command after lane promotion |

Important output summary (revalidation on `main` era, 2026-05-27):

```text
WinUI ZIP package probe
Status: pass
ZIP package: subagents\winui-zip-package-probe\current\OnslaughtCareerEditor.WinUI-local-probe-win-x64.zip
ZIP byte size: 242396931
ZIP SHA-256: 7888483b00054f25602678efa799ba46b75239f6755f0f507cb0057af790cc52
- PASS: extracted_launch_smoke
- PASS: extracted_home_navigation_smoke (exit code 0)
- PASS: extracted_media_smoke
- PASS: process_after
```

Initial pass SHA-256: `a05de018faf4ff6472418f0197836e677ebde220d4dd83e3c918ffb3048c6646` (byte size 242396781). Revalidation byte size differs slightly; treat SHA sidecar under ignored `subagents/` as authoritative per run.

Report JSON (ignored): `subagents/winui-zip-package-probe/current/zip-package-report.json` with `homeNavigationSmokeExitCode: 0`.

## What This Proves (additive to 2026-05-06)

- The extracted Release publish executable passes all explicit `WinUiHomeNavigationSmokeTests` after ZIP extract and launch smoke, including `HomeReviewSettingsButton` and Configuration Editor deep-link tab selection.
- The ZIP probe gates representative Media smoke after launch and home navigation when `--include-media-smoke` is set.

## What This Does Not Prove

- MSIX/AppInstaller packaging, signing, trust, SmartScreen, or installer UX (unchanged from 2026-05-06).
- Home navigation on paths other than the extracted disposable ZIP lane (debug build proof is separate explicit UIA).
- Full Settings, Save Lab, Media, Lore, or Patch Bench workflows beyond destination automation markers.
- Dated release-candidate ZIP naming is covered separately by `release/readiness/winui_zip_release_candidate_probe_2026-05-27.md`.

## Privacy / Release Safety

Committed evidence is public-safe. Generated ZIP contents, extract folders, UI Automation logs, and raw JSON remain under ignored `subagents/`.

## Related Historical Evidence

- `release/readiness/winui_zip_package_probe_2026-05-06.md` — launch + Media on extracted exe (SHA `ee906219…`); no home navigation.
