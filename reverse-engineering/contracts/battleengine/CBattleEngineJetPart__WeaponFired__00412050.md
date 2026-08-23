# CBattleEngineJetPart__WeaponFired

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineJetPart__WeaponFired` at `0x00412050`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00412050`

## Identity
- Body `[0x00412050,0x004121a2]`, 339 bytes, 99 closure instructions. Raw pristine-body SHA-256 `9526b4cfa6ff6853a291443c3bccce17556a05e5b45f7130954b9bc10af73e0f`; closure range SHA-256 `56a8a5ed28ea96f705322ca532a12a86bea8d8f628761c91fefb2cb7859f0200`; packet range-plus-bytes SHA-256 `add14a473da5a3fb3675fdab1b5a841ead94971f2147052df63b87a72abfaac4`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineJetPart__WeaponFired` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineJetPart__WeaponFired`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `unknown`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngineJetPart__WeaponFired(void * this, void * weapon)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngineJetPart__WeaponFired(void * this, void * weapon)
```
- Packet-declared parameter list: `void * this, void * weapon`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `_DAT_006236a4`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__CanSpawnBurstForResolvedEntry` `0x0040c2e0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature correction: CBattleEngine__CanSpawnBurstForResolvedEntry calls this through battleEngine +0x57c with the resolved weapon context; ret 0x4 and source/decompile evidence match JetPart weapon-fired quota, ammo depletion, heat/overheat, and cooldown bookkeeping. It does not prove CBattleEngine::WeaponFired stealth reset identity or runtime cloak behavior.”
- The displayed decompile is non-empty and SHA-256 `fc6417f5568e2875893a0a1541163fd7da6b0428c1b303f7df1ebd3786ddcee7`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 337 covered bytes; evidence `name=CBattleEngineJetPart__WeaponFired`.

## Evidence
- Immutable manifest `.scratch/wave2/manifests/cohort-5.json`, row 8; manifest specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00412050.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `fc6417f5568e2875893a0a1541163fd7da6b0428c1b303f7df1ebd3786ddcee7`.
- Digest derivation: closure SHA-256 hashes canonical range text `00412050:004121a2;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `unknown` and confidence `unknown`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::WeaponFired` line 776 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineJetPart.cpp/CBattleEngineJetPart__WeaponFired.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
