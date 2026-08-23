# CRound__SelectBestTargetReaderAndSyncAimState

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__SelectBestTargetReaderAndSyncAimState` at `0x004dac90`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004dac90`

## Identity
- Body `[0x004dac90,0x004dafe3]`, 852 bytes. Raw pristine-body SHA-256 `85a75f0919ce84cac40f96b2ccb2c78771026e81fd96dfdd78131f418bcae8c8`; closure range SHA-256 `794c414b6fb601554307cbf1e598e3dba129e11e7f64d3aa8d1c02a7f150933e`; packet range-plus-bytes SHA-256 `9f02e099ee262a517e63dd925efb68600bc2d6b3e9d868845314f3b99f14ab76`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__SelectBestTargetReaderAndSyncAimState`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `void __thiscall CRound__SelectBestTargetReaderAndSyncAimState(void * this, void * eventPayload)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __thiscall CRound__SelectBestTargetReaderAndSyncAimState(void * this, void * eventPayload)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer supplying one +0xf0 gate block, +0xe8/+0xec cells, coordinate/transform-like fields, and output fields +0x108..+0x114.
- `eventPayload` — forwarded unchanged as the final argument to the packet-listed event-add call.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_008550d0` — its address is passed to the packet-listed first/next iteration callees.
- `DAT_008551a0` — its address is passed to the packet-listed add callee after selected cell updates.
- `DAT_008a9d9c` — passed to the packet-listed random callee.
- `DAT_00672fd0` — read in the displayed event-time arithmetic.
- `EVENT_MANAGER` — its address is passed to the final packet-listed event-add call.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×2 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×1 (STATIC_DIRECT); `CSPtrSet__First` `0x00406d20` ×1 (STATIC_DIRECT); `CSPtrSet__Next` `0x00406d30` ×1 (STATIC_DIRECT); `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 (STATIC_DIRECT); `CRound__RemoveActiveReaderById` `0x004dab50` ×2 (STATIC_DIRECT); `Random__NextLCGAbs` `0x004de8d0` ×1 (STATIC_DIRECT); `CSPtrSet__AddToHead` `0x004e5a80` ×2 (STATIC_DIRECT); `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CRound__Init` `0x004d8410` ×1 site(s); `VFuncSlot_00_004d9910` `0x004d9910` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Runs only when pointed-to +0x48 equals 1. If +0xe8 is null and +0xec is nonnull, copies/reorders a twelve-float receiver block, iterates `DAT_008550d0`, applies a +0x34 bit gate, derives and normalizes a three-component vector, compares one component with the prior best and a cosine threshold selected by pointed-to +0x54, and calls the listed compatibility predicate. Passing entries can trigger the listed removal, setter, and global-set add sequence. It then writes either -1 values or selected +0xe8 values to +0x108..+0x110, writes `local_34` to +0x114, derives an event time from the listed random result and `DAT_00672fd0`, and calls the listed event helper with value `0xfa3` and `eventPayload`.

## Error / edge behavior
`this`, +0xf0, iteration entries, and several nested fields are largely unguarded. `local_34` is not visibly initialized on the null +0xe8 path, and decompiler `extraout_var` values participate in predicate tests, so exact boolean and +0x114 semantics are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004dac90`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `794c414b6fb601554307cbf1e598e3dba129e11e7f64d3aa8d1c02a7f150933e` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `9f02e099ee262a517e63dd925efb68600bc2d6b3e9d868845314f3b99f14ab76` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `85a75f0919ce84cac40f96b2ccb2c78771026e81fd96dfdd78131f418bcae8c8` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004dac90.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
1 — scan, vector scoring, compatibility gates, selected-cell update, output writes, and event scheduling are visible, but uninitialized/extraout values and indirect layout prevent exact semantics. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Machine-level provenance of `local_34` and both `extraout_var` values.
- Concrete meanings/units of the transform, threshold, output, and event-time fields.
- Iteration and membership invariants of both global roots.
