# CUnitAI__IsCachedAnchorPointValid

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__IsCachedAnchorPointValid` at `0x00447d50`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00447d50`

## Identity
- Body `[0x00447d50,0x00447f44]`, 501 bytes. Raw pristine-body SHA-256 `e653a96d6e58096daf7da24945d46e143a50343d1b9e325d54a8965b51f2a56d`; closure range SHA-256 `5f1c01b48274ef2e7dc02e00a6b1363a4c682c040aaade5a1a742c445354c339`; packet range-plus-bytes SHA-256 `42222b5225511e518fae53911103411c6051028c5d485c116b9b1651e88fde96`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__IsCachedAnchorPointValid` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)
```
- `unitAI` — receiver/base pointer containing cached floats +0x280..+0x28c, state +0x27c, and indirect slots including +0x40.

## Return value meaning
Returns 0 on any displayed nearby-entry rejection or clear occupancy-bit test; otherwise returns 1. Valid/anchor wording is counted name/comment intent only.

## Globals read/written
- `DAT_00704200` — its address is passed to the two packet-listed radius-iteration callees.
- `DAT_00855298` — read into `iVar4`, repeatedly restored during iteration, and then used as the base for byte/bit scanning.
- `DAT_006fadc8` — its address is passed to the packet-listed scalar-sampling callee.

## Callees relied on / callers
- Callees (packet structured array): `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` ×1 (STATIC_DIRECT); `CMapWho__GetFirstEntryWithinRadius` `0x00491ea0` ×1 (STATIC_DIRECT); `CMapWho__GetNextEntryWithinRadius` `0x00492020` ×1 (STATIC_DIRECT); `CMapWhoEntry__GetOwner` `0x00492c90` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDropship__SetDoorWingState2AndClampYawDelta` `0x00447a40` ×1 site(s); `CUnitAI__GetOrGenerateCachedAnchorPoint` `0x00447bb0` ×2 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Calls indirect slot +0x40 once and doubles that result to form the initial radius, then obtains nearby
entries through the two packet-listed iterator callees. For each entry, it calls the listed owner
getter, tests owner flag bit 0x10 and self-inequality, samples a scalar, and later invokes slot +0x40
twice on `unitAI` and twice on the nearby owner for the displayed distance comparison. It can return
0 after those height/distance calculations. If receiver +0x27c is neither 2 nor 3, it rounds another
slot +0x40 result and cached X/Y values, scans a bounded 256-by-256-style byte/bit region based at
`DAT_00855298`, and returns 0 when any tested bit is clear; otherwise it returns 1.

## Error / edge behavior
The decompile contains the suspicious condition `(float)uStack_10 + 25.0 != 0.0` after assigning a boolean to `uStack_10`; this appears always true for 0/1 and makes the exact nearby-entry rejection rule not_determinable. Receiver/owner pointers and indirect calls are largely unguarded.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00447d50`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5f1c01b48274ef2e7dc02e00a6b1363a4c682c040aaade5a1a742c445354c339` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `42222b5225511e518fae53911103411c6051028c5d485c116b9b1651e88fde96` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `e653a96d6e58096daf7da24945d46e143a50343d1b9e325d54a8965b51f2a56d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00447d50.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
0 — iterator and bit-scan structure are visible, but a suspicious decompiler expression materially prevents an honest exact validity contract. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Machine-level meaning of the `uStack_10` comparison.
- Layout and lifecycle of the `DAT_00855298` byte/bit base.
- Contracts of indirect +0x40 and nearby-entry owner fields.
