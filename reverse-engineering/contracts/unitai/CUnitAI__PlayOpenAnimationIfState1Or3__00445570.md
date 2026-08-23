# CUnitAI__PlayOpenAnimationIfState1Or3

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__PlayOpenAnimationIfState1Or3` at `0x00445570`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00445570`

## Identity
- Body `[0x00445570,0x004455b3]`, 68 bytes. Raw pristine-body SHA-256 `a9edbceb18f3709ae22bef55a84cfa282a6f4f9236f42104a6297797f3c62a00`; closure range SHA-256 `3c61ae98343f3e6bd724bb8381777df8334eca254dbee1417fed956f8a4b0f55`; packet range-plus-bytes SHA-256 `8afe1ffa29f58e19ec906d4556cf4931f4bc19a1fe45471d83bb5345733b59d7`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__PlayOpenAnimationIfState1Or3` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)
```
- `unitAI` — analyzed receiver pointer; the decompile reads/writes +0x280, follows nested +0x30, and dispatches through the receiver's first word. The parameter label is counted intent only.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_00623bb4` — its address is forwarded as a token to an indirect call and the packet-listed direct callee; packet stringRefs do not identify its text.

## Callees relied on / callers
- Callees (packet structured array): `CMesh__FindAnimationIndexByName` `0x004aa630` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDoorWingEngagement_CloseRange` `0x00445ad0` ×1 site(s); `CUnitAI__EnterDoorWingOpenTrackingState` `0x00446400` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
When +0x280 equals 1 or 3, stores 2 there, obtains an object through nested indirect slot +0x24 while forwarding `DAT_00623bb4`, passes that object/token to the packet-listed direct callee, and passes the resulting index to indirect slot +0xf0. Other +0x280 values cause no action. Open-animation wording is counted name/comment intent only.

## Error / edge behavior
The receiver and nested +0x30 pointer are unguarded. Token contents and contracts of indirect slots +0x24/+0xf0 are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00445570`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3c61ae98343f3e6bd724bb8381777df8334eca254dbee1417fed956f8a4b0f55` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `8afe1ffa29f58e19ec906d4556cf4931f4bc19a1fe45471d83bb5345733b59d7` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `a9edbceb18f3709ae22bef55a84cfa282a6f4f9236f42104a6297797f3c62a00` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00445570.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — the two-state gate, state write, token lookup, and dispatch are visible, but receiver ownership, token text, and indirect contracts are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Exact owner type passed by the structured callers.
- Text/role at `DAT_00623bb4` and contracts of both indirect slots.
