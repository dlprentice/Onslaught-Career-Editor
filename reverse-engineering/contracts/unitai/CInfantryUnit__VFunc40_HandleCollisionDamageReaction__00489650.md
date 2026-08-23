# CInfantryUnit__VFunc40_HandleCollisionDamageReaction

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CInfantryUnit__VFunc40_HandleCollisionDamageReaction` at `0x00489650`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00489650`

## Identity
- Body `[0x00489650,0x00489b38]`, 1257 bytes, 384 closure instructions. Raw pristine-body SHA-256 `7c6de4139b0a44ed45b5de2ab7993353b01db19c9e68da5137525e37800552d2`; closure range SHA-256 `f2036d2ad4e5b257c5b8463a80a2ac44443b163428ceda15196e167e8bdd33ef`; packet range-plus-bytes SHA-256 `2f470b17d76080d57a6675cbc88839a976701c2ecb5aeec1e9cda1c1c79357e2`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CInfantryUnit__VFunc40_HandleCollisionDamageReaction` comes from the current closure/register row. Packet label matches canonical tracked name `CInfantryUnit__VFunc40_HandleCollisionDamageReaction`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CInfantryUnit__VFunc40_HandleCollisionDamageReaction(void * this, void * collisionContext, void * otherThing, void * impactContext, void * damageContext)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CInfantryUnit__VFunc40_HandleCollisionDamageReaction(void * this, void * collisionContext, void * otherThing, void * impactContext, void * damageContext)
```
- Packet-declared parameter list: `void * this, void * collisionContext, void * otherThing, void * impactContext, void * damageContext`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0083d9c0`, `DAT_008a9d9c`, `s_ateam_0062d4ec`, `s_die_back_0062d530`, `s_die_forward_0062d554`, `s_die_left_0062d53c`, `s_die_right_0062d548`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CMesh__FindAnimationIndexByName` `0x004aa630` ×2 site(s) (STATIC_DIRECT).
- Callee `CRound__GetPresetScalarByConfigName` `0x004db090` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×4 site(s) (STATIC_DIRECT).
- Callee `CComplexThing__SetAnimMode` `0x004f44a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ApplyDamage` `0x004f9a90` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1076 boundary recovery: CInfantryUnit primary vtable 0x005e2730 slot 39 (slot address 0x005e27cc) DATA-xrefs to this previously missing function. Fresh pre-state listed the entry as INSTRUCTION_NO_FUNCTION with missing metadata and missing decompile; the recovered body ends at 0x00489b36 RET 0x10 and does not absorb the next adjacent entry/function at 0x00489b40. Body checks this+0x2c and otherThing+0x34 flags, samples CRound__GetPresetScalarByConfigName and Random__NextLCGAbs, computes distance/impact vectors, can call CUnit__ApplyDamage, and uses animation/effect dispatch helpers before returning through the shared tail at 0x00489b31. Static retail Ghidra metadata/xref/instruction/vtable evidence only; exact source virtual name, concrete CInfantryUnit/CUnitAI/layout semantics, runtime infantry behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `bcc599e257d0fb44cff18453886c895db81990120b9787c067d68da4ddbb13c5`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 5 callee record(s), and 5 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 549 covered bytes; evidence `name=CInfantryUnit__VFunc40_HandleCollisionDamageReaction`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 7; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00489650.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `bcc599e257d0fb44cff18453886c895db81990120b9787c067d68da4ddbb13c5`.
- Digest derivation: closure SHA-256 hashes canonical range text `00489650:00489b38;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062d4ec` length 6 SHA-256 `17f59eec788556664dc6950bb12435403e9e6ffbdf389a967a69c9b16817d227` value `ateam`.
- Packet string ref `0x0062d530` length 9 SHA-256 `c6c846be9a24c1916b1e4495e0ad2ea6d9cd5262a58cbdf24b89416de3f8c60c` value `die_back`.
- Packet string ref `0x0062d53c` length 9 SHA-256 `20eb54ca5f0ad6e25cfcf96c631b0b306d0d9e04cb5e6994b31bda23b2e712ce` value `die_left`.
- Packet string ref `0x0062d548` length 10 SHA-256 `353f22af3f8b91e301ad09f3f25c2ed1bf92a8b278edeaf1458affad4c349fee` value `die_right`.
- Packet string ref `0x0062d554` length 12 SHA-256 `6ad0a58cafa6e2c5a6d57be132f3ce526bfa3b631b8583b6df733288bfee8cb2` value `die_forward`.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
