# CRound__ShutdownAndDetachReaders

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__ShutdownAndDetachReaders` at `0x004d8370`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8370`

## Identity
- Body `[0x004d8370,0x004d8406]`, 151 bytes. Raw pristine-body SHA-256 `2bace4768233385e51b878144ec159348f6df7ce332e069291fed31c33a514f5`; closure range SHA-256 `63aa4d569bd61c9d1c0095023bd0c31655f851872a20f2a530ee02836d2acbcd`; packet range-plus-bytes SHA-256 `2b8a15c2deb62a326f0cab922c89e897a22934c7fcedeaff505b055498b9d3f5`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__ShutdownAndDetachReaders`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRound__ShutdownAndDetachReaders(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CRound__ShutdownAndDetachReaders(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer whose +0xec/+0xe8 nested cells and +0xe0 region are passed to direct callees.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `ExceptionList` — saved, replaced around the body, and restored before return.

## Callees relied on / callers
- Callees (packet structured array): `CActor__dtor_base` `0x004013d0` ×1 (STATIC_DIRECT); `CParticleManager__RemoveOwnerLinkFromGlobalList` `0x004cb050` ×1 (STATIC_DIRECT); `CSPtrSet__Remove` `0x004e5bd0` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CRound__scalar_deleting_dtor` `0x004d8350` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
For each of +0xec and +0xe8, calls the packet-listed remove callee only when the member and its nested +4 pointer are nonzero. It then calls the packet-listed +0xe0-region callee, calls the packet-listed base-pointer callee with `this`, restores `ExceptionList`, and returns.

## Error / edge behavior
`this` is unguarded. A nonzero +0xec/+0xe8 member is dereferenced at +4 before the nested null test; concrete ownership/removal semantics are unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8370`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `63aa4d569bd61c9d1c0095023bd0c31655f851872a20f2a530ee02836d2acbcd` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `2b8a15c2deb62a326f0cab922c89e897a22934c7fcedeaff505b055498b9d3f5` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `2bace4768233385e51b878144ec159348f6df7ce332e069291fed31c33a514f5` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8370.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — both nested guards and the final two-call order are explicit; ownership and exception-frame meaning remain partial. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Ownership and invariants of +0xe0/+0xe8/+0xec.
- Failure/side-effect contracts of the four structured direct-call sites.
