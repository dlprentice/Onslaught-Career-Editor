# CBattleEngineJetPart__HandleGroundEffect

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngineJetPart__HandleGroundEffect` at `0x00411630`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00411630`

## Identity
- Body `[0x00411630,0x00411a50]`, 1057 bytes. Raw pristine-body SHA-256 `fc34abb0b1a198ae939c507d049dd85100a0a75d6acc332831ca415317944b00`; closure range SHA-256 `ce5391070c58e31024f22838d89865bd77b7a0ea5c4e30bfbef1edb823e252b5`; packet range-plus-bytes SHA-256 `68ce67c7dc66870252fe97bdb70f19d461929e3d86b3f22aa9a10328eeb5abf0`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngineJetPart__HandleGroundEffect` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. The source-aligned USER_DEFINED name is intent evidence only.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineJetPart__HandleGroundEffect(void * this)
```
- `this` — receiver with a nested/back pointer at +0x18 and local fields +0x2c/+0x48; the nested object supplies many position, vector, orientation, and output fields.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_006fbdfc` — read as a cap/comparison scalar; domain and units unknown.
- `DAT_006fadc8` — its address is passed to the packet-listed sample-height and sample-normal callees.

## Callees relied on / callers
- Callees (packet structured array): `vector_constructor_iterator_nothrow` `0x004011b0` ×1 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×8 (STATIC_DIRECT); `Vec3__NormalizeInPlace` `0x00406d50` ×2 (STATIC_DIRECT); `Vec3__Cross` `0x00411a60` ×1 (STATIC_DIRECT); `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×1 (STATIC_DIRECT); `CMonitor__SampleHeightfieldNormalAtXY` `0x0047ec60` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngineJetPart__Move` `0x00410c50` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Using the pointer at `this+0x18`, forms a predicted three-float position by adding current +0x1c/+0x20/+0x24 to +0x7c/+0x80/+0x84 scaled by 20.0*0.5. It samples a scalar, caps it against `DAT_006fbdfc`, subtracts a predicted component, and continues only when nested +0xfc is nonzero and the resulting gap is below 5.0. Negative gap is clamped to zero; a derived `(5-gap)*0.0025` scales three nested fields and is sent through indirect slot +0x74. When local +0x2c is zero and +0x48 is 0.0, a positive nested +0x84 is multiplied by 0.9, trigonometric/vector work constructs a basis/normal using the packet-listed vector and sampler helpers, and nested floats +0x280 and +0x27c are incrementally updated. Exact lower-half dataflow is not fully recoverable from this decompile.

## Error / edge behavior
Receiver and nested pointers are largely unguarded. The body skips the main path when nested +0xfc is zero or the derived gap is at least 5.0. The decompile contains unresolved `unaff_ESI` and overlapping/possibly uninitialized stack temporaries (`fStack_bc` among them), so exact normal-selection and update coefficients are not_determinable without disassembly review.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00411630`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `ce5391070c58e31024f22838d89865bd77b7a0ea5c4e30bfbef1edb823e252b5` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `68ce67c7dc66870252fe97bdb70f19d461929e3d86b3f22aa9a10328eeb5abf0` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `fc34abb0b1a198ae939c507d049dd85100a0a75d6acc332831ca415317944b00` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00411630.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::HandleGroundEffect` line 546 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
1 — major gates, sampler/vector calls, damping, and field updates are visible, but unresolved registers/stack aliases materially limit exact semantics. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning/units of the sampled scalar, global cap, gap thresholds, and nested fields.
- Target/contracts of indirect slot +0x74 and any other indirect operations.
- Origins of `unaff_ESI` and `fStack_bc` and exact lower-half machine dataflow.
- Whether the source analog's ground-effect interpretation matches runtime behavior.
