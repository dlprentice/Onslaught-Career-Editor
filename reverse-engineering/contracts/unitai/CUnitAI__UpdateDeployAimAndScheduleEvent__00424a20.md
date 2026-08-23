# CUnitAI__UpdateDeployAimAndScheduleEvent

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__UpdateDeployAimAndScheduleEvent` at `0x00424a20`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00424a20`

## Identity
- Body `[0x00424a20,0x00424bd1]`, 434 bytes. Raw pristine-body SHA-256 `7682f1285153675dc8ef55531be9031b4fdfdaad33ca73790af3ceaf710c62b1`; closure range SHA-256 `5601ed76383dde319e32928cd863189fc0f4bf000a04ef587e18d6a56ce2b5be`; packet range-plus-bytes SHA-256 `bc412df55ef67bbf0d074269e7193c0a1f3315479fcaceb0192de5cf728cf0cf`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__UpdateDeployAimAndScheduleEvent` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)
```
- `this` — receiver/base pointer containing source/destination scalar blocks, a linked pointer at +0x110, offset fields +0x90..+0xa0, and event/phase state.

## Return value meaning
not_applicable (void).

## Globals read/written
- `EVENT_MANAGER` — its address is passed to the packet-listed event-add callee.

## Callees relied on / callers
- Callees (packet structured array): `CUnitAI__AdvanceDeployAnimationPhase` `0x00424be0` ×1 (STATIC_DIRECT); `CUnitAI__UpdateDeployTrackingTransformTowardTarget` `0x00424ca0` ×1 (STATIC_DIRECT); `CUnitAI__DecayDeployTrackingTransformToNeutral` `0x004250f0` ×1 (STATIC_DIRECT); `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CCockpit__VFunc_0_00424a00` `0x00424a00` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Copies +0xc/+0x10/+0x14/+0x18 to +0x1c/+0x20/+0x24/+0x28 and copies twelve dwords from +0x2c to +0x5c. When +0x110 is nonzero and bit 2 of its +0x2c byte is clear, it chooses one of two packet-listed direct callees according to linked +0x260, resets +0xc/+0x10/+0x14, combines `cos(+0xa0)` with +0x90/+0x94/+0x98, scales +0x90..+0x9c by 0.8, increments +0xa0 by 0.8 when any scaled magnitude exceeds 0.001, calls the packet-listed event helper with event value `0x7d1`, and calls the packet-listed phase helper.

## Error / edge behavior
The decompile assigns receiver +0x18 from `local_14[4]` without a visible initialization, so that store's exact value is not_determinable. Receiver accesses are unguarded; the main path is skipped for a null linked pointer or set bit 2.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00424a20`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5601ed76383dde319e32928cd863189fc0f4bf000a04ef587e18d6a56ce2b5be` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `bc412df55ef67bbf0d074269e7193c0a1f3315479fcaceb0192de5cf728cf0cf` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7682f1285153675dc8ef55531be9031b4fdfdaad33ca73790af3ceaf710c62b1` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00424a20.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — major copy/gate/damping/call structure is visible, but one stack value and higher-level transform/event meanings remain ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Origin of `local_14[4]` stored at +0x18.
- Meanings/units of the copied blocks, offset fields, and event value `0x7d1`.
