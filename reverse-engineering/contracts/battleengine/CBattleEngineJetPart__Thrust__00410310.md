# CBattleEngineJetPart__Thrust

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineJetPart__Thrust` at `0x00410310`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00410310`

## Identity
- Body `[0x00410310,0x00410482]`, 371 bytes, 105 closure instructions. Raw pristine-body SHA-256 `45d88c04f94fdaa793b9b26b2a92b76cdbdb35c8189e9dfbe7a3412937296aa6`; closure range SHA-256 `089c5175a6e5d3932eaedf6242e23b65cfc77741029abf594052fd047ef62232`; packet range-plus-bytes SHA-256 `b2126827de0b96acd3d71d354f523c0c4dec312546d8461fe5345d7bbd28d4d7`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineJetPart__Thrust` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineJetPart__Thrust`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngineJetPart__Thrust(void * this, float moveY)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineJetPart__Thrust(void * this, float moveY)
```
- Packet-declared parameter list: `void * this, float moveY`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CPlayer__ReceiveButtonAction` `0x004d3110` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source/decompile correction: CBattleEngineJetPart::Thrust updates the thruster value from moveY, tracks hard-forward timing, starts loop state when the forward/backward threshold sequence, energy gate, and velocity gate agree, and stores the last Y input. Runtime input behavior and concrete layout remain unproven.”
- The displayed decompile is non-empty and SHA-256 `dd77ce6f0908b447a2222c52df1d6f9e5f0ae4d0c4e7863cc46b3ee633e57ec1`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 1; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00410310.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `dd77ce6f0908b447a2222c52df1d6f9e5f0ae4d0c4e7863cc46b3ee633e57ec1`.
- Digest derivation: closure SHA-256 hashes canonical range text `00410310:00410482;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::Thrust` line 64 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineJetPart.cpp/CBattleEngineJetPart__Thrust.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
