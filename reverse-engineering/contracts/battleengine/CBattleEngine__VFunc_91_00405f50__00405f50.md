# CBattleEngine__VFunc_91_00405f50

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_91_00405f50` at `0x00405f50`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f50`

## Identity
- Body `[0x00405f50,0x00405f56]`, 7 bytes. Raw pristine-body SHA-256 `80f4df42ea1dfdf8ec028af4388393e2793c2c34ba56c8173831b3c4c97f1260`; closure range SHA-256 `0064ace06f30ebe80a0b2ee97b4df9d6181911a564ea9728868507cc7667c7ef`; packet range-plus-bytes SHA-256 `f35fb1bbe2d8ff34873b64c71fb16dd57063312fc9ecf6ddf17e4a15440a4ae1`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_91_00405f50` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet decompile comment: RTTI-derived vtable slot 91 of CBattleEngine's primary sub-object; asserts membership/slot only.
- Campaign grade: C1_CANDIDATE_PARTIAL (COVERED), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__fastcall` per packet signature: first argument in ECX (decompiler models it as `int param_1`; effectively the object pointer).

## Prototype and parameter semantics
```c
float10 __fastcall CBattleEngine__VFunc_91_00405f50(int param_1)
```
- `param_1` — base pointer; body reads `*(float *)(param_1 + 0x5d8)`:
```c
return (float10)*(float *)(param_1 + 0x5d8);
```
Field meaning at +0x5d8 is unknown.

## Return value meaning
Returns the 32-bit float stored at +0x5d8 widened to the x87 float10 return type. Unit/semantics unknown.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none. Callers: none recorded in packet; entry is an RTTI vtable-slot target (virtual dispatch).

## Behavior summary
Single field read: return `*(float*)(this + 0x5d8)` promoted through FPU. No branches.

## Error / edge behavior
not_determinable — no guards; NULL `param_1` behavior outside static scope of evidence.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f50; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0064ace06f30ebe80a0b2ee97b4df9d6181911a564ea9728868507cc7667c7ef` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `f35fb1bbe2d8ff34873b64c71fb16dd57063312fc9ecf6ddf17e4a15440a4ae1` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `80f4df42ea1dfdf8ec028af4388393e2793c2c34ba56c8173831b3c4c97f1260` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f50.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence COVERED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole body visible; accessor mechanics fully determined, field meaning open. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Semantic role and units of the +0x5d8 float; which virtual call sites reach the packet-commented
  CBattleEngine primary-vtable slot 91.
