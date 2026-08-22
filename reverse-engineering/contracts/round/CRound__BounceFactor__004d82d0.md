# CRound__BounceFactor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__BounceFactor` at `0x004d82d0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d82d0`

## Identity
- Body `[0x004d82d0,0x004d82d9]`, 10 bytes. Raw pristine-body SHA-256 `768a01e896e2198144e55e39b47aa9bcd771e8fd6dc1f1eb9dd8c2ec61e47732`; closure range SHA-256 `3cb54f42624cf3f6fd4b27d4c3eef998ee51610bbe0c6b015c43176fcfd02413`; packet range-plus-bytes SHA-256 `3b39caa99978a1f2f4b58671fb5946ce8b9d398ff4cd57cf6dac4f6e421b03df`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__BounceFactor`. Packet/decompile metadata name: `CRound__VFunc_47_004d82d0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `float10 __fastcall CRound__VFunc_47_004d82d0(int param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
float10 __fastcall CRound__VFunc_47_004d82d0(int param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base address used to follow +0xf0 and read a float at the pointed-to block's +0x30.

## Return value meaning
Returns the float at `*(param_1+0xf0)+0x30` in the packet-declared `float10` result form.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Performs one nested pointer load and returns one float; there are no displayed branches, calls, or writes.

## Error / edge behavior
Both pointer dereferences are unguarded. The scalar's meaning and units are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d82d0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3cb54f42624cf3f6fd4b27d4c3eef998ee51610bbe0c6b015c43176fcfd02413` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `3b39caa99978a1f2f4b58671fb5946ce8b9d398ff4cd57cf6dac4f6e421b03df` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `768a01e896e2198144e55e39b47aa9bcd771e8fd6dc1f1eb9dd8c2ec61e47732` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d82d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the nested scalar load is fully visible, but the tracked descriptive meaning and units are unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete type of `param_1` and its +0xf0 target.
- Meaning and units of the +0x30 float.
