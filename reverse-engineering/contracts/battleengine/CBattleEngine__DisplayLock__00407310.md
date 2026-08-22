# CBattleEngine__DisplayLock

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__DisplayLock` at `0x00407310`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00407310`

## Identity
- Body `[0x00407310,0x00407347]`, 56 bytes. Raw pristine-body SHA-256 `e502e3861de140d14213ca3aead3640f9c4a2b5e7bef298101627be374125931`; closure range SHA-256 `1110a019263b85e853b7a51c493742a55d3ca0476e0ba6befcdc2eba5a9cadc5`; packet range-plus-bytes SHA-256 `972522dd0b2fc160eb62128d5ff00d671a48a405af7ef28b813ec66da3a8eb30`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__DisplayLock` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (COVERED), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__thiscall`: `this` in ECX, one 4-byte stack argument (packet comment: RET 0x4); returns full EAX as BOOL-width int.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngine__DisplayLock(void * this, void * inWeapon)
```
- `inWeapon` — weapon pointer compared against the current part weapon; type kept opaque.

## Return value meaning
TRUE (1) only when the selected part's current weapon is non-null AND pointer-equal to `inWeapon`; otherwise FALSE (0):
```c
if ((pvVar1 != (void *)0x0) && (pvVar1 == inWeapon)) {
  return 1;
}
return 0;
```
Packet comment: retail writes full EAX; BOOL semantics (not C++ bool) per pinned source.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees (packet): `CBattleEngineJetPart__GetCurrentWeapon` 0x00412610 ×1, `CBattleEngineWalkerPart__GetCurrentWeapon` 0x00414030 ×1 — STATIC_DIRECT; counted names.
Callers (packet): `ProjectileBurst__SpawnFromCurrentPreset` 0x005069f0 ×1. Packet comment adds a static caller testing EAX before FireLock.

## Behavior summary
State-select then compare:
1. If `*(int*)(this+0x260) == 3` (jet state slot by counted-name context): `pvVar1 = CBattleEngineJetPart__GetCurrentWeapon(*(this+0x57c))`.
2. Else: `pvVar1 = CBattleEngineWalkerPart__GetCurrentWeapon(*(this+0x578))`.
3. Return 1 iff result non-null and equal to `inWeapon`, else 0.

## Error / edge behavior
Null current-weapon yields FALSE (explicit check). No other failure branches visible.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00407310; brief sessions/ttd_values empty. Packet comment separately records Level-521 raw boundary rows observing 17 calls with immediately paired entries from 0x005074BB — packet-recorded observation, no session ids available in lane inputs to cite further.

## Evidence
- Digest reconciliation: closure `bodyDigest` `1110a019263b85e853b7a51c493742a55d3ca0476e0ba6befcdc2eba5a9cadc5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `972522dd0b2fc160eb62128d5ff00d671a48a405af7ef28b813ec66da3a8eb30` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `e502e3861de140d14213ca3aead3640f9c4a2b5e7bef298101627be374125931` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00407310.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence COVERED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.
- Crosswalk row: BattleEngine.cpp `CBattleEngine::DisplayLock` line 980 — SOURCE_ANALOG
  (packet comment claims match to pinned BattleEngine.cpp:980-994; source (not proof)).

## Confidence
2 — complete body visible with fully determined branch semantics; per-call return association and false-reason classification remain open per packet comment. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Which callers consume FALSE vs TRUE and why (display gating vs fire gating); exact types behind +0x578/+0x57c.
