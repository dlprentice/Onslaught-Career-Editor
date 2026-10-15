# Runtime-witness corpus merge — DeepSeek Extended findings relocated and queued

Status: active — merged routing record; the witness tables themselves remain
untracked local evidence.
Last updated: 2026-08-18.
Evidence: MEASURED — per-file SHA-256-verified relocation of the DeepSeek
Extended workspace and its machine-built witness tables. Every row below is a
pointer to a named witness file; every claim in those files must be reproduced
from its cited byte/trace source before promotion.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Summary: the `F:\DS DEEP Review Extended` workspace (DeepSeek's read-only
investigation of the G:\ TTD corpus) now lives inside the repository under
gitignored `local-lab\ds-deep-review-extended\`, byte-verified. The `F:\`
paths in the bullets below are **historical origins**; they no longer
exist on disk as of 2026-08-17. This page
records which of its findings are consumed and which are queued as second
witnesses for pending promotions. It adds no grades and no Ghidra mutation on
its own authority.

## Relocation and verification

- `F:\DS DEEP Review Extended` → `local-lab\ds-deep-review-extended\`: 95 files,
  18,652,051 bytes, verified per-file byte-exact (zero content differences).
- `F:\rows.tsv` → `local-lab\ds-deep-review-extended\rows.tsv`: 7,833 bytes,
  SHA-256 `7530c0e52491e5eb328087cf05e20f772e6e2ae3fdee2ed2cd8c2d194c0d1b47`,
  byte-exact on both sides.
- The frozen drop `F:\DS DEEP Review` → `local-lab\ds-deep-review\`; verification
  receipt in `local-lab\migration-2026-08-17\`.
- Ground rules from the workspace's own README, carried here: everything in it
  is a lead, never authority — reproduce before promote.

## Falsifier settlements (witnesses in `data\`)

Recorded from `data\lane2-execution-report.md`,
`data\falsifier-batch2-results.md`, `data\zlib-export-dump.md`, and
`02-open-items-crossref.md`; primary-address execution counts come from the
machine join over the 72-trace coverage index (`data\exec-coverage-index.tsv`,
union 803,629 bytes):

- `0x00401b50` — the CActor prefix holds; observed receivers are `CCannon` /
  `CGroundVehicle` (executes in 61 traces).
- `0x0048c3b0` — receiver is `CInfluenceNode` at all observed sites; pending
  name `CInfluenceNode__CalculateInfluence` (468 calls across 3 sites).
- `0x0052ff20` — `InitBuiltins`: the registry is populated at startup (executes
  in 69/72 traces).
- `0x005363e0` — slot-21 name+fnptr proven `GetPlayer` (executes in 12 traces);
  its falsifier is live-interactive-defective and should be terminal'd carrying
  the slot-21 witness.
- `0x0043a860` and `0x0052db60` — static-only falsifiers, defective; both
  statically resolved (type enum 6=`CExplosionStatement`,
  7=`CComponentStatement` for the former).
- `0x004de0c0` / `0x004de2d0` — the three-translation-value hypothesis is
  FALSIFIED; the observed values are uninitialized-stack residue — recommend a
  behavior-descriptive rename (both execute in 69/72 traces).
- `0x00663070` — unreachable (a data address); falsifier to rewrite.
- External zlib: c4 ordinal 63 = `uncompress` (`0x27d8`), c5 ordinal 9 =
  `compress` (`0x1254`); zlib.dll loads at a fixed base in all logged sessions.
- External DSOUND b5 — TERMINAL; the premise is falsified. Retail loads host
  `C:\WINDOWS\SYSTEM32\DSOUND.dll` (ASLR), never a shipped DSOUND.dll; the name
  is `DirectSoundEnumerateA`.

## Boundary cohort runtime corroboration

`data\boundary-coverage.tsv` (77 rows) joins the FLAGGED(BOUNDARY) rows against
runtime execution of their claimed extension bytes: 13 EXTENSION_EXECUTES, 16
BODY_ONLY, 47 BODY_ALSO_UNEXERCISED, 1 NO_DECLARED_RANGE. The 13 positives
include `0x004160b0` (28 traces), `0x00417190` (51), `0x004ac4a0` (23), and
`0x0048a570` (all 3 level521 combat takes) — post-live receipts for the landed
41-row ceremony. Absence is weak evidence: 47/76 bodies never execute in the
retained corpus, so only the 13 positives count as corroboration.

## Name anchors

`data\name-anchor-join.tsv` (97 runtime name anchors): 48 exact ledger
corroborations, 14 prefix matches, 28 conflicts (mostly `IScript__*` prefix
omissions; one substantive: `0x0052ea40` trace `CAsmInstruction__ExecuteCall`
vs ledger `CInstructionOP_CALL__ExecuteCall`), and 7 LEDGER_MISSING including
`CWorld__LoadWorldFile` at `0x0050b720` — a real name absent from the
master-ledger. `data\name-retriage.tsv` (509 rows) and
`data\pre-triage-comment-xref-other.tsv` (327 rows) are the second-opinion
tables for the pending name and comment work.

## Queued promotions this corpus backs

The runtime-witnessed name corrections (`0x0048c3b0`, `0x0052ff20`,
`0x005363e0`, `0x0043a860`, `0x004398f0`) and the falsifier close-outs above are
frontier items 5 and 7 in `GOAL.md`; the witness rows live in
`local-lab\ds-deep-review-extended\data\` and are cited per-row when the
ceremonies are authored. The `g_D3DDeviceIndex` name at `0x0066061c` is REFUTED
by these witnesses (packed display-mode selector, bits 0-15 / 16-30 / flag 31)
and must not be promoted.
