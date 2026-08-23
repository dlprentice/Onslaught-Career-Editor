# CUnitAI__dtor_body

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__dtor_body` at `0x00415080`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00415080`

## Identity
- Body `[0x00415080,0x0041511e]`, 159 bytes. Raw pristine-body SHA-256 `4eeff7ba5b60311f0543c6c3891609aeed34d97db49511e91c9289830d0d054d`; closure range SHA-256 `385ff9aec84a006e6acfb8e8e8782bc931acd2b5f8d917585120c066426dd441`; packet range-plus-bytes SHA-256 `17ec5828d04809409b2566264b208bd849d3f9c98db2aff872a8b1ac93994e0b`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__dtor_body` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__dtor_body(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__dtor_body(void * this)
```
- `this` — receiver/base pointer whose first word is overwritten and whose +0x28/+0x24/+0xc fields are inspected.

## Return value meaning
not_applicable (void).

## Globals read/written
- `ExceptionList` — saved, replaced for the body, and restored.
- `PTR_CUnitAI__DispatchTimedAIEvent_004ff330_005d8d1c` — its address is written to the receiver's first word; behavioral meaning of the label is not proof.

## Callees relied on / callers
- Callees (packet structured array): `CMonitor__Shutdown` `0x004bac40` ×1 (STATIC_DIRECT); `CSPtrSet__Remove` `0x004e5bd0` ×3 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__scalar_deleting_dtor` `0x00415060` ×1 site(s); `Unwind@005d2b2c` `0x005d2b2c` ×1 site(s); `Unwind@005d3460` `0x005d3460` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Writes the displayed pointer constant to `*this`. For each of +0x28, +0x24, and +0xc, it calls the packet-listed remove helper only when the field is nonzero and the nested +4 pointer is nonzero, then calls the packet-listed shutdown helper once and restores `ExceptionList`.

## Error / edge behavior
The receiver is unguarded. A nonzero member causes an unguarded read of that member's +4 field; null member or null nested +4 skips the corresponding remove call.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00415080`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `385ff9aec84a006e6acfb8e8e8782bc931acd2b5f8d917585120c066426dd441` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `17ec5828d04809409b2566264b208bd849d3f9c98db2aff872a8b1ac93994e0b` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `4eeff7ba5b60311f0543c6c3891609aeed34d97db49511e91c9289830d0d054d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00415080.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the pointer write, three guarded removals, and final call are explicit; ownership and exception-frame semantics remain partial. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Ownership/invariants of the three linked fields.
- Exact role of the first-word pointer constant and shutdown call.
