# CFastVB__BuildTriangleStripFromSeedRecord

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__BuildTriangleStripFromSeedRecord` at `0x00570000` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00570000`

## Identity
- Body `[0x00570000,0x00570864]`, 2149 bytes, 684 closure instructions. Raw pristine-body SHA-256 `f52991e4dbba327e14df6226b5b065603856acddb6bd1d3362e7fdf141857e73`; closure range SHA-256 `16a06adade702b0b8e0a2643b68dbf09868da8d5941a3af654a8b5423802d247`; packet range-plus-bytes SHA-256 `642dc6f8237b5e120c8354d603baeaececf8697598be55c49ee71f1181e9e55a`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__BuildTriangleStripFromSeedRecord`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `40e17a7cf793f0574e52fd7ec0c399dbaf2a6eba89004bb91dd003eb9a031e95` and decompile SHA-256 `d02d20aa7a3716dde681b6c6d53666dba915839d5a830e838f4326cfccf26020` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void * this, void * edge_buckets, int generation_context)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void * this, void * edge_buckets, int generation_context)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `s_GetNextIndex__Duplicate_triangle_00656eb0`, `s_GetNextIndex__Triangle_doesn_t_h_00656eec`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `OID_T3_00426fd0` `0x00426fd0` x2 site(s) (STATIC_DIRECT).
- Callee `CRT__PrintfStdoutLocked` `0x0055e183` x18 site(s) (STATIC_DIRECT).
- Callee `CFastVB__ReleaseBufferAndResetTriplet_0056f260` `0x0056f260` x4 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountWordElements` `0x0056f280` x4 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyWordRangeToBufferAndAdvanceEnd` `0x0056f4b0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__ResolveOppositeAdjacencyRecord` `0x0056f580` x8 site(s) (STATIC_DIRECT).
- Callee `CFastVB__TriangleListContainsVertexTriplet_0056ff40` `0x0056ff40` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__StampRecordOwnerFields` `0x00570870` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertStripCandidatesIntoBuffer_005708a0` `0x005708a0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertWordAndGrow` `0x00572fa0` x10 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordAndGrow` `0x00573170` x7 site(s) (STATIC_DIRECT).
- Caller `CFastVB__GenerateStripCandidatesFromAdjacency` `0x005725e0` x2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave651 CFastVB strip-selection hardening: thiscall builder starts from a seed triangle/candidate record, grows forward and reverse 16-bit strip word spans through adjacency records, stamps selected triangle owner fields, may allocate synthetic 0x18-byte bridge records, and appends candidate batches through CFastVB__InsertStripCandidatesIntoBuffer_005708a0. The trailing generation_context is retained for the observed ABI but is not consumed by the current decompile. Static retail decompile/callsite evidence only; exact record layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `d02d20aa7a3716dde681b6c6d53666dba915839d5a830e838f4326cfccf26020`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 11 callee record(s), and 2 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 15; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `40e17a7cf793f0574e52fd7ec0c399dbaf2a6eba89004bb91dd003eb9a031e95`, and packet decompile SHA-256 `d02d20aa7a3716dde681b6c6d53666dba915839d5a830e838f4326cfccf26020`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00570000:00570864;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00656eb0` length 59 SHA-256 `c17510eb73bb616dddfebd7152c6bb6277b2074d277caddaceee8bc2eca1bf8a` value `GetNextIndex: Duplicate triangle probably got us derailed\n`.
- Packet string ref `0x00656eec` length 57 SHA-256 `8d290bb086d48824d4b4d473a49138d7cd69908ee6d8d3b5d87a190420594c47` value `GetNextIndex: Triangle doesn't have all of its vertices\n`.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
