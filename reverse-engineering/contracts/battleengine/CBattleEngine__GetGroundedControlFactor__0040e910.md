# CBattleEngine__GetGroundedControlFactor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetGroundedControlFactor` at `0x0040e910`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: unknown — no SOURCE_* crosswalk row in lane brief | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040e910`

## Identity
- Body `[0x0040e910,0x0040e939]`, 42 bytes. Raw pristine-body SHA-256 `99f979d0b165369c6ad85f61547994dc791207c6107fdf492506eaf50f0ddc40`; closure range SHA-256 `48caa78c0d0119793f88613592564e12c396035cae081fd94e8e3cf2752ee569`; packet range-plus-bytes SHA-256 `9c7403fd6b2bcfccc90161d101f0ad764bf038a38f850f902dda19ec380de821`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: CBattleEngine__GetGroundedControlFactor — Ghidra tracked/table name
  (USER_DEFINED label, counted name, not a recovered source symbol). Packet `name` field agrees.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED); packet closureClass is
  PREEXISTING_GEN19_C1_OR_C2 with confidence CANDIDATE_CONTRACT — not SEALED_STATIC_RECEIPT.

## Calling convention
`__fastcall` per packet; single pointer arg in ECX. No stack args.

## Prototype and parameter semantics
```c
float __fastcall CBattleEngine__GetGroundedControlFactor(void * unit)
```
- `unit` — first dereferenced as `*(int*)unit` to reach vtable slot `+0x10c`; the decompile does not
  expose an explicit argument or receiver for that indirect call. `unit` is passed explicitly to the
  threshold helper. Layout and indirect-call storage are unknown.
- Packet signature-hardening note: checks vtable `+0x10c` and `ElapsedTime__BelowThreshold_D4`
  before returning one of two global float factors; exact identity/layout unproven.

## Return value meaning
`5.0` when vtable-slot `+0x10c` returns nonzero AND `ElapsedTime__BelowThreshold_D4(unit)` returns 0;
otherwise `0.0`. Two-level float result; units/semantics of the levels unknown beyond the literals.

## Globals read/written
not_applicable — no DAT_/g_ symbols referenced directly by this body (the helper call is by address,
not through a named global shown here).

## Callees relied on / callers
- Callee: `ElapsedTime__BelowThreshold_D4` @ `0x00401fd0` (STATIC_DIRECT, 1 site).
- Virtual/thunk call: vtable slot `+0x10c` invoked on the object at `*unit` (target not resolved here).
- Callers: none recorded in the packet.

## Behavior summary
```c
iVar2 = (**(code **)(*(int *)unit + 0x10c))();
if (iVar2 != 0) {
    bVar1 = ElapsedTime__BelowThreshold_D4(unit);
    if (CONCAT31(extraout_var,bVar1) == 0) { return 5.0; }
}
return 0.0;
```
Virtual predicate gate, then a time-threshold negation decides between 5.0 and 0.0.

## Error / edge behavior
No null guard on `*unit` or its vtable before the indirect call. Behavior when the time-threshold
helper's argument state is degenerate is not_determinable from this body.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). The VA has no row in
`ttd-deep-mine/values.tsv`.

## Evidence
- Digest reconciliation: closure `bodyDigest` `48caa78c0d0119793f88613592564e12c396035cae081fd94e8e3cf2752ee569` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `9c7403fd6b2bcfccc90161d101f0ad764bf038a38f850f902dda19ec380de821` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `99f979d0b165369c6ad85f61547994dc791207c6107fdf492506eaf50f0ddc40` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040e910.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — full small body visible with clear branch structure; no runtime observation and the virtual
slot target is unresolved, so semantics stay partial per rule 7.

## Unresolved questions
- Which virtual function occupies slot `+0x10c` and what its nonzero return means.
- Units/meaning of the 5.0 and 0.0 factor levels.
