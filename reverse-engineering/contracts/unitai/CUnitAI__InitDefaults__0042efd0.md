# CUnitAI__InitDefaults

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__InitDefaults` at `0x0042efd0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0042efd0`

## Identity
- Body `[0x0042efd0,0x0042f218]`, 585 bytes. Raw pristine-body SHA-256 `88bf8da7dd8127b968e62e7400a299a13ae8d1fa4041cb7311dea8d95e9e21e7`; closure range SHA-256 `5b55affd7e999398b6a5c947b4bfd9fcfa1f7dad8d3ba5c91ec55e9c6b9d6f6d`; packet range-plus-bytes SHA-256 `f8dac3437271281699bc8f342aaafed871f205491fed971526aa66a9643c866f`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__InitDefaults` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__InitDefaults(void * unitAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__InitDefaults(void * unitAI)
```
- `unitAI` — writable base pointer receiving constants through +0x1a8 and one allocated NUL-terminated byte string at +0x30.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_009c3df0` — its address is passed to the one packet-listed allocator call.
- Packet stringRefs `C:\\dev\\ONSLAUGHT2\\WorldPhysicsManager.h` and `m-b-rubble` — the path is forwarded to allocation and `m-b-rubble` is copied into the allocated 0xb-byte buffer.

## Callees relied on / callers
- Callees (packet structured array): `CDXMemoryManager__Alloc` `0x005490e0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__CreateAndRegisterByName` `0x0042ee90` ×1 site(s); `CComponent__CreateAndRegisterByName` `0x00430e60` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Writes the displayed zero, one, sentinel, integer, and floating-point bit constants across the base through +0x1a8. It allocates 0xb bytes through the packet-listed allocator, stores the result at +0x30, copies the packet-recorded `m-b-rubble` bytes including the terminator, fills seven dwords from +0x164 with `0x3f800000`, and leaves +0x114 as 1. Higher-level default/physics meanings are counted intent only.

## Error / edge behavior
The base pointer is unguarded. The allocator result is used as a copy destination without a null check; concrete field types and ownership are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0042efd0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `5b55affd7e999398b6a5c947b4bfd9fcfa1f7dad8d3ba5c91ec55e9c6b9d6f6d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `f8dac3437271281699bc8f342aaafed871f205491fed971526aa66a9643c866f` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `88bf8da7dd8127b968e62e7400a299a13ae8d1fa4041cb7311dea8d95e9e21e7` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0042efd0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: `0x00625850` value "C:\\\\dev\\\\ONSLAUGHT2\\\\WorldPhysicsManager.h", UTF-8 SHA-256 `4431e8ec422d313eab0856cf4b4a174aaf7c67232847ab03bd079a115b11125e`; `0x00625878` value "m-b-rubble", UTF-8 SHA-256 `4c6b95a01c3c51ccc01be2f6712fd0827c0abc56799af5f381c4267e31f0bfa0`. Values are counted literals/source intent only.
- Crosswalk: none in the cohort brief.

## Confidence
2 — constant stores, allocation size, string copy, seven-element fill, and final values are explicit; field meanings and allocation failure contract remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Ownership/failure handling for the +0x30 allocation.
- Concrete types and meanings of the initialized fields and constants.
