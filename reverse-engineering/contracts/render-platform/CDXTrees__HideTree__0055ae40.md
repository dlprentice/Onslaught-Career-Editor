# CDXTrees__HideTree

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CDXTrees__HideTree` at `0x0055ae40` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0055ae40`

## Identity
- Body `[0x0055ae40,0x0055af89]`, 330 bytes, 102 closure instructions. Raw pristine-body SHA-256 `2251d8dd00f9eca25265ccb14a35a0167abd691241c77b8056bbd4430db68a82`; closure range SHA-256 `cac432bf9083cfedde8a87457a6e7a8654b4aa359d108fad46e8fc396f7053a8`; packet range-plus-bytes SHA-256 `8b24e5add6e2069887007445c4462e95ab3bdd842c3a68f57dd793e5f4e7c113`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CDXTrees__HideTree`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `4f6c92135bf99406ef071d6fa42f719408544a9a7dc6cd74b757838f0d0d5d3d` and decompile SHA-256 `1897ce4e6aa3ab2999a698549c424188acc09131d1fcad982bf7dd99eb372214` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CDXTrees__HideTree(void * this, void * tree_object)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CDXTrees__HideTree(void * this, void * tree_object)
```
- Packet-declared parameter list: `void * this, void * tree_object`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CVBuffer__Unlock` `0x005001e0` x2 site(s) (STATIC_DIRECT).
- Callee `CVBuffer__LockRange` `0x00500390` x2 site(s) (STATIC_DIRECT).
- Caller `CRTTree__Destructor` `0x004ddfd0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave618 CDXTrees head hardening: CRTTree__Destructor callsite 0x004de001 pushes the tree object and passes global tree renderer 0x009cc148 in ECX; RET 0x4 confirms one explicit stack argument. Body reads the tree vertex index at tree_object+0x30, requires both tree buffers to exist, locks 0x90 bytes at vertex_index*0x24 in each backing CVBuffer, zeros the four vertex position triples, then unlocks. Static retail decompile/xref/instruction evidence only; exact CRTTree/layout semantics, runtime tree destruction visibility, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `1897ce4e6aa3ab2999a698549c424188acc09131d1fcad982bf7dd99eb372214`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 658 covered bytes; evidence `name=CDXTrees__HideTree`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `4f6c92135bf99406ef071d6fa42f719408544a9a7dc6cd74b757838f0d0d5d3d`, and packet decompile SHA-256 `1897ce4e6aa3ab2999a698549c424188acc09131d1fcad982bf7dd99eb372214`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0055ae40:0055af89;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
