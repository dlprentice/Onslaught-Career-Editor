# CFastVB__PackScalarBlock_4BitEndpoints

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__PackScalarBlock_4BitEndpoints` at `0x00597a61` in the call-connected endpoint solving and scalar block-index quantization support; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00597a61`

## Identity
- Body `[0x00597a61,0x00597b86]`, 294 bytes, 102 closure instructions. Raw pristine-body SHA-256 `8c65d2a54979a8169e02a210e1ea8056cdbc39f589f0305441a7acbc1404b084`; closure range SHA-256 `8b8c5a0d6496a4a1c395d6d9a164259b8e4948ac4bf43c56bdc53fc7ff5dfa28`; packet range-plus-bytes SHA-256 `5ea7efc453c6904344197bb8ef4273e021fc54b81b2b0d31ceaca630fbebefbe`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__PackScalarBlock_4BitEndpoints`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `fc44e6c18db2da2a4aeb46fcacbc5aa2484473bb8a62de454668f2e5cb797499` and decompile SHA-256 `9a80371d92669a18671643ccb399225748ed93fb4a457f52d06eaa6aada3873d` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__stdcall` for `undefined4 __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)`. Reconciled bounded ABI: `int __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)`. Packet comment and trailing quantizer EAX status refute undefined/void semantics and bound the return as int-shaped status; RET 0x8 preserves two stack formals. The packet field is preserved as metadata, not asserted as true where refuted.

## Prototype and parameter semantics
```c
int __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)
```
- The effective prototype is bounded by the packet's own analyst comment and instruction/callsite facts. Packet field `undefined4 __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)` remains preserved above; stronger types, ownership, nullability, and any hidden-register meaning beyond the reconciliation note remain not_determinable.

## Return value meaning
The effective bounded signature declares `int`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `_DAT_009d241c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CFastVB__QuantizeScalarBlockIndices` `0x00596e23` x1 site(s) (STATIC_DIRECT).
- Caller `CTexture__EncodeDxt3AlphaBlock` `0x00598056` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “DXT3-style explicit-alpha plus color pack: initializes an 8-byte explicit-alpha output field, error-diffuses sixteen source alpha samples into 4-bit packed nibbles, then quantizes the color selector block at output+8 via the scalar quantizer path. Terminator RET 0x8 proves two stack dwords (dxt3_block_out, rgba_float_block16). Declared void return is false — body returns status-shaped EAX (int) after quantize. Shape is int __stdcall (void * dxt3_block_out, float * rgba_float_block16) (names provisional). Static retail texture-codec evidence only; exact DXT3 block ABI, diffusion policy, color/alpha coupling, runtime compression quality, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `9a80371d92669a18671643ccb399225748ed93fb4a457f52d06eaa6aada3873d`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s). Manifest subfamily: `block_index_quantization_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 24; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `fc44e6c18db2da2a4aeb46fcacbc5aa2484473bb8a62de454668f2e5cb797499`, and packet decompile SHA-256 `9a80371d92669a18671643ccb399225748ed93fb4a457f52d06eaa6aada3873d`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00597a61:00597b86;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
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
