# CBattleEngine__GetLaunchPosition

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__GetLaunchPosition` at `0x0040c990`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c990`

## Identity
- Body `[0x0040c990,0x0040d0ef]`, 1888 bytes, 483 closure instructions. Raw pristine-body SHA-256 `252ee87dd58ebfbecbd46922c3584acd523b3924bf5446e21a4d1d674a7828d7`; closure range SHA-256 `a83dac5887f95e7ba60f1f627d959603cfd7b176d88aae721f59164f81953c3f`; packet range-plus-bytes SHA-256 `17f711958f6926ecbe91919d3646169c1622ae084993c7bfd5aaef74f9ea6994`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__GetLaunchPosition` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__GetLaunchPosition`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngine__GetLaunchPosition(void * this, void * inWeapon, int inIndex, void * outPos, void * outOrientation, int inNeedOrientation)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__GetLaunchPosition(void * this, void * inWeapon, int inIndex, void * outPos, void * outOrientation, int inNeedOrientation)
```
- Packet-declared parameter list: `void * this, void * inWeapon, int inIndex, void * outPos, void * outOrientation, int inNeedOrientation`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_006234fc`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `vector_constructor_iterator_nothrow` `0x004011b0` ×2 site(s) (STATIC_DIRECT).
- Callee `Vec3__SetXYZ` `0x00401ec0` ×11 site(s) (STATIC_DIRECT).
- Callee `Vec3__Add` `0x00401ee0` ×2 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetRows` `0x00401f10` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__Magnitude` `0x004026b0` ×1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×2 site(s) (STATIC_DIRECT).
- Callee `CGeneralVolume__ctor_base` `0x0040b100` ×1 site(s) (STATIC_DIRECT).
- Callee `CWeaponStatement__UsesBallisticArcNoLocks` `0x0040d0f0` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__SubtractToOut` `0x0040d120` ×2 site(s) (STATIC_DIRECT).
- Callee `Vec3__ScaleToOut` `0x0040d150` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__Dot` `0x0040d180` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__ElevationOrZero` `0x0040d1a0` ×1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles` `0x0040d1f0` ×1 site(s) (STATIC_DIRECT).
- Callee `Mat34__TransformVec3ByBasisToOut` `0x0040d2c0` ×3 site(s) (STATIC_DIRECT).
- Callee `Mat34__MultiplyBasisToOut` `0x0040d320` ×2 site(s) (STATIC_DIRECT).
- Callee `CLine__ctor_fromEndpoints` `0x0040d470` ×1 site(s) (STATIC_DIRECT).
- Callee `OID__GetAttachmentOrOriginTransform` `0x0044a850` ×1 site(s) (STATIC_DIRECT).
- Callee `OID__GetAttachmentOrBaseOrientationMatrix` `0x0044a930` ×2 site(s) (STATIC_DIRECT).
- Callee `CPlayer__GetCurrentViewPoint` `0x004d2a70` ×2 site(s) (STATIC_DIRECT).
- Callee `CPlayer__GetCurrentViewOrientation` `0x004d2ae0` ×2 site(s) (STATIC_DIRECT).
- Callee `OID__SolveBallisticPitchToTarget` `0x005094b0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `3000-3069` defines `CBattleEngine::GetLaunchPosition` as `void CBattleEngine::GetLaunchPosition( CWeapon		*inWeapon, int			inIndex, FVector		&outPos, FMatrix		&outOrientation, BOOL		inNeedOrientation)`; exact extracted source-body SHA-256 `9714f6be0eab7d284f67945d7b9b158e066d97de7f82e2a1808bdcbc9b36826d`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=8, switch=0, for=0, while=0; named call tokens `AdjustAim`, `Azimuth`, `CalculateDesiredPitch`, `Elevation`, `FMatrix`, `FVector`, `GetCurrentViewOrientation`, `GetCurrentViewPoint`, `GetPrimaryOrientation`, `GetPrimaryPosition`, `GetRTEmitter`, `GetRenderThing`, `Gravity`, `Magnitude`, `ValidRound`, `targetLine`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave973 math/Mat34 vector review boundary recovery: recovered the missing Ghidra function object for CBattleEngine::GetLaunchPosition. Static evidence: SEH prologue at 0x0040c990, terminal RET 0x14 at 0x0040d0ed immediately before 0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks, five stack arguments after ECX, cockpit Gun emitter fallback, weapon primary position/orientation fallback, gravity and adjust-aim branches, camera view point/orientation reads, Vec3__ElevationOrZero and Mat34__SetFromEulerAngles calls, and source parity with references/Onslaught/BattleEngine.cpp lines 3000-3069. Static retail Ghidra/source evidence only; exact retail class layout, exact out-vector/out-matrix ABI, runtime launch-position behavior, BEA patching, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `0fd28d203f78bc257cda169707dadddaff0749195e6d1e500c88407b522bb272`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 21 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 3,122 covered bytes; evidence `name=CBattleEngine__GetLaunchPosition`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 11; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c990.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0fd28d203f78bc257cda169707dadddaff0749195e6d1e500c88407b522bb272`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040c990:0040d0ef;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::GetLaunchPosition` line 3000 (`SOURCE_ANALOG`), evidence not supplied in this crosswalk row. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
