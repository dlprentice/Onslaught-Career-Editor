# Contract coverage — first dashboard measurement

Status: active — first full-corpus run of the contract-status overlay
Last updated: 2026-08-22
Summary: the first measured status distribution over all 8,329 pinned
functions — the coverage dashboard baseline this overlay exists to produce.
Evidence: MEASURED — `tools/contract_coverage.py` over the tracked corpus:
8,329 register rows (pinned denominator), 752 note files, 36 manifest TSVs;
scan completes in ~2.5 s. Reproduce with
`py -3 tools/contract_coverage.py`; the machine-readable result is
[coverage.json](coverage.json) (schema `bea.re.contract-coverage.v1`).

## Status distribution (2026-08-22, Generation 31 authority)

Denominator: 8,329 functions / 14,365 contracts
(`developer_state.json` → `current_re_authority.counts`).

| Status | Count | Share |
| --- | ---: | ---: |
| STALE | 0 | 0.0% |
| DISPUTED | 44 | 0.5% |
| BLOCKED | 58 | 0.7% |
| VERIFIED | 591 | 7.1% |
| REVIEW_READY | 436 | 5.2% |
| PROVISIONAL | 1 | 0.0% |
| SKELETON | 7,199 | 86.4% |

## How to read the four numbers that matter

**SKELETON 86.4% is the honest headline and matches the campaign's own
grades.** The pinned authority grades 8,088 of 8,329 functions OPAQUE
(97.1%); the overlay's 7,199 (86.4%) is lower only because it also counts
functions whose notes pin measured bytes without a second witness as
PROVISIONAL/REVIEW_READY rather than OPAQUE. The two views agree on the core
fact: roughly seven in eight functions are accounted for but not contracted.
The card predicted this bucket would dominate; now the size is measured, dated,
and reproducible instead of asserted.

**VERIFIED 591 (7.1%) is promotion-receipt-driven.** Every one of these rows
carries a register evidence class ending PROMOTED / SURVIVED / REPLICATED
(boundary-cohort ceremonies, refuter adjudications, TTD write replication) or
two distinct witness kinds. This is the set of contracts where the repository's
own gates have already spoken.

**REVIEW_READY 436 (5.2%) is the actionable queue.** These are the campaign
C1_CANDIDATE_PARTIAL / C2_BOUNDED_RUNTIME rows — work whose evidence exists
and is bounded but which has not been through a promotion gate. They are the
cheapest next promotions.

**PROVISIONAL 1 is a true statement about note-to-register coverage, not a
scanner bug.** 427 note files carry `Evidence: MEASURED`, but almost every one
of those subjects already carries a C1/C2 grade or a block/dispute marker, so
the envelope note lands in REVIEW_READY/BLOCKED/DISPUTED instead. The single
pure-PROVISIONAL row is a function whose only evidence is a measured byte
envelope with no grade and no gate. The scanner records per-row which notes
fired (`notes[]` in coverage.json), so any of these classifications can be
audited against the canonical file in minutes.

DISPUTED 44 are the 2026-07-28 name-correction withdrawals and later demotions
— contested history carried openly by the notes themselves. BLOCKED 58 are
functions whose own notes forbid implementing from the current RE root until
an owning lane resolves; this is scope discipline made measurable. STALE 0:
the one redirect page in the corpus names its subject correctly, so nothing
classified stale this pass.

## What this dashboard does NOT claim

- It measures **evidence held**, not truth. A VERIFIED row is exactly as good
  as the gate that promoted it.
- The overlay is read-only over the canonical corpora; sibling lanes can move
  any individual classification by editing their own notes. Re-run the tool to
  re-measure; never hand-edit coverage.json.
