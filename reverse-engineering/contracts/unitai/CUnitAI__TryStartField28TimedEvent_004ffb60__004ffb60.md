# CUnitAI__TryStartField28TimedEvent_004ffb60

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__TryStartField28TimedEvent_004ffb60` at `0x004ffb60`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ffb60`

## Identity
- Body `[0x004ffb60,0x004ffba7]`, 72 bytes, 22 closure instructions. Raw pristine-body SHA-256 `37d2f71305897d3714c02d9f86f948ffadc2123fecab41e4493003a7738310e7`; closure range SHA-256 `aa0bf62569da32f3f88cd7cb6bfacbe8c80fbcf10c0ef016cc33d6729e0e8c2b`; packet range-plus-bytes SHA-256 `48c9d51a3cb21ae4fa7e775e362188362e8db08b0feaf3862f748a902b69fbf0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__TryStartField28TimedEvent_004ffb60` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__TryStartField28TimedEvent_004ffb60`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__TryStartField28TimedEvent_004ffb60(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__TryStartField28TimedEvent_004ffb60(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 7 and many CUnitAI-derived vtables point at this previously functionless boolean body. The body checks this+0x28 and a target flag, stores mode 2, writes a DAT_00672fd0-based timestamp to this+0x44, schedules event id 0xbba, returns 1 on activation, and returns 0 otherwise. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field/event semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `99a970a2f63807ccfff2c9a536519eddf2a04135c930406c0c59f87e1c7d6631`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 24; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ffb60.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `99a970a2f63807ccfff2c9a536519eddf2a04135c930406c0c59f87e1c7d6631`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ffb60:004ffba7;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
