# CBattleEngine__VFunc_15_00405ef0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_15_00405ef0` at `0x00405ef0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405ef0`

## Identity
- Body `[0x00405ef0,0x00405ef6]`, 7 bytes. Raw pristine-body SHA-256 `373b7124016847a7a38191579391991c506991d129924f9398ced63e0a6d4671`; closure range SHA-256 `5306c2e4b65ad3ae66b82940dc744408e2b005c2c07693c4d45234deeab58dd4`; packet range-plus-bytes SHA-256 `24e9c0492cd944504015b523a6b4e01f9d6d5947efd3eaf1bbb4645e4fa57936`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_15_00405ef0` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (COVERED), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__stdcall` per packet signature; no arguments modeled.

## Prototype and parameter semantics
```c
float10 __stdcall CBattleEngine__VFunc_15_00405ef0(void)
```
No parameters.

## Return value meaning
Returns the constant 35.0 on the x87 stack (`return (float10)35.0;`). Unit/meaning of the 35.0 value is unknown — only the constant is proven.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none. Callers: none recorded in packet.

## Behavior summary
Constant-return stub: loads 35.0 and returns it via FPU. No branches, no memory access.

## Error / edge behavior
not_determinable — no failure paths exist in a constant-return stub.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405ef0; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5306c2e4b65ad3ae66b82940dc744408e2b005c2c07693c4d45234deeab58dd4` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `24e9c0492cd944504015b523a6b4e01f9d6d5947efd3eaf1bbb4645e4fa57936` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `373b7124016847a7a38191579391991c506991d129924f9398ced63e0a6d4671` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405ef0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence COVERED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole body visible, return constant fully determined statically; the meaning/unit of 35.0 stays unknown. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- What quantity 35.0 represents (units unknown) and which vtable slot dispatches here.
