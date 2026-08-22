# CBattleEngine__FinalizeLinkedSetAndVFunc02

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__FinalizeLinkedSetAndVFunc02` at `0x00405f80`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f80`

## Identity
- Body `[0x00405f80,0x00405ff7]`, 120 bytes. Raw pristine-body SHA-256 `101c71a29c94523a9bdb4f2d4b0df60cf064bb4cdeca167a7be4b0e5a501f31a`; closure range SHA-256 `9cdac3202ef6f1af0f08742c0a494a9d261ac30ff66f208ed7f3e3e555fb3f0f`; packet range-plus-bytes SHA-256 `54472025f52bb2efa8335725bb8f4a4df8aba56cfe0246b9cf75c5685c7fae9f`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__FinalizeLinkedSetAndVFunc02` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet comment flags name debt ("address-suffixed VFunc_02 placeholder pending source slot identity"); rename applied in wave1127.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__fastcall`: `this` in ECX, no explicit stack arguments.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__FinalizeLinkedSetAndVFunc02(void * this)
```
No parameters beyond `this`.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_009c3df0` — read; allocator/context argument to `CDXMemoryManager__Free`.
- `DAT_008a9a98` — read; first argument to `CGame__GetController`.

## Callees relied on / callers
Callees (packet): `CSPtrSet__Remove` 0x004e5bd0 ×1, `CDXMemoryManager__Free` 0x00549220 ×1, `CGame__GetController` 0x004705d0 ×1, `CController__SetVibration` 0x0042e750 ×1, `ParticleEffectLink_T3_004cb0b0` 0x004cb0b0 ×1, `CUnit__VFunc02_CleanupWorldLinksAndForward` 0x004f95d0 ×1 — all STATIC_DIRECT; callee labels are counted names.
Callers: none recorded in packet.

## Behavior summary
Finalization sequence, fully ordered in the decompile:
1. Drain the linked set at `+0x250` (iterator mirrored to `+0x258`): `CSPtrSet__Remove` then `CDXMemoryManager__Free(&DAT_009c3df0, entry)` per element until empty.
2. If `+0x574` non-null: `controller = CGame__GetController(&DAT_008a9a98, *(int*)(*(int*)(this+0x574)+0x2c) - 1)`; if non-null, `CController__SetVibration(controller, 0.0, same index-1)` — vibration-zeroing per counted callee name only.
```c
pvVar2 = CGame__GetController(&DAT_008a9a98,*(int *)(*(int *)((int)this + 0x574) + 0x2c) + -1);
if (pvVar2 != (void *)0x0) {
  CController__SetVibration(pvVar2,0.0,...);
}
```
3. `ParticleEffectLink_T3_004cb0b0((char*)this + 0x5f8, 0)`.
4. Tail: `CUnit__VFunc02_CleanupWorldLinksAndForward(this)`.

## Error / edge behavior
Set drain and controller lookup are null-guarded; no failure branches otherwise. Behavior when +0x574's chain is stale: not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f80; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `9cdac3202ef6f1af0f08742c0a494a9d261ac30ff66f208ed7f3e3e555fb3f0f` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `54472025f52bb2efa8335725bb8f4a4df8aba56cfe0246b9cf75c5685c7fae9f` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `101c71a29c94523a9bdb4f2d4b0df60cf064bb4cdeca167a7be4b0e5a501f31a` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f80.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — control flow fully accounted; semantics lean on counted callee names (vibration, world-link cleanup) whose retail effects stay unproven, and closure is DARK.

## Unresolved questions
- Source vtable-slot identity behind the "VFunc02" label; whether SetVibration(0,… ) is a reset or no-op on D-input devices; ownership of the +0x250 set entries.
