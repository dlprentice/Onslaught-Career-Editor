# CUnitAI__HandleEvent

Status: active static contract; historical factory behavior retained
Last updated: 2026-09-27 (interface identity and stale argument declaration)
Summary: `CUnitAI::HandleEvent` interface identity at `0x004ff330`; historical timed-event findings remain bounded and its return meaning is unresolved.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ff330`

## September 27 identity and argument recheck

The [reviewed six-name scope](../../../tools/cohort-specs/switch-identities-20260927.manifest.tsv)
identifies `CUnitAI__HandleEvent` through the inherited `IListener` interface,
pinned `thing.h:110` declaration and the guarded recipient calls in the complete
`CEventManager::Flush` body at `0x0044b640` (`eventmanager.cpp:341,359`).
All 20 known RTTI holder uses agree on primary slot 0. This supplies a method
identity in the nonexclusive CUnitAI naming context, not an exclusive source-body
owner or complete semantic proof. Source pin: `5352a81c`.

All 422 original bytes / 148 instructions were compared with the pristine specimen
above. The unsigned switch bound at `0x004ff3d2`, branch at `0x004ff3d5` and jump
at `0x004ff3d7` select four DWORDs at `0x004ff4d8`. Complete normal-flow targets and
`RET 4` agree with one explicit stack argument. The incoming argument is
**dereferenced as an event record** (`word [event+4]`), not passed as a scalar event
code. The earlier factory signature below contradicted its own quoted plate note.
The working signature already uses `void * eventRecord`; this identity correction
does not change its provisional `int` return or certify a return-value contract.
No new original-code execution of this handler was performed for this recheck.

## Historical factory identity
- Body `[0x004ff330,0x004ff4d5]`, 422 bytes, 148 closure instructions. Raw pristine-body SHA-256 `3c35a60a6a8ab5f2e4ceddc0f745c2793413929995c8a1e7bb713c9e2a5af67d`; closure range SHA-256 `602dca9d477b14361fe8da85f05afbb969eb30f3bd2b82b6fc75336b20b263c5`; packet range-plus-bytes SHA-256 `19420ca0220d2fbbba341502ecfbadcfeee5f4fef8d94c6873c53f03c2defa24`. All three were independently recomputed over the exact single contiguous inclusive range.
- Historical closure/register and packet label: `CUnitAI__DispatchTimedAIEvent_004ff330`. It remains a lead in the plate comment; the current interface identity is `CUnitAI__HandleEvent`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
The historical packet records `__thiscall` for `int __thiscall CUnitAI__DispatchTimedAIEvent_004ff330(void * this, int event_code)`. The September 27 body/caller recheck above supports an ECX receiver and one explicit stack argument; complete parameter types and return semantics remain separate.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__HandleEvent(void * this, void * eventRecord)
```
- This is the current saved signature, with provisional return type. The historical packet list `void * this, int event_code` is superseded by the event-pointer finding. Concrete record layout, ownership, aliasing and nullability remain bounded to separately established field accesses.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×4 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family RET 0x4 timed-event dispatcher (owner mode gates, switch on event+4 codes 3000/0xbb9/0xbba/0xbbb, vtable forward or EVENT_MANAGER reschedule). ECX receiver; all exits `RET 0x4` prove one stack dword after this. Declared second stack formal `int event_code` is false — body indexes `*(event+4)` as an event object. Shape is `int __thiscall (void * this, void * event)` (do not invent typed event-object typedef beyond that plate). Static retail evidence only; exact event layouts, runtime AI UX, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `f703022500e2fe4cc7c97339170f51dda3a4e7a63e2715cbce802a44e8c41f13`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ff330.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `f703022500e2fe4cc7c97339170f51dda3a4e7a63e2715cbce802a44e8c41f13`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ff330:004ff4d5;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
Historical factory grade 1 — retained receipt, not a grade for this recheck. Its stale name/scalar argument are superseded above; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. The packet is preserved as history; its label is not the current name authority. The historical packet proposed no promotion.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
