# CRound__Init

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__Init` at `0x004d8410`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8410`

## Identity
- Body `[0x004d8410,0x004d8a46]`, 1591 bytes. Raw pristine-body SHA-256 `d00544a7f26d73df592d65951f68c0c72d232e9703428c1bb8613a9080b85241`; closure range SHA-256 `2dd9624514e11f9caebab3a2de74bba51e2acf2cb4b0a123082277188b2943d4`; packet range-plus-bytes SHA-256 `5d16075f405e5fba5bce44707880a94241589ae287a2e1d67cd454776c172145`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__Init`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall CRound__Init(void * this, void * init)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __thiscall CRound__Init(void * this, void * init)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — writable receiver/base pointer with copied scalar blocks, linked pointers, transform-like blocks, and several indirect slots.
- `init` — unguarded readable/writable pointer whose displayed fields are copied, overwritten, ORed, and passed to direct callees.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `ExceptionList` — saved, replaced, and restored.
- `DAT_009c3df0` — passed to both allocation calls.
- `DAT_00672fd0` — read for three displayed event-time arguments and arithmetic.
- `EVENT_MANAGER` — its address is passed to three structured event-add call sites.
- `DAT_0083cc88`, `DAT_0083cc8c`, `DAT_0083cc90`, and `DAT_0083cc94` — forwarded to the displayed effect-creation call.
- `DAT_006fadc8` — its address is passed to the displayed trace call.
- `DAT_008550f0` — its address is passed to the final conditional set-add call.

## Callees relied on / callers
- Callees (packet structured array): `CActor__Init` `0x004011e0` ×2 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×1 (STATIC_DIRECT); `CMeshRenderer__CopyBasisAndRefreshTime` `0x00403650` ×1 (STATIC_DIRECT); `CEventManager__AddEvent_AtTime` `0x0044b370` ×3 (STATIC_DIRECT); `CCollisionSeekingThing__ctor_base` `0x00488ef0` ×1 (STATIC_DIRECT); `CHLCollisionDetector__ctor_base` `0x00488f00` ×1 (STATIC_DIRECT); `CHeightField__TraceLineAgainstHeightfield` `0x00490a40` ×1 (STATIC_DIRECT); `CParticleManager__CreateEffect` `0x004cb3d0` ×1 (STATIC_DIRECT); `CRound__SelectBestTargetReaderAndSyncAimState` `0x004dac90` ×1 (STATIC_DIRECT); `CSPtrSet__AddToHead` `0x004e5a80` ×1 (STATIC_DIRECT); `CDXMemoryManager__Alloc` `0x005490e0` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CMissile__Init` `0x004baae0` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Copies five dwords from `init+0x3bc..+0x3cc` to `this+0x108..+0x118`, stores two further input fields, clears +0x128, and conditionally changes input flags/fields from values reached through `this+0xf0`. One major branch conditionally allocates and initializes one of two differently sized blocks, calls the packet-listed base initializer, schedules an event, optionally creates and copies data into a linked object, and may trace a line and schedule another event. The alternate branch overwrites `init+0x70`, calls the base initializer, schedules an event, and copies four receiver dwords to +0xf8..+0x104. A final gate may add `this` to a global set before the last packet-listed direct call.

## Error / edge behavior
`this`, `init`, the +0xf0 target, and several nested pointers/indirect slots are largely unguarded. Allocation failure is represented by null storage, but downstream ownership and base-initializer expectations are unknown; numerous decompiler locals and transform values are not fully attributable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8410`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `2dd9624514e11f9caebab3a2de74bba51e2acf2cb4b0a123082277188b2943d4` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `5d16075f405e5fba5bce44707880a94241589ae287a2e1d67cd454776c172145` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `d00544a7f26d73df592d65951f68c0c72d232e9703428c1bb8613a9080b85241` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8410.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: `0x00631d38` value "C:\\\\dev\\\\ONSLAUGHT2\\\\Round.cpp", UTF-8 SHA-256 `638245528f956398b41a3dd119ff5b09a0c0f28455aed2dd9ed0a79e3d20551b`. Literal values are evidence; any interpretation remains bounded to displayed use.
- Crosswalk: none in the cohort-4 brief.

## Confidence
1 — major copies, branch gates, allocations, event calls, trace, and final set/call are visible, but the large body has unresolved locals, indirect calls, and concrete field meanings. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete layouts and ownership of both allocated block shapes.
- Origins/meaning of unresolved stack transform values and indirect slot outputs.
- Semantic roles and units of all copied, timed, and traced fields.
