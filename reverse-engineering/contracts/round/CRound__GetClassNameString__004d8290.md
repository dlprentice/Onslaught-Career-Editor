# CRound__GetClassNameString

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__GetClassNameString` at `0x004d8290`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8290`

## Identity
- Body `[0x004d8290,0x004d8295]`, 6 bytes. Raw pristine-body SHA-256 `b255442129093c839144a11c6315d0c555714f692cb71fd92c9342397bdf8b6d`; closure range SHA-256 `fb64f446ba9c8e41295e3c0ebe3858b00f01cfcd3a5c2f6c9ca671bc107aa5d7`; packet range-plus-bytes SHA-256 `a9960ffbd0aa914cb65aac32e66ba8b6a628ca1e86514f5d8f8c839295a61da1`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__GetClassNameString`. Packet/decompile metadata name: `CRound__VFunc_7_004d8290`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__stdcall` for `char * __stdcall CRound__VFunc_7_004d8290(void)`. This packet signature has no receiver parameter; higher-level virtual-slot usage is not inferred from the convention alone.

## Prototype and parameter semantics
```c
char * __stdcall CRound__VFunc_7_004d8290(void)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- not_applicable — the packet signature has no explicit parameter.

## Return value meaning
Returns the address of the packet-recorded NUL-terminated string literal `CRound`.

## Globals read/written
- `s_CRound_00631d08` — its address is returned; packet stringRefs records value `CRound` at `0x00631d08`.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Returns one constant string address and performs no displayed branch, call, or write. The tracked descriptive name and packet vtable-slot name are both counted intent only.

## Error / edge behavior
No failure branch is displayed. Lifetime, encoding contract beyond the packet literal bytes, and consumer expectations are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8290`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `fb64f446ba9c8e41295e3c0ebe3858b00f01cfcd3a5c2f6c9ca671bc107aa5d7` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `a9960ffbd0aa914cb65aac32e66ba8b6a628ca1e86514f5d8f8c839295a61da1` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `b255442129093c839144a11c6315d0c555714f692cb71fd92c9342397bdf8b6d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8290.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: `0x00631d08` value "CRound", UTF-8 SHA-256 `ae5fd6ef61ca0c441fba9e8c63bc3fa23fa794eadc80dec4d0ba0c4fd2bc73e4`. Literal values are evidence; any interpretation remains bounded to displayed use.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the constant pointer return and literal are fully visible, while higher-level class-name intent is not semantic proof. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Consumer ownership/lifetime expectations for the returned pointer.
- Whether the literal is used as a class identifier is not established by this body alone.
