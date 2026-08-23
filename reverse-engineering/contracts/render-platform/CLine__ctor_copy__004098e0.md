# CLine__ctor_copy

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CLine__ctor_copy` at `0x004098e0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004098e0`

## Identity
- Body `[0x004098e0,0x0040994e]`, 111 bytes, 39 closure instructions. Raw pristine-body SHA-256 `8196b18dc22fd421a8d9c2c426b44dba7c0d2d663d79075df73f78f1f35a4496`; closure range SHA-256 `bca3e53ae12fedaf3dd9b7114937552e5b43a144327fb2f309d7f7e221838c7b`; packet range-plus-bytes SHA-256 `dc2cbb209e7bd115add62e59126c3d162a49f5386a9c10dddb27e1adf76b498d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CLine__ctor_copy`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `2a3687f291fd6ad0a9845334b9e9db2068938582bc9ab9555690f94d6c8a966e` and decompile SHA-256 `44bb75ee5d7aeb327fa911a97ca757ffe72667b1f63eeec43c0e90d374960a87` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CLine__ctor_copy(void * this, void * sourceLine)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CLine__ctor_copy(void * this, void * sourceLine)
```
- Packet-declared parameter list: `void * this, void * sourceLine`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CBattleEngine__Move` `0x004081c0` x1 site(s) (instruction-flow).
- Caller `CBattleEngine__CalcUnitOverCrossHair` `0x0040acc0` x1 site(s) (instruction-flow).
- Caller `CBattleEngine__HandleAutoAim` `0x0040b6d0` x1 site(s) (instruction-flow).
- Caller `CCSRay__CreateEffect` `0x00426a40` x1 site(s) (instruction-flow).
- Caller `CMCMech__GetFootHeight` `0x00499bc0` x1 site(s) (instruction-flow).
- Caller `CUnit__ApplyDamage` `0x004f9a90` x1 site(s) (instruction-flow).
- Caller `OID__CanFireAtTarget_BallisticArcA` `0x00507ab0` x4 site(s) (instruction-flow).
- Caller `OID__CanFireAtTarget_BallisticArcB` `0x005088b0` x1 site(s) (instruction-flow).
- Caller `CDXEngine__Render` `0x0053e2e0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Owner correction: body installs the CGeneralVolume base vtable then the CLine vtable while copying three 16-byte rows from sourceLine; ResolveVtableTypeNames confirms CGeneralVolume and CLine RTTI. Exact constructor identity, concrete CLine/CGeneralVolume layout, source identity, runtime behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `44bb75ee5d7aeb327fa911a97ca757ffe72667b1f63eeec43c0e90d374960a87`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 9 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 14; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `2a3687f291fd6ad0a9845334b9e9db2068938582bc9ab9555690f94d6c8a966e`, and packet decompile SHA-256 `44bb75ee5d7aeb327fa911a97ca757ffe72667b1f63eeec43c0e90d374960a87`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004098e0:0040994e;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
