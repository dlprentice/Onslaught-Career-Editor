# CMixerMap__InitSlot

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CMixerMap__InitSlot` at `0x00523190` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00523190`

## Identity
- Body `[0x00523190,0x005231f9]`, 106 bytes, 39 closure instructions. Raw pristine-body SHA-256 `4c73238fdce26ab139f04eee4d70be8e86c37c6bb97cc17bcd3ce63db66e32da`; closure range SHA-256 `c562b58ec53a156db1a0915418b85110a8a9a8282a6d607bcd8526dbd111a9e6`; packet range-plus-bytes SHA-256 `b4b3aa8e9b7b70988f74cf41191b812b37e12cec3721ef05520a736c9d0e2961`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CMixerMap__InitSlot`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `ba50241306312e61f6d44d8de5955b0a4ab54ce388a5edba37cefc863a24fa69` and decompile SHA-256 `cc8741ea7d6410631c0ab6b0881fd3a7d29917545de6b1c1b199eae6a11eb595` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CMixerMap__InitSlot(void * this, void * chunk_reader)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CMixerMap__InitSlot(void * this, void * chunk_reader)
```
- Packet-declared parameter list: `void * this, void * chunk_reader`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_mixermap_cpp_00640030`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CChunkReader__GetNext` `0x00423910` x3 site(s) (STATIC_DIRECT).
- Callee `CChunkReader__Read` `0x00423960` x2 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Caller `CMixerMap__Init` `0x005232b0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave566 signature/comment hardening: RET 0x4 plus prologue MOV ESI,ECX and caller 0x0052337f/0x00523381 prove a slot receiver plus one chunk_reader argument. The body consumes two chunk-reader tags, reads a 0x14-byte slot record, and when slot+0x04 is nonzero consumes another tag, allocates slot_count*0x51 bytes from mixermap.cpp line 0x86, stores it at slot+0x04, and reads that payload. Static retail evidence only; mixer slot field semantics, runtime audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `cc8741ea7d6410631c0ab6b0881fd3a7d29917545de6b1c1b199eae6a11eb595`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 3 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 22; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `ba50241306312e61f6d44d8de5955b0a4ab54ce388a5edba37cefc863a24fa69`, and packet decompile SHA-256 `cc8741ea7d6410631c0ab6b0881fd3a7d29917545de6b1c1b199eae6a11eb595`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00523190:005231f9;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00640030` length 31 SHA-256 `ae6b025210421d00c9d6139fce4233c7e7de7f178522afc98f2b2b60f33da3f6` value “C:\\dev\\ONSLAUGHT2\\mixermap.cpp”.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
