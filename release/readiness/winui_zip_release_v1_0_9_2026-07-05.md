# WinUI ZIP Release v1.0.9 - 2026-07-05

Status: release-candidate validated; GitHub publication pending in this release slice

This note tracks the v1.0.9 public ZIP release. It is a portable unsigned
Windows x64 ZIP with a checksum sidecar. It is not a signing result, MSIX,
Store package, installer, SmartScreen/reputation claim, runtime gameplay proof,
online capability promotion, or rebuild/visual parity claim.

## Release Source Updates

- `package.json` version: `1.0.9`
- `package-lock.json` root package versions: `1.0.9`
- `release/readiness/public_package.json` version: `1.0.9`
- `OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj` version:
  `1.0.9`
- `package.json` release-candidate ZIP script:
  `OnslaughtToolkit-winui-v1.0.9-win-x64.zip`
- `README.MD`, `README.RELEASE.md`, `CURRENT_CAPABILITIES.md`, and
  `lore-book/CURRENT_CAPABILITIES.md` describe v1.0.9 as the current public ZIP
  shape.
- `release/readiness/winui_action_reaction_map_v1_0_9_2026-07-05.md` records
  the first-time-user action/reaction map.
- `release/readiness/winui_control_action_matrix_v1_0_9_2026-07-05.tsv`
  records the source-derived per-control matrix.

## Candidate Artifact

The final v1.0.9 release-candidate probe built the final-named ZIP and passed
the package/layout/Lore/launch/Home/Media/process-cleanup checks.

- ZIP: `OnslaughtToolkit-winui-v1.0.9-win-x64.zip`
- ZIP size: `246804448`
- SHA-256: `e09439c40a4ff7197c4151e18651388b2515a71950ea2479b01266c00d918519`
- Checksum sidecar: `OnslaughtToolkit-winui-v1.0.9-win-x64.zip.sha256`
- Probe report:
  `subagents/winui-zip-release-candidate-probe/current/zip-package-report.json`
- Lore document count: `949`
- Root layout: `Launch Onslaught Toolkit.cmd`, `README.MD`, `LICENSE`,
  `app/`, `lore-book/`, `lore-pack/`
- Longest ZIP Explorer-relative path: `133` characters within the `180`
  character budget
- Launch smoke: pass
- Home navigation smoke: pass
- Home deep-link smoke: pass
- Lore reader smoke: pass
- Representative Media smoke: pass after `1` attempt
- WinUI process cleanup: pass (`<none>`)

## User-Facing Delta From v1.0.8

- The app version metadata is stamped as `1.0.9`.
- Save Lab write actions use copy-oriented labels:
  `Write patched save copy` and `Write options copy`.
- Media uses `Show in Explorer` for the shell-opening action.
- Asset Library uses `Write local package` for the local package materializer.
- Windowed & Mods uses `Launch safe game copy` and `Stop copied game` for the
  managed copied-game process flow.
- `Stop copied game` now asks for confirmation before closing or force-closing
  the managed copied process.
- Closing the toolkit now warns first when a managed copied game process is
  still registered.

## Validation

- `npm run test:winui-zip-release-candidate-probe` - pass
  - package name: `OnslaughtToolkit-winui-v1.0.9-win-x64.zip`
  - extracted launch smoke: pass
  - extracted Home navigation smoke: pass
  - extracted Lore smoke: pass
  - representative Media smoke: pass after `1` attempt
  - process cleanup: pass

Additional final repo gates are recorded in the release commit/final handoff.

## Boundaries

- No signing, installer, MSIX, Store package, or SmartScreen claim.
- No Battle Engine Aquila game files, copied executables, saves, media payloads,
  raw proof bundles, CDB logs, screenshots, full Ghidra databases, secrets, or
  bulky generated artifacts are committed.
- No installed game folder or original `BEA.exe` mutation.
- No Host/Join enablement, player-ready online claim, gameplay claim, rebuild
  parity claim, or visual parity claim.
