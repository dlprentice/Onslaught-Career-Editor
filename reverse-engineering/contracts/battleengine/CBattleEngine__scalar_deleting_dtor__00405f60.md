# CBattleEngine__scalar_deleting_dtor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__scalar_deleting_dtor` at `0x00405f60`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f60`

## Identity
- Body `[0x00405f60,0x00405f7f]`, 32 bytes. Raw pristine-body SHA-256 `3c586f7bfbfb55d7f168e94da46679d69ae1b74364d5a57215dcd9b67724e71b`; closure range SHA-256 `6fd0ad2f73e07fe0352a6bdb5a54e7ddfa472b2717cee575b8623ab60a550a0e`; packet range-plus-bytes SHA-256 `1d2d32b0834cece437f98733a77d1db8803386105057b552294233b91064123f`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__scalar_deleting_dtor` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__thiscall`: `this` in ECX, one stack argument (`flags`, byte); callee cleans one 4-byte stack slot per MSVC thiscall model. Packet tags include `allocator-delete-wrapper` / `scalar-deleting-destructor`.

## Prototype and parameter semantics
```c
void * __thiscall CBattleEngine__scalar_deleting_dtor(void * this, byte flags)
```
- `flags` — scalar-deleting-destructor flag word; bit 0 selects heap free after destruction:
```c
CBattleEngine__dtor_base(this);
if ((flags & 1) != 0) {
  CDXMemoryManager__Free(&DAT_009c3df0,this);
}
return this;
```

## Return value meaning
Returns `this` unchanged (visible in decompile), regardless of the free branch.

## Globals read/written
- `DAT_009c3df0` — read; allocator/context argument to `CDXMemoryManager__Free`.

## Callees relied on / callers
Callees: `CBattleEngine__dtor_base` 0x00405a40 ×1, `CDXMemoryManager__Free` 0x00549220 ×1 (both STATIC_DIRECT). Callers: none recorded in the packet.

## Behavior summary
Runs the full BattleEngine base destructor, then — only when `flags & 1` — frees the object through the game allocator; returns `this`. This is the standard MSVC "scalar deleting destructor" shape placed in the vtable delete slot.

## Error / edge behavior
No guards or failure branches visible. Behavior of `CDXMemoryManager__Free` on failure is out of scope of this body (not shown here).

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f60; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `6fd0ad2f73e07fe0352a6bdb5a54e7ddfa472b2717cee575b8623ab60a550a0e` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `1d2d32b0834cece437f98733a77d1db8803386105057b552294233b91064123f` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `3c586f7bfbfb55d7f168e94da46679d69ae1b74364d5a57215dcd9b67724e71b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f60.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.
- Crosswalk row: BattleEngine.cpp `CBattleEngine::~dtor` line 356 — SOURCE_ANALOG
  (source architecture cite: a deleting-dtor wrapper is expected at this role; source (not proof) of retail behavior).

## Confidence
2 — complete 11-instruction body visible with standard, unambiguous semantics; runtime deletion behavior remains separate proof (DARK closure). No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Which call sites invoke the delete slot with flags bit 0 set vs clear (runtime deletion path unobserved).
