# CUnitAI__TryStartFollowWaypoint_004fea30

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__TryStartFollowWaypoint_004fea30` at `0x004fea30`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fea30`

## Identity
- Body `[0x004fea30,0x004feab0]`, 129 bytes, 41 closure instructions. Raw pristine-body SHA-256 `31ecb2cdb3de3aa8f8550a3d45968d1d550076afa237d7507c004fd6d8f06bf5`; closure range SHA-256 `19e4a7ba85dad57df2ea07c35c512ad4798134c5eff5d0d410f28b17fea9997e`; packet range-plus-bytes SHA-256 `2658f350348889b7eb82e5aa7d0df851f7b8d0c46be3a8cf35f8068686fc835d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__TryStartFollowWaypoint_004fea30` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__TryStartFollowWaypoint_004fea30`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__TryStartFollowWaypoint_004fea30(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__TryStartFollowWaypoint_004fea30(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_0066f580`, `DAT_0066ffc8`, `DAT_00672fd0`, `s__s_CANT_start_following_waypoint_00633cb0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__AppendToStatusBufferV` `0x00472240` ×1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family vfunc: if this+0x24!=0 and this+0x20!=0, clears this+0x20, schedules EVENT_MANAGER event 0xbb9 with DAT_00672fd0 time base, returns 1; if this+0x24!=0 but this+0x20==0, calls owner vfunc +0x1c and logs 'CANT start following waypoint', returns 0; else returns 0. Static listing/xref/vtable evidence only; exact source virtual name, field meanings, runtime AI behavior, BEA patching, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `9c6bf3eda1f3e91a0326c4e08bdd20123b475973befc64665ba06ce8d5eb7439`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 4 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fea30.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `9c6bf3eda1f3e91a0326c4e08bdd20123b475973befc64665ba06ce8d5eb7439`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fea30:004feab0;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00633cb0` length 57 SHA-256 `72f44c817055940e7e6dbe784f7f51f6d7476d993e932822ab819528efa0ed74` value `%s CANT start following waypoints cos it already was !!!`.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
