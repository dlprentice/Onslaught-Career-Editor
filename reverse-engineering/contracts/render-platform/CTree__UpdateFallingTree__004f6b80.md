# CTree__UpdateFallingTree

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CTree__UpdateFallingTree` at `0x004f6b80` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f6b80`

## Identity
- Body `[0x004f6b80,0x004f6fc3]`, 1092 bytes, 298 closure instructions. Raw pristine-body SHA-256 `1d981c5c662ac0eeccc7e82e533acb5ba0db6931bfb489030cd83b08b3bce702`; closure range SHA-256 `b269ef4939978f56fd74fec05da1ec1b5f4b74f0e8f045c57a217d397fdc5cba`; packet range-plus-bytes SHA-256 `c0da6ae332048c1fbb7f5524e79df8191a711cd3b48cfd6fd1422b2c088fa66c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CTree__UpdateFallingTree`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `13c58b3b74b571663fbdb3570a8b0b1514de3ffa04bcc381ff3ee97f91bfb794` and decompile SHA-256 `31dfc6547d453fd95bbebb8e8932013db2649106ac06a36ba9dc0bfcada99b52` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CTree__UpdateFallingTree(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CTree__UpdateFallingTree(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_006fadc8`, `DAT_0082b400`, `DAT_00840ce8`, `DAT_00840cec`, `DAT_00840cf0`, `DAT_00840cf4`, `s_Tree_Ground_Hit_Effect_00633aa0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `Vec3__SetXYZ` `0x00401ec0` x1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` x1 site(s) (STATIC_DIRECT).
- Callee `CUnit__PushTransformHistoryAndSetCurrent` `0x004097a0` x1 site(s) (STATIC_DIRECT).
- Callee `Mat34__MultiplyBasisToOut` `0x0040d320` x1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_TimeFromNow` `0x0044b2d0` x1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` x1 site(s) (STATIC_DIRECT).
- Callee `CHeightField__TraceLineAgainstHeightfield` `0x00490a40` x1 site(s) (STATIC_DIRECT).
- Callee `ParticleEffectLink_T3_004cb040` `0x004cb040` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__RemoveOwnerLinkFromGlobalList` `0x004cb050` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__FindByNameAndTrackLinkSlot` `0x004cd7a0` x1 site(s) (STATIC_DIRECT).
- Caller `CTree__CreateFallingTree` `0x004f69b0` x1 site(s) (instruction-flow).
- Caller `CTree__HandleEvent` `0x004f7050` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave520 CTree signature/comment hardening: CTree__CreateFallingTree and the recovered event-handler boundary call this with ECX as the tree object. The body updates the falling-tree data at this+0x48 by copying current to previous matrix slots, tracing downward against the heightfield while velocity is positive, spawning the "Tree Ground Hit Effect" particle on sufficiently strong ground impact, damping/reversing velocity on contact, settling to DAT_00672fd0 and scheduling event 0x7d2 when motion falls below the threshold, otherwise integrating angle/velocity, rebuilding the rotation matrix, writing the current matrix, and rescheduling event 3000. Static retail evidence only; exact source identity, concrete layouts, runtime particle/physics behavior, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `31dfc6547d453fd95bbebb8e8932013db2649106ac06a36ba9dc0bfcada99b52`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 2 caller record(s), 11 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 20; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `13c58b3b74b571663fbdb3570a8b0b1514de3ffa04bcc381ff3ee97f91bfb794`, and packet decompile SHA-256 `31dfc6547d453fd95bbebb8e8932013db2649106ac06a36ba9dc0bfcada99b52`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004f6b80:004f6fc3;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00633aa0` length 23 SHA-256 `b074c9ea96d82e30513b04b4ffe4ab2f736fbfc9d3f4bd971589305fbf804208` value “Tree Ground Hit Effect”.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
