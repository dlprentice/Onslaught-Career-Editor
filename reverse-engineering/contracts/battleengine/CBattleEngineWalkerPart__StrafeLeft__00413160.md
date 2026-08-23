# CBattleEngineWalkerPart__StrafeLeft

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__StrafeLeft` at `0x00413160`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00413160`

## Identity
- Body `[0x00413160,0x0041335f]`, 512 bytes, 144 closure instructions. Raw pristine-body SHA-256 `f73bf900aff3f6b19d141656b8432f72a385d3fc58b2e7c3cd2305058deaf206`; closure range SHA-256 `6d568526fb98ee6d5940364aa998ac3368d8e8b90976f25d3014950813dfa10c`; packet range-plus-bytes SHA-256 `0b94db2122311a0c44bf230e70c30fba624fe1ea79f49c9217a9c20f851e9a54`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__StrafeLeft` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__StrafeLeft`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngineWalkerPart__StrafeLeft(void * this, float moveX)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineWalkerPart__StrafeLeft(void * this, float moveX)
```
- Packet-declared parameter list: `void * this, float moveX`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_006236b8`, `DAT_0066f580`, `DAT_00672fd0`, `DAT_00896988`, `_DAT_006236ac`, `_DAT_006236b0`, `_DAT_006236b4`, `_DAT_006236c0`, `s_do_dash_LEFT_00623934`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` ×1 site(s) (STATIC_DIRECT).
- Caller `CPlayer__ReceiveButtonAction` `0x004d3110` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature correction: WalkerPart strafe-left helper uses moveX, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, roll velocity bump, and lateral velocity injection. Runtime dash behavior remains unproven.”
- The displayed decompile is non-empty and SHA-256 `48bf6a11db05f90546758b65aa228babed4599eaf3612183aa146a32e34e834f`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 4 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Immutable manifest `.scratch/wave2/manifests/cohort-5.json`, row 16; manifest specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00413160.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `48bf6a11db05f90546758b65aa228babed4599eaf3612183aa146a32e34e834f`.
- Digest derivation: closure SHA-256 hashes canonical range text `00413160:0041335f;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00623934` length 13 SHA-256 `d6cc18f037cf95105121f511ba85a46d395841f399fa16d39b36297c3b801488` value `do dash LEFT`.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::StrafeLeft` line 214 (`SOURCE_ANALOG`), evidence not supplied in this crosswalk row. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
