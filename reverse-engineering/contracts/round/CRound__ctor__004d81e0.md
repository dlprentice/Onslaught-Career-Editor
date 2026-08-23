# CRound__ctor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__ctor` at `0x004d81e0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d81e0`

## Identity
- Body `[0x004d81e0,0x004d8283]`, 164 bytes. Raw pristine-body SHA-256 `6045284b21771d99a6229443e6f3ca9caad06df98834ec2cbb82b8b6fb008a1d`; closure range SHA-256 `c08c649e678c971c626f1b262485b62f55d955d718d1cdfdbabe6f62d456283b`; packet range-plus-bytes SHA-256 `b268421a6b00c28cae69791356febac883739e80f141eb101b8443bc78fd7131`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__ctor`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CRound__ctor(void * this, void * init)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void * __thiscall CRound__ctor(void * this, void * init)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — writable base pointer passed to the first direct callee, initialized at the displayed offsets, and returned.
- `init` — pointer stored unchanged at receiver offset +0xf0; further meaning is not_determinable here.

## Return value meaning
Returns the input `this` pointer after the displayed calls and stores.

## Globals read/written
- `ExceptionList` — saved, replaced during the body, and restored before return.
- `DAT_00672fd0` — read and copied to receiver offset +0xf4.

## Callees relied on / callers
- Callees (packet structured array): `ParticleEffectLink_T3_004cb040` `0x004cb040` ×1 (STATIC_DIRECT); `CComplexThing__ctor_base` `0x004f3e10` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CWorldPhysicsManager__CreateProjectile` `0x0050f7a0` ×2 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Calls the two packet-listed direct callees with `this` and `this+0xe0`, temporarily installs two pointer-table pairs, clears +0xe4/+0xe8/+0xec/+0x120/+0x124/+0x12c, stores `init` at +0xf0, copies `DAT_00672fd0` to +0xf4, writes 1 at +0x130, restores `ExceptionList`, and returns `this`.

## Error / edge behavior
`this` is unguarded. The direct-callee failure contracts and concrete layouts represented by the pointer-table constants are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d81e0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `c08c649e678c971c626f1b262485b62f55d955d718d1cdfdbabe6f62d456283b` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `b268421a6b00c28cae69791356febac883739e80f141eb101b8443bc78fd7131` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6045284b21771d99a6229443e6f3ca9caad06df98834ec2cbb82b8b6fb008a1d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d81e0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — call order, stores, global copy, and pointer return are explicit; allocation/lifetime and object-layout meanings remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete types and ownership of `this`, `init`, and the +0xe0/+0xe8/+0xec regions.
- Contracts of both direct callees and the installed pointer tables.
