# CMixerMap__DestroySlot

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CMixerMap__DestroySlot` at `0x00523210` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00523210`

## Identity
- Body `[0x00523210,0x0052322d]`, 30 bytes, 11 closure instructions. Raw pristine-body SHA-256 `d21080cc346354829c5d9b6e9efa3541cea0b12e7a121703d6b9de4515420707`; closure range SHA-256 `afaa722671637856f2cc3f33d1a07a3bd96be45c4cc30a33702ee925789ff60e`; packet range-plus-bytes SHA-256 `c03c68166f672adef47d427c50653fad92dc13ca9bdd8661bed722ff9a0b826f`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CMixerMap__DestroySlot`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `7ffe63985aedb67b56ce27e59588f7eef84d96d828948361d7ec3d34be2c84ba` and decompile SHA-256 `228dd02bc22888058355dfba2e264a901927eec990f7b17bd032fae3b0609e17` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CMixerMap__DestroySlot(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CMixerMap__DestroySlot(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave566 signature/comment hardening: ECX-only slot cleanup used directly and as an array destructor callback. The body frees the per-slot buffer pointer at this+0x04 through CDXMemoryManager__Free and clears that pointer. Static retail evidence only; slot payload semantics, runtime audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `228dd02bc22888058355dfba2e264a901927eec990f7b17bd032fae3b0609e17`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 0 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `batch-1`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 7 BEA.exe coverage bitmaps`.
- Session `batch-8`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 4 BEA.exe coverage bitmaps`.
- Session `batch-9`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-audio`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 9; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `7ffe63985aedb67b56ce27e59588f7eef84d96d828948361d7ec3d34be2c84ba`, and packet decompile SHA-256 `228dd02bc22888058355dfba2e264a901927eec990f7b17bd032fae3b0609e17`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00523210:0052322d;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
