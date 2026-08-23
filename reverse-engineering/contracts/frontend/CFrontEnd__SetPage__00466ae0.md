# CFrontEnd__SetPage

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__SetPage` at `0x00466ae0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466ae0`

## Identity
- Body `[0x00466ae0,0x00466b90]`, 177 bytes, 45 closure instructions. Raw pristine-body SHA-256 `06a8d37bc755e5341ca9156650d7caf2612e2a92978ce70baaa61bc765b6c018`; closure range SHA-256 `864de6d8a3bfed84486638a71f65baa875227c40dc9f46d2dffb714f2d5878af`; packet range-plus-bytes SHA-256 `4be8cfd351bfaef363659680cd95e49e0ff4ccc55b375ba7ed9ff37e8973b1a8`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__SetPage` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__SetPage`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__SetPage(void * this, int page, int time)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__SetPage(void * this, int page, int time)
```
- Packet-declared parameter list: `void * this, int page, int time`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CFrontEnd__HandleModalPanelButton` `0x0044dd60` ×2 site(s) (instruction-flow).
- Caller `CFEPBEConfig__ButtonPressed` `0x00450090` ×2 site(s) (instruction-flow).
- Caller `CFEPBriefing__ButtonPressed` `0x00451c20` ×2 site(s) (instruction-flow).
- Caller `CFEPDebriefing__ButtonPressed` `0x004568a0` ×1 site(s) (instruction-flow).
- Caller `CFEPDemoMain__DoAction` `0x00457ee0` ×1 site(s) (instruction-flow).
- Caller `CFEPDevelopment__RefreshWorldListCore` `0x00458710` ×1 site(s) (instruction-flow).
- Caller `CFEPDevSelect__VFunc_3_00458a10` `0x00458a10` ×1 site(s) (instruction-flow).
- Caller `CFEPDevSelect__VFunc_2_00458e00` `0x00458e00` ×2 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__SubObj8848__Process` `0x00459b00` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__SubObj8848__ButtonPressed` `0x00459c10` ×2 site(s) (instruction-flow).
- Caller `CFEPLevelSelect__ButtonPressed` `0x004606b0` ×2 site(s) (instruction-flow).
- Caller `CFEPLoadGame__ButtonPressed` `0x00461c60` ×1 site(s) (instruction-flow).
- Caller `CFEPLoadGame__DoLoad` `0x00461e20` ×2 site(s) (instruction-flow).
- Caller `CFEPMain__DoAction` `0x004623e0` ×5 site(s) (instruction-flow).
- Caller `CFEPMain__Process` `0x00462640` ×2 site(s) (instruction-flow).
- Caller `CFEPSaveGame__ButtonPressed` `0x00464630` ×1 site(s) (instruction-flow).
- Caller `CFEPSaveGame__Process` `0x00464730` ×2 site(s) (instruction-flow).
- Caller `CFEPSaveGame__CreateSave` `0x00464c50` ×3 site(s) (instruction-flow).
- Caller `CFrontEnd__Init` `0x004662a0` ×4 site(s) (instruction-flow).
- Caller `CFEPCredits__ButtonPressed` `0x0051a7f0` ×1 site(s) (instruction-flow).
- Caller `CFEPCredits__Process` `0x0051a820` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__ButtonPressed` `0x0051aaf0` ×2 site(s) (instruction-flow).
- Caller `CFEPDirectory__RefreshSaveFileList` `0x0051ad30` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__SubObj4034_T3_0051b660` `0x0051b660` ×1 site(s) (instruction-flow).
- Caller `CFEPLanguageTest__ButtonPressed` `0x0051c090` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayer__VFunc_3_0051ccb0` `0x0051ccb0` ×2 site(s) (instruction-flow).
- Caller `CFEPMultiplayer__VFunc_2_0051d020` `0x0051d020` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__ButtonPressed` `0x0051de60` ×1 site(s) (instruction-flow).
- Caller `CFEPOptions__SaveDefaultOptions` `0x0051f500` ×2 site(s) (instruction-flow).
- Caller `CFEPOptions__ProcessInput` `0x0051f600` ×1 site(s) (instruction-flow).
- Caller `CFEPScreenPos__ButtonPressed` `0x0051fa00` ×2 site(s) (instruction-flow).
- Caller `CFEPVirtualKeyboard__ButtonPressed` `0x00520370` ×1 site(s) (instruction-flow).
- Caller `CFEPVirtualKeyboard__HandleKeyToken` `0x00520cc0` ×1 site(s) (instruction-flow).
- Caller `CFEPWingmen__ButtonPressed` `0x00521d20` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `563-592` defines `CFrontEnd::SetPage` as `void	CFrontEnd::SetPage(EFrontEndPage page, SINT time)`; exact extracted source-body SHA-256 `8d7ecee187dba451f71a5e885cce2b883f4a39b4334e1669724cbb09e55f10de`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=2, switch=0, for=0, while=0; named call tokens `ASSERT`, `ActiveNotification`, `DeActiveNotification`, `TransitionNotification`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-parity: CFrontEnd::SetPage(EFrontEndPage page, SINT time). If time==0: DeActiveNotification on current page, then TransitionNotification+ActiveNotification on new page, set active. Else: sets up transition fields and calls TransitionNotification on destination page.”
- The displayed decompile is non-empty and SHA-256 `841869ba4f073af6ea0eb2ba91bfecb01c78a76c2a4a495904a9736a97b596e2`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 34 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 13; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00466ae0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `841869ba4f073af6ea0eb2ba91bfecb01c78a76c2a4a495904a9736a97b596e2`.
- Digest derivation: closure SHA-256 hashes canonical range text `00466ae0:00466b90;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::SetPage` line 563 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__SetPage.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
