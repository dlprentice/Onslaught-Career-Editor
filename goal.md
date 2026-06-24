# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Close WinUI music UTC sidecar timestamp normalization, then investigate the
staged-positive capture-source correlation mismatch from the latest 60-second
private raw bundle.

This slice starts after the public-primary migration hardening closeout at
`e4ca5904 Repo: align public-primary proof boundaries`. The public checkout
`C:\Users\david\source\Onslaught-Career-Editor` is the day-to-day source of
truth for project-owned work. The former private checkout is no longer the
normal working source.

This slice starts after the public-primary boundary clarification closeout at
`ea6e8dcd State: close public-primary boundary clarification`.

The executable target is the next bounded music/mod runtime proof step:

- fix the first-party UTC timestamp-shape blocker in the music proof
  materializer/builder chain;
- replay the latest private 60-second raw bundle through the fixed
  capture-source correlation builder without relaunching BEA;
- record the exact next fail-closed proof boundary if source correlation still
  does not accept;
- keep all bulky raw runtime outputs in ignored/external local proof roots;
- materialize a public-safe result only through the tracked materializer and
  final checker;
- keep `runtimeAudibleOutputProof=false` until a complete private raw bundle
  passes materializer and final-checker acceptance.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- Public `v1.0.2` app release remains published at
  `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2`.
- Public-primary source boundary clarification is closed and pushed at
  `ea6e8dcd State: close public-primary boundary clarification`.
- Public-primary migration hardening is closed and pushed:
  - private tracked paths measured: `24839`;
  - public tracked paths measured: `19295` after adding
    `tools/hard_payload_safety_check.py`;
  - accepted private-only hard-payload/scratch-payload paths: `5557`;
  - 27 private-only text RE scratch exports are now tracked in public;
  - `tools/public_primary_migration_inventory.py` now treats missing private RE
    scratch text as missing project material instead of accepting it as scratch.
- Remaining local-only material is hard payload or bulky generated evidence:
  actual game files, copied executable/runtime files, private media/input
  payloads, arbitrary saves/options, full Ghidra databases/backups, raw CDB
  logs, screenshots/frame dumps, secrets, build output, and bulky proof roots.
- Active public-primary docs were normalized so the public repo is described as
  the normal working source repo, not a sparse public candidate. The PR template
  now allows compact non-secret state/report text while continuing to reject
  hard payloads and raw proof output. The payload safety checker now has
  credential-like text deny patterns instead of an empty text denylist.
- Boundary clarification: `R4_DENY` in release accounting now means excluded
  from portable app ZIPs and legacy curated export payloads, not automatically
  absent from public source. Compact non-secret `.codex`, state, subagent text,
  readiness, and proof-summary material may be tracked; raw payloads and secrets
  remain excluded.
- The music CGame caller diagnostic is accepted as bounded diagnostic evidence:
  one copied-runtime level-100 run observed `CMusic__PlaySelection` returning
  to `0x0046e0bf`, the direct restart-loop music-selection call site inside
  `CGame__RestartLoopRunLevel`.
- The wrapper-entry `CGame__PlayMusicForCurrentLevel level=100` row remained
  absent in that diagnostic. The materializer/timeline/final-checker contract
  therefore carries explicit `musicSelectionProvenance` values and accepts only
  `cgame-wrapper` or `cgame-restart-loop-direct` selector provenance when the
  timestamped CDB log and timeline sidecar agree.
- `runtimeAudibleOutputProof=false` remains current truth. The diagnostic does
  not prove audible output, loopback/source-correlation acceptance, all cues,
  gameplay parity, online play, rebuild parity, or no-noticeable-difference
  parity.
- Two public-primary armed live-bundle attempts after the caller diagnostic did
  not accept audible output:
  - `music-audible-live-20260624-181120` failed before a proof claim because the
    executor omitted `--source-root` for the source-safety sidecar; the command
    shape is now fixed and covered by regression test.
  - `music-audible-live-20260624-181538` reached clean/staged CDB music-selection
    provenance but failed capture-source correlation because the 30-second raw
    WAV captures had zero samples; calibration-tone capture proved the loopback
    backend can record the endpoint, and the executor now requires/defaults to
    a 60-second live audio capture.
- The later 60-second private raw bundle
  `music-audible-live-20260624-144834` reached the capture-source correlation
  builder with non-silent clean/staged loopback captures and
  restart-loop-direct CDB music-selection provenance. The old `+00:00`
  timestamp blocker is fixed: private JSON sidecars may use `Z` or `+00:00`,
  and sanitized materialized proof output normalizes back to `Z`.
- Replaying that 60-second bundle now reaches the next fail-closed proof
  boundary: staged-positive capture correlation prefers the original
  `BEA_04` target over the replacement `BEA_02` source (`margin=-0.161892`,
  required `0.150000`, target `0.862302`, replacement `0.700409`). No
  capture-source sidecar was emitted and `runtimeAudibleOutputProof=false`
  remains current truth.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Installed Steam game files and original `BEA.exe` remain read-only.

## Latest Closed Slice

Public-primary migration and proof-boundary hardening closed at
`e4ca5904 Repo: align public-primary proof boundaries`; follow-up source
boundary clarification closed at
`ea6e8dcd State: close public-primary boundary clarification`.

Closed-slice validation:

```powershell
npm run test:public-primary-migration-inventory
npm run test:hard-payload-safety
npm run test:public-primary-migration-inventory
python tools\docsync_check.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
py -3 -c "import json; [json.load(open(p, encoding='utf-8')) for p in ['developer_agent_state.json','documentation_agent_state.json']] ; print('state json ok')"
git diff --cached --check
```

Final pushed-state verification:

```powershell
git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/main
Get-Process BEA,cdb -ErrorAction SilentlyContinue
```

## Validation For This Slice

Required before any commit/push:

```powershell
npm run test:winui-safe-copy-music-cgame-caller-diagnostic
npm run test:winui-safe-copy-music-cdb-timeline-sidecar
npm run test:winui-safe-copy-music-audible-output-materializer
npm run test:winui-safe-copy-music-audible-output-two-run-harness
npm run test:winui-safe-copy-music-audible-output-live-bundle-executor
npm run test:winui-safe-copy-music-timestamped-cdb-log-producer
npm run test:winui-safe-copy-music-source-music-safety-sidecar
npm run test:winui-safe-copy-music-ambient-no-bea-census
npm run test:winui-safe-copy-music-source-audio-correlation
npm run test:winui-safe-copy-music-capture-source-correlation
npm run test:winui-safe-copy-music-capture-source-correlation-builder
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
npm run test:winui-safe-copy-music-audible-output-contract
npm run test:hard-payload-safety
npm run test:doc-commands
npm run test:md-links
npm run test:repo-hygiene
```

Also required:

- state JSON parse;
- `git diff --check`;
- final `BEA.exe` / `cdb.exe` process cleanup check;
- public/private payload boundary check if any release, migration, or proof
  material changes.

## Next Executable Work

1. Validate and commit the UTC timestamp normalization plus source-root
   regression coverage.
2. Investigate why the staged-positive capture from the 60-second bundle still
   correlates more strongly to original `BEA_04` than replacement `BEA_02`.
3. Decide from evidence whether the next fix belongs in staging verification,
   audio capture timing, source-correlation windowing, or the live music preset.
4. Preserve `runtimeAudibleOutputProof=false` until a generated private raw
   bundle passes the materializer and final checker.
5. Update docs/state/evidence, validate, commit/push the green slice, then
   continue with patch/mod/runtime or online proof work from the public repo.

## Stop Conditions

- Any step would mutate the installed Steam game folder or original `BEA.exe`.
- Any tracked file is an actual game executable/DLL/archive/media payload,
  arbitrary save/options payload, full Ghidra database/backup, raw CDB log,
  screenshot/frame dump, secret, `.env*`, copied runtime output, or build
  artifact.
- Online wording or UI implies player-ready online multiplayer before required
  distinct-endpoint and source-bound runtime proofs exist.
- A runtime proof would require unavailable operator hardware/endpoints and no
  other bounded progress remains.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
