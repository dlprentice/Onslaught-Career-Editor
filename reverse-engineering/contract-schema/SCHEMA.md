# Contract status overlay — seven states over the existing evidence

Status: active — overlay model for contract coverage measurement
Last updated: 2026-08-22
Summary: maps a seven-state contract-status vocabulary onto what the existing
function notes, the evidence register, and the campaign TSV manifests already
express, so coverage becomes measurable without rewriting a single note.
Evidence: MEASURED — every marker pattern below was measured against the live
corpus on 2026-08-22 (`grep` distributions recorded in the sections that use
them): 427 of 752 note files carry `Evidence: MEASURED`, register evidence
classes total 11,470 across 8,329 rows, and 44 name-withdrawal lines / 58
implementation gates were counted by the shipped scanner.

## Why an overlay

The repository already holds its ground truth in three places: the per-function
notes under `reverse-engineering/binary-analysis/functions/**` (canonical,
owned by their named-system lanes), the tracked evidence-register projection
(`reverse-engineering/EVIDENCE-REGISTER.tsv`, one row per function in the
current_re_authority generation), and the dated TSV manifests beside it
(promotion cohorts, witness tables, patch census). None of those formats
changes because of this document.

What was missing is a single measurable question: **for each of the pinned
functions and contracts, how far has the evidence actually gotten?** The
overlay answers it mechanically. A scanner (`tools/contract_coverage.py`) reads
the three corpora, applies the rules below — grep-able markers, grade columns,
witness counts; no LLM calls — and writes
`reverse-engineering/contract-schema/coverage.json`.

Non-negotiables, inherited from the task card:

- Overlay only. No note under `functions/**` is rewritten to fit this model.
- The denominator is the pinned authority: 8,329 functions / 14,365 contracts
  (`developer_state.json` → `current_re_authority.counts`). Any other count in
  older prose is ignored by the scanner.
- A function whose notes carry no markers is classified honestly as SKELETON.
  The classifier never invents progress; it prefers under-classification.

## The seven statuses

Order matters: it is the precedence the scanner applies, highest first. A
function takes the highest status any mechanical rule fires on, except that
DISPUTED/STALE/BLOCKED record contest or constraint rather than progress and
therefore outrank everything.

| Status | Meaning | What our evidence looks like when it fires |
| --- | --- | --- |
| STALE | The note itself withdraws the subject: the page now redirects or declares its claims replaced. | A note whose own `Status:` header reads superseded/redirect (e.g. a renamed-owner redirect page). |
| DISPUTED | A claim about this function was contested and the contest is part of the record. | Withdrawn-filename addenda: the 2026-07-28 name-correction tables quoting superseded labels; "proven false and withdrawn"; interpretation "withdrawn pending a fresh body-level semantic review". This is DISPUTED *history*, not necessarily a dead end — the note usually carries the corrected successor. |
| BLOCKED | Acting on the contract is explicitly gated on an external condition. | Notes that forbid implementing or widening until another lane resolves: "do not implement Core from this RE root", "remains blocked", "do not implement from this mapping until that lane names the arm". Narrow markers only — scope discipline phrased as "did not X" is not a block. |
| VERIFIED | The contract has two independent witnesses or went through a promotion/adjudication gate. | Register evidence classes ending in PROMOTED (maintainer Ghidra boundary cohort ceremonies: backup, dry/apply/readback, tracked refresh), SURVIVED (independent-refutation and probe-refuter adjudications), or REPLICATED (TTD write replication with controls). Also: two distinct witness kinds — a MEASURED byte-read note *and* a manifest witness row, or either *and* controlled-runtime register evidence. |
| REVIEW_READY | The contract is fully written down and bounded, awaiting its promotion gate. | Register grade C1_CANDIDATE_PARTIAL or C2_BOUNDED_RUNTIME; or a MEASURED byte-read note that additionally carries second-witness language (twin re-read, independently reproduced, cross-build pair) without a formal promotion receipt. |
| PROVISIONAL | At least one measured fact is pinned, but the contract is not complete. | The per-function envelope notes: `Evidence: MEASURED`, body SHA-256, ret/prologue bytes, cheapest falsifier — PE-envelope contracts that stop short of full field-level semantics (grade PARTIAL_CONTRACT mappings live here). |
| SKELETON | Identity only: the function is accounted for but no measured contract exists here. | Everything else, by construction: FUN_* rows with analyst metadata only; wave read-back notes that save names/signatures/comments ("Saved/read-back") without behavioral claims; envelope-only mentions; untouched register OPAQUE rows. This is expected to be the largest bucket and saying so precisely is the point of the dashboard. |

The mapping onto the card's shorthand: envelope notes land in SKELETON or
PROVISIONAL depending on whether they pin bytes; MEASURED byte contracts are
PROVISIONAL or better; two-witness promoted rows are VERIFIED;
withdrawn-filename addenda are DISPUTED history; redirect pages are STALE;
externally-gated work is BLOCKED.

## Evidence classes (existing vocabulary, unchanged)

Each classified function also records which *classes* of evidence back it.
These are the repository's own terms, detected mechanically:

| Class | Detected from |
| --- | --- |
| `byte-read` | Note `Evidence: MEASURED` with body-byte pins; register `*_PE`/static-proof campaign classes. |
| `ttd-capture` | Register `TTD_*` evidence classes (call entry, data writes, zero-event controls, gap-free chains). |
| `pinned-source-line` | Register `SOURCE_CORRELATED_*` / `LOCKHIT_STATIC_SOURCE_JOIN`; notes citing `references/Onslaught/<file>.cpp:<line>`. |
| `controlled-runtime` | Register `RUNTIME_BOUNDED`, `RUNTIME_*REPLICATED`, `*_REFUTER_SURVIVED`, `INDEPENDENT_REFUTATION_SURVIVED`; notes describing copied-runtime or controlled-capture observations. |
| `ghidra-readback` | Wave read-back tables (`Saved/read-back`), boundary/name promotion receipts. |
| `name-only` | `ANALYST_METADATA_ONLY` with nothing above it — identity without contract. |

Classes are additive facts; the status is the decision. A VERIFIED row usually
carries two or more classes; a SKELETON row usually carries `name-only`.

## Mechanical classification procedure

Inputs, in read order:

1. **Register** — `reverse-engineering/EVIDENCE-REGISTER.tsv` (comment-headed
   TSV; skip `#` lines). Columns used: `entryVa`, `name`, `grade`,
   `resolution`, `contractState`, `evidence` (semicolon-joined classes).
   Every one of the 8,329 rows gets exactly one status out.
2. **Notes** — every `*.md` under `reverse-engineering/binary-analysis/functions/`.
   A note *covers* a register function when the file stem equals the register
   name, or the register name appears as a token in the note body. From each
   covered note the scanner lifts:
   - the header `Evidence:` grade (MEASURED ⇒ `byte-read` floor);
   - second-witness language (`twin`, `two-witness`, `independently re-read`,
     `independently reproduced`, `cross-build`);
   - dispute lines (any line matching withdrawn/superseded/refuted/
     proven false/demoted — names tokens on that line become DISPUTED);
   - block lines (do-not-implement / remains-blocked patterns — names on the
     line become BLOCKED);
   - note-level STALE (`Status:` header containing superseded/redirect, applied
     to the note's subject function only, i.e. the file stem).
3. **Manifests** — dated TSVs under `reverse-engineering/binary-analysis/`
   plus `patches/patch-surface-rows.tsv` whose header carries a witness-shaped
   column (`exactness`, `confidence` with MEASURED values, `byteProof`,
   `independentReDerivation`). A manifest row witnessing register name/liveName
   contributes one `MANIFEST_WITNESS` kind and a `MEASURED` confidence
   contributes toward PROVISIONAL.

Decision, per register row, first match wins:

```
STALE        note-subject Status: superseded/redirect
DISPUTED     name on a note dispute line
BLOCKED      name on a note block line
VERIFIED     >=2 distinct witness kinds
             OR register evidence class ~ /(PROMOTED|SURVIVED|REPLICATED)$/
REVIEW_READY register grade in {C1_CANDIDATE_PARTIAL, C2_BOUNDED_RUNTIME}
             OR note MEASURED + second-witness language
PROVISIONAL  note MEASURED covers the name
SKELETON     otherwise (honest default)
```

Witness kinds counted: `NOTE_MEASURED`, `MANIFEST_WITNESS`,
`REGISTER_CONTROLLED_RUNTIME` (any register evidence class in the
controlled-runtime family). Two *distinct* kinds ⇒ VERIFIED; the same kind
twice never promotes.

## Output

`reverse-engineering/contract-schema/coverage.json`, schema
`bea.re.contract-coverage.v1`: denominator block echoed from the pinned
authority, per-status counts, per-class counts, and a per-function array
(`va`, `name`, `status`, `evidenceClasses`, `witnessKinds`, `notes`, `flags`).
The scanner exits non-zero if the register is missing, the row count does not
equal the pinned function denominator, or a note parse raises — it fails closed
rather than publishing a partial dashboard.

## Limits, stated plainly

- Token-based note coverage can over-attribute a folder note's claims to every
  function it names. The dispute/block line rules are deliberately line-scoped
  for this reason, and the per-function `notes` array records exactly which
  file fired so any single row can be audited by hand.
- Status measures *evidence held*, not truth. A DISPUTED row often contains the
  correction; a VERIFIED row is only as good as the gates its promotion ran.
- The overlay never writes upstream formats. Regenerating coverage.json is
  idempotent and side-effect-free.
