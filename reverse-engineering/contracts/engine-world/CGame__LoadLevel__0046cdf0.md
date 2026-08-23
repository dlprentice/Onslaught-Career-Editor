# CGame__LoadLevel

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__LoadLevel` at `0x0046cdf0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046cdf0`

## Identity
- Body `[0x0046cdf0,0x0046d03a]`, 587 bytes, 151 closure instructions. Raw pristine-body SHA-256 `a73e7a3a800a66bafcb77882efb2350cb0a7f0e6db94b69f3d316db40fd86fdc`; closure range SHA-256 `ed3097e008c5caafbe4d73484c63a49724cab284683fca7dc0097a54e7e21564`; packet range-plus-bytes SHA-256 `8aad6feb08a74bc8706086c8dc637ce3c9534e7111c9ec4099cb9f28e5524409`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__LoadLevel` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__LoadLevel`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CGame__LoadLevel(void * this, int aLevel)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CGame__LoadLevel(void * this, int aLevel)
```
- Packet-declared parameter list: `void * this, int aLevel`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00663498`, `DAT_0066e854`, `DAT_0066eb90`, `DAT_0066f580`, `DAT_0083da30`, `DAT_00855090`, `DAT_0089c9a0`, `DAT_0089d758`, `DAT_008a1810`, `DAT_009c3df0`, `DAT_009cc148`, `s_C__dev_ONSLAUGHT2_game_cpp_0062bba4`, `s_G__LL_succeeded_0062bf40`, `s_Game__LoadLevel__d_0062bfd0`, `s_Size_of_CST_Persistent_thing_____0062bf50`, `s_Size_of_CST_thing____d_0062bf74`, `s_Size_of_complex_thing____d_0062bf8c`, `s_Size_of_thing____d_0062bfa8`, `s_Size_of_tree____d_0062bfbc`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__RenderLoadingScreen` `0x0042c810` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×7 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__GetPlayer0ControllerPort` `0x00466980` ×3 site(s) (STATIC_DIRECT).
- Callee `CPlayer__ctor` `0x004d2780` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__LoadWorldFile` `0x0050b520` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__IsMultiplayerMode` `0x0050d7d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__ctor` `0x005145f0` ×1 site(s) (STATIC_DIRECT).
- Callee `PlatformInput__ResetKeyStateTables` `0x005159b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFEPOptions__GetState` `0x0051f370` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__SetTrackSlotByFlag` `0x0053f010` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXTrees__BuildTreeGeometry` `0x0055a420` ×1 site(s) (STATIC_DIRECT).
- Caller `CGame__RestartLoopRunLevel` `0x0046dc30` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `685-761` defines `CGame::LoadLevel` as `BOOL CGame::LoadLevel( SINT aLevel )`; exact extracted source-body SHA-256 `a23a9f5947002a26943e2c41cb7b07076c8e1616c6cd8bd425cab23df132798a`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=5, switch=0, for=2, while=0; named call tokens `ASSERT`, `AddMessage`, `Build`, `CCONTROLLER`, `CPlayer`, `CThing::ResetThingCounter`, `FlushInputBuffers`, `GetControllerConfigurationNum`, `GetInvertYAxis`, `GetPlayer0ControllerPort`, `GetPlayer1ControllerPort`, `Init`, `IsMultiplayer`, `Load`, `RenderLoadingScreen`, `SetBlurAlpha`, `SetPlayer`, `SpawnThing`, `new`, `rand`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::LoadLevel(SINT). Sets current level state, logs size/debug info, loads WORLD data, creates player and controller objects (SP=1 / MP=2), builds tree geometry, resets key state / cutscene track, and returns TRUE/FALSE for level-load success. Does not construct camera objects in this body.”
- The displayed decompile is non-empty and SHA-256 `12b713c37bbd49e93b1b8ba2b15508d4ba961a2a86059cd025452d1de894f805`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 12 callee record(s), and 8 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046cdf0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `12b713c37bbd49e93b1b8ba2b15508d4ba961a2a86059cd025452d1de894f805`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046cdf0:0046d03a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062bba4` length 27 SHA-256 `86a1355ab896650258cd01feac2e5a2e6bc34037493f442376b9fb36693d32e9` value “C:\\dev\\ONSLAUGHT2\\game.cpp”.
- Packet string ref `0x0062bf40` length 16 SHA-256 `615ac7d2cae41e0e4e519c95c4c0ad678391f88600f8a2ef328504594122b1b8` value “G::LL succeeded”.
- Packet string ref `0x0062bf50` length 34 SHA-256 `b98b18cafa662cd717e11b8caab94959504074a39bb090a15638565c5d995c1f` value “Size of CST Persistent thing = %d”.
- Packet string ref `0x0062bf74` length 23 SHA-256 `95b3955d40c779e501f374fbdfa7a3214106d51aa22b51ec7e1966f320b36faf` value “Size of CST thing = %d”.
- Packet string ref `0x0062bf8c` length 27 SHA-256 `d6dc605b9aa9fcd8c5b83aea2c715d522f88c4c515381e75d66d36f159147121` value “Size of complex thing = %d”.
- Packet string ref `0x0062bfa8` length 19 SHA-256 `d3a978a05af55f801f32e96c88c3343599181f0548c53110df947837f6fc75b5` value “Size of thing = %d”.
- Packet string ref `0x0062bfbc` length 18 SHA-256 `6a68fd10719dada1d2b84784f902bb12366bea19049732bb0facdb18254fca01` value “Size of tree = %d”.
- Packet string ref `0x0062bfd0` length 19 SHA-256 `60125ff7d8ca4485df2c9adaef7a9c1fe77373c52001b39ec871f58d48787f37` value “Game::LoadLevel %d”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::LoadLevel` line 685 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__LoadLevel.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
