# CFastVB__QuantizeScalarBlockIndices

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__QuantizeScalarBlockIndices` at `0x00596e23` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00596e23`

## Identity
- Body `[0x00596e23,0x00597649]`, 2087 bytes, 683 closure instructions. Raw pristine-body SHA-256 `95f77fb38028f00cfadfbbd7cd0bcf8060e9d6172f62a78a1f9c7ea42014b5d8`; closure range SHA-256 `6b76ee865250073a5f7688d3bc189cc49332c004490520b4e4a50015042bbfd7`; packet range-plus-bytes SHA-256 `e9673acb50cfdf6b49bcfc4497e16a540f50fb835e10a495b287af7d8c45f8a0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__QuantizeScalarBlockIndices`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `87ee66e1b08b62120cc29f6f8f37a5d7355f80edbcf4e18a8881b6aaa3d4f08c` and decompile SHA-256 `d64328aaacc8a97dd477aa433bbd7fc7ae09fb01d5929198a804bbdbb195d28d` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)
```
- Packet-declared parameter list: `void * dxt_color_block_out, float alpha_mode_weight`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_005ef078`, `DAT_005ef088`, `DAT_00659ca0`, `DAT_00659ca4`, `DAT_00659ca8`, `_DAT_00659cb0`, `_DAT_00659cb4`, `_DAT_00659cb8`, `_DAT_009d241c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CDXTexture__UnpackRgb565ToRgbaFloat` `0x00596386` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__PackClampedRgbToR5G6B5` `0x00596480` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__SolveVectorEndpointPairFromSamples` `0x005968a4` x1 site(s) (STATIC_DIRECT).
- Caller `CTexture__EncodeDxtColorBlock_ErrorDiffuseAlpha` `0x00597949` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackScalarBlock_4BitEndpoints` `0x00597a61` x1 site(s) (instruction-flow).
- Caller `CFastVB__PackScalarBlock_InterpolatedEndpoints` `0x00597b87` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “DXT color-block quantizer over a sixteen-pixel float RGBA block: chooses the observed three- or four-color mode from alpha_mode_weight and alpha-lane checks, distributes quantization residuals across the 4x4 block, calls CFastVB__SolveVectorEndpointPairFromSamples, packs RGB565 endpoints, unpacks the chosen endpoints for selector fitting, writes the 32-bit selector mask into dxt_color_block_out, and returns 0. Terminator RET 0x8 proves two stack dwords (dxt_color_block_out, alpha_mode_weight). Declared two-arg stdcall plate is incomplete ABI — the sixteen-pixel float RGBA source block arrives in EAX (hidden; not a third stack formal). Shape is int __stdcall (void * dxt_color_block_out, float alpha_mode_weight) plus live-in EAX float * rgba_float_block16 (names provisional). Static retail texture-codec evidence only; exact hidden-EAX input ABI, output DXT block schema, alpha-mode semantics, residual diffusion policy, and runtime compression quality remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `d64328aaacc8a97dd477aa433bbd7fc7ae09fb01d5929198a804bbdbb195d28d`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 3 caller record(s), 3 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 128,502 cumulative covered bytes; evidence `name=CFastVB__QuantizeScalarBlockIndices`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 13; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `87ee66e1b08b62120cc29f6f8f37a5d7355f80edbcf4e18a8881b6aaa3d4f08c`, and packet decompile SHA-256 `d64328aaacc8a97dd477aa433bbd7fc7ae09fb01d5929198a804bbdbb195d28d`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00596e23:00597649;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
