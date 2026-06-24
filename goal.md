# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Close the public-primary source boundary clarification, then resume the WinUI
safe-copy music audible-output proof lane from the public primary repo.

This slice starts after the public-primary migration hardening closeout at
`e4ca5904 Repo: align public-primary proof boundaries`. The public checkout
`C:\Users\david\source\Onslaught-Career-Editor` is the day-to-day source of
truth for project-owned work. The former private checkout is no longer the
normal working source.

The executable target is the next bounded music/mod runtime proof step:

- run focused preflight gates for the current music audible-output live-bundle
  chain;
- use bounded Codex normal/adversarial consults before any armed live attempt;
- run one private live-bundle attempt only if source/proof roots, process
  hygiene, audio preflight, and proof-contract checks are clean;
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
- Latest pushed public-primary closeout before this clarification is
  `655666ba`; this slice has staged boundary-clarification changes pending
  validation/commit.
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
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Installed Steam game files and original `BEA.exe` remain read-only.

## Latest Closed Slice

Public-primary migration and proof-boundary hardening closed at
`e4ca5904 Repo: align public-primary proof boundaries`.

Closed-slice validation:

```powershell
npm run test:public-primary-migration-inventory
npm run test:hard-payload-safety
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

1. Finish focused music proof-chain preflight and consult review.
2. If preconditions are clean, run one armed private live-bundle attempt under
   the approved external/private runtime proof root.
3. If the attempt succeeds, materialize through the tracked materializer and
   final checker before changing any claim.
4. If the attempt fails, record the exact failed rung and preserve
   `runtimeAudibleOutputProof=false`.
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
