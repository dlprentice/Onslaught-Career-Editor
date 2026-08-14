# PC `.text` missing-function boundary preparation

Status: **reviewed preparation only; not admitted to Ghidra**
Date: 2026-08-13
Evidence: MEASURED — exact pristine retail bodies, complete bounded CFGs,
cross-build normalized demo twins, current 8,170-function exclusion, and
independent replay; UNKNOWN — original source symbols, runtime reachability,
semantics beyond the bounded classifications, and rebuild parity.
Verdict: 31 callable-entry boundaries are ready only for a later disposable
scratch-Ghidra admission test; none is currently admitted or named.

Specimen: pristine retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Assembly base: `dfa043f7d6c9c2655d4bcc35dae7984cb7e9753c`; the
landing tip is a later descendant with the same 8,170-function projection.

## Decision

Thirty-one callable-entry boundaries are ready for a later **disposable scratch
Ghidra admission test**, and nothing further. The reviewed immutable input is
[`text-gap-missing-function-boundaries-2026-08-13.tsv`](text-gap-missing-function-boundaries-2026-08-13.tsv).
Every range in that manifest is half-open: `start` is included and
`endExclusive` is not.

The manifest is 14,930 bytes, SHA-256
`afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586`.
It describes 14,049 reachable body bytes plus 294 padding bytes across three
gaps, or 14,343 bytes accounted for exactly. Admission would raise the known
retail lower bound from 8,170 to 8,201 Function entries; 8,201 is not a final
ceiling and is not the current saved count.

This preparation does not create or name a function, does not change a
signature, does not touch a Ghidra project, and does not authorize a live
promotion.

## Current projection correction

The candidate evidence was recovered before the latest 34-row Mission
vocabulary was joined as the current name authority. The current projection is
`ghidra-function-name-table-2026-08-13.tsv`, 8,170 rows / 503,177 bytes /
SHA-256
`d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd`.
The verifier also requires all 34 rows in
`mission-script-registry-new-function-vocabulary-normalization-2026-08-13.tsv`
to resolve to their current names in that projection.

The pre-latest-34 projection retained by the isolated preparation base is
502,854 bytes, SHA-256
`515170759dda2686db408d25296362275f8913f7be42b6f0536b986c591786ee`.
It is explicitly superseded as a current-name authority. A direct old/current
join has the same 8,170-address set and exactly 34 changed rows; all 34 are
name-only changes from each mutation-manifest `expectedPreName` to its
`proposedName`, with body minima and maxima unchanged.

All 31 candidate entries are absent from the current 8,170-function census, so
their current-name value is `NO_CURRENT_FUNCTION`, not a nearby CRT, packed
math, JPEG, or callback label. Their semantic name remains `UNASSIGNED`.
Open-question labels are limited to what is actually dark:

- the CRT-normalized package still lacks original retail symbol spelling and a
  runtime contract;
- the two packed-math queues still lack an exact linked-library partition,
  symbols, and runtime contracts;
- the callback queue still lacks exact selector roles, semantic identities,
  and runtime contracts.

The prior machine-local `candidate-manifest.tsv`, `result.ready.json`, report,
and companion tables remain frozen provenance. They are superseded only as a
pre-latest-34 current-name/dark-question projection; their byte, CFG,
cross-build, reference, and padding evidence is retained unchanged.

## Retained structural evidence

The read-only verifier requires the complete frozen recovery bundle byte for
byte, including its 46,070-byte analyzer
(`3154cf5ac92ad4008f92414f68f299b6c8b1b31bcb90e23307aa4134ea983022`)
and 36,410-byte READY result
(`a3df9d044754981e65eec7f16b0a5dab3b0275f6089a20958798e97873e19a11`).
It retains these independently checked facts:

- 31 pairwise-disjoint candidate CFGs reach approved terminals;
- 14,343 gap bytes partition as 14,049 callable-body bytes and 294 bytes of
  established `INT3`/NOP alignment padding, with no data/table bytes;
- all 31 PC-demo twins have identical relative CFG ranges, return geometry,
  instruction mnemonics, and normalized body bytes;
- the 64 unique jump-table targets in `CF-002` remain
  `SAME_FUNCTION_FRAGMENT`, not 64 extra functions;
- all 31 exact body sets have zero overlap with the current 8,287 exact Ghidra
  body ranges (`body-ranges.tsv`, 1,183,469 bytes, SHA-256
  `6703b759ac18528d61c4ad6f646f0fd6933eaf2a8892617f3ecc24b0ef8e0aae`);
- seven candidate-aligned `8B FF` pairs remain padding: zero current saved
  function starts on `8B FF`, while two saved aligned functions are preceded by
  that same pair;
- the three callback installs and three propagated references remain the only
  external gap references, while 10,296 current loose instruction bytes equal
  `CF-029..CF-031` exactly.

The PC demo is pinned at
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
The 32-bit CRT reference is pinned at
`d72870f695fc49e1cb9f4fc3f45e202a7effa26474067b0e328ce31affd4a437`.
Reference export names are provenance only and are not candidate names.

## Read-only replay

[`re_text_gap_boundary_prep.py`](../../tools/re_text_gap_boundary_prep.py)
is the narrow owner because the residual-boundary tool is tied to its sealed
520-target campaign and the Mission boundary owner is a post-scratch,
target-specific promotion authority. Neither can express this multi-range,
pre-admission set without weakening its own contract.

Run the verifier with the frozen evidence directory, pristine retail and demo
specimens, pinned 32-bit CRT, and current exact body-range export:

```powershell
python -I -B tools/re_text_gap_boundary_prep.py `
  --evidence-root local-lab/text-missing-function-recovery-20260813-v1 `
  --retail <pristine-retail-BEA.exe> `
  --demo <pc-demo-BEA.exe> `
  --crt-reference C:\Windows\SysWOW64\msvcrt.dll `
  --body-ranges local-lab/current-text-ownership-20260813-v1/export/body-ranges.tsv
```

The verifier is read-only and fail-closed. It requires the frozen evidence
seal, all three binary identities, the exact current projection and 34-row
Mission name join, exact current body ranges, gap tiling and hashes, candidate
body hashes, CFG/demo READY claims, dispatcher and callback rows, `8B FF`
convention, zero current collision, and byte-identical tracked manifest.

Preparation review ran two consecutive frozen-analyzer replays and two
consecutive projection-verifier replays. Each pair exited zero with
byte-identical summaries. The focused 11-test adverse suite also passed,
including stale projection, Mission-name drift, current-entry collision,
current-body overlap, saved-start `8B FF`, evidence-seal drift, and manifest
byte-drift rejections.

## Later scratch admission gate

A later owner may try these rows only in a disposable copy of the exact pinned
project, after the repository's backup and scratch-proof prerequisites. That
test must create exactly the listed half-open body sets, read them back in a
separate process, reproduce all 31 body-range and body-byte hashes, show no
cross-entry conflict or collateral change, and survive independent refutation.
Any boundary drift, body conflict, current-projection collision, unexpected
instruction/data ownership, or non-target change rejects the affected row.

Semantic names, signatures, argument contracts, runtime reachability,
behavior, source ownership outside the bounded CRT provenance, and rebuild
parity remain open after structural admission. Live/tracked promotion would be
a later, separately authorized operation under the canonical Ghidra procedure.
