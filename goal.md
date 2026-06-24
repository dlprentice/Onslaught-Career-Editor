# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Resume runtime/mod work from the new public-primary repo by validating the
migrated music audible-output live-bundle support and preparing the next safe
live attempt from this checkout.

The public-primary migration baseline is already committed and pushed:
`c58d0642 Migrate private project into public primary repo`. Normal development
should now happen from `C:\Users\david\source\Onslaught-Career-Editor` by
default. The former private repo may still contain stale or dirty local state,
but it is no longer the authority for normal source/docs/tools work.

This slice is bounded to the music audible-output proof ladder:

- keep `runtimeAudibleOutputProof=false` until the private live raw bundle
  passes the materializer and final checker;
- validate the migrated early exact-PID CDB attach support in
  `tools/winui_safe_copy_live_runtime_smoke.py` and
  `tools/run_winui_safe_copy_music_audible_output_live_bundle.py`;
- keep all copied game profiles, WAV captures, CDB logs, frames, screenshots,
  and raw live proof outputs in ignored local/external proof roots;
- do not change public release claims, Host/Join enablement, Ghidra state, or
  original installed game files.

## Current Truth

- Public-primary migration baseline is pushed to `origin/main` at
  `c58d06420e482421355d1e40f240db7d87e289d3`.
- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- `v1.0.2` app release remains published at
  `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2`.
- The five music/CDB files from the former private dirty tree are byte-identical
  in this public checkout, including early `--cdb-attach-phase after-launch`
  support for clean/staged music stages.
- A prior private live attempt reached clean-baseline copied BEA launch and
  exact-PID CDB attach, and saw lower-level music/decode rows, but the strict
  contract rejected the bundle because `CGame__PlayMusicForCurrentLevel
  level=100` was missing. That rejection still stands.
- Online multiplayer is still not player-ready. Host/Join remains disabled until
  distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof exist.
- WinUI 3 remains the current shipped app lane. Blazor/Tauri/Godot remain future
  evaluations, not active replacements for this slice.

## Validation For This Slice

Passed in this slice:

- `py -3 tools\winui_safe_copy_live_runtime_smoke_test.py` (14 tests);
- `py -3 tools\run_winui_safe_copy_music_audible_output_live_bundle_test.py`
  (17 tests);
- state/package JSON parse.
- `npm run test:hard-payload-safety`;
- `npm run test:doc-commands`;
- `py -3 tools\docsync_check.py`;
- `npm run test:repo-hygiene`;
- `git diff --check`.

Optional if the workstation/proof root is ready after the source/docs closeout:

- run one private music audible-output live raw-bundle attempt from the public
  repo and feed accepted raw artifacts through the materializer/final checker.

## Next Executable Work

1. Commit and push the public-runtime baton.
2. If local runtime prerequisites are clean, make one private music audible-output
   live raw-bundle attempt from the public repo using ignored/local proof roots.
3. Keep `runtimeAudibleOutputProof=false` unless the final checker accepts the
   complete live bundle.

## Stop Conditions

- A proposed tracked file is an actual BEA executable/DLL/game archive/media/save
  payload, full Ghidra database/backup, secret, `.env*`, copied runtime output,
  screenshot/frame dump, raw CDB log, or build artifact.
- A proposed runtime or patch step mutates the installed Steam game folder or
  original `BEA.exe`.
- Online wording or UI implies player-ready online multiplayer before required
  proofs exist.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
