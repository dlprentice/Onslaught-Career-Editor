# CUnitAI__PlayCloseAnimationIfState0Or2

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__PlayCloseAnimationIfState0Or2` at `0x004455c0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004455c0`

## Identity
- Body `[0x004455c0,0x00445602]`, 67 bytes. Raw pristine-body SHA-256 `115fe35c6fa0a839b7d7a0f94b4d173aedfc9fa7a0e85b51b15455f440ab1808`; closure range SHA-256 `1f4314583e2b1f11b0735c353d71e13b8c6c95c4a2cfdb1d6f7dd1cef203af07`; packet range-plus-bytes SHA-256 `1af760e598ffc503e5f2acd71de98017260f3062c55a3b44bdeec5582f8e0fc9`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__PlayCloseAnimationIfState0Or2` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)
```
- `unitAI` — analyzed receiver pointer; the decompile reads/writes +0x280, follows nested +0x30, and dispatches through the receiver's first word. The parameter label is counted intent only.

## Return value meaning
not_applicable (void).

## Globals read/written
- `s_close_006289e4` — packet stringRef value `close`, forwarded to an indirect call and the packet-listed direct callee.

## Callees relied on / callers
- Callees (packet structured array): `CMesh__FindAnimationIndexByName` `0x004aa630` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDoorWingEngagement_CloseRange` `0x00445ad0` ×1 site(s); `CUnitAI__UpdateDoorWingEngagement_LongRange` `0x00446150` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
When +0x280 equals 0 or 2, stores 3 there, obtains an object through nested indirect slot +0x24 while forwarding the packet-recorded `close` string, passes that object/string to the packet-listed direct callee, and passes the resulting index to indirect slot +0xf0. Other +0x280 values cause no action. Close-animation wording beyond the literal is counted name/comment intent only.

## Error / edge behavior
The receiver and nested +0x30 pointer are unguarded. Contracts of indirect slots +0x24/+0xf0 are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x004455c0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `1f4314583e2b1f11b0735c353d71e13b8c6c95c4a2cfdb1d6f7dd1cef203af07` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `1af760e598ffc503e5f2acd71de98017260f3062c55a3b44bdeec5582f8e0fc9` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `115fe35c6fa0a839b7d7a0f94b4d173aedfc9fa7a0e85b51b15455f440ab1808` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004455c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: `0x006289e4` value "close", UTF-8 SHA-256 `310ff200149b44a32f124023d7caba19a1a890763a980606813d3a3d4a085d36`. Values are counted literals/source intent only.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the two-state gate, state write, literal flow, lookup, and dispatch are explicit; owner and indirect contracts remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Exact owner type passed by the structured callers.
- Contracts of indirect slots +0x24 and +0xf0 and meaning of +0x280 states.
