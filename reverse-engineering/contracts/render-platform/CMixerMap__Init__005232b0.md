# CMixerMap__Init

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CMixerMap__Init` at `0x005232b0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005232b0`

## Identity
- Body `[0x005232b0,0x005233bd]`, 270 bytes, 80 closure instructions. Raw pristine-body SHA-256 `5cc6bc9ac86a5919012b24073be7a76847793a4144f1fd4230bbd497ed72411d`; closure range SHA-256 `529ede1afff4722040b47b53958faac5cbd6c0994affe42ecd5428150a63e971`; packet range-plus-bytes SHA-256 `0c1e0f168ccfb20d60d5c074737c44a0ad7bfb6bb892f3c2a33c6f86687ad4bb`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CMixerMap__Init`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `136c414b02298068da7f9d169686ce915dca8c4a92e9f81e90a337464d0d8a61` and decompile SHA-256 `7bc52aba14eae08cfbfd899ad839707fbb8944b7ced5312d1760d2c9ca48c198` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CMixerMap__Init(void * this, void * chunk_reader)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CMixerMap__Init(void * this, void * chunk_reader)
```
- Packet-declared parameter list: `void * this, void * chunk_reader`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_mixermap_cpp_00640030`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CChunkReader__GetNext` `0x00423910` x2 site(s) (STATIC_DIRECT).
- Callee `CChunkReader__Read` `0x00423960` x1 site(s) (STATIC_DIRECT).
- Callee `CMixerMap__InitSlot` `0x00523190` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x2 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` x1 site(s) (STATIC_DIRECT).
- Callee `CRT__EhVectorDestructorIterator_WithUnwind` `0x0055db0a` x1 site(s) (STATIC_DIRECT).
- Callee `eh_vector_constructor_iterator` `0x0055dc20` x1 site(s) (STATIC_DIRECT).
- Caller `CHeightField__DeserializeMapAndInitResources` `0x00491060` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave566 signature/comment hardening: RET 0x4 and CHeightField__DeserializeMapAndInitResources callsite prove a chunk_reader stack argument. The body destroys an existing slot array, allocates 0x14004 bytes for 0x1000 0x14-byte slots from mixermap.cpp line 0xf6, initializes them through the vector-constructor iterator with CMixerMap__DestroySlot cleanup, allocates a 0x40000 secondary buffer from line 0xf7, consumes a chunk tag, loops through the 0x1000 slots calling CMixerMap__InitSlot(slot,chunk_reader), then consumes another tag and reads the 0x40000 payload. Static retail evidence only; runtime MAP/mixer/audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `7bc52aba14eae08cfbfd899ad839707fbb8944b7ced5312d1760d2c9ca48c198`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 7 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `batch-1`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201 …`.
- Session `batch-2`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level600, level-opening-3m-v1-level611, level-opening-3m-v1-level612 …`.
- Session `batch-5`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level800 …`.
- Session `batch-6`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level857, level-opening-3m-v1-level858, level-opening-3m-v1-level859 …`.
- Session `batch-7`; question `contract-audio`; value: corroborated in 5/7 coverage sessions; evidence `level-opening-3m-v1-level901, level-opening-3m-v1-level902, level-opening-3m-v1-level903, level-opening-3m-v1-level904 …`.
- Session `batch-8`; question `contract-audio`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 4 BEA.exe coverage bitmaps`.
- Session `batch-9`; question `contract-audio`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-audio`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 10; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `136c414b02298068da7f9d169686ce915dca8c4a92e9f81e90a337464d0d8a61`, and packet decompile SHA-256 `7bc52aba14eae08cfbfd899ad839707fbb8944b7ced5312d1760d2c9ca48c198`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005232b0:005233bd;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00640030` length 31 SHA-256 `ae6b025210421d00c9d6139fce4233c7e7de7f178522afc98f2b2b60f33da3f6` value “C:\\dev\\ONSLAUGHT2\\mixermap.cpp”.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
