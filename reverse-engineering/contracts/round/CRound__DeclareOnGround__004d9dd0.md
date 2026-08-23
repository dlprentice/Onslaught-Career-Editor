# CRound__DeclareOnGround

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__DeclareOnGround` at `0x004d9dd0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d9dd0`

## Identity
- Body `[0x004d9dd0,0x004d9ee9]`, 282 bytes. Raw pristine-body SHA-256 `bdd3b27c15a77fe7a964a5c37fa3b055b3eb7c449c7f0944d2eeba7f504421f9`; closure range SHA-256 `cc5b25558a48c7e9660ebb7db348ffd4f28975f026db25242b200c6699b989fb`; packet range-plus-bytes SHA-256 `d70f1dc6e589ff88eb2d79d830cfd14254cf345e9c4d583fc9d4302f8516d291`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__DeclareOnGround`. Packet/decompile metadata name: `CRound__VFunc_68_004d9dd0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `undefined __fastcall CRound__VFunc_68_004d9dd0(int * param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
undefined __fastcall CRound__VFunc_68_004d9dd0(int * param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded integer-addressed receiver/base pointer used for nested field tests, copied four-dword groups, and one indirect slot +0xc8 call.

## Return value meaning
not_applicable — the decompile returns no value despite the packet's untyped `undefined` declaration.

## Globals read/written
- `ExceptionList` — saved/replaced around calls and restored.
- `DAT_006fadc8` — its address is passed to the packet-listed trace callee.

## Callees relied on / callers
- Callees (packet structured array): `CActor__SetFieldCcToNow_00402000` `0x00402000` ×1 (STATIC_DIRECT); `CHeightField__TraceLineAgainstHeightfield` `0x00490a40` ×1 (STATIC_DIRECT); `CRound__UpdateEffectTransformByMode_004d9f30` `0x004d9f30` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
If the float reached through word index 0x3c and offset +0x30 is nonzero, calls the first packet-listed direct callee and returns. Otherwise, only when the dword at the same block's +0x60 is zero, it builds two four-dword groups from receiver word ranges 0x23..0x26 and 7..10, calls the listed trace callee, conditionally copies four trace outputs back to receiver words 7..10, calls the listed mode helper with `(param_1, 1, null, null)`, and invokes indirect slot +0xc8.

## Error / edge behavior
The receiver, nested block, and indirect slot are unguarded. A zero trace result leaves the original receiver words unchanged; when pointed-to +0x60 is nonzero, no displayed call occurs. Ground/declaration wording is not proof.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d9dd0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `cc5b25558a48c7e9660ebb7db348ffd4f28975f026db25242b200c6699b989fb` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d70f1dc6e589ff88eb2d79d830cfd14254cf345e9c4d583fc9d4302f8516d291` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `bdd3b27c15a77fe7a964a5c37fa3b055b3eb7c449c7f0944d2eeba7f504421f9` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d9dd0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the early branch, trace gate, conditional copy, mode call, and indirect dispatch are visible; field and gameplay meanings remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete structure represented by receiver word indices and +0xf0-equivalent word 0x3c.
- Contract of indirect slot +0xc8 and meaning of mode value 1.
