# CUnitAI__CheckField24RangeAgainstCandidate_004feac0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__CheckField24RangeAgainstCandidate_004feac0` at `0x004feac0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004feac0`

## Identity
- Body `[0x004feac0,0x004febd5]`, 278 bytes, 105 closure instructions. Raw pristine-body SHA-256 `f55cd356242be88ae459172c9f60c8b866067e1af76e0bfa4be341aaed786a20`; closure range SHA-256 `9b538fd783fbde610069a1ef679b099db5e242dfe021d532244f53ea8baf79a7`; packet range-plus-bytes SHA-256 `81e362e2220df198b33dbfa14530db9a4425d726ece976e85a0d582ea9a7c1d2`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__CheckField24RangeAgainstCandidate_004feac0` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__CheckField24RangeAgainstCandidate_004feac0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__CheckField24RangeAgainstCandidate_004feac0(void * this, void * candidate)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__CheckField24RangeAgainstCandidate_004feac0(void * this, void * candidate)
```
- Packet-declared parameter list: `void * this, void * candidate`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_008a9d9c`, `_DAT_005d85bc`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “SharedUnitAI vtable slot-8 body (CInfantryAI `0x005dbf14` and derived tables; RET `0x4`): when `this+0x24` reader present, range-gates reader vs owner `this+0x8` positions against `_DAT_005d85bc`, optionally `CGenericActiveReader__SetReader` retarget via reader `+0x3c`, then owner aim vfunc `+0xf4` / self vfunc `+0x10`; if `this+0xc==0` schedules `CEventManager__AddEvent_AtTime` event `0xbb9` with stack `candidate` forwarded as event payload; empty-field24 / failure paths return self vfunc `+0x18`. Not a boolean predicate on the stack candidate. Rename toward field24 follow/update / waypoint-follow maintenance helper (drop CheckField24RangeAgainstCandidate) remains propose-only outside this comment lane. Static retail listing/xref/vtable evidence only; exact source virtual name, range/candidate semantics, runtime AI behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `be22ecd411d1cca123c396f54ae87fb2f922bab5bbbd4be80d7f172f4d6c7cf1`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 3 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 17; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004feac0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `be22ecd411d1cca123c396f54ae87fb2f922bab5bbbd4be80d7f172f4d6c7cf1`.
- Digest derivation: closure SHA-256 hashes canonical range text `004feac0:004febd5;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
