# CFastVB__InsertStripCandidatesIntoBuffer_005708a0

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__InsertStripCandidatesIntoBuffer_005708a0` at `0x005708a0` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005708a0`

## Identity
- Body `[0x005708a0,0x00570a89]`, 490 bytes, 190 closure instructions. Raw pristine-body SHA-256 `2f100deef0e691c36c08471ef4f3e7c25f77abcd4fc7b2876d7e845482bdd85c`; closure range SHA-256 `00474a48b064a8c42f3ee5336e652c60ce5ac05b486fd0da2d4a5c3a35a9c4b5`; packet range-plus-bytes SHA-256 `6d2dd9422dbbe3157473b91e4d98e0b3dc256855de40870788e9dcacbd9fa163`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__InsertStripCandidatesIntoBuffer_005708a0`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `2010859d8b4c5bd985fae85e5d15524d4df24c91af23ca639e9483b64377cfd1` and decompile SHA-256 `89dd34d71a8e633f0e2b57f7ebba9f8fba42616da8e6b8d46081cc4e6e689413` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__InsertStripCandidatesIntoBuffer_005708a0(void * this, void * primary_candidate_span, void * secondary_candidate_span)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__InsertStripCandidatesIntoBuffer_005708a0(void * this, void * primary_candidate_span, void * secondary_candidate_span)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `SharedVFunc__NoOpRet8_00405db0` `0x00405db0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00426fd0` `0x00426fd0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00449d40` `0x00449d40` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyDwordRange` `0x00572f50` x4 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountDwordsFromPointerSpan` `0x00573310` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordSpanFilled` `0x005736d0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__FillDwordSpanWithValue_00573ff0` `0x00573ff0` x2 site(s) (STATIC_DIRECT).
- Caller `CFastVB__BuildTriangleStripFromSeedRecord` `0x00570000` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB strip-candidate buffer insert helper: ECX receiver; reverse-inserts secondary candidates into this+0xc span, then grows/shifts primary pointer buffer at this+0x10/+0x14/+0x18 while inserting primary candidates (InsertDwordSpanFilled fan-out). Terminator `RET 0x8` proves two stack dwords after this (primary_candidate_span, secondary_candidate_span). Declared trailing `void * edi_context` is false — not callee-cleaned. Shape is `void __thiscall (void * this, void * primary_candidate_span, void * secondary_candidate_span)` (names provisional; address suffix retained). Static retail stripify evidence only; exact container layout, runtime render UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `89dd34d71a8e633f0e2b57f7ebba9f8fba42616da8e6b8d46081cc4e6e689413`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 7 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `2010859d8b4c5bd985fae85e5d15524d4df24c91af23ca639e9483b64377cfd1`, and packet decompile SHA-256 `89dd34d71a8e633f0e2b57f7ebba9f8fba42616da8e6b8d46081cc4e6e689413`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005708a0:00570a89;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
