# CBattleEngineWalkerPart__ChargeWeapon

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__ChargeWeapon` at `0x00413cf0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00413cf0`

## Identity
- Body `[0x00413cf0,0x00413ea6]`, 439 bytes, 137 closure instructions. Raw pristine-body SHA-256 `a3549b5cc91c9031465a9be5f2cc930f3a889757d37bc6423eef49d248a15ccc`; closure range SHA-256 `f543760d18905ce8247bbe8183737ccbed0afba69af47ad2aad7ac8a181fdcc3`; packet range-plus-bytes SHA-256 `560f019559dbb7b33fdcdca340e7252b1f402c169cb04e5bb9aced406ea57e11`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__ChargeWeapon` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__ChargeWeapon`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `unknown`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngineWalkerPart__ChargeWeapon(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineWalkerPart__ChargeWeapon(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×3 site(s) (STATIC_DIRECT).
- Callee `ProjectileBurst__SpawnFromPercentBucketFallback` `0x00506010` ×2 site(s) (STATIC_DIRECT).
- Callee `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` `0x005068f0` ×1 site(s) (STATIC_DIRECT).
- Callee `TargetProfileContext__CanProceedByTargetRangeGate` `0x0050a080` ×1 site(s) (STATIC_DIRECT).
- Caller `CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0` `0x00409ef0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-parity correction: WalkerPart ChargeWeapon updates current-entry charge/overheat gates and may dispatch projectile-burst fallback. Static source/decompile evidence only; exact retail CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime charge behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `417020b7ca6b1917517eb04f72da6a41d3f24f7ed871f70808200f22da67a27a`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 5 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 372 covered bytes; evidence `name=CBattleEngineWalkerPart__ChargeWeapon`.

## Evidence
- Immutable manifest `.scratch/wave2/manifests/cohort-5.json`, row 22; manifest specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00413cf0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `417020b7ca6b1917517eb04f72da6a41d3f24f7ed871f70808200f22da67a27a`.
- Digest derivation: closure SHA-256 hashes canonical range text `00413cf0:00413ea6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `unknown` and confidence `unknown`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::ChargeWeapon` line 519 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineWalkerPart.cpp/CBattleEngineWalkerPart__ChargeWeapon.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
