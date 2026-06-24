# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Finish the public-primary full migration/readiness pass so the public checkout
is the normal day-to-day repo for project-owned work, not a sparse export.

This slice starts after the music timestamp/proof-boundary closeout at
`e10db436 Runtime: accept UTC music proof sidecar timestamps`.

The operator direction is an aggressive private-to-public pivot: migrate and
track useful project material from the former private checkout when it is
source, docs, tools, tests, RE notes, wave notes, state batons, agent reports,
readiness notes, compact proof summaries, or other non-secret/non-payload text
that helps contributors and agents continue the work. The public repo should
feel complete, collaboration-ready, and usable as the working base.

The only local/ignored overlay classes for this slice are hard payloads and
machine-only outputs: actual game executables/DLLs/archives/media, extracted
asset payloads, arbitrary save/options payloads other than the tracked immutable
fixture, copied runtime profiles, raw screenshots/frame dumps, raw CDB logs,
bulky generated proof captures, full Ghidra databases/backups, secrets,
`.env*`, local config, runtime caches, and build/test/package outputs.

Executable target:

- run the private-vs-public migration inventory from a clean public `main`;
- use Codex normal/adversarial consults for migration completeness, public
  wording, hard-payload risk, and contributor readiness;
- promote any remaining safe private-only project material into public;
- tighten docs/checkers only where they still imply a sparse/sanitized export
  rather than a public-primary working repo;
- keep hard payloads ignored/local and represented by hashes, schemas, docs,
  compact proof summaries, and reproducible tools;
- validate with migration, payload-safety, docs/release, hygiene, and state
  gates, then commit/push the green public-main closeout.

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
- The UTC timestamp normalization/source-root regression slice is closed and
  pushed at `e10db436 Runtime: accept UTC music proof sidecar timestamps`.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Installed Steam game files and original `BEA.exe` remain read-only.

## Latest Closed Slice

Music UTC timestamp/proof-boundary normalization closed at
`e10db436 Runtime: accept UTC music proof sidecar timestamps`. The public repo is
clean and aligned at that commit before this migration/readiness slice begins.

Closed-slice validation:

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
python tools\docsync_check.py
npm run test:hard-payload-safety
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:repo-hygiene
py -3 -c "import json; [json.load(open(p, encoding='utf-8')) for p in ['developer_agent_state.json','documentation_agent_state.json']] ; print('state json ok')"
git diff --check
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
npm run test:public-primary-migration-inventory
npm run test:hard-payload-safety
python tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:repo-hygiene
```

Also required:

- state JSON parse;
- `git diff --check`;
- final `BEA.exe` / `cdb.exe` process cleanup check;
- public/private payload boundary check if any release, migration, or proof
  material changes.

## Next Executable Work

1. Wait for the current Codex consults to return and fold in their path-grounded
   migration/readiness findings.
2. Run the private-vs-public inventory and inspect every remaining private-only
   class that is not obviously hard payload, secret, build output, or bulky raw
   proof output.
3. Promote safe private-only project material into public and adjust docs/checks
   if they still imply the public repo is a sparse candidate instead of the
   working repo.
4. Validate, commit/push the public-primary migration/readiness closeout.
5. Resume patch/mod/runtime proof work from the public repo; preserve
   `runtimeAudibleOutputProof=false` until a generated private raw bundle passes
   the materializer and final checker.

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
