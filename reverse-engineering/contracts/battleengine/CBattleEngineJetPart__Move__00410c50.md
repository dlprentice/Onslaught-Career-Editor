# CBattleEngineJetPart__Move

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineJetPart__Move` at `0x00410c50`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00410c50`

## Identity
- Body `[0x00410c50,0x004114ca]`, 2171 bytes, 635 closure instructions. Raw pristine-body SHA-256 `0de35d19b47b1f11bd70b4c16313db461247c1232eb2c1a77a9bd91634b97484`; closure range SHA-256 `f1df0226291f8d242b7c80e679fda9053e4a527039f68fc47df93bf470cc5823`; packet range-plus-bytes SHA-256 `36260dde01561867fe2fe6cb8ddd2b475eb79763a5aa56d305e91856e5da9b4b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineJetPart__Move` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineJetPart__Move`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CBattleEngineJetPart__Move(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngineJetPart__Move(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CBattleEngine__Morph` `0x0040a580` ×2 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__GroundParticleEffect` `0x0040ef20` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__HandleSkimming` `0x00411500` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__HandleGroundEffect` `0x00411630` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__GetFriction` `0x00411aa0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEulerAngles__ctor_from_FMatrix` `0x0044adb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__UpdateTrackedRenderPair` `0x005078f0` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__Move` `0x004081c0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “CBattleEngineJetPart Move. ECX receiver; plain `RET` (c3) — no stack args. Catalog `__fastcall` vs peer JetPart `__thiscall` is spelling debt only. Sole CALL from CBattleEngine__Move loads ECX from BattleEngine+0x57c; body updates owned weapon emitters, energy/engine state, and related JetPart fields via main-part backpointer at +0x18. Static retail evidence only; concrete layout, runtime movement behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `53ba67c74d460a90c3129d98bdb85b582107fafb067da0ae3cc3a48b77dc5592`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 7 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 6; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00410c50.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `53ba67c74d460a90c3129d98bdb85b582107fafb067da0ae3cc3a48b77dc5592`.
- Digest derivation: closure SHA-256 hashes canonical range text `00410c50:004114ca;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::Move` line 305 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineJetPart.cpp/CBattleEngineJetPart__Move.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
