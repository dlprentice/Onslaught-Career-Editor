# CBattleEngineWalkerPart__WeaponFired

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__WeaponFired` at `0x004140d0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004140d0`

## Identity
- Body `[0x004140d0,0x00414406]`, 823 bytes, 220 closure instructions. Raw pristine-body SHA-256 `a9c2ed4de55f1c3bc4bee4a459e9e7c31e2ff17b8b3cd7eb286f5c0cbffb5f65`; closure range SHA-256 `ead4f6f352cb2efa35544cbfb7dfeb5f47d3523b5670f6702b1054ebc6223a54`; packet range-plus-bytes SHA-256 `d6881612dcc0b52a5579708de86d9916488e926b51abf7711e15ce67865dd26b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__WeaponFired` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__WeaponFired`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `unknown`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngineWalkerPart__WeaponFired(void * this, void * weapon)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngineWalkerPart__WeaponFired(void * this, void * weapon)
```
- Packet-declared parameter list: `void * this, void * weapon`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110` ×3 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__CanSpawnBurstForResolvedEntry` `0x0040c2e0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-parity correction: WalkerPart WeaponFired has one stack argument (ret 0x4) for the weapon pointer and updates store value/heat/overheat state for list, primary, and augmented weapons. Static source/decompile/instruction evidence only; exact retail CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime firing behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `bb615714042595147f361cf401dafa80be5515028d5ee4971d792703799ec155`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 480 covered bytes; evidence `name=CBattleEngineWalkerPart__WeaponFired`.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004140d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `bb615714042595147f361cf401dafa80be5515028d5ee4971d792703799ec155`.
- Digest derivation: closure SHA-256 hashes canonical range text `004140d0:00414406;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `unknown` and confidence `unknown`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::WeaponFired` line 686 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineWalkerPart.cpp/CBattleEngineWalkerPart__WeaponFired.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
