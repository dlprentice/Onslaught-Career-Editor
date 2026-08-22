# Execution Program

Status: active — the work-queue ledger for the maintainer's standing program
Last updated: 2026-08-21
Summary: what the current program has completed, what is next, and the gate
that completes each item. This file owns **queue state and receipts only** —
it never restates campaign counts, capability claims, validation choices, or
authority pins; each item names the owner that holds its truth.

## How to work this file

- One primary owner works it **serially** in gate order; items P3+ may be
  reordered by the maintainer, P1 before P2 may not (P2's snapshot merge
  after P1's ledger-only cut avoids campaign re-grounding churn).
- An item is **done only when its named gate produced its receipt** — a
  commit, a verifier exit, or a measured repin recorded here with a date.
  Substantial effort, a plan, or a green unrelated suite is not completion.
- Append receipts; never delete history. Superseded decisions are marked
  `SUPERSEDED` with the displacing receipt, not removed.
- Nothing in an item's execution weakens a fail-closed gate. Abort states go
  to `-superseded-` directories or marked rows, never silent rewrites.
- This is a governance ledger under the maintainer's standing goal, not a
  session handoff: session detail lives in git history and
  `developer_state.json` dated keys.

## Completed

### P0 — Integration spine (2026-08-21)

Doc-debt resolution (all seven stale authority statements, `test:docs`
clean), the two real unmerged works landed (`wt/t_0bace7cd` Pulse Cannon
ReadyToCharge + Charged-2; `onslaught/t_7d9a828d` FEMessBox/loading-bar),
branch/stash consolidation to `wt/bea-ghidra` only (bundle receipt
`local-lab/branch-archive-20260821/`, SHA-256 `79c6a544…`), and both known
Core failures resolved with measured causes, not re-fits: the Blaster
observable's ±2 mm reconstruction band (commit `87498824`) and the chain
tick pin via tick-pin-only bisect, boundary `e633b511` (commit `916a67d3`,
receipts `local-lab/chain-tick-bisect-20260821/`). Core measured 862/1/863
then 5/5 on the owning class filter. Receipt range:
`a8de28f3..916a67d3` (pushed).

## Next

### P1 — Campaign Generation 32: bulk reseat of the sealed static receipts

Admit the 7,945 `SEALED_STATIC_RECEIPT` rows of
`reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
into the campaign ledger in ONE generation, per the runbook at
`local-lab/gen32-reseat-prep-20260821/README.md` and the Gen 31 precedent
(`tools/build_generation31_authority.py` + its BUILDER-SPEC). Gate, in
order:

1. Literal-pin Generation 31 carry bridge in `tools/re_campaign.py`
   (precedent commit `a0a3987b`), committed **separately and first**, with
   bridge tests in `tools/re_campaign_tests.py`; the current pinned verify
   command in `developer_state.json` → `current_re_authority.verify` must
   still print `CAMPAIGN_VERIFIED` after the bridge lands. (Negative
   control already observed 2026-08-21: the bootstrap fails closed on a
   wrong pin.)

   > **AMENDMENT 2026-08-21 (measured before any P1 write).** The pinned
   > replay is **not green today and was not green before this program
   > started**: the bootstrap fails closed at Generation 24's projected
   > replay because the projection's current-source pin for
   > `SimulationTests.cs` (`bbb31414…`, as of the Aug-17 Gen 31 cut) was
   > legitimately moved by main `4be6931a` (Aug 19) and again by the
   > P0 pulse merge. See `developer_state.json` →
   > `_P1_PRECONDITION_FINDING_20260821` for the measured history. The
   > projection is working as designed — moved pinned sources force a
   > re-cut — so Generation 32 additionally refreshes the projection pins
   > to cut-time identities with a documented Aug-17→cut relationship.
   > Bridge-commit acceptance is therefore: bridge tests green AND the
   > bootstrap's failure remains exactly the recorded precondition failure,
   > with no new failure mode.
   >
   > **EXECUTION STATE 2026-08-21 (handoff).** Step 1's bridge is LANDED at
   > `be57e985`: `_verify_generation31_campaign_carry` admits the parent on
   > its sealed literal-pinned authority **without** re-running the frozen
   > chain (stamp `LITERAL_PINNED_SEALED_AUTHORITY_GENERATION31_NO_REPLAY`),
   > because the sealed chain's Gen-24 projection `--check-current` anchor
   > cannot be satisfied against legitimately moved sources. Consequence
   > adopted: a Generation 32 full replay never reaches the projection, so
   > **no projection refresh is needed** — the stale anchor retires with the
   > Gen-31 chain, and the new authority's verify command replaces the
   > broken Gen-31 command at repin. Pins were written from measured on-disk
   > hashes (hand transcription was caught producing mangled SHAs — always
   > derive pins programmatically). Before the builder lands: the full
   > `tools/re_campaign_tests.py` module must complete once (interrupted at
   > handoff; the only expected failure is the documented Gen-30 full-replay
   > precondition error). Continuation detail lives in
   > `local-lab/gen32-reseat-prep-20260821/README.md`.
2. Bespoke `build_generation32_authority.py`: per-row gate = the 53
   receipt-file SHA-256 checks; grade movement computed from the live Gen 31
   ledger (the TSV's `gradeBefore` is known-drifted); zero collateral
   outside the named rows; the closure TSV stays byte-identical
   (`cfe90af3…`); dry-run against a temp parent copy before any cut.
3. Canonical + replica cuts; frozen-bootstrap full replays print
   `CAMPAIGN_VERIFIED` with **freshly measured** pins (never the builder's
   own report); eight-ledger + reducer-file determinism; the three
   closure-reading proof tools (`re_cround_move_runtime.py`,
   `re_cround_handle_event_runtime.py`, `re_cexplosion_hit_runtime.py`)
   re-verified; campaign test classes serial and backgrounded.
4. `current_re_authority` repinned from on-disk truth (expect OPAQUE ~143,
   C1 ~8,176, adjudications ~13,843, `nextValidGeneration` 33 — measure at
   cut); scoreboard repinned; authority receipt emitted.

## Queued

### P2 — `wt/bea-ghidra` promotion (db.18632/33) through the full gate

The last unmerged branch. Full
[`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
ceremony (identity → backup → isolated scratch → dry-run → apply → readback
→ tracked refresh on byte equality), including the reviewer GO on the six
CMissile+CRound dual-owner SET_NAME rows. Operator authorization to proceed
through the gate was given by the maintainer on 2026-08-21 (standing goal);
the reviewer GO is still required before any live write. After merge:
resolve the db.18627/db.18633 documentation lag in
[`GOAL.md`](GOAL.md)/[`RE-INDEX.md`](reverse-engineering/RE-INDEX.md) and
`latestLiveGhidraState`.

### P3 — `developer_state.json` split

Extract the `_HERMES_SLICE_*` block and superseded mega-blocks into the
existing per-function note lane or dated local-lab reports (move, never
delete; the file's own `_maintenance` key mandates this). Gate: JSON valid,
`npm run test:docs` clean, every repointed reference re-resolved, and the
file's size/key-count reduction measured and recorded here.

### P4 — Batch function-triage packet exporter

One headless Ghidra run emits per-function packets (decompile, xrefs,
strings, RTTI/vtable links, tags, campaign grade, coverage) for an input VA
list — built from the existing Export* scripts. Gate: one invocation over a
named VA list produces complete packets; documented in
[`tools/README.md`](tools/README.md); consumed by at least one RE work item.

### P5 — TTD trace index / query root

A per-trace index over the retained 66-trace corpus so offline questions
stop spawning fresh cdb sessions. Gate: index build completes over the
corpus and answers one preregistered cross-trace question that today
requires a fresh `ttd_query.ps1` session.

### P6 — Campaign bookkeeping relief

Batch-close the ~2,600 already-triaged-out questions as terminal with their
existing verdicts; decouple campaign generations from structural Ghidra
promotions (re-ground only when a semantic grade moves); record both
policies in the campaign owner docs so the graded frontier — not artifact
counts — is the visible progress metric. Gate: a generation cut closing the
triaged-out rows with zero semantic movement, plus the policy recorded.

### P7 — Rebuild world-110 generalization

Convert the Level-100-shaped reconstruction into a level-data-driven one at
the second world: materializer extended to the world-110 archive, VM
admission widened, definition-set type generalized, campaign-flow tests for
100→110. Gate: PARITY rows for the new contracts and a green focused suite;
[`rebuild/README.md`](rebuild/README.md) "Current truth" updated.

### P8 — Human-input replay tapes

Record a real play session into a replayable `CommandTape`; replay runs
deterministically twice under `--expect`. Gate: one recorded session's tape
double-run green; the recording procedure documented under `rebuild/tools/`.

### P9 — Ferry sweep fixture split

Move the 40-run `Level100FerrySweepFixture` out of the default suite path
(retained as an explicit sweep command). Gate: default Core suite time
measured before/after; full sweep still available; suite re-measured and
[`VALIDATION.md`](VALIDATION.md) row updated.

### P10 — WinUI release pass

Cut the accumulated `## Unreleased` changelog into a versioned entry,
regenerate/verify third-party notices, run the
[`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md)
set and the ZIP probe clean. Publication steps remain maintainer-owned per
[`README.RELEASE.md`](README.RELEASE.md).

### P11 — CLI parity for UI-only capabilities

Quiet, community-neutral CLI verbs for the six capabilities reachable only
through the GUI today (cheats, media, lore, asset library, advanced save
editing, trainer control beyond `music`). Gate: per-verb CLI tests, CLI.md
updated, and the shipped/public copy stays free of internal process
language (`test:safety` plus a doc grep).

### P12 — `local-lab` disposition audit

Work the 79 GiB local corpus family-by-family per
[`AGENTS.md`](AGENTS.md): manifest + receipts read, tooling/tests/docs/
campaign inputs grepped before any "stale" call, staged via
`tools/lab_quarantine.py`, purged only under space pressure with separate
reason. No bulk deletion, ever. Gate: per-family disposition rows with
stage receipts under `D:\lab-quarantine`.
