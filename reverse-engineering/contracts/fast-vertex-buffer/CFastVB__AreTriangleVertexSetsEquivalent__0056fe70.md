# CFastVB__AreTriangleVertexSetsEquivalent

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__AreTriangleVertexSetsEquivalent` at `0x0056fe70` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0056fe70`

## Identity
- Body `[0x0056fe70,0x0056feb1]`, 66 bytes, 28 closure instructions. Raw pristine-body SHA-256 `522aea23cc199dea9cd9640e05593490275ec6e7742c2a367ab4f6eb13a650a9`; closure range SHA-256 `d20a48dccce2414b66c6ab02ce849e1911deeddacc946ea40fddfe95247a50f1`; packet range-plus-bytes SHA-256 `687d09dcaba518a344e9ed93cc43573744d8da81f3b88d2c61b594f28e954b31`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__AreTriangleVertexSetsEquivalent`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a97bbe56ae2f2b8cb4b49a6ed52c4f453ca4aa25ff8f344e9ddc6bf49e68a8f7` and decompile SHA-256 `7af4d9012ea3c8c255bda88e40d561b160b2b209632a92e2d99805502c49a581` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__cdecl` for `int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void * triangle_a, void * triangle_b)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void * triangle_a, void * triangle_b)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `int`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CFastVB__EmitTriangleStripIndexBuffer` `0x005710d0` x2 site(s) (instruction-flow).
- Caller `CFastVB__MergeAndOrderStripBatches` `0x005718c0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave651 CFastVB strip-selection hardening: cdecl predicate checks whether all three vertices from triangle_b appear in triangle_a regardless of order. Callers in CFastVB__EmitTriangleStripIndexBuffer and CFastVB__MergeAndOrderStripBatches use the return value as a match/rotation cue; boolean exactness is not overclaimed because the false path retains decompiler-carried vertex values. Static retail decompile/xref evidence only; exact return convention, runtime render output, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `7af4d9012ea3c8c255bda88e40d561b160b2b209632a92e2d99805502c49a581`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 2 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 13; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a97bbe56ae2f2b8cb4b49a6ed52c4f453ca4aa25ff8f344e9ddc6bf49e68a8f7`, and packet decompile SHA-256 `7af4d9012ea3c8c255bda88e40d561b160b2b209632a92e2d99805502c49a581`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0056fe70:0056feb1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
