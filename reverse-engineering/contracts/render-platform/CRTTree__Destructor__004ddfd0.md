# CRTTree__Destructor

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CRTTree__Destructor` at `0x004ddfd0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ddfd0`

## Identity
- Body `[0x004ddfd0,0x004de04b]`, 124 bytes, 34 closure instructions. Raw pristine-body SHA-256 `6ec1a752ec18eb17f7d89a78c5d80d7168b7ba61984ba99e3f2d596b1ea8b719`; closure range SHA-256 `6787de2cfb3005dc0540d890b35b639e112541e7d31e7ee95a0b0f49ffd4a7e5`; packet range-plus-bytes SHA-256 `e4538e7ea44a0420ba99796aedb13b78a3092d8a43d902978899d289c6629e7e`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CRTTree__Destructor`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `54d24a497952515e2291f435bc82c313bc5bc9b235ef50c246373f6cfe69d6f5` and decompile SHA-256 `f746391f9adb39cfb9a624d55f1d5ee6fb21517b4d3a57337bb2be6b3dd51d64` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRTTree__Destructor(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CRTTree__Destructor(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009cc148`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CDXTrees__HideTree` `0x0055ae40` x1 site(s) (STATIC_DIRECT).
- Caller `CRTTree__ScalarDeletingDestructor` `0x004de080` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave497 signature/comment hardening: resets the CRTTree vtable to 0x005deb9c, hides/unregisters the tree through CDXTrees__HideTree, decrements the resource refcount at this+0x14 -> +0x170 when present, clears this+0x14, restores the CRenderThing vtable 0x005deaac, and dispatches the child/owned pointer at this+0x10 with delete flag 1 when present. Static retail-binary evidence only; exact source name, concrete CRTTree layout, runtime tree lifetime behavior, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `f746391f9adb39cfb9a624d55f1d5ee6fb21517b4d3a57337bb2be6b3dd51d64`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 234 covered bytes; evidence `name=CRTTree__Destructor`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 5; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `54d24a497952515e2291f435bc82c313bc5bc9b235ef50c246373f6cfe69d6f5`, and packet decompile SHA-256 `f746391f9adb39cfb9a624d55f1d5ee6fb21517b4d3a57337bb2be6b3dd51d64`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004ddfd0:004de04b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
