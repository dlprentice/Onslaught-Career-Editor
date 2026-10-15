# CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` at `0x0040c340`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c340`

## Identity
- Body `[0x0040c340,0x0040c375]`, 54 bytes. Raw pristine-body SHA-256 `783826b0508c436544d88aa5299b8e5507d33108f4c6cc3a002ca2c276f12bdc`; closure range SHA-256 `062ae7f7fbe324ea8c7804a5a16a773171e6b26b8ced55094fb5322d82e49cc8`; packet range-plus-bytes SHA-256 `80a60106bf990e213f116b3521811fc7da268bc86182b8e52109deee34eb9ab2`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit pointer argument is modeled on the stack. The USER_DEFINED parameter name is descriptive intent only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange(void * this, void * burstContext)
```
- `this` — receiver whose +0x4b8/+0x4c0-related helper state is passed to the direct callee and whose float at +0x604 is updated.
- `burstContext` — pointer whose +0xa0 field is dereferenced; a float at +0x40 of that nested object is read twice. The source-level type and role are unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CBattleEngine__RandomizeOffsets4B8_4C0` `0x00407940` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Reads `x = *(float *)(*(int *)(burstContext+0xa0)+0x40)`, calls the packet-recorded offset-randomization helper with `(this, x)`, then stores `*(float *)(this+0x604) += x + x`. The counted function/parameter names suggest a burst context, but that interpretation is not retail semantic proof.

## Error / edge behavior
No null checks protect `burstContext` or its +0xa0 nested pointer. NaN/overflow behavior follows the machine floating-point operations and is otherwise not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040c340`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `062ae7f7fbe324ea8c7804a5a16a773171e6b26b8ced55094fb5322d82e49cc8` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `80a60106bf990e213f116b3521811fc7da268bc86182b8e52109deee34eb9ab2` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `783826b0508c436544d88aa5299b8e5507d33108f4c6cc3a002ca2c276f12bdc` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c340.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_HIGH`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — one read path, one direct call, and one accumulation are explicit; object meanings and units are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Type and meaning of the nested +0xa0 object and its +0x40 float.
- Meaning and units of receiver +0x604.
- Runtime distribution/effect of the direct callee.
