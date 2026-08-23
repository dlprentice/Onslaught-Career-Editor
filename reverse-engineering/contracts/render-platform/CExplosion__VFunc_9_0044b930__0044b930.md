# CExplosion__VFunc_9_0044b930

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CExplosion__VFunc_9_0044b930` at `0x0044b930` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044b930`

## Identity
- Body `[0x0044b930,0x0044bed4]`, 1445 bytes, 406 closure instructions. Raw pristine-body SHA-256 `963e787280b4cac16abe8b778e6579b14e3f978879dedec67b572cfd2ee05045`; closure range SHA-256 `1085fa9682a24a080980c7a7b9f4fa97635381ca8d6aa89ac63760744dcb2b15`; packet range-plus-bytes SHA-256 `48bfb0320b90280a7060fe982b58853c7a9d40f962c8162bcb954c6667d49fb8`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CExplosion__VFunc_9_0044b930`. The READY packet agrees. The dated closure spelling is superseded; this contract uses only the current name-table/register/packet identity and does not repeat the stale spelling.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `b41e11d4ba048e85b2e23e5380c577f1fb54b9a637e9f4a4109c2025bb6b6dc4` and decompile SHA-256 `a6b85d11349924de74297755ae777a8418a7a6de82f175c9f2a8702bc9597922` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `undefined __thiscall CExplosion__VFunc_9_0044b930(void * this, void * param_1)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
undefined __thiscall CExplosion__VFunc_9_0044b930(void * this, void * param_1)
```
- Packet-declared parameter list: `void * this, void * param_1`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `undefined`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_006755f8`, `DAT_006755fc`, `DAT_00675600`, `DAT_00675604`, `DAT_006fbdfc`, `DAT_0083d9c0`, `DAT_00855090`, `DAT_00896988`, `DAT_0089c9a0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` x1 site(s) (STATIC_DIRECT).
- Callee `CMeshRenderer__CopyBasisAndRefreshTime` `0x00403650` x1 site(s) (STATIC_DIRECT).
- Callee `CEngine__TrackBurstEventFromPreset` `0x0044a610` x1 site(s) (STATIC_DIRECT).
- Callee `ParticleEffectLink_T3_004cb040` `0x004cb040` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__RemoveOwnerLinkFromGlobalList` `0x004cb050` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` x2 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` x1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToHead` `0x004e5a80` x1 site(s) (STATIC_DIRECT).
- Callee `CComplexThing__Init` `0x004f3fd0` x1 site(s) (STATIC_DIRECT).
- Callee `CRT__AcosDispatch_ST0` `0x0055dcb0` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Class recovered from the binary's own MSVC RTTI: type descriptor -> complete object locator -> vtable, with the owning class resolved through the RTTIClassHierarchyDescriptor base-class array so an inherited method is attributed to the base that introduces it rather than to every derived class. Owner=CExplosion, vtable 0x005e4454 slot 9; slot 9 of CExplosion's PRIMARY (sub-object offset 0) vtable is this address. Ownership evidence: this address occurs in exactly one class vtable in the whole image, so no base class emits it. Function entry created 2026-07-27 from an RTTI vtable-slot target; the previous name was Ghidra's default FUN_0044b930, so no behavioural hypothesis was displaced. The name asserts CLASS MEMBERSHIP AND VTABLE SLOT ONLY - no method name is claimed, and the RTTI_CONFIRMED grade this name earns is TAUTOLOGICAL because the prefix was generated from the same RTTI the grader reads. Behaviour remains unproven. Wave: naming-wave-2026-07-27.”
- The non-empty packet decompile is bound by SHA-256 `a6b85d11349924de74297755ae777a8418a7a6de82f175c9f2a8702bc9597922`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 0 caller record(s), 10 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `b41e11d4ba048e85b2e23e5380c577f1fb54b9a637e9f4a4109c2025bb6b6dc4`, and packet decompile SHA-256 `a6b85d11349924de74297755ae777a8418a7a6de82f175c9f2a8702bc9597922`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0044b930:0044bed4;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
