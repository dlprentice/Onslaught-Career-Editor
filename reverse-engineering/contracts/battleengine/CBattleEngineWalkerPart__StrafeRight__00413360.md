# CBattleEngineWalkerPart__StrafeRight

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__StrafeRight` at `0x00413360`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00413360`

## Identity
- Body `[0x00413360,0x004135c1]`, 610 bytes, 172 closure instructions. Raw pristine-body SHA-256 `9872c30a8763e6aef8c5975c0055e934fe7ec4afeaab61e94da468ad9e1d918e`; closure range SHA-256 `eecabd726e2b054e5cf665729ef5d4da290c78eebbda1398e2b46d78f94736ae`; packet range-plus-bytes SHA-256 `e1bdb78546d35b58fe43e5866680f2463291338bfe55499cf4e4c28c3f6cf7e1`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__StrafeRight` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__StrafeRight`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngineWalkerPart__StrafeRight(void * this, float moveX)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineWalkerPart__StrafeRight(void * this, float moveX)
```
- Packet-declared parameter list: `void * this, float moveX`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_006236b8`, `DAT_0066f580`, `DAT_00672fd0`, `DAT_00896988`, `_DAT_006236ac`, `_DAT_006236b0`, `_DAT_006236b4`, `_DAT_006236c0`, `s_do_dash_RIGHT_00623944`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` ×1 site(s) (STATIC_DIRECT).
- Caller `CPlayer__ReceiveButtonAction` `0x004d3110` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature correction: WalkerPart strafe-right helper uses moveX, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, roll velocity decrement, and lateral velocity injection. Runtime dash behavior remains unproven.”
- The displayed decompile is non-empty and SHA-256 `67dd4359145a7832c54ffd50837d57288a15236726635d5b753ccbd57c73b95a`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 3 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 17; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00413360.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `67dd4359145a7832c54ffd50837d57288a15236726635d5b753ccbd57c73b95a`.
- Digest derivation: closure SHA-256 hashes canonical range text `00413360:004135c1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00623944` length 14 SHA-256 `911eb84aa770b6fe0ebcb2f97677be0674374c7d05bf84921ab9781ceb0c2e11` value `do dash RIGHT`.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::StrafeRight` line 265 (`SOURCE_ANALOG`), evidence not supplied in this crosswalk row. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
