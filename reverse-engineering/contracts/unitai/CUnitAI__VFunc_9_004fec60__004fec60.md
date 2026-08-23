# CUnitAI__VFunc_9_004fec60

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__VFunc_9_004fec60` at `0x004fec60`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fec60`

## Identity
- Body `[0x004fec60,0x004fef3f]`, 736 bytes, 229 closure instructions. Raw pristine-body SHA-256 `31974fd1b8d3abc3adc6d2ba0e3007478b5113af8c936caf9221dc5e89927911`; closure range SHA-256 `d55a9a7885dc9b58fdf08593cec98cdf7597eb06887680637640715585a2871a`; packet range-plus-bytes SHA-256 `1de1030537027112cd6795eb2dd8803ecdd8b5d0ce60d226d9bec969a8a4f827`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__VFunc_9_004fec60` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__VFunc_9_004fec60`.
- Packet name source `USER_DEFINED` and signature source `ANALYSIS` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `undefined __thiscall CUnitAI__VFunc_9_004fec60(void * this, void * param_1)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
undefined __thiscall CUnitAI__VFunc_9_004fec60(void * this, void * param_1)
```
- Packet-declared parameter list: `void * this, void * param_1`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `undefined`, but the displayed decompile declares `void` and reaches only a bare return. This signature/decompile contradiction is retained explicitly; no scalar return contract is claimed and confidence is 0.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ForwardAimTransformAndAttachTargetReader` `0x004fb650` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ClassifyTargetRangeBand` `0x004fb670` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__ForwardAttachedNodeVFunc14IfPresent` `0x004fce40` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ForwardAttachedNodeVFunc18IfPresent` `0x004fce80` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__ForwardAttachedNodeVFunc1CIfPresent` `0x004fcec0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` `0x004fd760` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- The packet contains no analyst comment, so this summary is bounded directly to the displayed decompile. After gates on receiver `+8` flags/state and `this+0x20`, a target at `this+0xc` is either handled through receiver slot `+0x100` when null or classified by `CUnit__ClassifyTargetRangeBand`; range classes 0/1/2 forward the target fields at `+0x1c/+0x20/+0x24/+0x28` through the packet-listed attached-node helpers at slots 0x18/0x1c/0x14. The alternate nested `receiver+0x148` path first requires its indirect `+0x14c` result to equal 1.
- If nested `receiver+0x164+0x19c` is nonzero and the linked-unit predicate succeeds, differences above 0.001 update `this+0x4c` and `this+0x58` by `(target-base)*0.028571429`, then the body builds an Euler matrix, transforms the stored offset relative to receiver position, and calls `CUnit__ForwardAimTransformAndAttachTargetReader`; this branch marks a local flag.
- Finally, the body calls receiver slot `+0x0c`, substitutes 0.0 when the transform branch marked the local flag, adds that value to `DAT_00672fd0`, and calls `CEventManager__AddEvent_AtTime` with event 3000, target `this`, priority 0, null data, and packet parameter `param_1` as the final reuse/event argument. Event meaning, field ownership, and timing units are not inferred from the numeric labels alone.
- The displayed decompile is non-empty and SHA-256 `5ac72048e7be7cca3529d5ae3f858f7eb4658b31374f66faa10b91228b36702b`; the summary above claims only its visible branches, arithmetic, arguments, and ordering.
- Structured inventory for this body: 0 caller record(s), 8 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Failure of the outer flag/state/`this+0x20` gate skips every visible side effect, including event insertion. A null `this+0xc` selects the receiver slot `+0x100` arm; classifier results outside 0/1/2 select none of the three attached-node forwards. Receiver/nested pointers and indirect targets are otherwise unguarded in the displayed decompile. Event-manager rejection/pool/future-time behavior belongs to the named callee contract and no rollback is visible here; NaN/overflow and concrete null-failure behavior remain not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 19; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fec60.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `5ac72048e7be7cca3529d5ae3f858f7eb4658b31374f66faa10b91228b36702b`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fec60:004fef3f;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
0 — exact identity, pristine bytes, arithmetic, branch order, event arguments, and structured edges are reconciled, but the packet signature says `undefined` while the displayed decompile says `void`; owner semantics and runtime causality remain unproved. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
