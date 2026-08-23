# CFastVB__SolveScalarEndpointPairFromSamples

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__SolveScalarEndpointPairFromSamples` at `0x00596589` in the call-connected endpoint solving and scalar block-index quantization support; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00596589`

## Identity
- Body `[0x00596589,0x005968a3]`, 795 bytes, 282 closure instructions. Raw pristine-body SHA-256 `18e026d6ef4f7b2e086b969e045166e93a8f4acbcb3c141c261e3ea419dc0c40`; closure range SHA-256 `3db45f27367c6a8a9b41ebd8547a369e88dac1172e3cf5ef16479dbbff90bb28`; packet range-plus-bytes SHA-256 `956982c3d0c411f7c36ae7ca3ac57fde3ea0127a1cd21aa3b09aee82a72b9e19`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__SolveScalarEndpointPairFromSamples`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `76ce6465de08357521c6c8c5d189f82f9f030a4a345a10ab1d9636b12c7319d7` and decompile SHA-256 `58705bb809fadf5df8abd39213858c5b8e8e8baac45aaeb1d924587db6e7744e` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__stdcall` for `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)`. Reconciled bounded ABI: `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)`. The three stack formals and RET 0xc remain; packet comment additionally pins a live-in EBX mode/endpoint-count input that ordinary C prototype syntax does not express. The packet field is preserved as metadata, not asserted as true where refuted.

## Prototype and parameter semantics
```c
void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)
```
- The effective prototype is bounded by the packet's own analyst comment and instruction/callsite facts. Packet field `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)` remains preserved above; stronger types, ownership, nullability, and any hidden-register meaning beyond the reconciliation note remain not_determinable.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_005eefc4`, `DAT_005eefe4`, `DAT_005ef004`, `DAT_005ef01c`, `_DAT_009d241c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CFastVB__PackScalarBlock_InterpolatedEndpoints` `0x00597b87` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Scalar endpoint pair solver over sixteen samples: scans scalar_samples16, chooses min/max candidates with special handling for the observed six-endpoint mode, builds interpolation weights from tables at DAT_005eefe4/DAT_005ef01c, iteratively refines endpoint_min_out and endpoint_max_out for up to eight passes, clamps both endpoints to 0.0..1.0, and uses hidden EBX as the endpoint-count/mode input. Terminator RET 0xc proves three stack dwords (endpoint_min_out, endpoint_max_out, scalar_samples16). Declared three-arg stdcall plate is incomplete ABI — endpoint-count/mode arrives in EBX (register-carried; not a fourth stack formal). Shape is void __stdcall (float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16) plus live-in EBX mode/endpoint-count (names provisional). Static retail texture-codec evidence only; exact hidden-register ABI, interpolation table identity, error metric, scalar source semantics, and runtime compression quality remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `58705bb809fadf5df8abd39213858c5b8e8e8baac45aaeb1d924587db6e7744e`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `block_index_quantization_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 22; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `76ce6465de08357521c6c8c5d189f82f9f030a4a345a10ab1d9636b12c7319d7`, and packet decompile SHA-256 `58705bb809fadf5df8abd39213858c5b8e8e8baac45aaeb1d924587db6e7744e`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00596589:005968a3;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
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
