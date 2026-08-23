# CBattleEngine__BuildInterpolatedWorldTransform

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__BuildInterpolatedWorldTransform` at `0x0040da30`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040da30`

## Identity
- Body `[0x0040da30,0x0040dc2c]`, 509 bytes, 143 closure instructions. Raw pristine-body SHA-256 `212161fafff8bf387903e963d7f15593de8395330dc84fce04c8a41779d4c14a`; closure range SHA-256 `ace9a3c4aed668c201843f2310336db38272f9956a5fcdf218ba50d4b9bb4b25`; packet range-plus-bytes SHA-256 `11c55e4af5e1a7e7a94f208e3fb435835cc5054cd808bbdbe6d06546858be5a1`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__BuildInterpolatedWorldTransform` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__BuildInterpolatedWorldTransform`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CBattleEngine__BuildInterpolatedWorldTransform(void * this, void * outWorldTransform)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CBattleEngine__BuildInterpolatedWorldTransform(void * this, void * outWorldTransform)
```
- Packet-declared parameter list: `void * this, void * outWorldTransform`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void *`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_008a9e44`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `Vec3__SetXYZ` `0x00401ec0` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__Add` `0x00401ee0` ×4 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetRows` `0x00401f10` ×3 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 site(s) (STATIC_DIRECT).
- Callee `Vec3__SubtractToOut` `0x0040d120` ×3 site(s) (STATIC_DIRECT).
- Callee `Vec3__ScaleToOut` `0x0040d150` ×3 site(s) (STATIC_DIRECT).
- Callee `Mat34__MultiplyBasisToOut` `0x0040d320` ×1 site(s) (STATIC_DIRECT).
- Caller `CHud__RenderTargetMarkers3D` `0x00484340` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “BattleEngine interpolated world/render helper. Terminator is `RET 0x4` (one stack dword after ECX `this`) — ABI-real out-buffer only; declared `unusedContext` is not stack-real. Body builds local Mat34 work then finishes with Vec3 stores into the out-buffer and returns that pointer. Inbound xref from CHud__RenderTargetMarkers3D (metadata plate still names CExplosionInitThing__RenderTargetMarkers3D). Static retail evidence only; concrete transform layout, rename toward Vec3 out-position, runtime render behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `234c1d0d2f57a5334ad90ff8b056e7adfa3e313113a44a2c893c7640787ff94d`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 7 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 508 covered bytes; evidence `name=CBattleEngine__BuildInterpolatedWorldTransform`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040da30.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `234c1d0d2f57a5334ad90ff8b056e7adfa3e313113a44a2c893c7640787ff94d`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040da30:0040dc2c;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
