# CBattleEngine__GetInterpolatedAutoAimPos

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetInterpolatedAutoAimPos` at `0x0040d7c0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040d7c0`

## Identity
- Body `[0x0040d7c0,0x0040da23]`, 612 bytes. Raw pristine-body SHA-256 `8f9cc42d045bb588fb6de7d2bfc79f988030a715facfe7ed82b0580465b0baa0`; closure range SHA-256 `de97964137c1a235c92c5c4690fa7a79f05a9d09e8261d59f9794bc30645b92c`; packet range-plus-bytes SHA-256 `5cb7fef69351b3c76a6a3622ea465e5b7a2fc0f22a639f11f0ea1fcfdfab06cc`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__GetInterpolatedAutoAimPos` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit pointer argument on the stack. The packet models a pointer return and a USER_DEFINED output-oriented signature.

## Prototype and parameter semantics
```c
void * __thiscall CBattleEngine__GetInterpolatedAutoAimPos(void * this, void * outPos)
```
- `this` — receiver supplying a pointer at +0x574, interpolation-offset fields at +0x4e8/+0x4ec and +0x4f4/+0x4f8, and global-fraction-dependent state.
- `outPos` — pointer passed to the final packet-listed vector-add call and returned unchanged. Exact destination/source direction of that helper call is not_determinable without its callee contract.

## Return value meaning
Returns the same `outPos` pointer value passed by the caller.

## Globals read/written
- `DAT_008a9e44` — read as the multiplier for position, orientation-basis, and two receiver-field interpolations.

## Callees relied on / callers
- Callees (packet structured array): `Vec3__SetXYZ` `0x00401ec0` ×1 (STATIC_DIRECT); `Vec3__Add` `0x00401ee0` ×4 (STATIC_DIRECT); `Mat34__SetRows` `0x00401f10` ×3 (STATIC_DIRECT); `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 (STATIC_DIRECT); `Vec3__SubtractToOut` `0x0040d120` ×3 (STATIC_DIRECT); `Vec3__ScaleToOut` `0x0040d150` ×3 (STATIC_DIRECT); `Mat34__MultiplyBasisToOut` `0x0040d320` ×1 (STATIC_DIRECT); `CPlayer__GetCurrentViewPoint` `0x004d2a70` ×1 (STATIC_DIRECT); `CPlayer__GetCurrentViewOrientation` `0x004d2ae0` ×1 (STATIC_DIRECT); `CPlayer__GetOldCurrentViewPoint` `0x004d2b40` ×1 (STATIC_DIRECT); `CPlayer__GetOldCurrentViewOrientation` `0x004d2bb0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CHud__RenderTargetMarkers3D` `0x00484340` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Uses the +0x574 object to fetch current and old view points and orientations through four packet-listed callees. It interpolates the three point components by `DAT_008a9e44`, derives and scales orientation-vector differences, assembles matrices with the packet-listed vector/matrix helpers, builds another matrix from two interpolated receiver-field pairs and a zero third argument, multiplies bases, selects three resulting matrix elements into a vector, performs a final vector add involving `outPos`, and returns `outPos`. The high-level `AutoAimPos` name/source analog is intent evidence only; exact coordinate conventions and write direction are not asserted.

## Error / edge behavior
Receiver, +0x574, and `outPos` are not null-guarded. The decompile contains `extraout_EAX`/row temporaries whose aliasing and argument roles are reconstruction artifacts. No clamp is visible for the interpolation multiplier.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040d7c0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `de97964137c1a235c92c5c4690fa7a79f05a9d09e8261d59f9794bc30645b92c` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `5cb7fef69351b3c76a6a3622ea465e5b7a2fc0f22a639f11f0ea1fcfdfab06cc` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `8f9cc42d045bb588fb6de7d2bfc79f988030a715facfe7ed82b0580465b0baa0` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040d7c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::GetInterpolatedAutoAimPos` line 3199 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
1 — the fetch/interpolate/matrix pipeline and returned pointer are visible, but decompiler temporaries obscure exact dataflow/output semantics. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Exact prototypes and destination/source ordering of the vector/matrix callees.
- Whether and where the final result is written through `outPos`.
- Coordinate system, units, and meaning of +0x4e8/+0x4ec/+0x4f4/+0x4f8.
