# CParticle__ApplyParentTransformOrStoreLink

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticle__ApplyParentTransformOrStoreLink` at `0x004c0150` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004c0150`

## Identity
- Body `[0x004c0150,0x004c0361]`, 530 bytes, 192 closure instructions. Raw pristine-body SHA-256 `a7f8fabc84a8437e5368c9b03e66bdfee37db8f1e9bf6299386e517868a3a05b`; closure range SHA-256 `fcd8a769a0a81284a7a470dfa0fd6793351359e255932f373131de2cdff6799f`; packet range-plus-bytes SHA-256 `701514d73f9b282760aa852f544890a87b7ccbb68cc5a4ba523ee45b5edb5111`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticle__ApplyParentTransformOrStoreLink`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `1e42e05f687e0f09b91b944d8443b33b43685a767e0d8b6665ca0489e6eb9e12` and decompile SHA-256 `80626218678cce6a43f3d8d231a3f8d128872a451613b2c946b924efae162af8` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `Vec3__SetXYZ` `0x00401ec0` x3 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetRows` `0x00401f10` x1 site(s) (STATIC_DIRECT).
- Callee `Mat34__TransformVec3ByBasisToOut` `0x0040d2c0` x1 site(s) (STATIC_DIRECT).
- Caller `CPDMesh__VFunc_10_004c4dc0` `0x004c4dc0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave476 owner/signature correction: this helper is reached from particle descriptor update/allocation code at raw caller 0x004c524f, takes a particle pointer, parent-particle pointer, and link-parent-only flag, and has no current CUnitAI evidence. Nonzero link_parent_only stores parent_particle at particle +0x58 and returns; otherwise it composes the particle basis/position fields +0x8..+0x54 through the parent transform when parent_particle and its transform block at +0xa0 are present, then adds parent position into particle +0x38/+0x3c/+0x40. Static retail-binary evidence only; exact particle layout, raw caller boundary/name, source identity, runtime particle behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `80626218678cce6a43f3d8d231a3f8d128872a451613b2c946b924efae162af8`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 3 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 1; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `1e42e05f687e0f09b91b944d8443b33b43685a767e0d8b6665ca0489e6eb9e12`, and packet decompile SHA-256 `80626218678cce6a43f3d8d231a3f8d128872a451613b2c946b924efae162af8`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004c0150:004c0361;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
