# CUnit__ClassifyTargetRangeBand

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnit__ClassifyTargetRangeBand` at `0x004fb670`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fb670`

## Identity
- Body `[0x004fb670,0x004fb774]`, 261 bytes, 96 closure instructions. Raw pristine-body SHA-256 `dbccefd367bf75de1a8ebca0fc0fbef3a62ca7d56f35c9abe12a6aca025f4c19`; closure range SHA-256 `c2771bae3893ea01d9316db322f7fc0d2391ec9fe00c3295526f028d38945b65`; packet range-plus-bytes SHA-256 `4975869e504b7e514f5a9e332995b791807489ef3cabfccd41f95be85ac9541a`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnit__ClassifyTargetRangeBand` comes from the current closure/register row. Packet label matches canonical tracked name `CUnit__ClassifyTargetRangeBand`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnit__ClassifyTargetRangeBand(void * this, void * target_unit)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnit__ClassifyTargetRangeBand(void * this, void * target_unit)
```
- Packet-declared parameter list: `void * this, void * target_unit`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CUnit__ComputeMinBallisticTravelDistance` `0x005096a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ComputeMaxBallisticTravelDistance` `0x005099a0` ×1 site(s) (STATIC_DIRECT).
- Caller `CCarverAI__UpdateAttackAndReschedule` `0x00422b90` ×1 site(s) (instruction-flow).
- Caller `CInfantryAI__UpdateSupportSelection_0048a030` `0x0048a030` ×1 site(s) (instruction-flow).
- Caller `CMechAI__VFunc_9_004a0450` `0x004a0450` ×1 site(s) (instruction-flow).
- Caller `CPlaneAI__VFunc_9_004d21c0` `0x004d21c0` ×1 site(s) (instruction-flow).
- Caller `CSubmarineAI__VFunc_9_004ef340` `0x004ef340` ×1 site(s) (instruction-flow).
- Caller `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×1 site(s) (instruction-flow).
- Caller `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×1 site(s) (instruction-flow).
- Caller `CUnitAI__VFunc_9_004fec60` `0x004fec60` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave523 Unit/Squad targeting signature/comment hardening: RET 0x4 proves one explicit target_unit stack argument after ECX; the prior second parameter was register carryover. The body returns 2 for null/too-close/invalid target cases, returns 1 for beyond-range cases, and returns 0 when the target is inside the usable range. Ballistic-owner units compare planar/3D target distance against CUnit__ComputeMinBallisticTravelDistance and CUnit__ComputeMaxBallisticTravelDistance through this+0x140; fallback units use profile range fields this+0x144->+0x3d0 offsets +0x2c/+0x30. Static retail evidence only; exact enum names, range semantics, runtime weapon behavior, source identity, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `fcdf32731e7da16b2aeabd51888aeacd4ffb3e7d882902fa6a7dbbdca020a6d6`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 8 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x004fb670.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `fcdf32731e7da16b2aeabd51888aeacd4ffb3e7d882902fa6a7dbbdca020a6d6`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fb670:004fb774;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `MEDIUM`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
