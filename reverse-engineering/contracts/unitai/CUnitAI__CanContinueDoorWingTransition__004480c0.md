# CUnitAI__CanContinueDoorWingTransition

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__CanContinueDoorWingTransition` at `0x004480c0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004480c0`

## Identity
- Body `[0x004480c0,0x0044810f]`, 80 bytes. Raw pristine-body SHA-256 `aaae27d0385af734727f74cb5fa383dfe9023edac55d79cdf182f6bae933294a`; closure range SHA-256 `b2b9b6ee0baa52db01ecbe2adb72f085aa90141765f5b66540b109e076c9c145`; packet range-plus-bytes SHA-256 `f50a32d5c6f0fbb83f0e1a03f3f155eda315478f4114ef010e2af3b0eb30f9ad`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__CanContinueDoorWingTransition` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `bool __fastcall CUnitAI__CanContinueDoorWingTransition(void * unitAi)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
bool __fastcall CUnitAI__CanContinueDoorWingTransition(void * unitAi)
```
- `unitAi` — receiver/base pointer read at +0x294 and used for indirect slot +0x144 and both packet-listed direct calls. The label is counted intent only.

## Return value meaning
Returns true when +0x294 is nonzero, or when the displayed child-result/target-result/direct-predicate chain succeeds; otherwise returns false.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×1 (STATIC_DIRECT); `CUnit__AreSpawnedChildrenReady` `0x004fd7e0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDropshipAI__VFunc_09_00448580` `0x00448580` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Returns true immediately for nonzero +0x294. Otherwise it calls the packet-listed child predicate; only when that result tests zero does it call indirect slot +0x144, call the same slot again to obtain a pointer when the first result is nonzero, and call the packet-listed second direct callee with `(unitAi, pointer, 1)`. A nonzero final result returns true; all other paths return false. Door/wing/ballistic wording is counted name/callee intent only.

## Error / edge behavior
The receiver and indirect slot are unguarded. Slot +0x144 is invoked twice and could yield different results; `extraout_var` participates in the first boolean test, so exact boolean widening is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x004480c0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `b2b9b6ee0baa52db01ecbe2adb72f085aa90141765f5b66540b109e076c9c145` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `f50a32d5c6f0fbb83f0e1a03f3f155eda315478f4114ef010e2af3b0eb30f9ad` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `aaae27d0385af734727f74cb5fa383dfe9023edac55d79cdf182f6bae933294a` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004480c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — early flag and final call chain are visible, but extraout boolean handling and repeated indirect lookup introduce material ambiguity. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Machine-level boolean widening represented by `extraout_var`.
- Contract/stability of repeated indirect slot +0x144 calls.
- Concrete meanings of the two direct-callee results.
