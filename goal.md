# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Close the public-primary full-migration hardening pass so day-to-day work uses
`C:\Users\david\source\Onslaught-Career-Editor` and the former private repo is
no longer a required source of truth for project-owned material.

This slice is bounded to repo migration/readiness work:

- work only from `C:\Users\david\source\Onslaught-Career-Editor`;
- keep public as the primary collaboration and working repo;
- track useful project material broadly: source, tests, tools, patch catalogs,
  RE docs, wave notes, state batons, agent reports, readiness notes, compact
  proof summaries, and useful text scratch exports;
- keep hard payloads local/ignored: game files, copied executables, private
  media/input payloads, arbitrary saves/options, full Ghidra databases/backups,
  raw screenshots/frame dumps, raw CDB logs, secrets, and generated build/proof
  output;
- preserve the installed Steam game folder and original `BEA.exe` as read-only;
- keep Host/Join and online wording disabled/non-player-ready;
- do not weaken public hard-payload guards to satisfy 1:1 path parity.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- `v1.0.2` app release remains published at
  `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2`.
- Public-primary migration is closed on public `main` at
  `c1c04564 Repo: close public-primary migration inventory`; the former private
  repo is no longer the normal source of truth.
- This hardening pass promoted 27 private-only `.c` / `.tsv` RE scratch exports
  from `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-27/**`
  and tightened the migration guard so missing private RE scratch text fails
  instead of being accepted as scratch.
- The music CGame caller diagnostic is accepted as bounded diagnostic evidence:
  one copied-runtime level-100 run observed `CMusic__PlaySelection` returning
  to `0x0046e0bf`, the direct restart-loop music-selection call site inside
  `CGame__RestartLoopRunLevel`. The wrapper-entry
  `CGame__PlayMusicForCurrentLevel level=100` row remained absent.
- `runtimeAudibleOutputProof=false` remains current truth. The diagnostic
  narrows the previous materializer failure to contract/attach-timing
  provenance; it does not prove audible output, all cues, gameplay parity,
  online play, rebuild parity, or no-noticeable-difference parity.
- Latest accepted diagnostic note:
  `release/readiness/winui_music_cgame_caller_diagnostic_2026-06-24.md`.
- Online multiplayer is still not player-ready. Host/Join remains disabled until
  distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof exist.
- WinUI 3 remains the current shipped app lane. Blazor/Tauri/Godot remain future
  evaluations, not active replacements for this slice.

## Closed Migration Evidence

Public-primary migration closeout at `c1c04564` accepted:

- former private tracked paths: `24839`
- public tracked paths after this migration hardening pass: `19294`
- accepted private-only hard-payload/scratch paths: `5557`

Migration validation passed:

- `npm run test:public-primary-migration-inventory`
- `npm run test:hard-payload-safety`
- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:repo-hygiene`
- `py -3 tools\release_profile_snapshot.py --check`
- `py -3 tools\release_curated_manifest.py --check`
- state JSON parse
- `git diff --cached --check`

Current hardening additions:

- 27 private-only text RE scratch exports promoted to public tracking.
- `tools/public_primary_migration_inventory.py` now only accepts payload-like
  scratch outputs (`.png`, `.fbx`, `.bes`) as private-only scratch; missing
  private RE scratch text is treated as missing project material.

## Latest Closed Slice Validation

The CGame caller diagnostic closeout passed:

- `py -3 -m py_compile tools\winui_safe_copy_music_cgame_caller_diagnostic_check.py`
- `npm run test:winui-safe-copy-music-cgame-caller-diagnostic`
- focused checker against the accepted local ignored diagnostic artifact
- CDB observer command validation
- state JSON parse
- `git diff --check`
- `npm run test:hard-payload-safety`
- `npm run test:doc-commands`
- `npm run test:public-allowlist`
- `npm run test:md-links`
- `npm run test:repo-hygiene`
- final process check: no `BEA.exe` or `cdb.exe`

## Validation For This Slice

Required before closeout:

- `npm run test:public-primary-migration-inventory`
- `npm run test:hard-payload-safety`
- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:repo-hygiene`
- focused music materializer/observer checks for the currently dirty music
  contract WIP
- process cleanup check if any runtime proof command is run
- docs/state JSON parse
- `git diff --check`

## Next Executable Work

1. Finish validation for the public-primary hardening pass.
2. Commit/push only after the repo is green and release/public boundaries are
   still clean.
3. Then return to patch/mod/runtime work from the public repo only, with
   `runtimeAudibleOutputProof=false` until a complete raw bundle passes the
   materializer and final checker.

## Stop Conditions

- A proposed tracked file is an actual BEA executable/DLL/game archive/media
  payload, full Ghidra database/backup, secret, `.env*`, copied runtime output,
  screenshot/frame dump, raw CDB log, or build artifact.
- A proposed runtime or patch step mutates the installed Steam game folder or
  original `BEA.exe`.
- Online wording or UI implies player-ready online multiplayer before required
  proofs exist.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
