# CBattleEngine__Rearm

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__Rearm` at `0x0040ac50`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040ac50`

## Identity
- Body `[0x0040ac50,0x0040acb1]`, 98 bytes. Raw pristine-body SHA-256 `10c2e75fccfb880843be9ae98c554762a9e9b3f7e0cf05eed0cff82282fed797`; closure range SHA-256 `4c314ce49fb1bd2a6290b666e772612fc2678d96a9f29c5f27457a70f3e9cd57`; packet range-plus-bytes SHA-256 `49d5358034788c4553c7423faff337f752dd25e717eb443a06968c3418c280d2`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__Rearm` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH`.

## Calling convention
`__thiscall`: the receiver is modeled in ECX and the packet models one explicit stack argument, `inAmount`. The signature is USER_DEFINED and therefore evidence about the analyzed ABI model, not a recovered retail source declaration.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__Rearm(void * this, float inAmount)
```
- `this` — receiver base used for six adjacent records beginning at +0x52c and for a configuration pointer at +0x4b0.
- `inAmount` — float used only when greater than zero; for each eligible record it scales a configuration-derived float before addition. Units and source-level meaning are unknown.

## Return value meaning
not_applicable (the packet and decompile model a void return).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): none.
- Callers (packet structured array): `VFuncSlot_39_004d8ae0` `0x004d8ae0` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
If `inAmount <= 0.0`, the body returns without stores. Otherwise it visits six adjacent floats starting at `this+0x52c`. A record is updated only when the float twelve float-elements beyond the current element is zero. The update adds `inAmount` times a float selected through `this+0x4b0`; if the result exceeds that selected float, the stored result is clamped to it. The exact pointed-to layout and the roles of the six values are not_determinable from this body.

## Error / edge behavior
Negative, zero, and unordered/NaN comparisons do not enter the update loop under the visible `0.0 < inAmount` test. No receiver/configuration null guards are visible. Floating-point overflow, NaN propagation, and aliasing effects are not_determinable statically.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040ac50`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `4c314ce49fb1bd2a6290b666e772612fc2678d96a9f29c5f27457a70f3e9cd57` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `49d5358034788c4553c7423faff337f752dd25e717eb443a06968c3418c280d2` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `10c2e75fccfb880843be9ae98c554762a9e9b3f7e0cf05eed0cff82282fed797` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040ac50.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Rearm` line 2256 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
2 — loop bounds, gate, arithmetic, and clamp are visible; record/configuration semantics remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meanings and units of the six values at +0x52c..+0x540.
- Meaning of the eligibility floats reached at a +0x30 relative displacement and the configuration-derived scale/cap fields.
- Whether the USER_DEFINED `Rearm`/`inAmount` names match retail terminology.
