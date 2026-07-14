# Active Goal

Status: ACTIVE
Last updated: 2026-07-14
Policy: `goal.policy.md`
Integration baseline: `5b5c7efb` (walker scalar v2 + Core `WalkerSpeedPerTick=100`)

## Objective

Aggressively reconstruct Battle Engine Aquila from the provided Onslaught C++
source, the pinned legacy AYA extractor, the existing safe Python extraction
pipeline, the repository's accumulated RE corpus, Steam static evidence, and
controlled copied-runtime measurements. Complete deterministic local extraction
coverage for every observed resource family and rebuild source-named game
systems in deterministic Core. Keep proprietary payloads local, preserve the
installed game and original executable, and label source hypotheses, Steam
agreements, runtime measurements, rebuild contracts, and unresolved differences
separately.

## Closed slice (do not re-open unless evidence is overturned)

Walker-forward **scalar speed** path is closed:

- Accepted two-attempt copied-runtime pair (historical private id `p27`;
  compact metrics retained under ignored `local-proofs/wt/p27-compact/`).
- Public contract:
  `reverse-engineering/game-mechanics/walker-forward-scalar-response-v2.json`
  (`battleengine-walker-forward-scalar-response.v2`).
- Translation policy accepted:
  `reverse-engineering/game-mechanics/walker-forward-retail-to-core-translation-policy.md`.
- Core: `WalkerSpeedPerTick = 100` (milli-retail @ 30 Hz); rebuild goldens updated;
  `npm run test:rebuild` green at landing.
- Lab hygiene: full game trees under `local-proofs/wt/p18`–`p27` and playback
  roots pruned; keep compact evidence only. Prefer reusable lab copies for
  future live runs; do not retain multi-GB profile trees after closeout.

## Current Slice

Continue reconstruction with the next **bounded** rebuild-grade measurement and
harden runtime proof storage so disk does not explode.

1. **Proof storage hygiene (tooling):** teach the walker / live-runtime pair
   runner to (a) optionally reuse a durable authorized lab profile base and
   (b) after attempt closeout, delete `profile-app-config` game trees and runner
   build junk while retaining compact evidence (raw/metrics/status/receipt/
   closeout). Document the keep/delete policy in a tracked RE or tools note.
   Validate with unit tests; do not require a live BEA launch for the hygiene
   unit gate.
2. **Next scalar system — jet forward/thrust response (measurement first):**
   obtain one fresh exactly-two-attempt **copied-runtime** measurement of
   jet-mode forward/thrust scalar response (receipt-bound, Steam/original
   untouched). If either attempt fails, fix tooling/analysis and retry; publish
   **no** Core constant change without two accepts. Prefer compact evidence
   retention after closeout.
3. **Only if both jet attempts pass:** publish a bounded scalar contract in
   retail units, accept a separate retail→Core translation policy, then update
   deterministic Core (e.g. `JetSpeedPerTick`) + goldens + `npm run test:rebuild`.
4. **Preserve boundaries:** walker source-reference stays outside `rebuild/`;
   do not claim parity-complete reconstruct; Home native-focus remains unaccepted
   until a separate native run; no release/tag from this slice.
5. **AYA / full corpus export** remains desirable but is **not** the primary
   executable item of this slice while legacy native extractor DLLs / VS C++
   targets remain blocked (MSB4278). If that blocker clears, record
   `ADVANCEMENT` and may supersede item 2 only with human direction.

No release or tag is authorized by this slice.

## Validation hints

- Hygiene/tooling: focused Python tests for the runner/closeout strip; no live
  game required for unit proof.
- Jet measurement: smallest live gate that proves the contract; name skipped
  gates in the handoff. Run .NET builds/tests serially.
- After Core change: `npm run test:rebuild` (not whole-repo release suites).
- Boundary: `npm run test:hard-payload-safety` before push if paths near
  payload edges change.
- Never mutate installed Steam / original `BEA.exe`.

## Current Slice Progress - 2026-07-14 (housekeeping)

- Freed ~8.6 GB under ignored `local-proofs/wt/` by deleting full-profile pair
  trees `p18`–`p27` and playback roots; retained `p27-compact` (~0.3 MB) plus
  local `RETENTION.md`.
- Public walker contract and Core mapping remain on main at `5b5c7efb`.
- Next worker should start at Current Slice items 1–2 above.
