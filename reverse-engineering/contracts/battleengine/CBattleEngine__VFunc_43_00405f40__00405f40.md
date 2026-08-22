# CBattleEngine__VFunc_43_00405f40

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_43_00405f40` at `0x00405f40`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f40`

## Identity
- Body `[0x00405f40,0x00405f45]`, 6 bytes. Raw pristine-body SHA-256 `b52c9718ff4b35c4b06b87c6c1d1a260033a3ddfea0a50b9bcf5fb0e7bbad67c`; closure range SHA-256 `70a417c2d518f9602a7d71f9140f4eed5adf6a9a72b6bc927561791fa471860f`; packet range-plus-bytes SHA-256 `a87a8d97bd3feaab6812241b847dcdebc94c1df6a2ce2a3cb3445d19a1b751f5`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_43_00405f40` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet decompile comment: RTTI-derived vtable slot 43 of CBattleEngine's primary sub-object; asserts membership/slot only.
- Campaign grade: C1_CANDIDATE_PARTIAL (COVERED), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__stdcall` per packet signature; no arguments modeled.

## Prototype and parameter semantics
```c
undefined4 __stdcall CBattleEngine__VFunc_43_00405f40(void)
```
No parameters.

## Return value meaning
Returns the constant `0x68` (104):
```c
return 0x68;
```
Meaning/unit of the constant is unknown — only the value is proven.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none. Callers: none recorded in packet.

## Behavior summary
Constant-return stub: EAX = 0x68. No branches, no memory access.

## Error / edge behavior
not_determinable — no failure paths exist in a constant-return stub.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f40; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `70a417c2d518f9602a7d71f9140f4eed5adf6a9a72b6bc927561791fa471860f` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `a87a8d97bd3feaab6812241b847dcdebc94c1df6a2ce2a3cb3445d19a1b751f5` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `b52c9718ff4b35c4b06b87c6c1d1a260033a3ddfea0a50b9bcf5fb0e7bbad67c` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f40.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence COVERED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole body visible; returned constant fully determined statically, its meaning unknown. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- What 0x68 denotes to callers (count? id? size?) and which virtual call sites reach the
  packet-commented CBattleEngine primary-vtable slot 43.
