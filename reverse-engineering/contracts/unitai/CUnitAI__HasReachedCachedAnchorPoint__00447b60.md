# CUnitAI__HasReachedCachedAnchorPoint

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__HasReachedCachedAnchorPoint` at `0x00447b60`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00447b60`

## Identity
- Body `[0x00447b60,0x00447ba1]`, 66 bytes. Raw pristine-body SHA-256 `7f6dd1f092ddaeb611f1bddd59e1a791fd6614d94d0f9f6c566fc1e251b96382`; closure range SHA-256 `d74d98509808936643dbf9468265ab8da446cc7b84b1bc9008abab0011e3e602`; packet range-plus-bytes SHA-256 `39dc91c7cf9cbc38d47d4f904660e3443859c00e15ddddc67d150c39fbc66343`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__HasReachedCachedAnchorPoint` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)
```
- `unitAI` — receiver/base pointer read at +0x1c/+0x20, +0x280/+0x284, and +0x290. The label is counted intent only.

## Return value meaning
Returns 1 exactly when +0x290 is nonzero and the 2D Euclidean distance between (+0x1c,+0x20) and (+0x280,+0x284) is below 10.0; otherwise returns 0.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): none recorded; any visible indirect dispatch has no structured direct-callee VA.
- Callers (packet structured array): `CDropshipAI__VFunc_09_00448580` `0x00448580` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Tests +0x290, subtracts two pairs of receiver floats, computes `sqrt(dx*dx + dy*dy)`, and compares it with 10.0. The cache/anchor wording is counted name/comment intent only.

## Error / edge behavior
The receiver is unguarded. NaN produces a false less-than comparison under ordinary floating-point behavior; coordinate units are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00447b60`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `d74d98509808936643dbf9468265ab8da446cc7b84b1bc9008abab0011e3e602` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `39dc91c7cf9cbc38d47d4f904660e3443859c00e15ddddc67d150c39fbc66343` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7f6dd1f092ddaeb611f1bddd59e1a791fd6614d94d0f9f6c566fc1e251b96382` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00447b60.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — flag gate, two-component distance, threshold, and numeric return are explicit; coordinate roles and units remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning of +0x290 and units/roles of both coordinate pairs.
- Whether 10.0 is inclusive by higher-level design; the body uses strict `<`.
