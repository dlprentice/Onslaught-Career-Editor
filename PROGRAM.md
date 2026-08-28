# Execution Program

Status: active — the work-queue ledger for the maintainer's standing program
Last updated: 2026-08-23
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
   >
   > **EXECUTION STATE 2026-08-22 (run 693).** Builder + wiring + tests are
   > LANDED on main as `01301e95`. Two in-session full-module baseline runs
   > died with their agent sessions and record no count (superseded). The
   > baseline was relaunched DETACHED from agent sessions via Windows Task
   > Scheduler task `OnslaughtGen32Baseline` (start 2026-08-22 02:04 local):
   > raw verbose log goes to
   > `local-lab/gen32-reseat-prep-20260821/unittest-gen32-run-20260822b.log`
   > and the one-line summary (`Ran N tests` / OK or FAILED / exit code) to
   > `local-lab/gen32-reseat-prep-20260821/run-count.txt` when it finishes.
   > No P1 receipt is claimed until that completed count exists.
   >
   > **EXECUTION STATE 2026-08-22 (run 712) — P1 CUT SEQUENCE COMPLETE.**
   > Post-fix gate: full module ran 180 tests
   > (`unittest-gen32-postfix-full.log`): 173 ok + the same 5 documented
   > projection-chain errors + 2 frozen-bootstrap subprocess-timeout flakes
   > that re-ran green standalone (byte-pinned historical reducers the diff
   > cannot touch); accepted as the baseline failure family plus named
   > load flakes. Fix layer landed `fd6d8145`: multi-owner sibling carry
   > reattachment (`_reattach_multiowner_sibling_contracts`) + Gen32
   > evidence refs as measured `path#sha256=…` tokens + zero UNSCORED
   > adjudication rows (Gen-11 precedent). Dry-run green with zero new
   > blockers (`local-lab/gen32-dryrun-20260822`). Canonical cut
   > `generation-32-current-8329-db18625-v1` READY `08ed8964…`
   > (9,539,597 B) and replica `…-replica-v1` READY `e8230547…`, reducer
   > `4c465010…` in both; all EIGHT ledgers byte-identical across the two
   > cuts and the two READYs differ only in generatedAtUtc/lastWriteUtc
   > wall-clock fields the frozen replay normalizes
   > (`gen32-ready-determinism-resolution-20260822.log`). Falsifiers:
   > canonical and replica frozen-bootstrap full replays printed
   > `CAMPAIGN_VERIFIED` exit 0 against freshly MEASURED pins
   > (`falsifier-canonical/replica-20260822.txt`). Sealed closure stayed
   > byte-identical `cfe90af3…`. Proof tools:
   > `re_cexplosion_hit_runtime.py` verifies PASS end-to-end on the current
   > tree; `re_cround_move_runtime.py` / `re_cround_handle_event_runtime.py`
   > refuse exactly the two rebuild-source pins legitimately moved BEFORE
   > the cut (50f871ec Aug-06, 383d5b3e Aug-14; the sealed Aug-12 proofs had
   > stamped then-uncommitted working-tree blobs absent from git history)
   > while every retail-side anchor matches and their forged-evidence
   > selftests pass (6 and 9 attacks;
   > `gen32-proof-tools-20260822.log`) — re-proofing those two tools
   > against the moved owners is successor work, not a Gen32 gate.
   > External authority receipt emitted
   > (`generation-32-current-8329-db18625-authority.ready.json`, 3,612 B,
   > `6238430d…`); `current_re_authority` repinned from on-disk truth:
   > OPAQUE 203 (8088 − 7,885 admitted), functions C1_CANDIDATE_PARTIAL
   > 8,116 + C2 10, adjudications 5,898, REBUILD_READY 16 preserved,
   > nextValidGeneration 33, progressed-carry accounting 26,596/26,596
   > accounted / 0 unaccounted including the reattached multi-owner sibling
   > `C-2b931aa6e8e588c0`; the pinned verify command reproduces
   > `CAMPAIGN_VERIFIED` (`gen32-repin-verify-20260822.log`; it needs the
   > machine Python 3.14 — a 3.11 interpreter fails closed on the frozen
   > reducer's 3.12+ f-string syntax). Pushed to origin/main.
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

**Live-ceremony portion COMPLETED 2026-08-18/19 (historical).** The six-row
CMissile+CRound `name-cohort-round-dual-owner` SET_NAME family carried its own
family-specific reviewer GO (not an earlier or other-family GO), and the live
ceremony ran through the full gate — verified PRE backup → exact measured
identity → isolated rehearsal → family-specific reviewer GO → live apply →
separate-process readback → verified D POST → F twin → tracked refresh on byte
equality. Together with the five preceding shared-framework cohorts
(`varargs-cohort2`, unique-owner, fun-unique-owner,
placeholder-unique-owner, cockpit-dual-owner) this rolled tracked/live
`db.18627` → **`db.18633`** with internal functions held at 8,329. The
canonical owner [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
holds the current pins; this ledger records completion only.

**Remaining P2 work is offline integration/repair only (no further live
ceremony):** carry the corrected candidate (`wt/t_a5329ed3` @ `f17e5716`,
which separates the historical db.18623 reproduction geometry from the
db.18627 live-ceremony authority and fails closed on swapped/stale identities)
onto fresh main, reconcile the two conflicted documentation owners, and repin
the stale state selector. Receipt:

**2026-08-23 — P2 integration receipt (wt/t_57e0ae2f over fresh main
`67d9d610`).** Transplanted the corrected candidate's 18 clean paths blob-exact:
snapshot renames `db.18626→db.18633` / `db.18627→db.18632`, the six new
cohort spec+manifest pairs, the varargs-cohort2 spec correction,
`GhidraApplyCohortManifestLive.java`, `ghidra_cohort_replay.py`, and
`ghidra_cohort_framework_tests.py`. Manually reconciled both merge conflicts:
[`RE-INDEX.md`](reverse-engineering/RE-INDEX.md) keeps its selector-only shape
and gains the db.18633 lineage as historical narrative only;
[`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
takes the candidate's db.18633 payload/history/recovery pins, drops the
obsolete branch-lag prose, and adds one normative ordered ceremony (verified PRE
backup → exact identity → isolated rehearsal → family-specific reviewer GO →
live apply → separate-process readback → verified D POST → optional F twin only
if policy permits → tracked refresh only on byte equality; G: read-only, H:
no write, never rewrite ACLs/ownership). `latestLiveGhidraState` repinned to
db.18633 / 187,501,445 bytes / inventory `df4527a9…`. Gates: docs/JSON/link
checks clean, `git diff --check` clean, 85/85 framework tests with zero skips,
seven manifest pins match, and
`py -3 tools/ghidra_cohort_replay.py --verdict` exits 0 on canonical copied
receipts only — no live or headless Ghidra process, no volume write, no main
merge.

### P3 — `developer_state.json` split

Extract the `_HERMES_SLICE_*` block and superseded mega-blocks into the
existing per-function note lane or dated local-lab reports (move, never
delete; the file's own `_maintenance` key mandates this). Gate: JSON valid,
`npm run test:docs` clean, every repointed reference re-resolved, and the
file's size/key-count reduction measured and recorded here.

**2026-08-23 — P3 batch 1 gate receipt (wt/t_40c27403, `caf42f67` rebased as
`c75127e2`).** Moved exactly 25 `_HERMES_SLICE_20260819_*` keys into their
already-existing owning function notes under
[`reverse-engineering/binary-analysis/functions/`](reverse-engineering/binary-analysis/functions/)
(24 notes already carried every distinctive token — body SHA-256 prefix, byte
count, E8/E9 counts, steward cycle id, landed/task hex ids — checked
programmatically; one gap in `IScript__VFunc_2_00533810.md` was closed by a
verbatim dated append of the slice string before key removal). Surgical span
deletion only: the file is not byte-reproducible by `json.dumps(indent=2)`
(+1,375 B measured drift), so exactly the 25 single-line key entries were
removed with zero insertions and every surviving key verified value-identical.
Measured: `developer_state.json` **939,162 → 928,237 B, raw delta −10,925 B**
(exactly the removed physical-line bytes; the preflight's −9,500 B serialized
simulation was invalid and is superseded by this receipt); **4,575 → 4,550
lines**; **599 → 574 top-level keys**; SHA-256 `43f97e7686eb4c6c…b6199` →
`802bf97c04ba189b…524aa`. History moved, never deleted: all 25 destination
notes preserve their slice's distinctive facts (body SHA-256 prefix, byte
count, E8/E9 counts, steward cycle id, landed/task hex ids); the one note
whose recorded history was incomplete (`IScript__VFunc_2_00533810.md`)
additionally carries the full original slice value appended verbatim under
its dated moved-history heading — the other 24 preserve the required facts
without restating the serialized value word-for-word. Census: zero tracked
exact-key references to any of the 25 keys outside `developer_state.json`
itself, except one deliberate residual — that same mandated moved-history
heading names `_HERMES_SLICE_20260819_533810` inside its own destination
note.
Remaining `_HERMES_SLICE_*`: 492 keys across later batches;
`current_re_authority`, `_RECURSIVE_RE_CAMPAIGN_2026_08_02`, `goal_status`,
and every other key untouched. Gates: JSON valid at 574 keys;
`git grep -F` finds zero tracked hits for 24 of the 25 keys; for
`_HERMES_SLICE_20260819_533810` it returns three raw hits — this receipt's
own two prose mentions (the census sentence above and this gate summary)
plus the single substantive deliberate residual, the moved-history heading
inside `IScript__VFunc_2_00533810.md`; docs
sub-gates green (doc headers
2,009 files / 0 violations; re-function-doc-names 2,040 assertions DRIFTED=0;
evidence-register header current; current-authority PASS).

### P4 — Batch function-triage packet exporter

One headless Ghidra run emits per-function packets (decompile, xrefs,
strings, RTTI/vtable links, tags, campaign grade, coverage) for an input VA
list — built from the existing Export* scripts. Gate: one invocation over a
named VA list produces complete packets; documented in
[`tools/README.md`](tools/README.md); consumed by at least one RE work item.

**2026-08-22 — P4 gate receipt (wt/bea-p4-packets, `0c4e0e2d` + `27e2e916`, pushed).** One headless Ghidra invocation (`-readOnly -noanalysis`) over `tools/packet-va-cgame-level-flow.txt` (the five tracked CGame level-flow VAs from `ghidra-functions.md`) against the verified D: POST backup `D:\BEA-Ghidra-Backups\2026-08-17-vftable65-post-live` produced 5 complete `bea.re.triage-packet.v1` packets in 13s at `D:\packet-runs\cgame-level-flow-gate` — decompile slices, callers/callees STATIC_DIRECT edges, defined strings with referrers, observed vtable evidence, and campaign grade joined from the closure TSV (manifest records its pinned hash `cfe90af3…`). Body bytes match the published table (1504/208/587/1531/1382); CGame__Update shows exactly its two known callers. A second run reported `SKIP all 5` without launching Ghidra (image-hash incremental). Consumed by an RE work item: a packet run re-verified commit 31138fff's published SetWindVector claims from the same image — `callers: []` (zero direct calls) and the note's exact 94-byte body digest `3cf457a3…40c0d` recomputed from the pristine specimen (the packet's own bodyDigest covers Ghidra's 96-byte body incl. the `c2 0c 00` ret tail; both instruments agree on one specimen). Documented in `tools/README.md` § "Function-triage packets (P4)". Focused gate: `py -3 tools\export_packets_tests.py` (9/9, fake headless, registered in `npm run test:tools` sweep). Live-project refusal by default; every invocation read-only.

### P5 — TTD trace index / query root

A per-trace index over the retained 66-trace corpus so offline questions
stop spawning fresh cdb sessions. Gate: index build completes over the
corpus and answers one preregistered cross-trace question that today
requires a fresh `ttd_query.ps1` session.

**2026-08-23 — P5 gate receipt (wt/t_ad6d1e50, corrected on wt/t_e30c197b).**
The gate closed by extending the canonical family, not replacing it:
`tools/ttd_coverage_index.py` (build + query) and its focused suite consume
the existing read-only receipts in place. Build over `G:\bea-ttd` validated
all **72 receipts** (66 campaign + 2 pilot + 1 pilot-replicate + 3
level521-native takes; the same set the authoritative `exec-coverage-index.tsv`
join was built from), 481,127 range rows, union 803,629 bytes — byte-equal to
the ds-deep stats union, so the two instruments agree on corpus identity.
Receipt-set hash (sorted relpath+sha256 lines):
`926b6ec66befc8e0060d49efc6c00d485ab6a6ed563b55c79d86bf829b7d5c39`. Two
consecutive builds were byte-identical (file SHA-256 `925a6dc9…3eef`,
canonical content binding `6931b976…282a`). The build is fail-closed on
malformed, duplicate, out-of-domain, or self-disagreeing rows; unreadable
subtrees fail rather than disappearing; full module identity, gap accounting,
and required hit/miss controls are bound across receipts. Quarantined-counter
and timer-stopped trace classes are recorded verbatim rather than silently
dropped or amnestied. Independent review RED on the original tip (`7408b7d2`)
proved deep readback still accepted a re-bound Windows drive-absolute receipt
(`C:/evil/coverage.jsonl`) and a wrong-basename receipt
(`level-clean/not-coverage.txt`) after both hashes were honestly recomputed;
the correction adds canonical per-trace receipt-path validation (relative,
forward-slash, normalized, no drive/UNC/rooted/parent syntax, basename must
be `coverage.jsonl`) enforced before membership at readback and at build, with
re-bound semantic readback tests reproducing both RED indexes exactly and a
shape matrix over the accepted/rejected path forms. All corpus hashes,
memberships, and the preregistered answer are unchanged by the correction —
only the fail-closed surface moved.

Preregistered query answered from receipts only (no cdb session): of the nine
FireLock body PCs (`0x00407060…0x00407134`, note `CBattleEngine__FireLock.md`),
only the entry `0x00407060` appears in any retained trace — the three played
level521-native takes — and the other eight appear nowhere; ApplyDamage
must-hit control `0x004f9a90` hit 21 traces; current-time BSS must-miss
control `0x00672fd0` hit none. Query-input SHA-256 (ordered address list plus
both controls) is
`35867093cf21ab89a1bc2946e8aaeb5c8a06b925ea3d5b4a6accd2103edaa9bd`. A
raw-JSON cross-walk reproduced every membership. This is a per-byte coverage
answer about retained traces, not a contract-grade change. Focused gate:
`py -3 tools\ttd_coverage_index_tests.py` (53/53 after the canonical-path
correction), registered in `npm run test:tools`; documented in
[`tools/README.md`](tools/README.md) § wholesale instruments.

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
stage receipts under `H:\graveyard\lab-quarantine`.
