# CParticleSet__InitType11

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleSet__InitType11` at `0x004cd290` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cd290`

## Identity
- Body `[0x004cd290,0x004cd2c9]`, 58 bytes, 17 closure instructions. Raw pristine-body SHA-256 `7f7b1d9d2831bad9d249b8311fcd61a6bdd99550ff7cd879c17cc305e3f5a179`; closure range SHA-256 `0d30c85e5359cf3163cd7ca2feaa52731e3b418abfb2246cabf30316522b66b0`; packet range-plus-bytes SHA-256 `f75e97e47528c08fc342eefebaa99f9730ae5c607f91885758d655a280cffeff`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleSet__InitType11`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `3df251c6eebab710444b498617d0989804d4396a0b35d0e65458e9d133eaf2ed` and decompile SHA-256 `8a3a844c2054c70633bd7ca23d4fb3e229238684c51c67b1b77550e4a8ebc896` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CParticleSet__InitType11(void * particle_set)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CParticleSet__InitType11(void * particle_set)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `PTR_CPDMesh__scalar_deleting_dtor_005ddb3c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CParticleSet__CreateByType` `0x004cc020` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave464 correction: Initializes ParticleSet type 11 by clearing shared base fields, installing vtable PTR_CPDMesh__scalar_deleting_dtor_005ddb3c, and seeding observed defaults including +0x64=100 and +0x74=1. Static retail-binary evidence only; exact type semantics, source identity, runtime behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `8a3a844c2054c70633bd7ca23d4fb3e229238684c51c67b1b77550e4a8ebc896`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `3df251c6eebab710444b498617d0989804d4396a0b35d0e65458e9d133eaf2ed`, and packet decompile SHA-256 `8a3a844c2054c70633bd7ca23d4fb3e229238684c51c67b1b77550e4a8ebc896`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cd290:004cd2c9;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
