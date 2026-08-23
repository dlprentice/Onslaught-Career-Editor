# CRound__SpawnConfiguredProjectile

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__SpawnConfiguredProjectile` at `0x004db150`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004db150`

## Identity
- Body `[0x004db150,0x004db5f0]`, 1185 bytes. Raw pristine-body SHA-256 `60326e8cab2e07465328ba742765348790d9258cb8b3ad0297301c39022d4277`; closure range SHA-256 `95aed53ead3f4c07601ad075eddfa876841c4cfc4239bb22b8f44051cbb74fc1`; packet range-plus-bytes SHA-256 `8fa7cc93ad2e7e32138f02ff43174862ddbf321e766b55def452ab51386ccda7`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__SpawnConfiguredProjectile`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRound__SpawnConfiguredProjectile(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CRound__SpawnConfiguredProjectile(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer supplying origin-like floats, a +0xf0 block, +0xe8/+0xec cells, and an incremented +0x118 value.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_008a9d9c` — passed to three packet-listed random call sites.
- `DAT_006fadc8` — its address is passed to two packet-listed scalar sampling call sites.
- `DAT_008551a0` — its address is passed to the conditional packet-listed set-add call.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×2 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×2 (STATIC_DIRECT); `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 (STATIC_DIRECT); `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×2 (STATIC_DIRECT); `CInitThing__ctor` `0x0048dcf0` ×1 (STATIC_DIRECT); `CRound__RemoveActiveReaderById` `0x004dab50` ×1 (STATIC_DIRECT); `CRound__FindNearbyHostileWithinProjectileRadius` `0x004daba0` ×1 (STATIC_DIRECT); `Random__NextLCGAbs` `0x004de8d0` ×3 (STATIC_DIRECT); `CSPtrSet__AddToHead` `0x004e5a80` ×1 (STATIC_DIRECT); `CWorldPhysicsManager__CreateProjectile` `0x0050f7a0` ×1 (STATIC_DIRECT); `CRT__AcosDispatch_ST0` `0x0055dcb0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `VFuncSlot_00_004d9910` `0x004d9910` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Calls the listed nearby-selection helper. A null result causes two random-derived horizontal values around receiver +0x1c/+0x20 and one sampled third value; a nonnull result is queried through indirect slot +0x168. It calls the listed creation helper with +0xf0 and, on nonnull result, constructs a large local payload, derives separation and orientation-like numeric blocks, copies a twelve-float block, scales a three-component value, stores selected pointed-to fields, binds +0xec through a listed setter, conditionally replaces another cell with the selected pointer and adds to `DAT_008551a0`, computes another three-component separation and optional random adjustment, then invokes indirect slot +0x24 on the created object with the payload.

## Error / edge behavior
`this`, +0xf0, selected/created object fields, and indirect slots are largely unguarded. Creation failure skips the payload path. `local_448`/`local_438` and several payload fields lack clear initialization on all paths, limiting exact dataflow.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004db150`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `95aed53ead3f4c07601ad075eddfa876841c4cfc4239bb22b8f44051cbb74fc1` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `8fa7cc93ad2e7e32138f02ff43174862ddbf321e766b55def452ab51386ccda7` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `60326e8cab2e07465328ba742765348790d9258cb8b3ad0297301c39022d4277` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004db150.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
1 — selection/fallback, object-creation gate, payload construction, cell binding, random adjustment, and final indirect dispatch are visible; large unresolved payload and indirect contracts prevent exact semantics. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete layout and initialization of the large local payload.
- Contracts of indirect slots +0x168 and +0x24 and the created object's fields.
- Units/roles of all sampled, random-derived, and scaled values.
