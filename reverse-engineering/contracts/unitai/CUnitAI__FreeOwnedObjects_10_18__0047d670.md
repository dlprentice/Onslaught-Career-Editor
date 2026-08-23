# CUnitAI__FreeOwnedObjects_10_18

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__FreeOwnedObjects_10_18` at `0x0047d670`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0047d670`

## Identity
- Body `[0x0047d670,0x0047d6c8]`, 89 bytes, 24 closure instructions. Raw pristine-body SHA-256 `5a00acc7c2412048eb3cdb411c35b3e14aa6b89d0f5049e106d520afb1017a4d`; closure range SHA-256 `f7b89627b598bf493c5b33f3174f81667aa6ff397bc83653a6cf30b5ec40ae4b`; packet range-plus-bytes SHA-256 `ec3c3ed955573272a995fbea07789eb9cd0e8d429b40a99fd9c219e36fcacefd`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__FreeOwnedObjects_10_18` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__FreeOwnedObjects_10_18`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__FreeOwnedObjects_10_18(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__FreeOwnedObjects_10_18(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_009c3df0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CDXMemoryManager__Free` `0x00549220` ×2 site(s) (STATIC_DIRECT).
- Caller `Unwind@005d2c53` `0x005d2c53` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d2ed3` `0x005d2ed3` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d2f08` `0x005d2f08` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d34c3` `0x005d34c3` ×1 site(s) (instruction-flow).
- Caller `Unwind@005d34f8` `0x005d34f8` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Unwind-target cleanup helper: frees owned object pointers at +0x18 then +0x10 through CDXMemoryManager__Free(&DAT_009c3df0,...); decompile shows frees but no slot-clear stores. All inbound xrefs are Unwind@* sites — not Guide-owned +0x34/+0x3c slots of the adjacent CGroundVehicleGuide ctor/dtor. CUnitAI__ stem is unsupported. Rename propose-only toward an unwind/shared cleanup stem (e.g. SEH__FreeOwnedObjects_10_18 / owner once SEH parent is bound) outside this comment lane. Static retail evidence only; ownership completeness, runtime behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `8219267706d4b290fac3bc5a7c17553cafa045fc28b25683ab4df81e5fa2af1a`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 5 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 6; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0047d670.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `8219267706d4b290fac3bc5a7c17553cafa045fc28b25683ab4df81e5fa2af1a`.
- Digest derivation: closure SHA-256 hashes canonical range text `0047d670:0047d6c8;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
