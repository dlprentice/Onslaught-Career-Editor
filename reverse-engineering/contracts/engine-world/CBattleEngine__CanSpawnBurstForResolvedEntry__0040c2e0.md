# CBattleEngine__CanSpawnBurstForResolvedEntry

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__CanSpawnBurstForResolvedEntry` at `0x0040c2e0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c2e0`

## Identity
- Body `[0x0040c2e0,0x0040c336]`, 87 bytes, 28 closure instructions. Raw pristine-body SHA-256 `3d755ee793a412419c9ffcabe94a88d88d6c75513af315c229b5a9d7f23b3d82`; closure range SHA-256 `93986dadd29db3ac11505d565c73c180ac03e2758e29d3769f63703bdba03022`; packet range-plus-bytes SHA-256 `51c8cab2bcb66ba40a7405fa4f4eecb5dd3e6ce8d2a868ebee47f42728c3592e`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__CanSpawnBurstForResolvedEntry` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__CanSpawnBurstForResolvedEntry`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngine__CanSpawnBurstForResolvedEntry(void * this, void * burstContext)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngine__CanSpawnBurstForResolvedEntry(void * this, void * burstContext)
```
- Packet-declared parameter list: `void * this, void * burstContext`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CBattleEngineJetPart__WeaponFired` `0x00412050` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__WeaponFired` `0x004140d0` ×1 site(s) (STATIC_DIRECT).
- Caller `ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature re-audit: BattleEngine-owned burst quota helper. Called by the current-preset projectile-burst body with a weapon/burst context, tries the +0x57c and +0x578 part paths, clears +0x5d8 on success, and returns a boolean-style result. Helper-level static evidence only; this does not prove exact CWeapon::Fire, CBattleEngine::WeaponFired, or stealth-reset runtime behavior.”
- The displayed decompile is non-empty and SHA-256 `091658f4a3f97925e3407dadb1d341a9130aa57d1bf0a607a09e57eed893438c`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 200 covered bytes; evidence `name=CBattleEngine__CanSpawnBurstForResolvedEntry`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 10; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c2e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `091658f4a3f97925e3407dadb1d341a9130aa57d1bf0a607a09e57eed893438c`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040c2e0:0040c336;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
