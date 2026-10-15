# CUnitAI__UpdateField28TargetReaderGate_004ffbb0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__UpdateField28TargetReaderGate_004ffbb0` at `0x004ffbb0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ffbb0`

## Identity
- Body `[0x004ffbb0,0x004ffdc9]`, 538 bytes, 173 closure instructions. Raw pristine-body SHA-256 `76ba731fe0d45a277013a54c9526266b1dbb5f0e2f697630ae1dc9d4c3057a20`; closure range SHA-256 `1cef7d72aafbdb085e836881923eb7a9053121d1fc4d25eeb478c8cda65f8f63`; packet range-plus-bytes SHA-256 `b9ccfe1142b381212f3ee93858f23ebcea341f9d324f931a4eb5c68c368aa2b0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__UpdateField28TargetReaderGate_004ffbb0` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__UpdateField28TargetReaderGate_004ffbb0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__UpdateField28TargetReaderGate_004ffbb0(void * this, void * candidate)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__UpdateField28TargetReaderGate_004ffbb0(void * this, void * candidate)
```
- Packet-declared parameter list: `void * this, void * candidate`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_006fadc8`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×2 site(s) (STATIC_DIRECT).
- Callee `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1082 AI vtable-boundary recovery: DATA xref 0x005dbf3c (CInfantryAI vtable 0x005dbf14 slot 10) and other DATA xrefs point at this previously functionless RET 0x4 body. The body checks this+0x28 and owner/unit virtual gates, may call through target virtual slots, and ends before the adjacent export symbol CWarspite__SetReaderAndRefreshSupportSelection at 0x004ffdd0 (adjacency only; this body does not CALL that neighbor). Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete reader/candidate semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `659d66419dccdf371ac383cdc9de2bf59c02568f1fa761aed4857bafc7f6401e`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 3 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ffbb0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `659d66419dccdf371ac383cdc9de2bf59c02568f1fa761aed4857bafc7f6401e`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ffbb0:004ffdc9;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
