# Source-to-binary crosswalk — canonical five-wave reducer

Status: review candidate — exact corrected base plus five independently reviewed expansion receipts
Date: 2026-08-23

Summary: the canonical crosswalk now contains exactly 1,783 pinned-source definitions: 180 SOURCE_EXACT (10.1%), 344 SOURCE_ANALOG (19.3%), 1178 NO_MATCH_FOUND (66.1%), 70 NOT_IN_RETAIL (3.9%), and 11 CANDIDATE_UNRESOLVED (0.6%). The exact 634-definition omission set is closed with zero omitted, extra, or duplicate stable key.

Evidence: MEASURED — REUSED: the corrected 1,149-row base and 57 already settled wave definitions; EXTENDED: 577 accepted omission definitions with their reviewed source/retail boundaries; NEW_MEASUREMENT: 0. This reducer performs no new byte, runtime, Ghidra, PS2, drive, or retail-payload measurement.

Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes. The specimen, installed game, saves, binaries, Ghidra projects, and G:/H: corpora were not opened or written.

## Exact reconciliation

| Measure | Count |
| --- | ---: |
| Accepted corrected-base definitions | 1,149 |
| Accepted five-wave additions | 634 |
| Canonical source definitions | 1,783 |
| Pinned AST inventory definitions | 1,783 |
| Stable-key omissions | 0 |
| Stable-key extras | 0 |
| Stable-key duplicates | 0 |
| Populated-VA rows | 519 |
| Unique populated VAs | 515 |
| Pinned C/C++ files represented or explicitly zero-definition | 106 |

The stable identity is `(source_file, source_line, source function, signature)`. Every appended row also carries its accepted target branch and resolved source owner. The 1,149 base data lines remain physically byte-identical to the corrected base and resolve one-to-one through the hash-pinned 1,783-row inventory; their target branches were read back from the pinned source without rewriting those six-column lines.

## Classification contract

| Class | Canonical meaning |
| --- | --- |
| `SOURCE_EXACT` | Accepted evidence explicitly supports the same source-function body at the named retail VA. This is not a campaign `VERIFIED` promotion. |
| `SOURCE_ANALOG` | A named retail candidate and bounded relationship exist, without source-body equality. |
| `NO_MATCH_FOUND` | Bounded current-authority search found no supported target; renamed, folded, inlined, split, or absent emission remains falsifiable. |
| `NOT_IN_RETAIL` | The accepted target-selection receipt excludes the definition from this PC retail specimen. |
| `CANDIDATE_UNRESOLVED` | An accepted named/folded typed-wrapper candidate remains ambiguous; VA stays empty pending unique identity. |

`REVIEW_READY`, `SOURCE_ANALOG`, source agreement, and receipt acceptance are not retail `VERIFIED` promotions. This reducer copies classifications; it does not reinterpret, promote, or collapse them.

## Accepted Git lineage and artifact hashes

| Input | Accepted root | Landing | Definitions SHA-256 | RETAIL-DELTA SHA-256 | RECEIPT SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Corrected base | `7ac8247416764f41ffa92313aa82393856beae38` | `784367bd43f9ec13125521b00fe0c8352670ffdd` | `e37f13b37e9ce9d712174e35b86fc1f7ebcfc693fe9957448a8f39ff03829479` (crosswalk) | — | `a9a3d29a18655ef97e61591610c2721d934112b2a7a58acf264debe11a798c7f` (report) |
| W1 save/session/input/frontend | `39bc52a7c19be84b2877df83ca8cc244f9f272a8` | `efdfe9dd83a236b2ab7d8c2e1d729b543e306906` | `35b5b06be014464a1218ffc78ca312a225d667cf24d411fb1410d7cdeb93549b` | `f9feac8dce3d78004745ba067deda69e68803930327e2e83521b8b84b0cbd959` | `8e7da7cef5b00c2c641e111e01e19cc3132bbd77e8bd63496228a4db30cb0150` |
| W2 thing/BattleEngine/camera | `07fca645affb4d0483d35a52d0e70f39c784d15a` | `561c2099` | `d516756db15e51d2be4bf64798df48e3e1c716cb33f687c00a8dff5c90896693` | `e90352c35767ec4cb357656b82d925a80b5cc958772833f904cfad459c1235b4` | `0cf8de6c48ec1918c3584d3c12abbed156444145cfd28ac040e618e4f31af80e` |
| W3 audio/music | `3fb3f143ccdbba7b81ebc2d108c75c77184d3969` | `e92eb952` | `debf05d070f6e9bc54ac73d07a98eeca773db083ff0b9e5eb55612a28682384d` | `865885ad104e4840c1eb507e99288da7fd194a24b1dd46c76f30ddb1eaa396be` | `b71630b6887a230c5ff24f3aa25561b28e01a16f1068035f485549b196e896b4` |
| W4 memory/container/archive | `e3f470b1f9a839ee2bc5a41d41b0edbafe9ff89e` | `c6170bc8` | `132315189eb7897efc9708fbfea868f9c120d1389bdee786137d49db5e5350a7` | `afa3d47077c140f8b659f70bb0923233da31e333c577484b09c5c214d8fb094d` | `a983dd227fae162b60b260726dd45d99b104198ba9729cfcba3349c7125245c9` |
| W5 engine/render/platform/shell | `e229057918034a2d11a66a21bc3e3331136a5068` | `20608237` | `074385f8fd1de291f55dec9c565beb07aad87a3e6adfa4767515b8b23c357060` | `e72edc4060aafa94b2a15b1ec978a8ed95d1d8cc0a8bb9a9be5241af38db4a03` | `c8d8c6850d1bf8ad1a817609d084fc5056db0111f2dd9f2d566f192f351bc09e` |

Shared predecessor hashes:

- Pinned source inventory: `91bfee284185379db52c7d044e42a59b3f5ba75306c1150a0e56bdbb33705912` (1,783 unique stable keys).
- Frozen partition: `bc36791975f43d5da6b584727df3eb7d29402e18c550dd3d96e01bba0c301fde` (634 rows).
- Expansion plan: `604d5db76ecc9811b55321c5ec443f346c9be32515b6d8ed526142622d7ec393`.
- Execution contract: `12a0f72ea2b1606ee673824ee801586cefe815e0aa899d2fe55073e7c4509f18`.
- Expansion manifest: `6f58de995a27a0088749f40e06907969d3213872b40d1bf0bb450afda1fd216e`.
- Cold-check sample: `5235ff8e61fd12d9e4b17caf256d06c4a693cfd50bcce20d20261f42f21813bb`.
- Current name table: `4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213`.
- Current static closure: `cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974`.
- Current Generation-32 evidence register: `4862fc61391c9bf65cd7183752e99b9b02b6bfb721e5b4b5c1e7c5fae5b885b4`.

## Reuse accounting

| Wave | REUSED | EXTENDED | NEW_MEASUREMENT | Total |
| --- | ---: | ---: | ---: | ---: |
| W1 save/session/input/frontend | 11 | 169 | 0 | 180 |
| W2 thing/BattleEngine/camera | 46 | 155 | 0 | 201 |
| W3 audio/music | 0 | 23 | 0 | 23 |
| W4 memory/container/archive | 0 | 94 | 0 | 94 |
| W5 engine/render/platform/shell | 0 | 136 | 0 | 136 |
| **Wave total** | **57** | **577** | **0** | **634** |

The accepted wave receipts define these dispositions. `REUSED` means an existing reviewed authority already settled the retail relationship; `EXTENDED` means the wave added exact source/target/boundary/falsifier/rebuild routing to the frozen omission key; `NEW_MEASUREMENT` is zero because no new binary or runtime probe ran.

## Per-wave classification counts

| Wave | Rows | EXACT | ANALOG | NO_MATCH | NOT_IN_RETAIL | CANDIDATE_UNRESOLVED |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| W1 save/session/input/frontend | 180 | 8 | 3 | 169 | 0 | 0 |
| W2 thing/BattleEngine/camera | 201 | 32 | 5 | 164 | 0 | 0 |
| W3 audio/music | 23 | 1 | 1 | 21 | 0 | 0 |
| W4 memory/container/archive | 94 | 0 | 6 | 70 | 7 | 11 |
| W5 engine/render/platform/shell | 136 | 0 | 9 | 104 | 23 | 0 |

## Accepted folded populated-VA groups

Only the three W2 `SOURCE_FOLDED` groups repeat a populated VA:

| VA | Source definitions |
| --- | --- |
| `0x004040a0` | `CThing::GetRenderEndPos`; `CThing::GetRenderPos`; `CThing::GetRenderStartPos` |
| `0x0043e9f0` | `CThing::GetOldPos`; `CThing::GetSoundPos` |
| `0x0043ea20` | `CComplexThing::GetOldOrientation`; `CComplexThing::GetSoundOrientation` |

## Canonical TSV projection

The first six columns retain the v1 projection (`file`, `function`, `src_line`, `classification`, `va_or_empty`, `evidence_path`). Appended v2 columns preserve the accepted signature, target branch, resolved owner, original source-key function, retail name/candidate, retail-delta status, source/retail boundary, falsifier, and wave identity.

The corrected base lines intentionally remain six physical fields so their bytes do not change. Appended wave rows carry all 15 fields. A conforming reader must parse the header and treat absent trailing base fields as empty; canonical stable-key validation joins those base anchors to the accepted inventory rather than inventing metadata.

Canonical `crosswalk.tsv` SHA-256: `675b6aea18bc516ab563554372aba3dc9de467dba7aa22abbd1c8635be22ac71`.

## Per-file coverage

Counts below are mechanically derived from the canonical TSV. Zero-definition source files remain visible rather than disappearing from the denominator.

| File | Definitions | EXACT | ANALOG | NO_MATCH | NOT_IN_RETAIL | CANDIDATE_UNRESOLVED |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `activereader.cpp` | 1 | 0 | 1 | 0 | 0 | 0 |
| `activereader.h` | 11 | 0 | 1 | 10 | 0 | 0 |
| `actor.cpp` | 19 | 1 | 9 | 9 | 0 | 0 |
| `actor.h` | 11 | 3 | 0 | 8 | 0 | 0 |
| `Array.cpp` | 0 | 0 | 0 | 0 | 0 | 0 |
| `Array.h` | 25 | 0 | 0 | 25 | 0 | 0 |
| `BattleEngine.cpp` | 114 | 1 | 40 | 73 | 0 | 0 |
| `BattleEngine.h` | 49 | 5 | 0 | 44 | 0 | 0 |
| `BattleEngineConfigurations.cpp` | 5 | 0 | 0 | 5 | 0 | 0 |
| `BattleEngineConfigurations.h` | 1 | 0 | 0 | 1 | 0 | 0 |
| `BattleEngineDataManager.cpp` | 8 | 0 | 3 | 5 | 0 | 0 |
| `BattleEngineDataManager.h` | 26 | 0 | 0 | 26 | 0 | 0 |
| `BattleEngineJetPart.cpp` | 39 | 0 | 25 | 14 | 0 | 0 |
| `BattleEngineJetPart.h` | 5 | 0 | 0 | 5 | 0 | 0 |
| `BattleEngineWalkerPart.cpp` | 41 | 0 | 26 | 15 | 0 | 0 |
| `BattleEngineWalkerPart.h` | 5 | 0 | 0 | 5 | 0 | 0 |
| `Camera.cpp` | 47 | 0 | 22 | 25 | 0 | 0 |
| `Camera.h` | 28 | 0 | 2 | 26 | 0 | 0 |
| `Career.cpp` | 41 | 20 | 3 | 18 | 0 | 0 |
| `Career.h` | 27 | 3 | 0 | 24 | 0 | 0 |
| `chunker.cpp` | 17 | 0 | 5 | 12 | 0 | 0 |
| `chunker.h` | 3 | 0 | 0 | 3 | 0 | 0 |
| `CLIParams.cpp` | 3 | 0 | 0 | 3 | 0 | 0 |
| `CLIParams.h` | 1 | 0 | 0 | 1 | 0 | 0 |
| `Controller.cpp` | 18 | 10 | 3 | 5 | 0 | 0 |
| `Controller.h` | 9 | 0 | 0 | 9 | 0 | 0 |
| `d3dapp.cpp` | 17 | 0 | 11 | 6 | 0 | 0 |
| `d3dapp.h` | 11 | 0 | 0 | 11 | 0 | 0 |
| `DX.H` | 0 | 0 | 0 | 0 | 0 | 0 |
| `DXEngine.cpp` | 24 | 2 | 4 | 14 | 4 | 0 |
| `DXEngine.h` | 7 | 0 | 0 | 7 | 0 | 0 |
| `DXFrontend.cpp` | 4 | 0 | 1 | 3 | 0 | 0 |
| `DXFrontend.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `DXGame.cpp` | 2 | 0 | 0 | 2 | 0 | 0 |
| `DXGame.h` | 2 | 0 | 0 | 2 | 0 | 0 |
| `DXMemBuffer.cpp` | 19 | 6 | 1 | 12 | 0 | 0 |
| `DXMemBuffer.h` | 3 | 0 | 0 | 3 | 0 | 0 |
| `DXMemoryManager.cpp` | 18 | 5 | 4 | 7 | 2 | 0 |
| `DXMemoryManager.h` | 14 | 0 | 0 | 8 | 6 | 0 |
| `EditorD3DApp.cpp` | 17 | 0 | 0 | 17 | 0 | 0 |
| `EditorD3DApp.h` | 11 | 0 | 0 | 0 | 11 | 0 |
| `EndLevelData.cpp` | 2 | 0 | 1 | 1 | 0 | 0 |
| `EndLevelData.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `engine.cpp` | 34 | 1 | 15 | 18 | 0 | 0 |
| `engine.h` | 39 | 0 | 0 | 39 | 0 | 0 |
| `event.cpp` | 1 | 0 | 0 | 1 | 0 | 0 |
| `event.h` | 5 | 0 | 0 | 5 | 0 | 0 |
| `eventmanager.cpp` | 14 | 8 | 0 | 6 | 0 | 0 |
| `eventmanager.h` | 6 | 0 | 0 | 6 | 0 | 0 |
| `FEPGoodies.cpp` | 38 | 0 | 11 | 27 | 0 | 0 |
| `FEPGoodies.h` | 3 | 0 | 0 | 3 | 0 | 0 |
| `FEPLoadGame.cpp` | 8 | 0 | 4 | 4 | 0 | 0 |
| `FEPLoadGame.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `FEPSaveGame.cpp` | 12 | 0 | 7 | 5 | 0 | 0 |
| `FEPSaveGame.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `FrontEnd.cpp` | 38 | 0 | 23 | 15 | 0 | 0 |
| `Frontend.h` | 21 | 0 | 0 | 21 | 0 | 0 |
| `game.cpp` | 79 | 38 | 21 | 20 | 0 | 0 |
| `game.h` | 58 | 0 | 0 | 58 | 0 | 0 |
| `InitThing.cpp` | 18 | 0 | 1 | 17 | 0 | 0 |
| `InitThing.h` | 34 | 0 | 0 | 34 | 0 | 0 |
| `ltshell.cpp` | 44 | 0 | 2 | 42 | 0 | 0 |
| `ltshell.h` | 42 | 0 | 8 | 34 | 0 | 0 |
| `membuffer.h` | 3 | 0 | 0 | 3 | 0 | 0 |
| `MemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 | 0 |
| `MemoryCard.h` | 2 | 0 | 0 | 2 | 0 | 0 |
| `MemoryManager.cpp` | 41 | 0 | 18 | 23 | 0 | 0 |
| `MemoryManager.h` | 23 | 0 | 0 | 23 | 0 | 0 |
| `Music.cpp` | 27 | 5 | 4 | 18 | 0 | 0 |
| `Music.h` | 8 | 0 | 0 | 8 | 0 | 0 |
| `PCController.cpp` | 7 | 0 | 6 | 1 | 0 | 0 |
| `PCController.h` | 6 | 5 | 0 | 1 | 0 | 0 |
| `PCEngine.cpp` | 18 | 0 | 0 | 18 | 0 | 0 |
| `PCEngine.h` | 11 | 0 | 0 | 0 | 11 | 0 |
| `PCFEPLoadGame.cpp` | 0 | 0 | 0 | 0 | 0 | 0 |
| `PCFEPLoadGame.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `PCFEPSaveGame.cpp` | 0 | 0 | 0 | 0 | 0 | 0 |
| `PCFEPSaveGame.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `PCFrontend.cpp` | 6 | 0 | 0 | 6 | 0 | 0 |
| `PCFrontend.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `PCGame.cpp` | 3 | 0 | 0 | 3 | 0 | 0 |
| `PCGame.h` | 2 | 0 | 0 | 2 | 0 | 0 |
| `PCMemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 | 0 |
| `PCMemoryCard.h` | 17 | 0 | 1 | 16 | 0 | 0 |
| `PCPlatform.cpp` | 32 | 0 | 7 | 25 | 0 | 0 |
| `PCPlatform.h` | 9 | 0 | 0 | 9 | 0 | 0 |
| `pcsoundmanager.cpp` | 17 | 11 | 1 | 5 | 0 | 0 |
| `pcsoundmanager.h` | 4 | 1 | 0 | 3 | 0 | 0 |
| `Platform.cpp` | 1 | 0 | 0 | 1 | 0 | 0 |
| `Platform.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `Player.cpp` | 18 | 1 | 12 | 5 | 0 | 0 |
| `Player.h` | 14 | 0 | 0 | 14 | 0 | 0 |
| `ResourceAccumulator.cpp` | 9 | 0 | 0 | 9 | 0 | 0 |
| `ResourceAccumulator.h` | 8 | 0 | 0 | 8 | 0 | 0 |
| `scheduledevent.cpp` | 2 | 2 | 0 | 0 | 0 | 0 |
| `scheduledevent.h` | 10 | 0 | 0 | 10 | 0 | 0 |
| `SoundManager.cpp` | 48 | 26 | 3 | 19 | 0 | 0 |
| `SoundManager.h` | 18 | 0 | 1 | 17 | 0 | 0 |
| `SPtrSet.cpp` | 13 | 0 | 3 | 10 | 0 | 0 |
| `SPtrSet.h` | 24 | 0 | 2 | 11 | 0 | 11 |
| `storage.cpp` | 0 | 0 | 0 | 0 | 0 | 0 |
| `storage.h` | 0 | 0 | 0 | 0 | 0 | 0 |
| `thing.cpp` | 47 | 2 | 32 | 13 | 0 | 0 |
| `thing.h` | 98 | 24 | 0 | 74 | 0 | 0 |
| `XBoxMemoryCard.cpp` | 36 | 0 | 0 | 0 | 36 | 0 |
| `XBoxMemoryCard.h` | 0 | 0 | 0 | 0 | 0 | 0 |

## Validation state

- PASS: accepted corrected-base root/landing and all five accepted wave root/landing artifacts read back byte-identically.
- PASS: exact union `1,149 corrected base + 634 frozen partition = 1,783 inventory`; zero omission, extra, or duplicate stable key.
- PASS: every appended classification, populated VA/name, evidence string, source/retail boundary, falsifier, and target branch matches its accepted definitions/delta receipt byte-for-byte as a decoded TSV field; source owners are copied from accepted fields or losslessly resolved from accepted qualified functions where the receipt has no owner column.
- PASS: all 519 populated rows resolve to 515 current name-table, closure, and Generation-32 register VAs; repeated VAs are exactly the three accepted folded groups.
- PASS: 3531 path-shaped evidence tokens resolve; bounded authority labels remain labels rather than fabricated paths.
- PASS: two fresh reducer roots produced byte-identical `crosswalk.tsv` and `REPORT.md` hashes.
- PASS: equivalent five-wave joined invariants plus available receipt validators, documentation links/headers/name assertions/evidence header, `npm run test:docs`, and `git diff --check`.

## Evidence boundaries

- The reducer preserves accepted wave meanings. It does not turn `SOURCE_AGREES`, `SOURCE_EXACT`, `SOURCE_ANALOG`, or review readiness into campaign verification.
- `NO_MATCH_FOUND` and `CANDIDATE_UNRESOLVED` remain explicit falsifiable frontiers, not claims of binary absence.
- Source target selection proves only the accepted compile/platform branch. Retail identity remains limited by each row's copied evidence boundary and falsifier.
- Reconstruction dispositions stay in the reviewed wave receipts; this two-file reducer does not edit rebuild, source contracts, receipt roots, named systems, campaign state, or developer state.
