# CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` at `0x004135d0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004135d0`

## Identity
- Body `[0x004135d0,0x004135da]`, 11 bytes, 5 closure instructions. Raw pristine-body SHA-256 `830e32791fddba2114efcd1a81683c45cc0f9a7ab57d46f2eade1832729248f3`; closure range SHA-256 `769e8bd5457505e25784a0dca22f27146659c9fcfbbc751e3e73504a9e25fafe`; packet range-plus-bytes SHA-256 `0ad127987fe4b92724f11837935883db56839249542f66ccbc8356f25d87e4d9`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `CANDIDATE_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CBattleEngine__Morph` `0x0040a580` ×1 site(s) (instruction-flow).
- Caller `CBattleEngine__VFunc_104_0040e7d0` `0x0040e7d0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature correction: WalkerPart predicate returns whether dash/special-walker counter +0x44 is active, matching the source GetIsDoingSpecialWalkerMove shape. Runtime dash behavior and concrete layout remain unproven.”
- The displayed decompile is non-empty and SHA-256 `bd7d823d2f24d9c50963425ff9dd8507d8a9b3ee46057b92e9929bca7cca2c1c`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Immutable manifest `.scratch/wave2/manifests/cohort-5.json`, row 18; manifest specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004135d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `bd7d823d2f24d9c50963425ff9dd8507d8a9b3ee46057b92e9929bca7cca2c1c`.
- Digest derivation: closure SHA-256 hashes canonical range text `004135d0:004135da;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `CANDIDATE_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::GetIsDoingSpecialWalkerMove` line 320 (`SOURCE_ANALOG`), evidence not supplied in this crosswalk row. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
