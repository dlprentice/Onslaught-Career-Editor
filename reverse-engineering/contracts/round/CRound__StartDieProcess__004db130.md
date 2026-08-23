# CRound__StartDieProcess

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__StartDieProcess` at `0x004db130`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004db130`

## Identity
- Body `[0x004db130,0x004db141]`, 18 bytes. Raw pristine-body SHA-256 `7e2fbd18483548889909606c71d115fa6f162daa4fc9e0232939af06655cb1f6`; closure range SHA-256 `1993eb35fbdaabcd88d0930633d40d058b87087b5b197a1721129674c7e07da6`; packet range-plus-bytes SHA-256 `8d964ff51485315ef7d4df9bc83e518c76026fbc46987144e7054100f9c1e253`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__StartDieProcess`. Packet/decompile metadata name: `CRound__VFunc_50_004db130`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `int __fastcall CRound__VFunc_50_004db130(void * param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
int __fastcall CRound__VFunc_50_004db130(void * param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base pointer inspected at +0x120 and conditionally forwarded to the sole packet-listed direct callee.

## Return value meaning
Returns 0 when `*(param_1+0x120)` is nonzero; otherwise returns the integer result of the packet-listed direct callee unchanged.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): `CComplexThing__StartDieProcess` `0x004f4430` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Tests one dword at +0x120, either returns zero immediately or calls the sole listed callee with `param_1` and forwards its result.

## Error / edge behavior
`param_1` is unguarded. Die-process wording comes from counted labels and does not prove the meaning of +0x120 or the callee result.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004db130`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `1993eb35fbdaabcd88d0930633d40d058b87087b5b197a1721129674c7e07da6` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `8d964ff51485315ef7d4df9bc83e518c76026fbc46987144e7054100f9c1e253` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7e2fbd18483548889909606c71d115fa6f162daa4fc9e0232939af06655cb1f6` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004db130.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the one-field guard, direct call, and exact result forwarding are explicit; high-level meaning remains unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning of +0x120 and its nonzero states.
- Return-value and side-effect contract of the direct callee.
