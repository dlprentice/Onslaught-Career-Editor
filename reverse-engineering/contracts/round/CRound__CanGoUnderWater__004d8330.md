# CRound__CanGoUnderWater

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__CanGoUnderWater` at `0x004d8330`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8330`

## Identity
- Body `[0x004d8330,0x004d8339]`, 10 bytes. Raw pristine-body SHA-256 `c53cb3534a10d96d95d69e776931bb1e999f75ce32548c4a7e17faa8d897e6e5`; closure range SHA-256 `a7f783b80d057ce6f5e5ed8abeebf7b2cee44af1f051566806417eed12f10a72`; packet range-plus-bytes SHA-256 `12adbbcadefecbf2aa864b9ecb38c35dfebece5bc72eb878ba7b9077336fff9c`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__CanGoUnderWater`. Packet/decompile metadata name: `CRound__VFunc_49_004d8330`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `undefined4 __fastcall CRound__VFunc_49_004d8330(int param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
undefined4 __fastcall CRound__VFunc_49_004d8330(int param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base address used to follow +0xf0 and read a dword at the pointed-to block's +0x5c.

## Return value meaning
Returns the unchanged dword at `*(param_1+0xf0)+0x5c`.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Performs one nested pointer load and returns one dword; no branch, call, or write is displayed.

## Error / edge behavior
Both pointer dereferences are unguarded. Boolean interpretation implied by the tracked name is counted intent only and is not proven by the untyped return.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8330`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `a7f783b80d057ce6f5e5ed8abeebf7b2cee44af1f051566806417eed12f10a72` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `12adbbcadefecbf2aa864b9ecb38c35dfebece5bc72eb878ba7b9077336fff9c` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `c53cb3534a10d96d95d69e776931bb1e999f75ce32548c4a7e17faa8d897e6e5` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8330.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the dword load is fully visible; return type and descriptive meaning remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete type and value domain of the +0x5c field.
- Whether consumers interpret the dword as boolean.
