# CUnitAI__GetTargetHeadingWithOffset

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__GetTargetHeadingWithOffset` at `0x00428bc0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00428bc0`

## Identity
- Body `[0x00428bc0,0x00428bdd]`, 30 bytes. Raw pristine-body SHA-256 `fd2ab05edb597e19b9d28831b501db4bd61610cbd2ecb9fd4aceba0db7f8c1ac`; closure range SHA-256 `5ff329453a4ff3110d507d743a551e777d3f6421b9f45138d87b70166e3f8ea8`; packet range-plus-bytes SHA-256 `371eaa0a550347cad7bb8c6758f60cb65c9c2cb525b58cebf6a6a44e4955c935`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__GetTargetHeadingWithOffset` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)
```
- `this` — receiver/base pointer read at +0x26c and +0x274; a nonnull +0x26c pointer is read at +0x114.

## Return value meaning
Returns the sum of linked +0x114 and receiver +0x274 as `double` when +0x26c is nonzero; otherwise returns `0.0`. Heading/offset wording is counted name/comment intent only.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): none recorded; any visible indirect dispatch has no structured direct-callee VA.
- Callers (packet structured array): `CComponentGuide__UpdateHeadingTowardTargetClamped` `0x00429270` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Tests receiver +0x26c. If nonzero, reads one float from that object's +0x114, adds receiver float +0x274, and returns the result widened to `double`; otherwise returns `0.0`.

## Error / edge behavior
The receiver is unguarded; the linked +0x114 read is guarded only by +0x26c being nonzero. NaN/overflow behavior follows the machine floating-point operations and is otherwise not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00428bc0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5ff329453a4ff3110d507d743a551e777d3f6421b9f45138d87b70166e3f8ea8` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `371eaa0a550347cad7bb8c6758f60cb65c9c2cb525b58cebf6a6a44e4955c935` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `fd2ab05edb597e19b9d28831b501db4bd61610cbd2ecb9fd4aceba0db7f8c1ac` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00428bc0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the null gate, two-field addition, widening, and zero fallback are explicit; units and field roles remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Units and roles of linked +0x114 and receiver +0x274.
- Whether the widened return has additional ABI constraints.
