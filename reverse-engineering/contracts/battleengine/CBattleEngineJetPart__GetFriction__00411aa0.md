# CBattleEngineJetPart__GetFriction

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngineJetPart__GetFriction` at `0x00411aa0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00411aa0`

## Identity
- Body `[0x00411aa0,0x00411b63]`, 196 bytes. Raw pristine-body SHA-256 `2abb7df4e2c05f1a4d9b3fb14d8b564e41b27df0187f233fe58db80317ff6637`; closure range SHA-256 `9cc360e8c5b17744083bec0aee07fb5ad4b814e6cdbe046a0f1c19962e19ed22`; packet range-plus-bytes SHA-256 `3fe4d47f52723cdb0aa62608834b09424128ba057c995e30982fda8a27a53e7b`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngineJetPart__GetFriction` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The packet models a 32-bit float return.

## Prototype and parameter semantics
```c
float __thiscall CBattleEngineJetPart__GetFriction(void * this)
```
- `this` — receiver with nested/back pointer +0x18. The nested object supplies +0x1c sample position, float-like +0x24, and an indirect vtable slot +0x6c.

## Return value meaning
Returns 0.98 when the capped-sample difference is at least 3.0; returns 0.99 on the default paths; in one middle-band/low-vector-magnitude path returns `1.0 - unresolved_local*0.01`, whose exact value is not_determinable from the decompile.

## Globals read/written
- `DAT_006fbdfc` — read and used as an upper cap for the sampled float.
- `DAT_006fadc8` — its address is passed to the packet-listed sampler.

## Callees relied on / callers
- Callees (packet structured array): `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngineJetPart__Move` `0x00410c50` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Samples a double using nested `+0x1c`, converts it to float, and caps it to at most `DAT_006fbdfc`. It subtracts the nested float at +0x24. A difference at least 3.0 returns 0.98. A difference below 1.0 returns 0.99. In the middle band [1.0,3.0), it invokes indirect slot +0x6c, treats the result as a three-float pointer, and if its magnitude is below 1.5 returns an expression based on an unresolved local; otherwise it returns 0.99. Friction/terrain terminology and physical units are not independently proven.

## Error / edge behavior
The receiver, +0x18 pointer, indirect return, and vector pointer are unguarded. The decompile renders `local_10` as an undefined byte array but later converts it as a float in the middle-band return expression; that value is not honest to reconstruct without instruction review. NaN comparisons may route to the default path depending on instruction semantics, which are not established here.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00411aa0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `9cc360e8c5b17744083bec0aee07fb5ad4b814e6cdbe046a0f1c19962e19ed22` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `3fe4d47f52723cdb0aa62608834b09424128ba057c995e30982fda8a27a53e7b` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `2abb7df4e2c05f1a4d9b3fb14d8b564e41b27df0187f233fe58db80317ff6637` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00411aa0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::GetFriction` line 609 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
1 — tier gates and fixed returns are visible, but the middle-band return uses an unresolved decompiler local and an indirect target. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Instruction-level source/value represented by `(float)local_10`.
- Contract of indirect slot +0x6c and nullability of its return.
- Meanings/units of thresholds 1.0, 1.5, 3.0 and returns 0.98/0.99.
