# CUnitAI__Update

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__Update` at `0x004fef40`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fef40`

## Identity
- Body `[0x004fef40,0x004ff321]`, 994 bytes, 300 closure instructions. Raw pristine-body SHA-256 `7aca029cc9b576958d86a01282e847e6b624d29dcbc23b4ae2b89cbf8193fffe`; closure range SHA-256 `e39944ad5f5c17b54941b7ff7204609f72aecb3f98553dd5109773fb2d6ff305`; packet range-plus-bytes SHA-256 `9127a58d3e0444850ca7f4530555efd73c8cb948001dbab8654e4a04829efd11`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__Update` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__Update`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `float __fastcall CUnitAI__Update(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
float __fastcall CUnitAI__Update(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `float`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `vector_constructor_iterator_nothrow` `0x004011b0` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__SetXYZ` `0x00401ec0` ×3 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×7 site(s) (STATIC_DIRECT).
- Callee `CUnit__ForwardAimTransformAndAttachTargetReader` `0x004fb650` ×3 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__SelectBestSupportOrEscort` `0x004fb840` ×2 site(s) (STATIC_DIRECT).
- Callee `CWarspite__GetMountedUnitPitchOrZero` `0x004fbc90` ×1 site(s) (STATIC_DIRECT).
- Callee `CWarspite__TransitionToUndeploying` `0x004fde70` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave528 Unit/Warspite command-tail signature/comment hardening: ECX-only vtable update returns a float-like delay/angle value through the x87 path. The body advances base state, checks owner unit vfunc +0x150, handles target/reader state, updates aim through CUnit__ForwardAimTransformAndAttachTargetReader, refreshes support selection through CSquadNormal__SelectBestSupportOrEscort, may call CWarspite__TransitionToUndeploying, and returns randomized timing/oscillation values from profile flags. Static retail evidence only; exact return contract, Warspite state layout, runtime AI behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `77c66f4c1018ca9940b8e60b676339ec87a2703e2703ae5846b82e2df48a8124`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 9 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 20; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fef40.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `77c66f4c1018ca9940b8e60b676339ec87a2703e2703ae5846b82e2df48a8124`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fef40:004ff321;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
