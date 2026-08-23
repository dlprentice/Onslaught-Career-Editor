# CExplosion__VFunc_39_0044bf10

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CExplosion__VFunc_39_0044bf10` at `0x0044bf10` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044bf10`

## Identity
- Body `[0x0044bf10,0x0044c0ee]`, 479 bytes, 152 closure instructions. Raw pristine-body SHA-256 `39e060a24fb364ff853e91d4825136bf8859bce85dea28d03a48c7e0928d7872`; closure range SHA-256 `80319dc9c4cc075e5bd93896a8846f9d50239e9daacc63d0d944d481040b1919`; packet range-plus-bytes SHA-256 `97d8ed93eaf4c8bf3bec6cc56bca426479ecb5df76df8741aa2c188e8b2fc8f5`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CExplosion__VFunc_39_0044bf10`. The READY packet agrees. The dated closure spelling is superseded; this contract uses only the current name-table/register/packet identity and does not repeat the stale spelling.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a641ad51035e8b80aacb75f57922792c7a89da39e627a0ab2e39e8097073027c` and decompile SHA-256 `9ed7e0a6449b19ecacdebff7532b627ae566dc91d63bbdd440ea7dba9026da3a` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C2_BOUNDED_RUNTIME` / register contract state `OPEN_AFTER_SURVIVED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `undefined __thiscall CExplosion__VFunc_39_0044bf10(void * this, int * param_1, int * param_2)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
undefined __thiscall CExplosion__VFunc_39_0044bf10(void * this, int * param_1, int * param_2)
```
- Packet-declared parameter list: `void * this, int * param_1, int * param_2`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `undefined`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CComplexThing__Hit` `0x004f4480` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Class recovered from the binary's own MSVC RTTI: type descriptor -> complete object locator -> vtable, with the owning class resolved through the RTTIClassHierarchyDescriptor base-class array so an inherited method is attributed to the base that introduces it rather than to every derived class. Owner=CExplosion, vtable 0x005e4454 slot 39; slot 39 of CExplosion's PRIMARY (sub-object offset 0) vtable is this address. Ownership evidence: this address occurs in exactly one class vtable in the whole image, so no base class emits it. Function entry created 2026-07-27 from an RTTI vtable-slot target; the previous name was Ghidra's default FUN_0044bf10, so no behavioural hypothesis was displaced. The name asserts CLASS MEMBERSHIP AND VTABLE SLOT ONLY - no method name is claimed, and the RTTI_CONFIRMED grade this name earns is TAUTOLOGICAL because the prefix was generated from the same RTTI the grader reads. Behaviour remains unproven. Wave: naming-wave-2026-07-27.”
- The non-empty packet decompile is bound by SHA-256 `9ed7e0a6449b19ecacdebff7532b627ae566dc91d63bbdd440ea7dba9026da3a`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 0 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `batch-1`; question `contract-round-impact`; value: corroborated in 3/10 coverage sessions; evidence `level-opening-3m-v1-level110, level-opening-3m-v1-level231, level-opening-3m-v1-level232`.
- Session `batch-2`; question `contract-round-impact`; value: corroborated in 3/10 coverage sessions; evidence `level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level322`.
- Session `batch-3`; question `contract-round-impact`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level511`.
- Session `batch-4`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-round-impact`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level854`.
- Session `batch-6`; question `contract-round-impact`; value: corroborated in 1/11 coverage sessions; evidence `level-opening-3m-v1-level862`.
- Session `batch-7`; question `contract-round-impact`; value: corroborated in 1/7 coverage sessions; evidence `level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-round-impact`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-round-impact`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 3; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a641ad51035e8b80aacb75f57922792c7a89da39e627a0ab2e39e8097073027c`, and packet decompile SHA-256 `9ed7e0a6449b19ecacdebff7532b627ae566dc91d63bbdd440ea7dba9026da3a`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0044bf10:0044c0ee;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
