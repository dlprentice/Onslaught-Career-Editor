# CParticleManager__UpdateParticleAndRecycleIfDead

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleManager__UpdateParticleAndRecycleIfDead` at `0x004cb920` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cb920`

## Identity
- Body `[0x004cb920,0x004cba29]`, 266 bytes, 90 closure instructions. Raw pristine-body SHA-256 `9bdb062f28cff1c2c4ecd8c0ba34fe596829066d6dba96cebe2305f5bc70e6b8`; closure range SHA-256 `14517cf82bb2d2bc3ca4d1cf9f8df34bdc32b1ed652068712164fb43fe7a122c`; packet range-plus-bytes SHA-256 `871b28ae2c8d324f130ede15ea13f400e679ceddb4b1a3754b9cae063d52b7f3`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleManager__UpdateParticleAndRecycleIfDead`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `394a576597548fd83bd99991c45b80b8ea5c5122791edbbdc55b621706f0062c` and decompile SHA-256 `e2e15ab738666dff39452e92647b6b19943cf746aaf37bd447762d1f828c257f` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c63f8`, `DAT_009c63fc`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `Vec3__SetXYZ` `0x00401ec0` x1 site(s) (STATIC_DIRECT).
- Callee `CParticle__Destroy` `0x004cae50` x1 site(s) (STATIC_DIRECT).
- Caller `CPDEmitter__VFunc_10_004c1a90` `0x004c1a90` x1 site(s) (instruction-flow).
- Caller `CPDTimeline__VFunc_10_004c2640` `0x004c2640` x1 site(s) (instruction-flow).
- Caller `CPDTrail__VFunc_10_004c36b0` `0x004c36b0` x1 site(s) (instruction-flow).
- Caller `CPDMesh__VFunc_10_004c4dc0` `0x004c4dc0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave994 signature correction: RET 0x4 and the entry-frame read at 0x004cb924 prove one stack argument (particle) after ECX carries the particle manager receiver; this removes the stale unused_context parameter from the Wave463 signature. The body updates one particle's lifetime and position, refreshes attached handle activity/backlink fields, applies the observed death-flag logic, dispatches particle-set vfunc +0x28, and recycles dead particles to the manager free list. Static retail-binary evidence only; runtime particle behavior, exact manager/particle/handle layouts, source identity, BEA patching, and rebuild parity remain separate proof.”
- The non-empty packet decompile is bound by SHA-256 `e2e15ab738666dff39452e92647b6b19943cf746aaf37bd447762d1f828c257f`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 4 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `394a576597548fd83bd99991c45b80b8ea5c5122791edbbdc55b621706f0062c`, and packet decompile SHA-256 `e2e15ab738666dff39452e92647b6b19943cf746aaf37bd447762d1f828c257f`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cb920:004cba29;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
