# CUnitAI__CreateAndRegisterByName

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__CreateAndRegisterByName` at `0x0042ee90`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0042ee90`

## Identity
- Body `[0x0042ee90,0x0042efc0]`, 305 bytes. Raw pristine-body SHA-256 `f973f476ac611c1ea48da273705ac6cfa93fd4e7fbaf96de6e3f4d6dc7970529`; closure range SHA-256 `675049c4cfa43d5888709c02df7050baca4103d75b100d00e8f8134bbcee6071`; packet range-plus-bytes SHA-256 `7a47d8cbe709bea1e4993a17dd2c8711cdeee6f64f43a0cc149517df716fc2e8`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__CreateAndRegisterByName` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__cdecl` for `void __cdecl CUnitAI__CreateAndRegisterByName(char * name)`. ABI details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __cdecl CUnitAI__CreateAndRegisterByName(char * name)
```
- `name` — NUL-terminated byte string scanned for length, copied into a new allocation, and compared case-insensitively with two packet-recorded strings.

## Return value meaning
not_applicable under the packet signature (void). The newly allocated pointer is instead passed to the final packet-listed set helper.

## Globals read/written
- `DAT_009c3df0` — its address is passed to both allocation calls.
- `DAT_008553fc` — read and passed with the new pointer to the final direct callee.
- Packet stringRefs `Fenrir Main Gun`, `Fenrir`, and `C:\\dev\\ONSLAUGHT2\\WorldPhysicsManager.h` — the first two are comparison operands and the path is forwarded to allocations.

## Callees relied on / callers
- Callees (packet structured array): `CUnitAI__InitDefaults` `0x0042efd0` ×1 (STATIC_DIRECT); `CSPtrSet__Init` `0x004e5840` ×4 (STATIC_DIRECT); `CSPtrSet__AddToTail` `0x004e5b20` ×1 (STATIC_DIRECT); `CDXMemoryManager__Alloc` `0x005490e0` ×2 (STATIC_DIRECT); `stricmp` `0x00568390` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitStatement__CreateUnitAndRecurse` `0x0042ede0` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Allocates 0x1ac bytes through the packet-listed allocator. On nonnull result it initializes four fields through the packet-listed set initializer, scans `name`, allocates `length+1`, copies the bytes and terminator to +0xb0, calls the packet-listed defaults helper, compares `name` with the two packet-recorded Fenrir strings through two listed `stricmp` sites, and stores 1 at +0x1a4 on either equality. It then calls the packet-listed tail-add helper with `DAT_008553fc` and the pointer, including a null pointer when the first allocation failed. Class/registration meanings are counted intent only.

## Error / edge behavior
`name` is unguarded. The second allocation result is written through without a null check, and a failed first allocation still reaches the final tail-add call with null; allocator/set invariants are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0042ee90`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `675049c4cfa43d5888709c02df7050baca4103d75b100d00e8f8134bbcee6071` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `7a47d8cbe709bea1e4993a17dd2c8711cdeee6f64f43a0cc149517df716fc2e8` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `f973f476ac611c1ea48da273705ac6cfa93fd4e7fbaf96de6e3f4d6dc7970529` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0042ee90.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: `0x00624890` value "Fenrir Main Gun", UTF-8 SHA-256 `05a30a77a970a161f3781c0bae3729f814b818b1291209584d12ea0e7f3f5ee7`; `0x00625848` value "Fenrir", UTF-8 SHA-256 `98250a10bcfa095013ddd610ff34ce99aea0f9eef1f7e9a70762726a338a927a`; `0x00625850` value "C:\\\\dev\\\\ONSLAUGHT2\\\\WorldPhysicsManager.h", UTF-8 SHA-256 `4431e8ec422d313eab0856cf4b4a174aaf7c67232847ab03bd079a115b11125e`. Values are counted literals/source intent only.
- Crosswalk: none in the cohort brief.

## Confidence
1 — allocation, four initializations, copy, comparisons, flag, and final add are visible, but failure behavior and ownership are unsafe or unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether null pointers are accepted by the final set helper.
- Capacity/ownership and failure contract of the name allocation.
- Meaning of +0x1a4 and the two special string comparisons.
