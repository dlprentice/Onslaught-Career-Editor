# CFastVB__SelectNextStripTriangle

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__SelectNextStripTriangle` at `0x0056fdc0` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0056fdc0`

## Identity
- Body `[0x0056fdc0,0x0056fe6e]`, 175 bytes, 63 closure instructions. Raw pristine-body SHA-256 `a163ee2e20c9ee8f291b43921c85ce09545e59a6241e703fb5ed5f4997a03f74`; closure range SHA-256 `e6158249ec9a863cb6d6ce927258f0ed223073dae5a1033d5b330699aea90b26`; packet range-plus-bytes SHA-256 `e9a9dc76acfda5195151e3e732e08125ef3f7612ae5710197d5d2efc42966ded`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__SelectNextStripTriangle`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `f4b5d9810530a0521e2e80de9e2c15b3f7e74ce30830b8f660e5c47eaa902f03` and decompile SHA-256 `681e9b41462cfbefa2934bcb31929379e6ceea39166c712d430137695d4d7a44` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__thiscall` for `void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets, void * edi_context)`. Reconciled bounded ABI: `void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets)`. Packet comment and RET 0x8 refute the packet field's trailing edi_context formal; only two stack dwords follow ECX this. The packet field is preserved as metadata, not asserted as true where refuted.

## Prototype and parameter semantics
```c
void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets)
```
- The effective prototype is bounded by the packet's own analyst comment and instruction/callsite facts. Packet field `void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets, void * edi_context)` remains preserved above; stronger types, ownership, nullability, and any hidden-register meaning beyond the reconciliation note remain not_determinable.

## Return value meaning
The effective bounded signature declares `void *`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `__ftol` `0x0055e128` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__SelectTriangleWithMaxOpenEdges` `0x0056fce0` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__GenerateStripCandidatesFromAdjacency` `0x005725e0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB strip triangle selector: ECX receiver; chooses next unclaimed triangle from triangle_record_span, optionally seeds from CFastVB__SelectTriangleWithMaxOpenEdges when this+0x1c armed, advances float selector at this+0x18, returns triangle ptr or null in EAX. Terminator `RET 0x8` proves two stack dwords after this (triangle_record_span, edge_buckets). Declared trailing `void * edi_context` is false — not callee-cleaned. Shape is `void * __thiscall (void * this, void * triangle_record_span, void * edge_buckets)` (names provisional). Static retail strip selection evidence only; exact randomization policy, runtime render UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `681e9b41462cfbefa2934bcb31929379e6ceea39166c712d430137695d4d7a44`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `f4b5d9810530a0521e2e80de9e2c15b3f7e74ce30830b8f660e5c47eaa902f03`, and packet decompile SHA-256 `681e9b41462cfbefa2934bcb31929379e6ceea39166c712d430137695d4d7a44`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0056fdc0:0056fe6e;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
