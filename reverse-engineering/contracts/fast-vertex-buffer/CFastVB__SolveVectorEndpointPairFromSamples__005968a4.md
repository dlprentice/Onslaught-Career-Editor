# CFastVB__SolveVectorEndpointPairFromSamples

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__SolveVectorEndpointPairFromSamples` at `0x005968a4` in the call-connected endpoint solving and scalar block-index quantization support; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005968a4`

## Identity
- Body `[0x005968a4,0x00596e22]`, 1407 bytes, 518 closure instructions. Raw pristine-body SHA-256 `5f55513ae58463d8b5da3f882fcc09f7248f33495968ae46090d2b18106b3346`; closure range SHA-256 `b9af8e0d8ffb165459a9f3173e80487cd3f0805c4797cfdb500146020c5b2d1c`; packet range-plus-bytes SHA-256 `a7d8d76a2ebee4feb7a397730f207ae469f616c8b6e432d96adae1b3d00f6604`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__SolveVectorEndpointPairFromSamples`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `390cbe7de387450044fb239a16a1ce775b4af40cbf5612e13fbe0696827bba30` and decompile SHA-256 `b3011513a46ad4a4a4bca42c1cd7a0aa3abc293a75d58164c4645f2f86e1b00d` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_005ef03c`, `DAT_005ef04c`, `DAT_005ef05c`, `DAT_005ef068`, `DAT_00659ca0`, `DAT_00659ca4`, `DAT_00659ca8`, `DAT_00659cac`, `_DAT_009d241c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CFastVB__QuantizeScalarBlockIndices` `0x00596e23` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave701 static read-back: scans sixteen four-float sample rows, selects an RGB bounding axis, chooses endpoint ordering from variance buckets, optionally refines RGB endpoints with interpolation tables for endpoint_count 3 or 4, and writes the resulting RGB endpoint pair. Static metadata only; exact sample stride/layout, DXT mode identity, vector error metric, interpolation table provenance, and runtime compression quality remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `b3011513a46ad4a4a4bca42c1cd7a0aa3abc293a75d58164c4645f2f86e1b00d`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `block_index_quantization_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `390cbe7de387450044fb239a16a1ce775b4af40cbf5612e13fbe0696827bba30`, and packet decompile SHA-256 `b3011513a46ad4a4a4bca42c1cd7a0aa3abc293a75d58164c4645f2f86e1b00d`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005968a4:00596e22;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
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
