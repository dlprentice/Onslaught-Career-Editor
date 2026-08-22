# CBattleEngine__dtor_base

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__dtor_base` at `0x00405a40`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405a40`

## Identity
- Body `[0x00405a40,0x00405d75]`, 822 bytes. Raw pristine-body SHA-256 `a1825666adaebfdc26d1b57b82c6255c6015d4733af17df22c2111e8571e8fd0`; closure range SHA-256 `ee66d0337f44ef3821a545793446cccd8d666f77ad8528c2997651ba7897202f`; packet range-plus-bytes SHA-256 `5ea0814deda4bf690cea01622e235ac53c113438fb472c0e2055e8b145c919c8`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__dtor_base` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__fastcall` per packet. Single `this` in ECX; no stack arguments observed in the decompile.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__dtor_base(void * this)
```
- `this` — object whose fields are torn down; base-subobject destructor body. Field offsets used:
  +0x8, +0x140, +0x250, +0x264, +0x284/+0x28c, +0x294/+0x29c, +0x2a4/+0x2ac,
  +0x4c8, +0x4cc, +0x4e0, +0x528, +0x574, +0x578, +0x57c, +0x5e8, +0x5ec,
  +0x5f4, +0x5f8, and +0x620. Meanings beyond what the code shows are unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_009c3df0` — read; passed as allocator/context argument to `CDXMemoryManager__Free` (role inferred from call shape only).
- `PTR_CBattleEngine__HandleEvent_005d89c4`, `PTR_CBattleEngine__VFunc_0_00406050_005d894c` — image data addresses written into `*this` and `*(this+8)` (vtable installs).
- MSVC SEH chain (`ExceptionList`, handler `LAB_005d11e0`) — saved/restored around the body.

## Callees relied on / callers
Callees (packet): `CSPtrSet__Remove` 0x004e5bd0 ×7, `CSPtrSet__Clear` 0x004e5c60 ×5, `CDXMemoryManager__Free` 0x00549220 ×5, `CGenericActiveReader__dtor` 0x0044b1d0 ×2, `CParticleManager__RemoveOwnerLinkFromGlobalList` 0x004cb050 ×2, `ParticleEffectLink_T3_004cb0b0` 0x004cb0b0 ×1, `CBattleEngineJetPart__dtor_base` 0x004102a0 ×1, `CBattleEngineWalkerPart__dtor_base` 0x00412cf0 ×1, `CUnit__dtor_base` 0x004f84e0 ×1. All STATIC_DIRECT.
Callers (packet): `CBattleEngine__scalar_deleting_dtor` 0x00405f60 (×1). Additional virtual/thunk callers: none recorded.

## Behavior summary
Destructor-base teardown. Order from the decompile:
1. Installs BattleEngine vtables at `*this` and `*(this+8)`.
2. Drains the set at `+0x620`: for each entry — `CSPtrSet__Remove`, `ParticleEffectLink_T3_004cb0b0(entry,0)`, `CParticleManager__RemoveOwnerLinkFromGlobalList(entry)`, `CDXMemoryManager__Free`.
3. Walks the set at `+0x284` dispatching each element's vtable slot +4 with argument 1 (owned-object release); iterator kept at `+0x28c`.
4. Walks sets at `+0x294` and `+0x2a4`, calling `CGenericActiveReader__dtor` then `CDXMemoryManager__Free` on each entry.
5. Clears `+0x140`; if `+0x528` non-null, dispatches its vtable slot +4(1) and nulls it.
6. Destroys and frees walker part `+0x578` (`CBattleEngineWalkerPart__dtor_base`) and jet part `+0x57c` (`CBattleEngineJetPart__dtor_base`), nulling each slot.
7. Releases parked reader pointers `+0x5ec` and `+0x5f4` via their vtable slot 0 / slot +4 with argument 1.
8. Removes monitored safe-pointer registrations for `+0x5e8`, `+0x574`, `+0x4e0`, `+0x4cc`, `+0x4c8`, `+0x264` (each: if pointer non-null, remove it from the set pointed to by its +4), clears sets `+0x2a4`, `+0x294`, `+0x284`, `+0x250`, calls `CParticleManager__RemoveOwnerLinkFromGlobalList(this+0x5f8)`, clears `+0x620`.
9. Tail-calls `CUnit__dtor_base(this)`.

Load-bearing fragment (step 2):
```c
while ((puVar1 = *(undefined4 **)((int)this + 0x620), puVar1 != (undefined4 *)0x0 &&
       (pvVar3 = (void *)*puVar1, pvVar3 != (void *)0x0))) {
  CSPtrSet__Remove((int *)((int)this + 0x620),pvVar3);
```

## Error / edge behavior
Every walk/set op is null-guarded; loops terminate when the head or current entry is NULL. No failure branches, allocation, or early returns visible. Behavior on already-torn-down state is not_determinable from static evidence.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405a40; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `ee66d0337f44ef3821a545793446cccd8d666f77ad8528c2997651ba7897202f` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `5ea0814deda4bf690cea01622e235ac53c113438fb472c0e2055e8b145c919c8` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `a1825666adaebfdc26d1b57b82c6255c6015d4733af17df22c2111e8571e8fd0` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405a40.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — full control flow statically accounted and mechanically unambiguous, but field/unit semantics are partial and closure is DARK with no runtime corroboration.

## Unresolved questions
- Exact BattleEngine concrete layout and the semantic meaning of each offset above.
- Whether any caller reaches this body other than the scalar-deleting wrapper (no other inbound xrefs in packet).
- Runtime cleanup ordering vs. the static order above is separate proof.
