# CBattleEngine__VFunc_0_00406050

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_0_00406050` at `0x00406050`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00406050`

## Identity
- Body `[0x00406050,0x004060a4]`, 85 bytes. Raw pristine-body SHA-256 `c4b0641c0f459325225d694817a6dfcee1614c89cb3499e73adb6e410b4965c1`; closure range SHA-256 `3abe8192389466a84ceab424e9bbd9f2902c17289dd8c4b03c5034d37bdaaee1`; packet range-plus-bytes SHA-256 `75cecdd52fd0f712a50faf2dae9da191f1d444329df4b8c3221018848967be58`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_0_00406050` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED), closure class PREEXISTING_GEN19_C1_OR_C2 (packet campaignGrade confidence CANDIDATE_CONTRACT).

## Calling convention
`__thiscall`: `this` in ECX, one stack argument `param_1` (pointer to a 4-dword out buffer, written through).

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_0_00406050(void * this, undefined4 * param_1)
```
- `param_1` — out buffer; four dwords copied from locals after the calls below (positions 0..3).

## Return value meaning
not_applicable — decompile models no meaningful return; results are delivered through `param_1`.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: `CActor__GetRenderPos` 0x00401be0 ×1 (STATIC_DIRECT; counted name). One indirect virtual call through `(*(*(this-8)) + 0xc0)` when `*(this+0x5e8) == 1` — target unresolved statically. Callers: none recorded in packet.

## Behavior summary
```c
CActor__GetRenderPos(this,&local_10);
if (*(int *)((int)this + 0x5e8) == 1) {
  fVar1 = (**(code **)(*(int *)((int)this + -8) + 0xc0))();
  local_8 = (float)(fVar1 + (float10)local_8);
}
*param_1 = local_10; param_1[1] = local_c; param_1[2] = local_8; param_1[3] = local_4;
```
Fetches the actor render position into locals; if state word +0x5e8 equals 1, adds the float10 result of an indirect vtable call on the object at `this-8` (slot +0xc0) to the third dword (Z-slot by position); copies all four dwords to the caller's buffer. The vtable-call return's unit and the meaning of +0x5e8 are unknown.

## Error / edge behavior
The +0x5e8 branch dereferences `*(this-8)` unguarded; behavior outside mode 1 is a plain passthrough of GetRenderPos output. Other failure modes: not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00406050; brief sessions/ttd_values empty. Brief closure OPEN_EXECUTED is carried from the closure row without per-VA deep-mine rows to cite.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3abe8192389466a84ceab424e9bbd9f2902c17289dd8c4b03c5034d37bdaaee1` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `75cecdd52fd0f712a50faf2dae9da191f1d444329df4b8c3221018848967be58` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `c4b0641c0f459325225d694817a6dfcee1614c89cb3499e73adb6e410b4965c1` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00406050.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — control flow fully visible; but one indirect dispatch target is unresolved and the semantic roles of the four out dwords and +0x5e8 gate are partial.

## Unresolved questions
- Target of the +0xc0 virtual slot on the `this-8` object; units added to local_8; meaning of +0x5e8==1.
