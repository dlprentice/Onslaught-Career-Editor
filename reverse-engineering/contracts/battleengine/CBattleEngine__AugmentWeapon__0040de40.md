# CBattleEngine__AugmentWeapon

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__AugmentWeapon` at `0x0040de40`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040de40`

## Identity
- Body `[0x0040de40,0x0040df7b]`, 316 bytes. Raw pristine-body SHA-256 `303985a0888cb93cce3bb1440ce33c0ab8daab5075a7655f9facdf9ab7f18fbc`; closure range SHA-256 `d6ad9416b575928938961d2d43257b069b765bf8a5f5509cb70154bc49adc9c4`; packet range-plus-bytes SHA-256 `da3bf7e147119b90547c012bc416a42504decc5623ee8c79aad240f4bc3d0a64`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__AugmentWeapon` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_HIGH`.

## Calling convention
`__thiscall`: receiver in ECX; no explicit stack parameters. USER_DEFINED/source-analog naming is not retail proof.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__AugmentWeapon(void * this)
```
- `this` — receiver with component pointers +0x578/+0x57c, selector +0x260, indexed arrays +0x52c/+0x55c, fields +0x588/+0x2cc/+0x2f8/+0x2fc/+0x300/+0x30c, and indirect virtual slot +0x1d4.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_00672fd0` — read and copied to receiver +0x300 and +0x30c on the update path.
- `s_hud__s_00623314` — format string reference (`hud\\%s`).
- `DAT_00896988` and `_DAT_008969b8` — passed to sound lookup/play calls.

## Callees relied on / callers
- Callees (packet structured array): `CBattleEngineJetPart__LoseWeaponCharge` `0x00412000` ×1 (STATIC_DIRECT); `CMonitor__ClearCurrentTrackedEntryFlag60` `0x00414010` ×1 (STATIC_DIRECT); `CSoundManager__GetEffectByName` `0x004e1910` ×1 (STATIC_DIRECT); `CSoundManager__PlayEffect` `0x004e1940` ×1 (STATIC_DIRECT); `sprintf` `0x0055de9b` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngine__Move` `0x004081c0` ×1 site(s).
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Derives a pointer from `[[this+0x578]+0x18]`, then an index from nested +0xa4/+0x24. It enters the main path if the indexed 32-bit value at +0x55c is nonzero or the indexed float at +0x52c is positive. It calls indirect slot +0x1d4 and, when that result equals the derived pointer, clears +0x588; selector +0x260 then chooses either the packet-listed +0x578 clear helper for value 2 or the packet-listed +0x57c lose-charge helper for value 3. A nested +0xa4/+0x34 value is compared across further indirect calls, and +0x2cc is set to 1.0 if it differs. The main path then stores the global scalar to +0x300, 10.0 to +0x2f8, 1 to +0x2fc, performs a formatted sound lookup/play sequence, and stores the global scalar to +0x30c. Higher-level augmentation/weapon terminology is not independently proven.

## Error / edge behavior
The nested +0x578 chain and indirect-call results are dereferenced without null guards. If both indexed eligibility tests fail, no visible stores/calls occur. The decompile again omits the `%s` argument although packet stringRefs includes `hud_weapon_augmented`; exact effect-name construction is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040de40`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `d6ad9416b575928938961d2d43257b069b765bf8a5f5509cb70154bc49adc9c4` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `da3bf7e147119b90547c012bc416a42504decc5623ee8c79aad240f4bc3d0a64` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `303985a0888cb93cce3bb1440ce33c0ab8daab5075a7655f9facdf9ab7f18fbc` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040de40.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_HIGH`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: `0x00623314` = `hud\\%s`; `0x00623540` = `hud_weapon_augmented`. String association is static evidence, not execution proof.
- Crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::AugmentWeapon` line 3302 (`SOURCE_ANALOG`) — counted/source intent only, never retail semantic proof.

## Confidence
1 — gating and major stores/calls are visible, but repeated indirect calls, nested layouts, and missing format argument leave material ambiguity. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Contract and stability of indirect slot +0x1d4 across its three calls.
- Meanings of all indexed arrays and state fields.
- Actual sound-format substitution and failure behavior.
- Whether global-scalar copies are timestamps and what their units are.
