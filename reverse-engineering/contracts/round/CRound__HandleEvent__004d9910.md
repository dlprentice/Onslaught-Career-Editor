# CRound__HandleEvent

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__HandleEvent` at `0x004d9910`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; TTD-session execution rows are cited below; they corroborate execution only.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d9910`

## Identity
- Body `[0x004d9910,0x004d9d45]`, 1078 bytes. Raw pristine-body SHA-256 `d54da932205b40f631e650c2f3902faa230f69c1efe029c428aff1305cff2c2b`; closure range SHA-256 `5b0e5818d0c66e68b43e7c3a1ca900b63e18323899045b044641df99af629864`; packet range-plus-bytes SHA-256 `0de64b67a1279dcb6defe59cb0aa760c224308dcf65e3d9b9fb208312a49b15b`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__HandleEvent`. Packet/decompile metadata name: `VFuncSlot_00_004d9910`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall VFuncSlot_00_004d9910(void * this, void * event_record)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __thiscall VFuncSlot_00_004d9910(void * this, void * event_record)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer whose +0xf0 block, state fields, vector-like values, allocation cell +0x38, and indirect slot +0xc8 participate in event-selected paths.
- `event_record` — unguarded pointer whose word at +4 selects the switch arm; its float at +0x10 is read on arm 4001, and the pointer is forwarded unchanged on arm 4003 and the default arm.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `ExceptionList` — saved, replaced on selected paths, and restored before ordinary return or the two explicit early returns.
- `DAT_009c3df0` — its address is passed to both displayed allocation calls on the gated 4000 path.
- `DAT_006fadc8` — its address is passed to the displayed heightfield trace call.
- `DAT_00672fd0` — read for the 4000 event time and the 4001 time-delta calculation.
- `EVENT_MANAGER` — its address is passed to the displayed event-add call with event value 2000.
- `DAT_006fbdfc` — read as the 4001 comparison threshold after subtracting literal 0.001.

## Callees relied on / callers
- Callees (packet structured array): `CActor__HandleEvent` `0x004019e0` ×1 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×1 (STATIC_DIRECT); `CCSRay__CreateEffect` `0x00426a40` ×1 (STATIC_DIRECT); `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 (STATIC_DIRECT); `CMonitor__ctor` `0x00466120` ×1 (STATIC_DIRECT); `CHeightField__TraceLineAgainstHeightfield` `0x00490a40` ×1 (STATIC_DIRECT); `CEngine__InitRoundLaunchStateDefaults` `0x004d9d60` ×1 (STATIC_DIRECT); `CRound__UpdateEffectTransformByMode_004d9f30` `0x004d9f30` ×4 (STATIC_DIRECT); `CRound__SelectBestTargetReaderAndSyncAimState` `0x004dac90` ×1 (STATIC_DIRECT); `CRound__SpawnConfiguredProjectile` `0x004db150` ×1 (STATIC_DIRECT); `CDXMemoryManager__Alloc` `0x005490e0` ×2 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Switches on the word at `event_record+4`. Arm 4000 follows gates at pointed-to +0x4c/+0x74/+0x50: its largest path builds local data, performs two allocations, invokes an indirect slot through receiver +0x38, and, when receiver +0x2c bit 0x04 is clear, traces a line. The two trace outcomes write different receiver position/state fields, call the packet-listed transform helper with mode 0 or 1, set bit 0x04, schedule event 2000 at `DAT_00672fd0+0.1`, and return; other 4000 paths call the transform helper with mode 0 where displayed and/or invoke indirect slot +0xc8. Arm 4001 runs only when pointed-to +0x30 and receiver +0x120 are zero, optionally adjusts +0x1c/+0x20/+0x24 from the event time and scaled receiver values, chooses transform-helper mode 1 or 2 from the +0x24 threshold, and conditionally invokes slot +0xc8. Arm 4002 calls the listed projectile helper, clears +0x120, and invokes slot +0xc8. Arm 4003 forwards to the listed target-selection helper. The default arm forwards to the listed base event handler.

## Error / edge behavior
`this`, `event_record`, +0xf0, nested fields, and indirect slots are not validated. The two allocation results are null-tested, but the receiver +0x38 result is later dereferenced for an indirect call; allocation/lifetime guarantees are not_determinable. Several local payload values have no clear visible initialization, and exact event schema, field meanings, external effects, and indirect-call contracts remain unproven.

## Runtime corroboration (TTD, bounded)
The cohort-4 brief supplies these ten exact TTD rows:
- `batch-1` — corroborated in 7/10 coverage sessions
- `batch-2` — corroborated in 7/10 coverage sessions
- `batch-3` — corroborated in 8/10 coverage sessions
- `batch-4` — corroborated in 2/10 coverage sessions
- `batch-5` — corroborated in 5/10 coverage sessions
- `batch-6` — corroborated in 4/11 coverage sessions
- `batch-7` — corroborated in 2/7 coverage sessions
- `batch-8` — corroborated in 1/4 coverage sessions
- `batch-9` — corroborated in 2/3 coverage sessions
- `batch-10` — no coverage collector output for this batch's sessions
These rows prove bounded execution only (bounded: batch-1, batch-2, batch-3, batch-4, batch-5, batch-6, batch-7, batch-8, batch-9, batch-10). Execution coverage alone does not prove the semantic contract, parameter/field meanings, side-effect completeness, or parity, and it does not justify promotion.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5b0e5818d0c66e68b43e7c3a1ca900b63e18323899045b044641df99af629864` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `0de64b67a1279dcb6defe59cb0aa760c224308dcf65e3d9b9fb208312a49b15b` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `d54da932205b40f631e650c2f3902faa230f69c1efe029c428aff1305cff2c2b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d9910.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: ten rows are quoted exactly in Runtime corroboration; they establish bounded execution only, not semantic correctness.
- Packet stringRefs: `0x00631d38` value "C:\\\\dev\\\\ONSLAUGHT2\\\\Round.cpp", UTF-8 SHA-256 `638245528f956398b41a3dd119ff5b09a0c0f28455aed2dd9ed0a79e3d20551b`. Literal values are evidence; any interpretation remains bounded to displayed use.
- Crosswalk: none in the cohort-4 brief.

## Confidence
1 — the switch keys, major gates, direct-call routing, selected writes, event scheduling, and fallbacks are visible, but the large arm-4000 payload, unresolved locals, indirect slots, and field meanings prevent a complete contract. Confidence is capped at 3 because execution coverage alone does not prove the semantic contract. Proposed promotion: false.

## Unresolved questions
- Concrete schema and source-level meaning of switch values 4000 through 4003 and `event_record+0x10`.
- Initialization and layout of the large arm-4000 local payload and both allocated objects.
- Contracts of indirect slot +0xc8 and the indirect call through receiver +0x38, including allocation-failure behavior.
- Completeness of external writes/effects and meanings of all receiver and pointed-to fields.
