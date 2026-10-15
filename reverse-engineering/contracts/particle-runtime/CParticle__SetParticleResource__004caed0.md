# CParticle__SetParticleResource

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticle__SetParticleResource` at `0x004caed0` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004caed0`

## Identity
- Body `[0x004caed0,0x004caf2c]`, 93 bytes, 31 closure instructions. Raw pristine-body SHA-256 `dfd0f42ee962da128d6e155be4d4ef601539421d337ce39f7b4f542d62b00e35`; closure range SHA-256 `36e2fb85a2a6b3cff8b8184f4ef19e890651c842c65ea36b13081d9b840bce6b`; packet range-plus-bytes SHA-256 `f85f301d37024db57136912d74fd6a8ccd6c3b84304468d8dfda012975d4d515`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticle__SetParticleResource`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `4c47e79532ce43ab45cd712bb7ed9656a57709021d39faff7fca00de53e88991` and decompile SHA-256 `fcf33e3704854731fea0befdaf50715e0887598513e5fd09e220c676c4938fc1` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `bool __thiscall CParticle__SetParticleResource(void * this, int resource_size)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
bool __thiscall CParticle__SetParticleResource(void * this, int resource_size)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `bool`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact ABI domain, sentinel behavior, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_ParticleManage_00630e60`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Caller `CEngine__ConfigureParticleBurstForDistance` `0x004c35d0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave463 correction: Replaces the particle +0x88 resource block with a CDXMemoryManager__Alloc of resource_size bytes (alignment 0x10, ParticleManager.cpp site) after freeing any existing block through the same particle-set vfunc +0x38 guard used by CParticle__Destroy. Returns whether the new allocation succeeded. Static retail-binary evidence only; exact layout, source identity, and runtime behavior remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `fcf33e3704854731fea0befdaf50715e0887598513e5fd09e220c676c4938fc1`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 2 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 3; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `4c47e79532ce43ab45cd712bb7ed9656a57709021d39faff7fca00de53e88991`, and packet decompile SHA-256 `fcf33e3704854731fea0befdaf50715e0887598513e5fd09e220c676c4938fc1`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004caed0:004caf2c;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
