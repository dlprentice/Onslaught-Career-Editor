# CUnitAI__InitDefaults_AutoConfigTestPath

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__InitDefaults_AutoConfigTestPath` at `0x004239f0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004239f0`

## Identity
- Body `[0x004239f0,0x00423bba]`, 459 bytes. Raw pristine-body SHA-256 `f7880354d98dbec574e79e988905adc3b588d76dcdc63e04ac4d5520f2ca1188`; closure range SHA-256 `05e102ddbac24136ea510d721b965610c13136ceb5b16dde56fbf12e8d561b19`; packet range-plus-bytes SHA-256 `762cc688f83fd68f3eb20c06f4ba08d37f98d8c8906960a999aa120fce1a61db`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__InitDefaults_AutoConfigTestPath` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `void * __fastcall CUnitAI__InitDefaults_AutoConfigTestPath(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void * __fastcall CUnitAI__InitDefaults_AutoConfigTestPath(void * this)
```
- `this` — writable base pointer receiving numerous byte and dword constants, two copied byte strings, and the returned pointer value.

## Return value meaning
Returns the input `this` pointer after the stores and copies.

## Globals read/written
- `DAT_00624484` — scanned as a NUL-terminated byte sequence and copied to +0x2d4.
- `DAT_0066e94e` — read to select +0x318 as `0xffffffff` or `120000`.
- `s_c__beaautoconfigtest__00624488` — packet stringRef value `c:\\beaautoconfigtest\\`, copied to +0x44.

## Callees relied on / callers
- Callees (packet structured array): none recorded; any visible indirect dispatch has no structured direct-callee VA.
- Callers (packet structured array): `FUN_004239c0` `0x004239c0` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Writes the constants shown by the decompile across receiver offsets through +0x31c. It copies the packet-recorded `c:\\beaautoconfigtest\\` string to +0x44, copies the NUL-terminated bytes at `DAT_00624484` to +0x2d4, sets +0x318 to `0xffffffff` when `DAT_0066e94e` is zero and to `120000` otherwise, then returns `this`. Higher-level default/configuration meanings are counted intent only.

## Error / edge behavior
The receiver and destination capacities are unguarded, and both source sequences are scanned until NUL. Exact field widths beyond the displayed byte/dword stores are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x004239f0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `05e102ddbac24136ea510d721b965610c13136ceb5b16dde56fbf12e8d561b19` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `762cc688f83fd68f3eb20c06f4ba08d37f98d8c8906960a999aa120fce1a61db` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `f7880354d98dbec574e79e988905adc3b588d76dcdc63e04ac4d5520f2ca1188` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004239f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: `0x00624488` value "c:\\\\beaautoconfigtest\\\\", UTF-8 SHA-256 `de51c2c40191e0d8fe8bea2964fe7e8fe166691886f9741cf7f9d8c1b810dad7`. Values are counted literals/source intent only.
- Crosswalk: none in the cohort brief.

## Confidence
2 — constant stores, two copies, selector, and pointer return are explicit; field meanings and destination capacities are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Content and role of `DAT_00624484`.
- Concrete object layout and capacity of buffers at +0x44 and +0x2d4.
