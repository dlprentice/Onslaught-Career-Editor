# CBattleEngine__VFunc_7_00405ed0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_7_00405ed0` at `0x00405ed0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405ed0`

## Identity
- Body `[0x00405ed0,0x00405ed5]`, 6 bytes. Raw pristine-body SHA-256 `1c703b38a06868669dcbc94a74a327108c71f1145620cf5935aa3f5266de6960`; closure range SHA-256 `5f44d0cefd05128508110f3e5c5a66dc4bb522b5313c3ac246906b842d083be5`; packet range-plus-bytes SHA-256 `7443d71cc9c7351d43ae3cc7eccb71eb0d406f87edd10e3ab7b3cd58867dd429`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_7_00405ed0` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__stdcall` per packet signature; takes no arguments (no `this` parameter modeled by the decompiler).

## Prototype and parameter semantics
```c
char * __stdcall CBattleEngine__VFunc_7_00405ed0(void)
```
No parameters.

## Return value meaning
Returns the address of the string literal `"CBattleEngine"` at 0x0062325c (stringRefs: value `CBattleEngine`, length 14 incl. NUL). Whole body:
```c
return s_CBattleEngine_0062325c;
```
Likely a class-name accessor, but the consumer side is unknown — only the returned pointer is proven.

## Globals read/written
- `s_CBattleEngine_0062325c` (0x0062325c) — read; string literal `"CBattleEngine"`.

## Callees relied on / callers
Callees: none. Callers: none recorded in packet.

## Behavior summary
Two-instruction stub that returns a fixed pointer to the `"CBattleEngine"` string constant. No branches, no state access.

## Error / edge behavior
not_determinable — no failure paths exist in a constant-return stub.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405ed0; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5f44d0cefd05128508110f3e5c5a66dc4bb522b5313c3ac246906b842d083be5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `7443d71cc9c7351d43ae3cc7eccb71eb0d406f87edd10e3ab7b3cd58867dd429` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `1c703b38a06868669dcbc94a74a327108c71f1145620cf5935aa3f5266de6960` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405ed0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — entire body visible and semantics (constant pointer return) fully determined statically; no runtime corroboration available. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Which vtable slot(s) reference this address and what callers do with the returned name pointer.
