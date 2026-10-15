# CFrameTimer__Frame

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFrameTimer__Frame` at `0x00423720` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00423720`

## Identity
- Body `[0x00423720,0x004237c7]`, 168 bytes, 61 closure instructions. Raw pristine-body SHA-256 `70b0c5ba8b68d8175b099e028e6b3b6559d0c6aa96a914360858718fc48e3da7`; closure range SHA-256 `e7c18e57bf574e159ba9beb78e285cd28cd686025b8aa0120741e26a79586f01`; packet range-plus-bytes SHA-256 `4fc9a84633b7447c38b88e0ab17cd43980df199636117ba3acd77a258ea84f72`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFrameTimer__Frame`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `3cc803f6a8499affb12013dc4d796e5b710d66bfe6240720158340aa420d6c45` and decompile SHA-256 `7ff212fbc91f81605210ed5868ae4bcc1889b2bcb7325e973d89c148762cf608` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CFrameTimer__Frame(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CFrameTimer__Frame(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `PCPlatform__DeviceFlip` `0x005158f0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Name/signature correction: CFrameTimer per-frame update called from PCPlatform__DeviceFlip; samples QPC/timeGetTime, stores elapsed ticks, smooths the FPS/frame-scale field, and refreshes reciprocal frame timing. Exact CFrameTimer layout, runtime timing behavior, tags, locals, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `7ff212fbc91f81605210ed5868ae4bcc1889b2bcb7325e973d89c148762cf608`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `batch-1`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201 …`.
- Session `batch-2`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level600, level-opening-3m-v1-level611, level-opening-3m-v1-level612 …`.
- Session `batch-5`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level800 …`.
- Session `batch-6`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level857, level-opening-3m-v1-level858, level-opening-3m-v1-level859 …`.
- Session `batch-7`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level901, level-opening-3m-v1-level902, level-opening-3m-v1-level903, level-opening-3m-v1-level904 …`.
- Session `batch-8`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `level521-native-20260802-0018-take4, startup-to-main-menu-20260729-173124, options-open-manual-01, frontend-manual-02`.
- Session `batch-9`; question `contract-frame`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-frame`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `3cc803f6a8499affb12013dc4d796e5b710d66bfe6240720158340aa420d6c45`, and packet decompile SHA-256 `7ff212fbc91f81605210ed5868ae4bcc1889b2bcb7325e973d89c148762cf608`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00423720:004237c7;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
