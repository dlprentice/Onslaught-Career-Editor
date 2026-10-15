# CParticleManager__AllocateParticle

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleManager__AllocateParticle` at `0x004cb5c0` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cb5c0`

## Identity
- Body `[0x004cb5c0,0x004cb8f6]`, 823 bytes, 239 closure instructions. Raw pristine-body SHA-256 `e6415e33c86052b311bf7db6762d88908ea01cca7fbbbfd65726738443cc3e3a`; closure range SHA-256 `c95a4e412dcffe819d2dc5536bd0d8f5a217bf10144f9c9c313359b5a9c92a54`; packet range-plus-bytes SHA-256 `a88031d98aad24ed04c8b7f6229fd64036b761ddfc0b59f1b104239b474fa6a9`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleManager__AllocateParticle`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a51b58c5dab6fbc706d38b2d90d80ab0eafa120f0cc4093cdff826abd2ebd52b` and decompile SHA-256 `2e81aefcd0b6e3aaf9a74748664b3afa2f0cc065f88e7b6e18900e231cde2517` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void *`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact ABI domain, sentinel behavior, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `DAT_0082b3a0`, `DAT_0082b3d0`, `DAT_0082b3d4`, `DAT_0082b3d8`, `DAT_0082b3dc`, `DAT_0082b3e0`, `DAT_0082b3ec`, `DAT_0082b3f0`, `DAT_0082b3f4`, `DAT_008a9a98`, `DAT_009c3df0`, `DAT_009c6400`, `s_C__dev_ONSLAUGHT2_ParticleManage_00630e60`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CGame__IsMultiplayer` `0x004725d0` x2 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__AppendNodeToActiveList` `0x004c0510` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__UnlinkNodeFromActiveList` `0x004c0560` x1 site(s) (STATIC_DIRECT).
- Callee `CParticle__Destroy` `0x004cae50` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__Init` `0x004cb0e0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Caller `CPDEmitter__VFunc_10_004c1a90` `0x004c1a90` x1 site(s) (instruction-flow).
- Caller `CPDTimeline__VFunc_10_004c2640` `0x004c2640` x1 site(s) (instruction-flow).
- Caller `CPDTrail__VFunc_10_004c36b0` `0x004c36b0` x1 site(s) (instruction-flow).
- Caller `CPDMesh__VFunc_10_004c4dc0` `0x004c4dc0` x1 site(s) (instruction-flow).
- Caller `CPDFoR__Update` `0x004c5410` x1 site(s) (instruction-flow).
- Caller `CParticleManager__CreateEffect` `0x004cb3d0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave463 correction: Allocates or recycles a particle node from the manager free list, creates another manager pool when capacity allows, applies effect-type LOD skip thresholds, initializes node transform/state fields, links the particle set, and dispatches the particle-set vfunc +0x24 initializer. Static retail-binary evidence only; runtime LOD behavior, exact layout, source identity, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `2e81aefcd0b6e3aaf9a74748664b3afa2f0cc065f88e7b6e18900e231cde2517`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 6 caller record(s), 6 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 11; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a51b58c5dab6fbc706d38b2d90d80ab0eafa120f0cc4093cdff826abd2ebd52b`, and packet decompile SHA-256 `2e81aefcd0b6e3aaf9a74748664b3afa2f0cc065f88e7b6e18900e231cde2517`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cb5c0:004cb8f6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00630e60` length 38 SHA-256 `c1807ca6bc166c0c0bb6801fe91470d2c70fb7abc1d73c6934b80f449aea18e0` value `C:\\dev\\ONSLAUGHT2\\ParticleManager.cpp`.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
