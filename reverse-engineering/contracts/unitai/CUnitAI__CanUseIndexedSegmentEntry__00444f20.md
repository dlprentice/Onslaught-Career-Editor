# CUnitAI__CanUseIndexedSegmentEntry

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__CanUseIndexedSegmentEntry` at `0x00444f20`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00444f20`

## Identity
- Body `[0x00444f20,0x0044500c]`, 237 bytes. Raw pristine-body SHA-256 `0e79d11cbd2a59246204c9b972686f2589a05d982a66e99204fc54dd791e6d83`; closure range SHA-256 `34c981874ead321a59c3991999832e3bdb309c9ebd208fa0c3037aa5780e954c`; packet range-plus-bytes SHA-256 `3f5eec2b3a74198dbcd430b03e987f9110fc98624c622e206f4a655647835429`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__CanUseIndexedSegmentEntry` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `bool __thiscall CUnitAI__CanUseIndexedSegmentEntry(void * this, int entryIndex)`: the receiver is modeled as `this`; explicit parameters follow the analyzed signature. Parameter labels are counted intent only.

## Prototype and parameter semantics
```c
bool __thiscall CUnitAI__CanUseIndexedSegmentEntry(void * this, int entryIndex)
```
- `this` — receiver/base pointer supplying indexed tables, fallback links, scalar fields, and two direct-callee arguments.
- `entryIndex` — signed integer used in multiple unchecked `*4` table offsets.

## Return value meaning
Returns a boolean selected by the displayed fallback chain, indirect predicates, two direct-call results, one float comparison, and the selected entry's +0x38 field. Higher-level eligibility meaning is counted name/comment intent only.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): `CDestroyableSegment__SumActiveValueRecursive` `0x00442890` ×1 (STATIC_DIRECT); `CDestroyableCoreSegment__AreCoreChildrenDestroyed` `0x004433f0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDestructableSegmentsMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` `0x00494fa0` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Loads the entry from the +4 table. If absent, it follows +0x10/+0x30; a null fallback returns true, while a successful indirect +0x24 result may traverse nested +0x160/+0x98 links and return whether a related entry's +0x38 is zero; other fallback cases return true. For a present entry, when receiver +0x24 is zero, indirect slot +0x14 returns zero, and entry word index 0x10 equals 1, it calls both packet-listed direct callees using receiver +0xc; the first result controls whether the second float result is compared with `0.3 * receiver(+0x18)`. Paths not returning false finish by testing whether entry word index 0xe is zero.

## Error / edge behavior
Table pointers, nested links, and `entryIndex` bounds are largely unguarded. Indirect slot meanings and the decompiler's float return from the second direct callee are not_determinable beyond the displayed comparison.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00444f20`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `34c981874ead321a59c3991999832e3bdb309c9ebd208fa0c3037aa5780e954c` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `3f5eec2b3a74198dbcd430b03e987f9110fc98624c622e206f4a655647835429` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `0e79d11cbd2a59246204c9b972686f2589a05d982a66e99204fc54dd791e6d83` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00444f20.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — branch structure and both direct calls are visible, but unchecked nested traversal and indirect predicates make the high-level contract ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Valid table bounds and concrete entry layout.
- Contracts of indirect slots +0x24 and +0x14.
- Meanings/units of +0x18 and the second direct-call float.
