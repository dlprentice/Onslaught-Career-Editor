# CBattleEngineJetPart__GetIsDoingSpecialAirMove

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngineJetPart__GetIsDoingSpecialAirMove` at `0x00411b70`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00411b70`

## Identity
- Body `[0x00411b70,0x00411b8f]`, 32 bytes. Raw pristine-body SHA-256 `facfc5325094b5aa07aa73b85aff75d47e8313c9a4b2b9bf24a746786d020a6b`; closure range SHA-256 `0c30a55cbc296b57016c086227a48dac9c45f28cdb03b0b950a522526eb289da`; packet range-plus-bytes SHA-256 `e482f4d156f6534b9ac1ca04edd0a93c7c884fe2fd8f7fe55e16daf72f23c5e7`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngineJetPart__GetIsDoingSpecialAirMove` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The int return is explicitly rendered.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngineJetPart__GetIsDoingSpecialAirMove(void * this)
```
- `this` — receiver whose 32-bit field at +0x2c and float at +0x48 are tested.

## Return value meaning
Returns 0 only when +0x2c equals zero and +0x48 equals 0.0; otherwise returns 1. Interpreting this as a special-air-move predicate follows USER_DEFINED/source-analog intent.

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `CBattleEngine__Morph` `0x0040a580` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Evaluates the conjunction `int(+0x2c)==0 && float(+0x48)==0.0`. Returns 0 for that conjunction and 1 for all other visible cases. No stores or calls occur.

## Error / edge behavior
A NaN at +0x48 is not equal to 0.0 and therefore yields 1. No receiver guard is visible. The exact meaning of nonzero integer/float states is unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00411b70`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0c30a55cbc296b57016c086227a48dac9c45f28cdb03b0b950a522526eb289da` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e482f4d156f6534b9ac1ca04edd0a93c7c884fe2fd8f7fe55e16daf72f23c5e7` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `facfc5325094b5aa07aa73b85aff75d47e8313c9a4b2b9bf24a746786d020a6b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00411b70.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::GetIsDoingSpecialAirMove` line 638 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — both field tests and booleanized return are complete; field semantics remain source-intent only. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete meanings/types of +0x2c and +0x48.
- Whether NaN is possible/meaningful for +0x48.
- Whether caller treats return strictly as boolean.
