# CFrontEnd__Init

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__Init` at `0x004662a0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004662a0`

## Identity
- Body `[0x004662a0,0x00466874]`, 1493 bytes, 357 closure instructions. Raw pristine-body SHA-256 `fbf1070d7fe16c820d57a6082d9e0296097a4d72c6665ed3e90910383e6a47f4`; closure range SHA-256 `cec5cd3289aca8a239f756ff9601de46ac5e1e44426df01261ce6cb51962cbd5`; packet range-plus-bytes SHA-256 `bc363b07cf1e028ff4de017382141b2ad033c0562629984c1ce6845f6f5db33d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__Init` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__Init`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)
```
- Packet-declared parameter list: `void * this, int entry, int in_loaded_system`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00662dcc`, `DAT_00662dd0`, `DAT_00662f40`, `DAT_0066304c`, `DAT_006630cc`, `DAT_00663498`, `DAT_00675688`, `DAT_0083d448`, `DAT_0083d454`, `DAT_00889a48`, `DAT_00896988`, `DAT_0089d760`, `DAT_0089d91c`, `DAT_008a9580`, `DAT_008a9584`, `DAT_008a9aac`, `DAT_008a9ab4`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_FrontEnd_cpp_00629df0`, `s_FEP__d____00629e18`, `s_done__00629e10`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `DebugTrace` `0x0040c640` ×3 site(s) (STATIC_DIRECT).
- Callee `CCareer__Update` `0x0041bd00` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoading` `0x0042bbc0` ×2 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingRange` `0x0042cf40` ×5 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingFraction` `0x0042cf70` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__Init` `0x0044b060` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__InitPageStateDefaults` `0x0044d320` ×1 site(s) (STATIC_DIRECT).
- Callee `CFEPMultiplayerStart__SubObj39B8__QueuePageId` `0x00459810` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__SetPage` `0x00466ae0` ×4 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__LoadSharedResources` `0x004687e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMusic__PlaySelection` `0x004bb8c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__ReloadLanguageSampleBank` `0x004e2c50` ×1 site(s) (STATIC_DIRECT).
- Callee `CText__Ctor` `0x004f2150` ×1 site(s) (STATIC_DIRECT).
- Callee `CText__Init` `0x004f21f0` ×1 site(s) (STATIC_DIRECT).
- Callee `SharedVFunc__ReturnTrue_004fdc10` `0x004fdc10` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__ctor` `0x005145f0` ×1 site(s) (STATIC_DIRECT).
- Callee `PlatformInput__ResetKeyStateTables` `0x005159b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXFrontEndVideo__SetDefaultSize` `0x00541240` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__Run` `0x004684d0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `49-342` defines `CFrontEnd::Init` as `BOOL	CFrontEnd::Init(EFrontEndEntry entry,BOOL inLoadedSystem)`; exact extracted source-body SHA-256 `8b73bb0d2189c0cd8c933cba4a9d0052cfd24fc077d881815a56c6c04d229fcf`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=24, switch=0, for=4, while=0; named call tokens `ASSERT`, `ActiveNotification`, `Blank`, `CCONTROLLER`, `CacheFile`, `FlushInputBuffers`, `GetAutoSave`, `GetSong`, `GetTickCount`, `GetTrackForCredits`, `GetTrackForFrontEnd`, `InProgress`, `Initialise`, `Load`, `LoadXAPFile`, `PlaySelection`, `SetAutoSave`, `SetCurrentCard`, `SetLoading`, `SetLoadingFraction`, `SetLoadingRange`, `SetPage`, `SetSaveMode`, `SetSuccessFEP` (+7 more tokens).
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: CFrontEnd startup initializer matching source CFrontEnd::Init(EFrontEndEntry, BOOL) at the coarse control-flow level: loading ranges, shared frontend resources, page table wiring, controller allocation, initial page selection, language text set initialization, and frontend music start. Static retail-binary/source-bridge evidence only; exact CFrontEnd layout, page enum values, platform-specific source identity, runtime frontend behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `6ff953fc9a05d8b36f5deca7de8e3ac680208ce3364abc1149a48548207bfae7`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 20 callee record(s), and 3 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 8; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x004662a0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `6ff953fc9a05d8b36f5deca7de8e3ac680208ce3364abc1149a48548207bfae7`.
- Digest derivation: closure SHA-256 hashes canonical range text `004662a0:00466874;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00629df0` length 31 SHA-256 `8fabb7b4645aa9be0f949a5981382e3fa4ff713b3997b9f35178ea05b769a245` value “C:\\dev\\ONSLAUGHT2\\FrontEnd.cpp”.
- Packet string ref `0x00629e10` length 7 SHA-256 `792673424db5a300e24b11cea37df0a678a34760f5250ac8ba7ebba28c5152bc` value “done.\n”.
- Packet string ref `0x00629e18` length 10 SHA-256 `6d7daf5068ec6e1b43ea60eb9acf03a93e5b8d7744a2a4ea8c478e28c6538994` value “FEP %d...”.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::Init` line 49 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
