# CUnitAI__RefreshCachedComponentTransform

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__RefreshCachedComponentTransform` at `0x00428500`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00428500`

## Identity
- Body `[0x00428500,0x00428707]`, 520 bytes. Raw pristine-body SHA-256 `176381253b56aa477a4203dc10c84b3dd0bc91e11f0bc159444c465cd6a7e51d`; closure range SHA-256 `2523bb917b41b23ed0829b22cb06143117a6ad7eebd522e46f2beb222f0f2b3b`; packet range-plus-bytes SHA-256 `e392d63691eca58e04b2dc3897d86ac257b2f5a4503c51ce45750b8207cb02ea`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__RefreshCachedComponentTransform` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)
```
- `this` — receiver/base pointer with a cache marker at +0x278, state/link fields, angle-like floats +0x250/+0x254, and a twelve-dword destination at +0x3c.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_008a9aac` — compared with +0x278 and then stored there after a refresh attempt.
- `s_Component_006248d4` — packet stringRef value `Component`, passed to an indirect call when +0x26c is nonzero.

## Callees relied on / callers
- Callees (packet structured array): `Vec3__SetXYZ` `0x00401ec0` ×1 (STATIC_DIRECT); `Mat34__SetRows` `0x00401f10` ×1 (STATIC_DIRECT); `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CComponent__UpdateActivationStateAndSpawnPickup` `0x00428110` ×1 site(s); `CComponent__GetRenderPosFromActorOrCache` `0x00428710` ×1 site(s); `CComponent__GetRenderOrientationFromActorOrCache` `0x00428770` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Returns without work when +0x278 equals `DAT_008a9aac`. Otherwise, when bit 2 at +0x2c is clear or the nested +0x164/+0x198 value is zero, it builds one matrix from +0x250/+0x254, optionally performs an indirect call with the packet-recorded `Component` string and receiver fields when +0x26c is nonzero, combines displayed row values, calls the packet-listed row setter, and copies twelve dwords to +0x3c. It finally stores `DAT_008a9aac` at +0x278.

## Error / edge behavior
The nested +0x164 dereference and receiver are unguarded. Several local matrix values and `row0` lack visible initialization when the optional indirect call is absent, so exact transform dataflow is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00428500`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `2523bb917b41b23ed0829b22cb06143117a6ad7eebd522e46f2beb222f0f2b3b` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e392d63691eca58e04b2dc3897d86ac257b2f5a4503c51ce45750b8207cb02ea` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `176381253b56aa477a4203dc10c84b3dd0bc91e11f0bc159444c465cd6a7e51d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00428500.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: `0x006248d4` value "Component", UTF-8 SHA-256 `ce54f0e22dbb39de8a6d9ae0b32b3ecac5bc749fddcb78e4f1e572212b338d63`. Values are counted literals/source intent only.
- Crosswalk: none in the cohort brief.

## Confidence
1 — cache gate, optional string-bearing indirect call, matrix arithmetic, copy, and marker update are visible, but local initialization is ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Initialization/provenance of `row0` and local matrix values.
- Contract of the +0x26c indirect call and meaning of the `Component` selector.
