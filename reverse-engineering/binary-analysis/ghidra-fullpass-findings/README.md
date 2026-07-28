# Ghidra fullpass findings

Status: closed record — the W001–W018 wave reviews ran on 2026-07-23/24 and are
not being re-run. Read this tree as a dated discovery record, **not** as a live
name reference.
Last updated: 2026-07-28
Summary: the primary and adversarial review notes for the read-only quality
expedition of 2026-07-23, covering the complete 6,411-function inventory of that
day's headless export across waves W001–W018. It answers "what did agents
conclude in the wave?" — not "what does the live database say now", and not
"what was written to it".

Read-only quality expedition over the maintainer Ghidra DB copied from
`C:\Users\david\Ghidra\Projects` into this worktree's disposable
`local-lab/ghidra-fullpass-2026-07-23/project-ro`. The expedition's branch was
merged to `main` on 2026-07-25 and its worktree no longer exists; see
[`../ghidra-fullpass-expedition-handoff-2026-07-25.md`](../ghidra-fullpass-expedition-handoff-2026-07-25.md),
which is itself marked HISTORIC.

## Names here are as of 2026-07-23

**Added 2026-07-28.** Every `### 0xADDR Name` heading — and every name,
signature, comment and tag quoted anywhere in this tree — is **as of the
2026-07-23 headless export**. None of it is a live reading. Addresses are stable
and are the join key; **names are not.**

MEASURED 2026-07-28, by joining all 12,822 shard headings (6,411 distinct
addresses, each appearing once in a primary shard and once in its adversarial
pair) against the 2026-07-27 live readback
`local-lab/re-ledger/naming-wave-2026-07-27/inv-LIVE2-functions.tsv` (7,555 rows,
gitignored):

| Measurement | Count |
| --- | --- |
| Shard addresses absent from the live database | **0** |
| Shard addresses whose live name differs from the name quoted here | **370** |
| …of those, graded `ok` by the primary **and** `confirm` by the adversary | **247** |

So 247 addresses in this tree carry the strongest endorsement this review can
issue — dual-cleared — attached to a name string that no longer exists anywhere.
For example, `CUnit__UpdateMotionAndTrailEffects` is live as
`CAirUnit__UpdateMotionAndTrailEffects`. **Resolve any name in this tree against
the live database before relying on it.**

Two of the 370 are not ageing. They are **withdrawals of names proven false**,
and each carries its own dated supersede block in both its primary and its
adversarial shard:

| Address | Name graded here | Live | Withdrawal |
| --- | --- | --- | --- |
| `0x0048c300` | `CInfluenceMap__dtor` — graded `ok`, `confirm` | `DestructorBody_0048c300` | [`../name-grading-ledger-2026-07-26.md`](../name-grading-ledger-2026-07-26.md) |
| `0x005386d0` | `CScriptEventNB__Destructor` — graded `possible_missing_neighbor`, `confirm` | `DestructorBody_005386d0` | [`../name-grading-ledger-2026-07-27-demotion2.md`](../name-grading-ledger-2026-07-27-demotion2.md) |

**Which rename moved which address is only partly settled.** Of the 370, 345 are
accounted for by a named rename or demotion map under `local-lab/re-ledger/`
(330 of the 332 SAFE_REPREFIX renames of 2026-07-25; 13 from
`rename-wave13-2026-07-26`; 13 from `rename-wave14-2026-07-26`; and the two
demotions above). The remaining **25 are UNKNOWN** — no map in that directory
accounts for them, and no cause is asserted for them here. Also measured: the
533-name wave of 2026-07-27 accounts for **none** of the 370, because not one of
its 533 addresses is in this corpus at all. Re-running the attribution against
the full mutation logs under `local-lab/re-ledger/mutation-waves-2026-07-27/`
would settle the residual.

## Coverage

**Added 2026-07-28.** The waves reviewed **6,411 functions** — the complete
function inventory of the 2026-07-23 export — partitioned 25 to a shard: 15
shards per wave for W001–W017 (375 each), and 2 shards for W018 (25 + 11 = 36).
The 6,411 is reached three independent ways: the sum of `- Function count:`
across the 257 primary shards, the sum of the 18 wave-closeout tables, and the
union of the 18 export `metadata.tsv` files. The same inventory is established
in tracked evidence by
[`../ghidra-full-reaudit-closeout-2026-07-13.md`](../ghidra-full-reaudit-closeout-2026-07-13.md).

The live database has since grown past that inventory. At the 2026-07-27
readback it held 7,555 functions: all 6,411 reviewed here still exist, and
**1,144 further functions — 15.1% of the live database — have never been through
any wave.** A reader planning the next review pass should take the unreviewed set
as the set difference against a *fresh* inventory; 7,555 is a copied count from a
dated readback and will move again. Where those 1,144 came from is recorded in
the lab ledgers and is not re-derived here; what is measured is that none of the
533 addresses named in the 2026-07-27 wave belongs to this corpus.

## Authority (do not confuse with the correction lab)

| This tree | Correction expedition lab |
| --- | --- |
| **Discovery notes** — primary/adversarial wave reviews (W001–W018) | **`local-lab/ghidra-fullpass-2026-07-23/`** (gitignored) — queues, plans, dual QC, apply logs, ops |
| Answers: “what did agents conclude in the wave?” | Answers: “what was dual-CLEARED and written to the live DB?” |

- Full map: `local-lab/ghidra-fullpass-2026-07-23/corrections/apply/_AUTHORITY_LAB_VS_RE.md`
- Live working DB: `C:\Users\david\Ghidra\Projects`
- Tracked Ghidra snapshot (may lag live):
  [`../../ghidra/README.md`](../../ghidra/README.md)
- RE front door: [`../../RE-INDEX.md`](../../RE-INDEX.md)

A path like `W001/primary/A01.md` is **not** proof the live database was mutated.
Mutation evidence lives under the lab’s `corrections/apply/` and apply logs.

## Layout

- `WNNN/primary/AXX.md` — primary review for one shard
- `WNNN/adversarial/BXX.md` — adversarial check of the matching primary shard
- `WNNN/wave-closeout.md` — the wave's two rollup tables, written after the
  adversarial phase: the **pre-adversarial** primary verdict totals, and the
  adversarial disposition totals. **The two are not reconciled into a single
  post-adversarial figure.** Corrected 2026-07-28: this line previously read
  "wave rollup after adversarial", which invited the primary `ok` count to be
  read as the wave's outcome. It is not — across all 18 waves 709 of the 6,411
  addresses drew a non-`confirm` disposition (121 dispute, 508 upgrade_severity,
  80 downgrade), and none of that is reflected in any primary-side total. Each
  closeout now says so in its own `## Notes`.

## Shard header contract

Every shard carries `- Phase:`, `- Function count:` and `- Reviewed at:`, and
those three are gated on all 514 shards by
[`../../../tools/doc_header_check.py`](../../../tools/doc_header_check.py) under
the `WAVE-SHARD` class of
[`../../../DOCUMENTATION.md`](../../../DOCUMENTATION.md). Two further fields —
`- Export root:`, and on an adversarial shard a pointer to the primary it checks
— are required only of shards reviewed on or after 2026-07-28, because this
expedition's shards are not uniform and will not be re-reviewed.

Measured 2026-07-28 across all 514 shards, recorded here so the non-uniformity
does not have to be discovered again:

| Header field | Primary (257) | Adversarial (257) |
| --- | --- | --- |
| `Phase`, `Function count`, `Reviewed at` | 257 | 257 |
| `Export root` | 257 | 150 |
| pointer to the paired primary | n/a | 76 spell it `Primary`, 87 `Paired primary`, 16 carry both, **110 carry neither** |
| `Targets` | 141 | 105 |
| `Prior file` | 81 | 60 |
| `Address range` | 50 | 36 |
| `Agent` | 47 | 51 |
| `Scope` | 38 | 74 |

The 18 `wave-closeout.md` files are uniform on `Closed at` / `Primary shards` /
`Adversarial shards`; as of 2026-07-28 they additionally carry the `Status:` /
`Date:` / `Verdict:` / `Evidence:` header required of their class. None of them
states an export root, a database snapshot or a specimen hash, and none quotes a
retail address.

**UNRESOLVED.** 107 adversarial shards name no export root and 110 name no
paired primary. Backfilling both was considered and **not done**: a backfilled
value would be a reconstruction sitting in the position where a reviewer's own
record belongs, and nothing in the file would say so. What would settle it is a
per-shard check that each shard's addresses lie inside its own wave's
`metadata.tsv`, written back as an explicitly reconstructed field rather than as
an original one.

## Rules

- Documentation only unless a later correction pass is separately authorized.
- Bound claims to static evidence from headless exports (`analyzeHeadless`).
- Prefer propose-only corrections; never invent runtime proof.
- Host Ghidra paths and headless posture:
  [`../../ghidra/README.md`](../../ghidra/README.md).
- If a prior finding file exists, append a dated revision section rather than
  silently overwriting unless the coordinator marks a relaunch replace.
- Quote names with an as-of date, or resolve them live. See
  [Names here are as of 2026-07-23](#names-here-are-as-of-2026-07-23).

## Known limits of this tree

- **Names drift; this tree does not.** The 370 above is a snapshot taken
  2026-07-28 and will grow with every rename. It is not maintained automatically.
- **The compound-verdict separator was never normalised.** 3 of the corpus's
  primary `- Verdict:` lines write a compound verdict with `,` or `;` where the
  rest use ` + `. Splitting those on whitespace invented two verdict categories
  in the W015 and W016 closeouts, corrected in place on 2026-07-28. The shard
  lines themselves were deliberately **left as their authors wrote them** —
  editing dated discovery notes to suit a rollup script is the wrong direction of
  fix. Harden the generator instead.
- **Shard summary tables are secondary to shard bodies.** Two shards' `## Summary`
  tables disagreed with their own `- Verdict:` lines (`W005/primary/A12.md`,
  `W011/primary/A08.md`), corrected in place on 2026-07-28. Where a table and a
  body disagree, the body and the wave closeout are the record.
