# CUnitAI__PlayHitAnimationAndSetFlag

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__PlayHitAnimationAndSetFlag` at `0x00428cb0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00428cb0`

## Identity
- Body `[0x00428cb0,0x00428ce3]`, 52 bytes. Raw pristine-body SHA-256 `8eb7f4b1d2505bed6eb8d51622033333dedca0445e5a73c4eb96ca15c29c213d`; closure range SHA-256 `fe076dfaca8c017250edeb95f2f30f6e608de5b63257d03d386fbbb1c3ec1d87`; packet range-plus-bytes SHA-256 `b261a563bc41e53b75e01d4f4b924790310d3072972767ac2df1c47cb4ec4b83`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__PlayHitAnimationAndSetFlag` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)
```
- `this` — receiver/base pointer used for indirect calls through its first word and nested +0x30 pointer, and written at +0x2bc (decimal 700).

## Return value meaning
not_applicable (void).

## Globals read/written
- `PTR_DAT_006248e8` — its address is forwarded as a token to an indirect call and to the packet-listed direct callee; packet stringRefs do not identify its text.

## Callees relied on / callers
- Callees (packet structured array): `CMesh__FindAnimationIndexByName` `0x004aa630` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CGillM__TriggerRandomArmHitAnimationIfReady` `0x00479db0` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Uses an indirect +0x24 call through the nested +0x30 pointer with `PTR_DAT_006248e8`, passes the returned object and token to the one packet-listed direct callee, forwards the resulting index to indirect slot +0xf0 on `this`, and stores 1 at +0x2bc. Hit/animation wording is counted name/comment intent only.

## Error / edge behavior
The receiver and nested +0x30 pointer are unguarded. Contracts of indirect slots +0x24/+0xf0 and the token contents are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00428cb0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `fe076dfaca8c017250edeb95f2f30f6e608de5b63257d03d386fbbb1c3ec1d87` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `b261a563bc41e53b75e01d4f4b924790310d3072972767ac2df1c47cb4ec4b83` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `8eb7f4b1d2505bed6eb8d51622033333dedca0445e5a73c4eb96ca15c29c213d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00428cb0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — token flow, index lookup, indirect dispatch, and final flag store are visible, but token and indirect contracts are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Text/role referenced by `PTR_DAT_006248e8`.
- Contracts of indirect slots +0x24 and +0xf0 and meaning of +0x2bc.
