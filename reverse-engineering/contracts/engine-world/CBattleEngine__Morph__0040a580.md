# CBattleEngine__Morph

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__Morph` at `0x0040a580`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040a580`

## Identity
- Body `[0x0040a580,0x0040a880]`, 769 bytes, 224 closure instructions. Raw pristine-body SHA-256 `c68b3693adb38cf592353905c177abbaaa1bebaf000694282affaf60421e1093`; closure range SHA-256 `7badfbd601fe43f5898133f3e3c258be61908d44f73e9d6c0c706d620d4777f2`; packet range-plus-bytes SHA-256 `019d1854810153629cf801a39a99dbf24243ba60ce1228f6580aa272e4ae27cd`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__Morph` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__Morph`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CBattleEngine__Morph(void * battleEngine)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__Morph(void * battleEngine)
```
- Packet-declared parameter list: `void * battleEngine`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_0067a748`, `DAT_00896988`, `s_flytowalk_006234bc`, `s_walktofly_006234b0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CBattleEngine__SwapPrimarySecondaryPartReadersForState` `0x00406460` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__GetIsDoingSpecialAirMove` `0x00411b70` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__LoseWeaponCharge` `0x00412000` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` `0x004135d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__ClearCurrentTrackedEntryFlag60` `0x00414010` ×1 site(s) (STATIC_DIRECT).
- Callee `CGeneralVolume__BeginFlyToWalkTransition` `0x00424920` ×1 site(s) (STATIC_DIRECT).
- Callee `CGeneralVolume__BeginWalkToFlyTransition` `0x00424990` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×2 site(s) (STATIC_DIRECT).
- Callee `CInfluenceMapManager_T3_0048c000` `0x0048c000` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__FadeTo` `0x004e1260` ×2 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__GetSoundEventForThing` `0x004e1880` ×2 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` ×3 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__IsEffectPlaying` `0x004e1ab0` ×1 site(s) (STATIC_DIRECT).
- Callee `SharedUnitAnimation__PlayAnimationByNameIfPresent` `0x004f4560` ×2 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__Move` `0x004081c0` ×1 site(s) (instruction-flow).
- Caller `CBattleEngine__ClearFlag58CAndMorphIfState3` `0x0040dcc0` ×1 site(s) (instruction-flow).
- Caller `CBattleEngineJetPart__Move` `0x00410c50` ×2 site(s) (instruction-flow).
- Caller `CPlayer__ReceiveButtonAction` `0x004d3110` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `2038-2124` defines `CBattleEngine::Morph` as `void CBattleEngine::Morph()`; exact extracted source-body SHA-256 `032e8e1936ebfaff697bea5543554ba7e5b41ce765f294208e15fea133247a58`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=17, switch=0, for=0, while=0; named call tokens `AddEvent`, `AddResidual`, `AutoZoomOut`, `FadeTo`, `GetIsDoingSpecialAirMove`, `GetIsDoingSpecialWalkerMove`, `GetSoundEventForThing`, `GetThreat`, `GetTime`, `IsEffectPlaying`, `IsOnGround`, `LoseWeaponCharge`, `MassiveHackPutUsInRightMesh`, `MorphIntoJetCockpit`, `MorphIntoWalkerCockpit`, `PlayEffect`, `SetAnimMode`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source bridge/name correction: body matches Stuart CBattleEngine::Morph() by state gates, special-move lockouts, weapon-charge loss, BECOME_WALKER/BECOME_JET events 0x1771/6000, flytowalk/walktofly animation paths, cockpit/part transition calls, and transform audio hooks. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `7ecaf8bde88689b745911139c4b7a154d2d9dfe6021da8da743d57f011cc466c`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 14 callee record(s), and 2 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4`; question `corpus-combat-only`; value: combat-exclusive; 329 covered bytes; evidence `name=CBattleEngine__Morph`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 7; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040a580.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `7ecaf8bde88689b745911139c4b7a154d2d9dfe6021da8da743d57f011cc466c`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040a580:0040a880;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006234b0` length 10 SHA-256 `38b70f1a3a76f778dab6b4fd4e00b4412b30778989bdb07b28151b88487e9558` value “walktofly”.
- Packet string ref `0x006234bc` length 10 SHA-256 `598797526faa7cc0b5260b1d00855c55b4aa7ee7e50f33d674503a04649d828a` value “flytowalk”.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Morph` line 2038 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Morph.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
