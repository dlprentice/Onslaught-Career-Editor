# CBattleEngineJetPart__Turn

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineJetPart__Turn` at `0x00410490`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineJetPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00410490`

## Identity
- Body `[0x00410490,0x00410669]`, 474 bytes, 150 closure instructions. Raw pristine-body SHA-256 `ab7d98c7851747a5cdb7e83eac9e3f68f587e2847a87b75daec5a260c640da76`; closure range SHA-256 `6c0b212936107841cbd66c1d158e3fba97a27013c073f82c24d809356ee9ad45`; packet range-plus-bytes SHA-256 `913efc59b4b3132e12ad10c4dc7a1426a85ec701d47ce979f4c0eb1a71c3d0e5`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineJetPart__Turn` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineJetPart__Turn`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngineJetPart__Turn(void * this, float moveX)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngineJetPart__Turn(void * this, float moveX)
```
- Packet-declared parameter list: `void * this, float moveX`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGeneralVolume__ToDoubleIdentity` `0x00409e60` ×2 site(s) (STATIC_DIRECT).
- Caller `CPlayer__ReceiveButtonAction` `0x004d3110` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source/decompile correction: CBattleEngineJetPart::Turn applies yaw and roll velocity from moveX, scales by configuration turn rate, zoom, low-speed grounded movement, slow movement, and transform-start interpolation before updating main-part yaw/roll velocity. Runtime input behavior and concrete layout remain unproven.”
- The displayed decompile is non-empty and SHA-256 `559f043f162a1ae4afca45be0ad16cc7290e790467f4d84ff9a20a03c7a5bbaf`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00410490.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `559f043f162a1ae4afca45be0ad16cc7290e790467f4d84ff9a20a03c7a5bbaf`.
- Digest derivation: closure SHA-256 hashes canonical range text `00410490:00410669;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineJetPart.cpp` `CBattleEngineJetPart::Turn` line 109 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngineJetPart.cpp/CBattleEngineJetPart__Turn.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
