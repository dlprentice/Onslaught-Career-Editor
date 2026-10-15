# CParticleManager__UpdateRenderNodesAndResetState

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleManager__UpdateRenderNodesAndResetState` at `0x004cbc60` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cbc60`

## Identity
- Body `[0x004cbc60,0x004cbc96]`, 55 bytes, 22 closure instructions. Raw pristine-body SHA-256 `a26e08791f4905b0b3d3756d2c1ac9fc6ad6d5c43345cc565ab08e88d70dfb6b`; closure range SHA-256 `a49319542784fd92ef796cf6bde192e16d0238c0921ac5af40594e0c60e88b81`; packet range-plus-bytes SHA-256 `ed85ba23800684f2801bf553fbc19bde843f61f8fb063150e75b5d1404ae5d11`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleManager__UpdateRenderNodesAndResetState`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `86d73dd3a8865557c4408a5768102e070008bca1d53dd5cf54e57f0f606f4f8e` and decompile SHA-256 `6a4cd64059450122f7140f9abded1a3501dee997ae00b8d523aba17319af5353` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__cdecl` for `void __cdecl CParticleManager__UpdateRenderNodesAndResetState(void)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __cdecl CParticleManager__UpdateRenderNodesAndResetState(void)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0082b404`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `RenderState_Set` `0x00513bc0` x1 site(s) (STATIC_DIRECT).
- Caller `CDXEngine__Render` `0x0053e2e0` x1 site(s) (instruction-flow).
- Caller `CDXFrontEnd__SetupRenderMatricesAndProjection` `0x00540c30` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave822 static read-back/signature hardening: no-argument render-node helper walks DAT_0082b404 via node+0x40, calls vfunc +0x4 to identify observed type 0xb nodes, calls vfunc +0x5c with argument 0 for those nodes, then restores render-state slot 0xf to 1 through RenderState_Set. Xrefs are CDXEngine__Render and CDXFrontEnd__SetupRenderMatricesAndProjection. Static retail Ghidra evidence only; exact render-node type identity, runtime render behavior, source-body identity, BEA patching, and rebuild parity remain deferred.”
- The non-empty packet decompile is bound by SHA-256 `6a4cd64059450122f7140f9abded1a3501dee997ae00b8d523aba17319af5353`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 2 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 15; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `86d73dd3a8865557c4408a5768102e070008bca1d53dd5cf54e57f0f606f4f8e`, and packet decompile SHA-256 `6a4cd64059450122f7140f9abded1a3501dee997ae00b8d523aba17319af5353`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cbc60:004cbc96;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
