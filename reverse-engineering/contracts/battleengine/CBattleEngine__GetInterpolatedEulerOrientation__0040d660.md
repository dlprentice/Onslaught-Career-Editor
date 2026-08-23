# CBattleEngine__GetInterpolatedEulerOrientation

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetInterpolatedEulerOrientation` at `0x0040d660`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040d660`

## Identity
- Body `[0x0040d660,0x0040d7ba]`, 347 bytes. Raw pristine-body SHA-256 `1fc4a987d89b06d1ae7d804f0bd28af8fc2edade765a3f9eec09bdec839e4b06`; closure range SHA-256 `48023e2f2eb5f08b58015171fc7747c0901b6124e6c51e2edad98a54b93874df`; packet range-plus-bytes SHA-256 `a7de14d268f7eef68e2a33c5523ad7fa3d57fbb47869b2ab923dd17382ddd09c`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__GetInterpolatedEulerOrientation` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit output pointer on the stack. The USER_DEFINED Euler-oriented naming is source intent, while the three-component writes are direct evidence.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__GetInterpolatedEulerOrientation(void * this, void * outEuler)
```
- `this` — receiver supplying three current floats at +0x114/+0x118/+0x11c and three comparison/base floats at +0x590/+0x594/+0x598.
- `outEuler` — output pointer receiving three consecutive 32-bit float stores at offsets 0, 4, and 8. No size/alignment contract is visible.

## Return value meaning
not_applicable (void); results are written through `outEuler`.

## Globals read/written
- `DAT_008a9e44` — read repeatedly as the interpolation multiplier; range and timing semantics are unknown.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `CDXCompass__Render` `0x00427210` ×2 site(s); `CHud__RenderTacticalRadarContacts` `0x00484c50` ×2 site(s); `CHud__RoutePanel_T3_004858d0` `0x004858d0` ×1 site(s); `CDXCompass__RenderWorldSpaceOverlay` `0x0053cd30` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
For each of three component pairs, conditionally adjusts the comparison value by plus or minus approximately 2π when the values straddle thresholds near plus/minus π/2. It then writes `(current-adjusted_comparison)*DAT_008a9e44 + original_comparison` for each component to the output. The body proves three wrapped floating interpolations; component names and angular units beyond the observed constants remain source-intent interpretations.

## Error / edge behavior
`outEuler` and `this` are unguarded. NaN comparisons bypass wrap adjustments in the usual unordered way and propagate through arithmetic. The interpolation multiplier is not clamped in this body.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040d660`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `48023e2f2eb5f08b58015171fc7747c0901b6124e6c51e2edad98a54b93874df` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `a7de14d268f7eef68e2a33c5523ad7fa3d57fbb47869b2ab923dd17382ddd09c` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `1fc4a987d89b06d1ae7d804f0bd28af8fc2edade765a3f9eec09bdec839e4b06` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040d660.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::GetInterpolatedEulerOrientation` line 3187 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — all three wrap and interpolation paths are explicit; semantic component names and multiplier range are unproven. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Formal component order and units.
- Expected range of `DAT_008a9e44` and behavior outside it.
- Why wrap thresholds are ±π/2 rather than another boundary, and whether decompiler pairing is exact.
