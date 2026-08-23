# CFastVB__PackClampedRgbToR5G6B5

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__PackClampedRgbToR5G6B5` at `0x00596480` in the call-connected endpoint solving and scalar block-index quantization support; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00596480`

## Identity
- Body `[0x00596480,0x00596588]`, 265 bytes, 90 closure instructions. Raw pristine-body SHA-256 `a6a8ae14f25c36b4174e4ad54098fad2c3ab1c1c422ecf9a958f71a138c6cff8`; closure range SHA-256 `17c47e97bf6f0e514c0dcd1f5e315fd60373c283fc3100d24f81d6540397436c`; packet range-plus-bytes SHA-256 `03fb6dc4f7c491764567d3e4c3ecf0689ca43760b9fab4531db808a93bf1f944`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__PackClampedRgbToR5G6B5`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `4272b3364a406175a7fc7d36560c3246e0d136c16c0a3e474477aaef99ae4f7d` and decompile SHA-256 `86d6a90ef444fa52e2cdb1b08847696d553d2ed1819e25dde8c6c4758091b38d` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `uint`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `_DAT_009d241c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CFastVB__QuantizeScalarBlockIndices` `0x00596e23` x2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave701 static read-back: clamps the first three float channels at rgb_float_triplet into 0.0..1.0, rounds red/blue through the 5-bit scale constant and green through the 6-bit scale constant, and packs the result into an RGB565 word. Static metadata only; exact rounding-mode control-word side effect, color-space convention, input stride, and runtime texel fidelity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `86d6a90ef444fa52e2cdb1b08847696d553d2ed1819e25dde8c6c4758091b38d`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s). Manifest subfamily: `block_index_quantization_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `4272b3364a406175a7fc7d36560c3246e0d136c16c0a3e474477aaef99ae4f7d`, and packet decompile SHA-256 `86d6a90ef444fa52e2cdb1b08847696d553d2ed1819e25dde8c6c4758091b38d`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00596480:00596588;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
