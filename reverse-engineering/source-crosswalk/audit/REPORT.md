# Source crosswalk corpus integrity audit

Status: complete independent audit receipt
Date: 2026-08-22

Summary: the 1,164-row Gold crosswalk is row-count stable but is not a complete or fully supportable inventory. A fresh AST inventory found 1,783 C++ function definitions across 106 pinned `*.cpp`/`*.h` files. Exactly 1,149 definitions join to crosswalk rows; 634 definitions are omitted and 15 crosswalk rows are not functions. Row-level evidence has 200 failures, and populated-VA authority comparison has 35 disagreement rows.

Evidence: MEASURED — deterministic source AST inventory, row-by-row source/evidence resolution, tracked name-table/static-closure joins, and a two-run byte-identical replay; SOURCE — pinned `references/Onslaught`; UNKNOWN — compiler-selected build membership and any function definitions not recovered by the bounded parser.

Specimen: tracked retail authorities are bound to pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; this audit did not open or read the binary.

## Verdict and denominators

| Measure | Result |
| --- | ---: |
| Pinned source files scanned | 106 (52 cpp, 54 h) |
| AST function definitions | 1783 |
| Crosswalk data rows | 1164 |
| Valid source-definition joins | 1149 |
| Omitted source definitions | 634 |
| Crosswalk extras (non-functions) | 15 |
| Exact duplicate `(file,function,line)` rows | 0 |
| Same-file repeated function labels retained by line | 19 groups / 54 row findings |
| Populated VA rows | 466 |
| SOURCE_ANALOG rows without a VA | 7 |

The reconciliation is exact: `1,783 - 634 = 1,149` matched source definitions and `1,164 - 15 = 1,149` valid crosswalk rows. Alternative preprocessor branches remain distinct definitions at distinct source lines. Overloads and duplicate labels were not normalized together.

## Crosswalk classes and row statuses

| Classification | Rows |
| --- | ---: |
| `SOURCE_EXACT` | 136 |
| `SOURCE_ANALOG` | 337 |
| `NO_MATCH_FOUND` | 651 |
| `NOT_IN_RETAIL` | 40 |

| Domain | Status | Rows |
| --- | --- | ---: |
| structural | `FAIL` | 15 |
| structural | `PASS` | 1101 |
| structural | `PASS_AMBIGUOUS_NAME` | 48 |
| evidence | `FAIL` | 200 |
| evidence | `PASS` | 316 |
| evidence | `PASS_SHARED_METHOD` | 648 |
| authority | `DISAGREEMENT` | 35 |
| authority | `NOT_APPLICABLE` | 698 |
| authority | `PASS` | 431 |

Evidence interpretation:

- All 136 `SOURCE_EXACT` rows have populated normalized in-range VAs. One is evidentially mismatched: `Music.cpp:182 CMusic::Play` cites `0x004bb450`, while its own semantics row identifies that VA as `CMusic::DeviceChangeTrack` at source line 166 and says the saved `CMusic__Play` name is wrong.
- Of 337 `SOURCE_ANALOG` rows, 168 cite no evidence path and 190 lack a cited bounded analogy reason. Two note-only/empty-VA PCPlatform rows do not resolve a named retail analog.
- Of 651 `NO_MATCH_FOUND` rows, 648 pass only through the original report's shared exact/prefix/variant/name-note search method. Three are contradicted by normalized hits in the current tracked name table: `CDXEngine::ShutDown`, `CThing::AddShutdownEvent`, and `CThing::StartDieProcess`.
- All 40 `NOT_IN_RETAIL` rows have empty VAs and are enclosed by direct Xbox-only lexical guards; the PC retail specimen identity supplies the build/platform side of the claim.
- Every cited path exists as a file. Eleven citations do not resolve to this row's VA/source anchor/function identity; existence alone is not counted as evidence.

## Defect classes

`row-audit.tsv` can carry multiple codes per row, so this table is not additive.

| Finding code | Rows |
| --- | ---: |
| `ANALOG_REASON_EVIDENCE_WEAK` | 190 |
| `ANALOG_EVIDENCE_PATH_MISSING` | 168 |
| `SOURCE_NAME_AMBIGUOUS` | 54 |
| `CROSSWALK_VA_COLLISION` | 34 |
| `CROSSWALK_EXTRA_ROW` | 15 |
| `EVIDENCE_TARGET_UNRESOLVED` | 11 |
| `NO_MATCH_NAME_TABLE_HIT` | 3 |
| `ANALOG_RETAIL_ANALOG_UNNAMED` | 2 |
| `AUTHORITY_SIZE_RANGE_DISAGREEMENT` | 1 |
| `EXACT_IDENTITY_EVIDENCE_WEAK` | 1 |

## Authority cross-check

All 466 populated VAs were checked against both the tracked 8,329-row Ghidra name table and the dated 8,136-row static-closure TSV. Results: 431 pass and 35 disagreement rows; 698 empty-VA rows are not applicable.

- No populated crosswalk VA is missing from either authority.
- No joined row has a name-table/static-closure name disagreement or an unexpected closure grade.
- One joined body-range disagreement exists: `FEPGoodies.cpp:2521 CFEPGoodies::TransitionNotification` at `0x0045ffa0`; name table `bodyMax=0x00460041`, static closure `bodyMax=0x0046001c`, closure `bodyBytes=125`, grade `C1_CANDIDATE_PARTIAL`.
- 16 repeated-VA groups affect 34 rows. They are retained as disagreements rather than silently treated as aliases.

### Repeated VA groups

- `0x004015e0` — <code>actor.cpp:74:CActor::Move</code>; <code>actor.cpp:178:CActor::MoveTo</code>
- `0x0041bd00` — <code>Career.cpp:379:CCareer::Update</code>; <code>Career.cpp:519:CCareer::UpdateBaseWorldExistsStuffForNode</code>
- `0x00421200` — <code>Career.cpp:1040:CCareer::Load</code>; <code>Career.cpp:1095:CCareer::Load</code>
- `0x00421350` — <code>Career.cpp:1068:CCareer::Save</code>; <code>Career.cpp:1128:CCareer::Save</code>
- `0x0045e0d0` — <code>FEPGoodies.cpp:1718:CFEPGoodies::RenderPreCommon</code>; <code>FEPGoodies.cpp:1825:CFEPGoodies::Render</code>
- `0x00461d90` — <code>FEPLoadGame.cpp:88:CFEPLoadGame::RenderPreCommon</code>; <code>FEPLoadGame.cpp:93:CFEPLoadGame::Render</code>
- `0x00464a80` — <code>FEPSaveGame.cpp:171:CFEPSaveGame::RenderPreCommon</code>; <code>FEPSaveGame.cpp:176:CFEPSaveGame::Render</code>
- `0x00468200` — <code>FrontEnd.cpp:1048:CFrontEnd::RenderSlidingScreen</code>; <code>FrontEnd.cpp:1259:CFrontEnd::Render</code>; <code>FrontEnd.cpp:1528:CFrontEnd::RenderEnd</code>
- `0x0046c360` — <code>game.cpp:246:CGame::Init</code>; <code>game.cpp:662:CGame::InitOneOffResources</code>; <code>game.cpp:674:CGame::InitRestartResources</code>
- `0x004a1810` — <code>MemoryManager.cpp:502:CMemoryHeap::AllocTiny</code>; <code>MemoryManager.cpp:613:CMemoryHeap::Alloc</code>
- `0x004a1ca0` — <code>MemoryManager.cpp:828:CMemoryHeap::Free</code>; <code>MemoryManager.cpp:1147:CMemoryHeap::FreeAll</code>
- `0x004f44a0` — <code>thing.cpp:763:CComplexThing::SetAnimMode</code>; <code>thing.cpp:788:CComplexThing::SetAnimMode</code>
- `0x00517c60` — <code>pcsoundmanager.cpp:468:CPCSoundManager::GetSampleLength</code>; <code>pcsoundmanager.cpp:477:CPCSoundManager::GetSampleLengthInSamples</code>
- `0x0053e2e0` — <code>DXEngine.cpp:313:CDXEngine::RenderArrow</code>; <code>DXEngine.cpp:637:CDXEngine::Render</code>
- `0x00548570` — <code>DXMemBuffer.cpp:394:CDXMemBuffer::Read</code>; <code>DXMemBuffer.cpp:467:CDXMemBuffer::ReadString</code>
- `0x00549220` — <code>DXMemoryManager.cpp:247:CDXMemoryManager::Free</code>; <code>DXMemoryManager.cpp:291:CDXMemoryManager::FreeAll</code>

## Priority cold-read sample

Cold-read sample: 11 / 11 `SOURCE_EXACT` pass; 8 / 11 `SOURCE_ANALOG` pass. The analog failures are the actor `MoveTo`/`GetFractionTime` rows and `DXEngine::RenderArrow`.

Cold-read against source signatures/bodies plus every cited evidence item. The pinned source tree has no frustum file and no settings-named cpp/h file; Career Load/Save covers the settings/options tail, and DXEngine Render/RenderArrow covers the render lens.

| Class | Source | VA | Outcome | Cold-read basis |
| --- | --- | --- | --- | --- |
| `SOURCE_EXACT` | <code>BattleEngine.cpp:63 CBattleEngine::Init</code> | `0x00404dd0` | **PASS** | Function note names the exact source line and retail VA and pins the retail initialization envelope and call sequence. |
| `SOURCE_EXACT` | <code>Career.cpp:93 CCareerNode::Blank</code> | `0x0041b740` | **PASS** | Note explicitly says Verified vs Source: Yes, names CCareerNode::Blank, and matches the source reset fields. |
| `SOURCE_EXACT` | <code>Career.cpp:133 CCareerNode::SetBaseThingExistTo</code> | `0x0041b770` | **PASS** | Note explicitly joins the named method and VA and reproduces the source bit-index/set-clear algorithm. |
| `SOURCE_EXACT` | <code>Career.cpp:181 CCareer::GetLevelStructure</code> | `0x0041b7b0` | **PASS** | Note says Verified vs Source: Yes and identifies the constant-address return of level_structure. |
| `SOURCE_EXACT` | <code>game.cpp:246 CGame::Init</code> | `0x0046c360` | **PASS** | Function note and lifecycle TSV both name the exact source line and initialization sequence. |
| `SOURCE_EXACT` | <code>game.cpp:292 CGame::InitRestartLoop</code> | `0x0046c430` | **PASS** | Function note and lifecycle TSV explicitly identify the restart-loop reset/allocation owner. |
| `SOURCE_EXACT` | <code>game.cpp:414 CGame::Shutdown</code> | `0x0046c990` | **PASS** | The note gives the exact source owner and retail boundary; the lifecycle TSV adds SOURCE_BODY_DEMO_TWIN identity. |
| `SOURCE_EXACT` | <code>game.cpp:530 CGame::ShutdownRestartLoop</code> | `0x0046ca70` | **PASS** | Note and lifecycle TSV explicitly map the named teardown path and its source line. |
| `SOURCE_EXACT` | <code>game.cpp:624 CGame::LoadResources</code> | `0x0046cd30` | **PASS** | Function note says Verified vs Source: Yes and matches the source resource-load sequence and failure return. |
| `SOURCE_EXACT` | <code>game.cpp:1260 CGame::RestartLoopRunLevel</code> | `0x0046dc30` | **PASS** | Function note and lifecycle TSV name the exact inner restart-loop lifecycle and bounded retail/demo divergence. |
| `SOURCE_EXACT` | <code>DXEngine.cpp:637 CDXEngine::Render</code> | `0x0053e2e0` | **PASS** | Render note names the exact source line, VA, per-view render role, and callsite parity. |
| `SOURCE_ANALOG` | <code>BattleEngine.cpp:842 CBattleEngine::FireLock</code> | `0x00407060` | **PASS** | Byte-contract note names the source range as architecture, then bounds the retail inline Fired stores and unproven fields/callees. |
| `SOURCE_ANALOG` | <code>BattleEngine.cpp:882 CBattleEngine::LockHit</code> | `0x00407140` | **PASS** | Byte-contract note names the source walk/remove/delete sequence and bounds the retail inline destructor/free divergence. |
| `SOURCE_ANALOG` | <code>BattleEngine.cpp:1270 CBattleEngine::Move</code> | `0x004081c0` | **PASS** | RTTI/vtable and body-order note names the retail analog while explicitly limiting the claim to high-confidence static identity. |
| `SOURCE_ANALOG` | <code>Career.cpp:1095 CCareer::Load</code> | `0x00421200` | **PASS** | Note and save-format TSV identify the Xbox-shaped source analog and bound the retail PC options/tail and flag divergence. |
| `SOURCE_ANALOG` | <code>Career.cpp:1128 CCareer::Save</code> | `0x00421350` | **PASS** | Note and save-format TSV identify the source serializer shape and bound the retail PC options/tail and progress-flag difference. |
| `SOURCE_ANALOG` | <code>actor.cpp:178 CActor::MoveTo</code> | `0x004015e0` | **FAIL** | Only the name table is cited; it names this VA CActor__Move, while source MoveTo is a distinct superclass forwarder and the same VA is also assigned to CActor::Move. |
| `SOURCE_ANALOG` | <code>actor.cpp:262 CActor::GetFractionTime</code> | `0x00401b50` | **FAIL** | The retail name exists, but the row cites no evidence path and gives no bounded reason for analogy. |
| `SOURCE_ANALOG` | <code>game.cpp:910 CGame::FillOutEndLevelData</code> | `0x0046d470` | **PASS** | Detailed byte-contract note names the exact source line and bounds the retail base-things/scalar/objective behavior and remaining unknowns. |
| `SOURCE_ANALOG` | <code>game.cpp:1122 CGame::RunIntroFMV</code> | `0x0046d890` | **PASS** | Function note names the high-confidence source mapping and bounds Steam-only skip inputs and retail behavior. |
| `SOURCE_ANALOG` | <code>game.cpp:2503 CGame::DeclarePlayerDead</code> | `0x0046f550` | **PASS** | Function note explicitly names the source method, retail VA, death-routing role, and build-specific branching boundary. |
| `SOURCE_ANALOG` | <code>DXEngine.cpp:313 CDXEngine::RenderArrow</code> | `0x0053e2e0` | **FAIL** | Only the name table is cited and it names the VA CDXEngine__Render; source RenderArrow is a separate function and the exact Render row owns the same VA. |

## Per-file reconciliation

| Source file | AST definitions | Crosswalk rows | Omissions | Extras |
| --- | ---: | ---: | ---: | ---: |
| `activereader.cpp` | 1 | 1 | 0 | 0 |
| `activereader.h` | 11 | 0 | 11 | 0 |
| `actor.cpp` | 19 | 19 | 0 | 0 |
| `actor.h` | 11 | 0 | 11 | 0 |
| `Array.cpp` | 0 | 0 | 0 | 0 |
| `Array.h` | 25 | 2 | 23 | 0 |
| `BattleEngine.cpp` | 114 | 114 | 0 | 0 |
| `BattleEngine.h` | 49 | 2 | 47 | 0 |
| `BattleEngineConfigurations.cpp` | 5 | 5 | 0 | 0 |
| `BattleEngineConfigurations.h` | 1 | 0 | 1 | 0 |
| `BattleEngineDataManager.cpp` | 8 | 8 | 0 | 0 |
| `BattleEngineDataManager.h` | 26 | 25 | 1 | 0 |
| `BattleEngineJetPart.cpp` | 39 | 39 | 0 | 0 |
| `BattleEngineJetPart.h` | 5 | 0 | 5 | 0 |
| `BattleEngineWalkerPart.cpp` | 41 | 41 | 0 | 0 |
| `BattleEngineWalkerPart.h` | 5 | 0 | 5 | 0 |
| `Camera.cpp` | 47 | 47 | 2 | 2 |
| `Camera.h` | 28 | 0 | 28 | 0 |
| `Career.cpp` | 41 | 41 | 0 | 0 |
| `Career.h` | 27 | 0 | 27 | 0 |
| `chunker.cpp` | 17 | 17 | 0 | 0 |
| `chunker.h` | 3 | 0 | 3 | 0 |
| `CLIParams.cpp` | 3 | 3 | 0 | 0 |
| `CLIParams.h` | 1 | 0 | 1 | 0 |
| `Controller.cpp` | 18 | 18 | 0 | 0 |
| `Controller.h` | 9 | 4 | 5 | 0 |
| `d3dapp.cpp` | 17 | 17 | 0 | 0 |
| `d3dapp.h` | 11 | 0 | 11 | 0 |
| `DX.H` | 0 | 0 | 0 | 0 |
| `DXEngine.cpp` | 24 | 23 | 1 | 0 |
| `DXEngine.h` | 7 | 1 | 6 | 0 |
| `DXFrontend.cpp` | 4 | 4 | 0 | 0 |
| `DXFrontend.h` | 0 | 0 | 0 | 0 |
| `DXGame.cpp` | 2 | 2 | 0 | 0 |
| `DXGame.h` | 2 | 0 | 2 | 0 |
| `DXMemBuffer.cpp` | 19 | 19 | 0 | 0 |
| `DXMemBuffer.h` | 3 | 0 | 3 | 0 |
| `DXMemoryManager.cpp` | 18 | 17 | 1 | 0 |
| `DXMemoryManager.h` | 14 | 2 | 12 | 0 |
| `EditorD3DApp.cpp` | 17 | 17 | 0 | 0 |
| `EditorD3DApp.h` | 11 | 0 | 11 | 0 |
| `EndLevelData.cpp` | 2 | 2 | 0 | 0 |
| `EndLevelData.h` | 0 | 0 | 0 | 0 |
| `engine.cpp` | 34 | 34 | 0 | 0 |
| `engine.h` | 39 | 0 | 39 | 0 |
| `event.cpp` | 1 | 1 | 0 | 0 |
| `event.h` | 5 | 0 | 5 | 0 |
| `eventmanager.cpp` | 14 | 14 | 0 | 0 |
| `eventmanager.h` | 6 | 0 | 6 | 0 |
| `FEPGoodies.cpp` | 38 | 38 | 0 | 0 |
| `FEPGoodies.h` | 3 | 1 | 2 | 0 |
| `FEPLoadGame.cpp` | 8 | 8 | 0 | 0 |
| `FEPLoadGame.h` | 0 | 0 | 0 | 0 |
| `FEPSaveGame.cpp` | 12 | 12 | 0 | 0 |
| `FEPSaveGame.h` | 0 | 0 | 0 | 0 |
| `FrontEnd.cpp` | 38 | 38 | 1 | 1 |
| `Frontend.h` | 21 | 0 | 21 | 0 |
| `game.cpp` | 79 | 77 | 7 | 5 |
| `game.h` | 58 | 3 | 55 | 0 |
| `InitThing.cpp` | 18 | 18 | 1 | 1 |
| `InitThing.h` | 34 | 32 | 3 | 1 |
| `ltshell.cpp` | 44 | 43 | 1 | 0 |
| `ltshell.h` | 42 | 2 | 40 | 0 |
| `membuffer.h` | 3 | 0 | 3 | 0 |
| `MemoryCard.cpp` | 1 | 1 | 0 | 0 |
| `MemoryCard.h` | 2 | 1 | 1 | 0 |
| `MemoryManager.cpp` | 41 | 39 | 2 | 0 |
| `MemoryManager.h` | 23 | 4 | 19 | 0 |
| `Music.cpp` | 27 | 27 | 0 | 0 |
| `Music.h` | 8 | 2 | 6 | 0 |
| `PCController.cpp` | 7 | 8 | 1 | 2 |
| `PCController.h` | 6 | 0 | 6 | 0 |
| `PCEngine.cpp` | 18 | 18 | 0 | 0 |
| `PCEngine.h` | 11 | 0 | 11 | 0 |
| `PCFEPLoadGame.cpp` | 0 | 0 | 0 | 0 |
| `PCFEPLoadGame.h` | 0 | 0 | 0 | 0 |
| `PCFEPSaveGame.cpp` | 0 | 0 | 0 | 0 |
| `PCFEPSaveGame.h` | 0 | 0 | 0 | 0 |
| `PCFrontend.cpp` | 6 | 6 | 0 | 0 |
| `PCFrontend.h` | 0 | 0 | 0 | 0 |
| `PCGame.cpp` | 3 | 3 | 0 | 0 |
| `PCGame.h` | 2 | 0 | 2 | 0 |
| `PCMemoryCard.cpp` | 1 | 1 | 0 | 0 |
| `PCMemoryCard.h` | 17 | 14 | 3 | 0 |
| `PCPlatform.cpp` | 32 | 32 | 0 | 0 |
| `PCPlatform.h` | 9 | 1 | 8 | 0 |
| `pcsoundmanager.cpp` | 17 | 17 | 0 | 0 |
| `pcsoundmanager.h` | 4 | 2 | 2 | 0 |
| `Platform.cpp` | 1 | 1 | 0 | 0 |
| `Platform.h` | 0 | 0 | 0 | 0 |
| `Player.cpp` | 18 | 18 | 1 | 1 |
| `Player.h` | 14 | 0 | 14 | 0 |
| `ResourceAccumulator.cpp` | 9 | 9 | 0 | 0 |
| `ResourceAccumulator.h` | 8 | 0 | 8 | 0 |
| `scheduledevent.cpp` | 2 | 2 | 0 | 0 |
| `scheduledevent.h` | 10 | 0 | 10 | 0 |
| `SoundManager.cpp` | 48 | 48 | 0 | 0 |
| `SoundManager.h` | 18 | 3 | 15 | 0 |
| `SPtrSet.cpp` | 13 | 12 | 3 | 2 |
| `SPtrSet.h` | 24 | 0 | 24 | 0 |
| `storage.cpp` | 0 | 0 | 0 | 0 |
| `storage.h` | 0 | 0 | 0 | 0 |
| `thing.cpp` | 47 | 47 | 0 | 0 |
| `thing.h` | 98 | 1 | 97 | 0 |
| `XBoxMemoryCard.cpp` | 36 | 36 | 0 | 0 |
| `XBoxMemoryCard.h` | 0 | 0 | 0 | 0 |

## Crosswalk extras — all 15 named

These rows point at member initializers, static data, or switch labels rather than function definitions.

- <code>Camera.cpp:348 mLength</code>
- <code>Camera.cpp:719 mPos</code>
- <code>FrontEnd.cpp:37 mAllLevelsCheatActive</code>
- <code>InitThing.cpp:80 mAttachScriptsToUnits</code>
- <code>PCController.cpp:15 CController::mMappings</code>
- <code>PCController.cpp:144 CController</code>
- <code>Player.cpp:25 mNumber</code>
- <code>SPtrSet.cpp:27 mSize</code>
- <code>SPtrSet.cpp:38 mSize</code>
- <code>game.cpp:2521 CWorld::kSinglePlayer</code>
- <code>game.cpp:2533 CWorld::kCooperativeMultiplayer</code>
- <code>game.cpp:2548 CWorld::kVersusMultiplayer</code>
- <code>game.cpp:3106 CWorld::kCooperativeMultiplayer</code>
- <code>game.cpp:3129 CWorld::kVersusMultiplayer</code>
- <code>InitThing.h:422 mSquadDelay</code>

## Repeated source labels — all groups named

These are not collapsed. They include overloads, conditional definitions, and parser labels that need the source line to remain unambiguous.

- <code>Array.h:operator_subscript</code> — lines `103,117`
- <code>BattleEngine.cpp:CBattleEngine::PlayHudSample</code> — lines `3161,3180`
- <code>BattleEngineDataManager.cpp:CBattleEngineData::Load</code> — lines `148,588`
- <code>BattleEngineDataManager.h:GetConfiguration</code> — lines `272,289,418`
- <code>BattleEngineDataManager.h:Load</code> — lines `301,338`
- <code>CLIParams.cpp:CCLIParams::GetParams</code> — lines `85,390`
- <code>Career.cpp:CCareer::Load</code> — lines `1040,1095`
- <code>Career.cpp:CCareer::Save</code> — lines `1068,1128`
- <code>FEPGoodies.cpp:goodies_prepare_projection</code> — lines `1790,1808`
- <code>FEPGoodies.cpp:goodies_restore_projection</code> — lines `1800,1818`
- <code>InitThing.h:Copy</code> — lines `144,379,435,645,651,699,751,810,850,876`
- <code>InitThing.h:Load</code> — lines `170,391,454,665,709,764,819,858`
- <code>SPtrSet.cpp:mSize</code> — lines `27,38`
- <code>chunker.cpp:CChunkReader::Open</code> — lines `108,123`
- <code>eventmanager.cpp:CEventManager::AddEvent</code> — lines `143,152,170`
- <code>game.cpp:CWorld::kCooperativeMultiplayer</code> — lines `2533,3106`
- <code>game.cpp:CWorld::kVersusMultiplayer</code> — lines `2548,3129`
- <code>game.cpp:ReceiveButtonAction</code> — lines `1240,4094`
- <code>thing.cpp:CComplexThing::SetAnimMode</code> — lines `763,788`

## Omitted source definitions — all 634 named

The list below is the deterministic AST inventory minus rows joined by exact source file/line and compatible function identity.

- <code>activereader.h:17 CGenericActiveReader::~dtor</code> — <code>~CGenericActiveReader()</code>
- <code>activereader.h:19 CGenericActiveReader::ToReadDied</code> — <code>ToReadDied()</code>
- <code>activereader.h:32 CActiveReader::CActiveReader</code> — <code>CActiveReader()</code>
- <code>activereader.h:33 CActiveReader::CActiveReader</code> — <code>CActiveReader(T* to_read)</code>
- <code>activereader.h:34 CActiveReader::CActiveReader</code> — <code>CActiveReader(CActiveReader&lt;T&gt;&amp; copy)</code>
- <code>activereader.h:35 CActiveReader::SetReader</code> — <code>SetReader(T* to_read)</code>
- <code>activereader.h:36 CActiveReader::operator==</code> — <code>operator ==(T* right_term)</code>
- <code>activereader.h:37 CActiveReader::operator!=</code> — <code>operator !=(T* right_term)</code>
- <code>activereader.h:38 CActiveReader::operator=</code> — <code>operator =(T* right_term)</code>
- <code>activereader.h:39 CActiveReader::operator-&gt;</code> — <code>* operator -&gt;()</code>
- <code>activereader.h:40 CActiveReader::ToRead</code> — <code>* ToRead()</code>
- <code>actor.h:18 SetThingType</code> — <code>SetThingType(ULONG t)</code>
- <code>actor.h:24 GetVelocity</code> — <code>GetVelocity()</code>
- <code>actor.h:25 SetVelocity</code> — <code>SetVelocity(const FVector&amp; vel)</code>
- <code>actor.h:26 AddVelocity</code> — <code>AddVelocity(const FVector&amp; vel)</code>
- <code>actor.h:27 GetOldPos</code> — <code>GetOldPos()</code>
- <code>actor.h:28 GetOldOrientation</code> — <code>GetOldOrientation()</code>
- <code>actor.h:35 GetLocalLastFrameMovement</code> — <code>GetLocalLastFrameMovement()</code>
- <code>actor.h:40 Stop</code> — <code>Stop()</code>
- <code>actor.h:53 GetLastTimeOnGround</code> — <code>GetLastTimeOnGround()</code>
- <code>actor.h:54 GetLastTimeInWater</code> — <code>GetLastTimeInWater()</code>
- <code>actor.h:55 GetLastTimeOnObject</code> — <code>GetLastTimeOnObject()</code>
- <code>Array.h:15 CArray::CArray</code> — <code>CArray(int sz)</code>
- <code>Array.h:16 CArray::~dtor</code> — <code>~CArray()</code>
- <code>Array.h:18 CArray::CArray</code> — <code>CArray(int sz)</code>
- <code>Array.h:19 CArray::~dtor</code> — <code>~CArray()</code>
- <code>Array.h:21 CArray::operator=</code> — <code>&amp; operator =(CArray&lt;T&gt;&amp; copy)</code>
- <code>Array.h:22 CArray::SetAll</code> — <code>SetAll(T val)</code>
- <code>Array.h:23 CArray::Size</code> — <code>Size()</code>
- <code>Array.h:27 CArray::ReSize</code> — <code>ReSize(int size)</code>
- <code>Array.h:29 CArray::ReSize</code> — <code>ReSize(int size)</code>
- <code>Array.h:32 CArray::ReSize</code> — <code>ReSize(int size)</code>
- <code>Array.h:35 CArray::ReSize</code> — <code>ReSize(int size)</code>
- <code>Array.h:43 CArray::operator[]</code> — <code>&amp; operator [] (int item)</code>
- <code>Array.h:58 CSArray::operator=</code> — <code>&amp; operator =(CSArray&lt;T, size&gt;&amp; copy)</code>
- <code>Array.h:59 CSArray::SetAll</code> — <code>SetAll(T val)</code>
- <code>Array.h:60 CSArray::Size</code> — <code>Size()</code>
- <code>Array.h:65 CSArray::operator[]</code> — <code>&amp; operator [] (int item)</code>
- <code>Array.h:78 COSet::COSet</code> — <code>COSet(int initial_size = 1)</code>
- <code>Array.h:79 COSet::operator=</code> — <code>&amp; operator =(COSet&lt;T&gt;&amp; copy)</code>
- <code>Array.h:80 COSet::Add</code> — <code>Add(const T&amp; item)</code>
- <code>Array.h:81 COSet::First</code> — <code>* First()</code>
- <code>Array.h:82 COSet::Next</code> — <code>* Next()</code>
- <code>Array.h:83 COSet::Finalise</code> — <code>Finalise()</code>
- <code>Array.h:84 COSet::Size</code> — <code>Size()</code>
- <code>BattleEngine.h:96 GetZoom</code> — <code>GetZoom()</code>
- <code>BattleEngine.h:97 GetOldZoom</code> — <code>GetOldZoom()</code>
- <code>BattleEngine.h:108 AttachEquipment</code> — <code>AttachEquipment(CEquipment* eqi)</code>
- <code>BattleEngine.h:110 GetUnitOverCrossHair</code> — <code>* GetUnitOverCrossHair()</code>
- <code>BattleEngine.h:111 GetUnitOverCrossHairRegardlessOfRange</code> — <code>* GetUnitOverCrossHairRegardlessOfRange()</code>
- <code>BattleEngine.h:117 GetAutoAimTarget</code> — <code>* GetAutoAimTarget()</code>
- <code>BattleEngine.h:120 TrackingActive</code> — <code>TrackingActive()</code>
- <code>BattleEngine.h:125 GetMaxVelocity</code> — <code>GetMaxVelocity()</code>
- <code>BattleEngine.h:127 SetThingType</code> — <code>SetThingType(ULONG t)</code>
- <code>BattleEngine.h:161 GetLockList</code> — <code>&amp; GetLockList()</code>
- <code>BattleEngine.h:162 GetFiredLockList</code> — <code>&amp; GetFiredLockList()</code>
- <code>BattleEngine.h:170 GetState</code> — <code>GetState()</code>
- <code>BattleEngine.h:171 GetYawVel</code> — <code>&amp; GetYawVel()</code>
- <code>BattleEngine.h:172 GetRollVel</code> — <code>&amp;    GetRollVel()</code>
- <code>BattleEngine.h:173 GetPitchVel</code> — <code>&amp;    GetPitchVel()</code>
- <code>BattleEngine.h:175 GetLastDamageTime</code> — <code>&amp;    GetLastDamageTime()</code>
- <code>BattleEngine.h:181 GetIsPoweredUp</code> — <code>GetIsPoweredUp()</code>
- <code>BattleEngine.h:183 GetCockpit</code> — <code>* GetCockpit()</code>
- <code>BattleEngine.h:184 GetWalkerPart</code> — <code>* GetWalkerPart()</code>
- <code>BattleEngine.h:185 GetJetPart</code> — <code>* GetJetPart()</code>
- <code>BattleEngine.h:187 BounceFactor</code> — <code>BounceFactor()</code>
- <code>BattleEngine.h:193 GetTransformStartTime</code> — <code>GetTransformStartTime()</code>
- <code>BattleEngine.h:195 GetRadarWarningReceiver</code> — <code>*GetRadarWarningReceiver()</code>
- <code>BattleEngine.h:198 ResetTarget</code> — <code>ResetTarget()</code>
- <code>BattleEngine.h:210 GetWeaponOverheatedTime</code> — <code>GetWeaponOverheatedTime()</code>
- <code>BattleEngine.h:226 GetConfiguration</code> — <code>*GetConfiguration()</code>
- <code>BattleEngine.h:227 GetConfigurationName</code> — <code>* GetConfigurationName()</code>
- <code>BattleEngine.h:229 SetPlayer</code> — <code>SetPlayer(class CPlayer *player)</code>
- <code>BattleEngine.h:234 SetInfinateEnergy</code> — <code>SetInfinateEnergy(BOOL val)</code>
- <code>BattleEngine.h:238 GetSoundMaterial</code> — <code>GetSoundMaterial()</code>
- <code>BattleEngine.h:250 IsAThreat</code> — <code>IsAThreat()</code>
- <code>BattleEngine.h:252 GetPlayer</code> — <code>*GetPlayer()</code>
- <code>BattleEngine.h:257 GetChangedWeaponTime</code> — <code>GetChangedWeaponTime()</code>
- <code>BattleEngine.h:260 GetLowEnergyStartTime</code> — <code>GetLowEnergyStartTime()</code>
- <code>BattleEngine.h:261 GetLowArmourStartTime</code> — <code>GetLowArmourStartTime()</code>
- <code>BattleEngine.h:262 GetDangerStartTime</code> — <code>GetDangerStartTime()</code>
- <code>BattleEngine.h:265 IsStalling</code> — <code>IsStalling()</code>
- <code>BattleEngine.h:266 GetStallTime</code> — <code>GetStallTime()</code>
- <code>BattleEngine.h:267 GetAugmentedTime</code> — <code>GetAugmentedTime()</code>
- <code>BattleEngine.h:274 GetStealth</code> — <code>GetStealth()</code>
- <code>BattleEngine.h:276 GetCanBeImpostered</code> — <code>GetCanBeImpostered()</code>
- <code>BattleEngine.h:279 GetAugActiveTime</code> — <code>GetAugActiveTime()</code>
- <code>BattleEngine.h:280 GetAugValue</code> — <code>GetAugValue()</code>
- <code>BattleEngine.h:281 IsAugActive</code> — <code>IsAugActive()</code>
- <code>BattleEngine.h:310 GetAmmoDepletedTime</code> — <code>GetAmmoDepletedTime()</code>
- <code>BattleEngine.h:314 PlayIncommingMissileSound</code> — <code>PlayIncommingMissileSound()</code>
- <code>BattleEngine.h:324 GetDamageFlashList</code> — <code>* GetDamageFlashList()</code>
- <code>BattleEngineConfigurations.h:26 UBattleEngineConfigurations::CountConfigurations</code> — <code>CountConfigurations()</code>
- <code>BattleEngineDataManager.h:270 UBattleEngineDataManager::CountConfigurations</code> — <code>CountConfigurations()</code>
- <code>BattleEngineJetPart.h:37 CBattleEngineJetPart::GetFlightModel</code> — <code>GetFlightModel()</code>
- <code>BattleEngineJetPart.h:38 CBattleEngineJetPart::SetFlightModel</code> — <code>SetFlightModel(EJetFlightModel nm)</code>
- <code>BattleEngineJetPart.h:77 CBattleEngineJetPart::DoingLoop</code> — <code>DoingLoop()</code>
- <code>BattleEngineJetPart.h:78 CBattleEngineJetPart::DoingRoll</code> — <code>DoingRoll()</code>
- <code>BattleEngineJetPart.h:80 CBattleEngineJetPart::GetThrusterValue</code> — <code>GetThrusterValue()</code>
- <code>BattleEngineWalkerPart.h:37 CBattleEngineWalkerPart::GetCurrentWalkCycle</code> — <code>GetCurrentWalkCycle()</code>
- <code>BattleEngineWalkerPart.h:38 CBattleEngineWalkerPart::GetOldWalkCycle</code> — <code>GetOldWalkCycle()</code>
- <code>BattleEngineWalkerPart.h:48 CBattleEngineWalkerPart::GetPrimaryWeapon</code> — <code>* GetPrimaryWeapon()</code>
- <code>BattleEngineWalkerPart.h:49 CBattleEngineWalkerPart::GetAugWeapon</code> — <code>* GetAugWeapon()</code>
- <code>BattleEngineWalkerPart.h:74 CBattleEngineWalkerPart::GetDashCount</code> — <code>GetDashCount()</code>
- <code>Camera.cpp:344 CPanCamera::CPanCamera</code> — <code>CPanCamera::CPanCamera(CThing* for_thing, CBSpline* curve, float length)</code>
- <code>Camera.cpp:717 CControllableCamera::CControllableCamera</code> — <code>CControllableCamera::CControllableCamera(FVector pos, FMatrix orientation)</code>
- <code>Camera.h:24 CCamera::GetOldPos</code> — <code>GetOldPos()</code>
- <code>Camera.h:25 CCamera::GetOldOrientation</code> — <code>GetOldOrientation()</code>
- <code>Camera.h:27 CCamera::GetOldZoom</code> — <code>GetOldZoom()</code>
- <code>Camera.h:30 CCamera::~dtor</code> — <code>~CCamera()</code>
- <code>Camera.h:43 CThingCamera::CThingCamera</code> — <code>CThingCamera(CThing* for_thing)</code>
- <code>Camera.h:51 CThingCamera::GetThing</code> — <code>* GetThing()</code>
- <code>Camera.h:68 CThing3rdPersonCamera::GetIsThingCamera</code> — <code>* GetIsThingCamera()</code>
- <code>Camera.h:72 CThing3rdPersonCamera::GetThing</code> — <code>* GetThing()</code>
- <code>Camera.h:126 CPanCamera::GetZoom</code> — <code>GetZoom()</code>
- <code>Camera.h:127 CPanCamera::GetShowHUD</code> — <code>GetShowHUD()</code>
- <code>Camera.h:176 CControllableCamera::GetPos</code> — <code>GetPos()</code>
- <code>Camera.h:177 CControllableCamera::GetOrientation</code> — <code>GetOrientation()</code>
- <code>Camera.h:178 CControllableCamera::GetZoom</code> — <code>GetZoom()</code>
- <code>Camera.h:179 CControllableCamera::GetShowHUD</code> — <code>GetShowHUD()</code>
- <code>Camera.h:180 CControllableCamera::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>Camera.h:181 CControllableCamera::GetControlType</code> — <code>GetControlType()</code>
- <code>Camera.h:184 CControllableCamera::GetOldPos</code> — <code>GetOldPos()</code>
- <code>Camera.h:185 CControllableCamera::GetOldOrientation</code> — <code>GetOldOrientation()</code>
- <code>Camera.h:189 CControllableCamera::UpdateFrameCount</code> — <code>UpdateFrameCount()</code>
- <code>Camera.h:210 CGenericCamera::CGenericCamera</code> — <code>CGenericCamera()</code>
- <code>Camera.h:211 CGenericCamera::GetPos</code> — <code>GetPos()</code>
- <code>Camera.h:212 CGenericCamera::GetOrientation</code> — <code>GetOrientation()</code>
- <code>Camera.h:213 CGenericCamera::GetZoom</code> — <code>GetZoom()</code>
- <code>Camera.h:214 CGenericCamera::GetShowHUD</code> — <code>GetShowHUD()</code>
- <code>Camera.h:226 CInterpolatedCamera::GetPos</code> — <code>GetPos()</code>
- <code>Camera.h:227 CInterpolatedCamera::GetOrientation</code> — <code>GetOrientation()</code>
- <code>Camera.h:228 CInterpolatedCamera::GetZoom</code> — <code>GetZoom()</code>
- <code>Camera.h:229 CInterpolatedCamera::GetShowHUD</code> — <code>GetShowHUD()</code>
- <code>Career.h:32 CGrade::CGrade</code> — <code>CGrade(char g)</code>
- <code>Career.h:33 CGrade::CGrade</code> — <code>CGrade(WCHAR g)</code>
- <code>Career.h:35 CGrade::operator&gt;=</code> — <code>operator &gt;= (const CGrade right) const</code>
- <code>Career.h:36 CGrade::operator==</code> — <code>operator == (const CGrade right) const</code>
- <code>Career.h:53 CGoodie::CGoodie</code> — <code>CGoodie()</code>
- <code>Career.h:69 CCareerNodeLink::CCareerNodeLink</code> — <code>CCareerNodeLink()</code>
- <code>Career.h:129 CCareer::Load</code> — <code>Load(char *source, bool suggest_next_level)</code>
- <code>Career.h:133 CCareer::SizeOfSaveGame</code> — <code>SizeOfSaveGame()</code>
- <code>Career.h:138 CCareer::GetNode</code> — <code>* GetNode(int num)</code>
- <code>Career.h:139 CCareer::GetLink</code> — <code>* GetLink(int num)</code>
- <code>Career.h:140 CCareer::GetGoodieState</code> — <code>GetGoodieState(int goodie_num)</code>
- <code>Career.h:141 CCareer::SetGoodieState</code> — <code>SetGoodieState(int goodie_num, EGoodieState state)</code>
- <code>Career.h:153 CCareer::InProgress</code> — <code>InProgress()</code>
- <code>Career.h:154 CCareer::SetInProgress</code> — <code>SetInProgress()</code>
- <code>Career.h:156 CCareer::GetSlots</code> — <code>&amp; GetSlots()</code>
- <code>Career.h:161 CCareer::GetIsGod</code> — <code>GetIsGod(int player)</code>
- <code>Career.h:162 CCareer::SetIsGod</code> — <code>SetIsGod(int player, BOOL val)</code>
- <code>Career.h:166 CCareer::GetSoundVolume</code> — <code>GetSoundVolume()</code>
- <code>Career.h:167 CCareer::SetSoundVolume</code> — <code>SetSoundVolume(float val)</code>
- <code>Career.h:169 CCareer::GetMusicVolume</code> — <code>GetMusicVolume()</code>
- <code>Career.h:170 CCareer::SetMusicVolume</code> — <code>SetMusicVolume(float val)</code>
- <code>Career.h:172 CCareer::GetControllerConfigurationNum</code> — <code>GetControllerConfigurationNum(int player)</code>
- <code>Career.h:173 CCareer::SetControllerConfigurationNum</code> — <code>SetControllerConfigurationNum(int player, int val)</code>
- <code>Career.h:176 CCareer::GetInvertYAxis</code> — <code>GetInvertYAxis(int player)</code>
- <code>Career.h:177 CCareer::SetInvertYAxis</code> — <code>SetInvertYAxis(int player, BOOL val)</code>
- <code>Career.h:178 CCareer::GetVibration</code> — <code>GetVibration(int player)</code>
- <code>Career.h:179 CCareer::SetVibration</code> — <code>SetVibration(int player, BOOL val)</code>
- <code>chunker.h:30 CChunker::WhereAmI</code> — <code>WhereAmI()</code>
- <code>chunker.h:48 CChunkReader::GetSize</code> — <code>GetSize()</code>
- <code>chunker.h:50 CChunkReader::GetMemBuffer</code> — <code>*GetMemBuffer()</code>
- <code>CLIParams.h:8 CCLIParams::~dtor</code> — <code>~CCLIParams()</code>
- <code>Controller.h:194 CController::SetConfigurationNum</code> — <code>SetConfigurationNum(int num)</code>
- <code>Controller.h:195 CController::GetConfigurationNum</code> — <code>GetConfigurationNum()</code>
- <code>Controller.h:197 CController::GetReverseLookYAxis</code> — <code>GetReverseLookYAxis()</code>
- <code>Controller.h:202 CController::IsPresent</code> — <code>IsPresent()</code>
- <code>Controller.h:258 CController::GetPadNumber</code> — <code>GetPadNumber()</code>
- <code>d3dapp.h:180 CD3DApplication::ConfirmDevice</code> — <code>ConfirmDevice(D3DCAPS8*,DWORD,D3DFORMAT)</code>
- <code>d3dapp.h:181 CD3DApplication::OneTimeSceneInit</code> — <code>OneTimeSceneInit()</code>
- <code>d3dapp.h:182 CD3DApplication::InitDeviceObjects</code> — <code>InitDeviceObjects()</code>
- <code>d3dapp.h:183 CD3DApplication::RestoreDeviceObjects</code> — <code>RestoreDeviceObjects()</code>
- <code>d3dapp.h:184 CD3DApplication::FrameMove</code> — <code>FrameMove()</code>
- <code>d3dapp.h:185 CD3DApplication::Render</code> — <code>Render()</code>
- <code>d3dapp.h:186 CD3DApplication::InvalidateDeviceObjects</code> — <code>InvalidateDeviceObjects()</code>
- <code>d3dapp.h:187 CD3DApplication::DeleteDeviceObjects</code> — <code>DeleteDeviceObjects()</code>
- <code>d3dapp.h:188 CD3DApplication::FinalCleanup</code> — <code>FinalCleanup()</code>
- <code>d3dapp.h:200 CD3DApplication::GetHWnd</code> — <code>GetHWnd()</code>
- <code>d3dapp.h:202 CD3DApplication::ForceToWindow</code> — <code>ForceToWindow()</code>
- <code>DXEngine.cpp:1166 Vert::FVF</code> — <code>FVF()</code>
- <code>DXEngine.h:60 CDXEngine::GetScreenTexture</code> — <code>*GetScreenTexture()</code>
- <code>DXEngine.h:61 CDXEngine::TriggerScreenCapture</code> — <code>TriggerScreenCapture()</code>
- <code>DXEngine.h:62 CDXEngine::TriggerPartialScreenCapture</code> — <code>TriggerPartialScreenCapture(int top,int bottom)</code>
- <code>DXEngine.h:69 CDXEngine::GetOutlineTexture</code> — <code>* GetOutlineTexture()</code>
- <code>DXEngine.h:70 CDXEngine::GetOpaqueTexture</code> — <code>* GetOpaqueTexture()</code>
- <code>DXEngine.h:83 CDXEngine::SetDefaultMaterial</code> — <code>SetDefaultMaterial()</code>
- <code>DXGame.h:15 CDXGame::SetBaseTime</code> — <code>SetBaseTime(float t)</code>
- <code>DXGame.h:16 CDXGame::SetFrameTime</code> — <code>SetFrameTime(float t)</code>
- <code>DXMemBuffer.h:41 CDXMemBuffer::IsMoreData</code> — <code>IsMoreData()</code>
- <code>DXMemBuffer.h:45 CDXMemBuffer::GetData</code> — <code>*GetData()</code>
- <code>DXMemBuffer.h:51 CDXMemBuffer::WhereAmI</code> — <code>WhereAmI()</code>
- <code>DXMemoryManager.cpp:65 CDXMemoryManager::Init</code> — <code>CDXMemoryManager::Init(UINT aSize, UINT aTexDataSize, UINT aVBDataSize)</code>
- <code>DXMemoryManager.h:34 CDXMemoryManager::SetMerge</code> — <code>SetMerge( BOOL aMerge )</code>
- <code>DXMemoryManager.h:69 CDXMemoryManager::GetDefaultHeapSize</code> — <code>GetDefaultHeapSize()</code>
- <code>DXMemoryManager.h:70 CDXMemoryManager::GetDefaultUsedSize</code> — <code>GetDefaultUsedSize()</code>
- <code>DXMemoryManager.h:71 CDXMemoryManager::GetDefaultPeakSize</code> — <code>GetDefaultPeakSize()</code>
- <code>DXMemoryManager.h:73 CDXMemoryManager::GetTexDataHeapSize</code> — <code>GetTexDataHeapSize()</code>
- <code>DXMemoryManager.h:74 CDXMemoryManager::GetTexDataUsedSize</code> — <code>GetTexDataUsedSize()</code>
- <code>DXMemoryManager.h:75 CDXMemoryManager::GetTexDataPeakSize</code> — <code>GetTexDataPeakSize()</code>
- <code>DXMemoryManager.h:76 CDXMemoryManager::GetVBDataHeapSize</code> — <code>GetVBDataHeapSize()</code>
- <code>DXMemoryManager.h:77 CDXMemoryManager::GetVBDataUsedSize</code> — <code>GetVBDataUsedSize()</code>
- <code>DXMemoryManager.h:78 CDXMemoryManager::GetVBDataPeakSize</code> — <code>GetVBDataPeakSize()</code>
- <code>DXMemoryManager.h:82 CDXMemoryManager::GetDefaultHeap</code> — <code>*   GetDefaultHeap()</code>
- <code>DXMemoryManager.h:83 CDXMemoryManager::GetThingHeap</code> — <code>*   GetThingHeap()</code>
- <code>EditorD3DApp.h:178 CEditorD3DApp::ConfirmDevice</code> — <code>ConfirmDevice(D3DCAPS8*,DWORD,D3DFORMAT)</code>
- <code>EditorD3DApp.h:179 CEditorD3DApp::OneTimeSceneInit</code> — <code>OneTimeSceneInit()</code>
- <code>EditorD3DApp.h:180 CEditorD3DApp::InitDeviceObjects</code> — <code>InitDeviceObjects()</code>
- <code>EditorD3DApp.h:181 CEditorD3DApp::RestoreDeviceObjects</code> — <code>RestoreDeviceObjects()</code>
- <code>EditorD3DApp.h:182 CEditorD3DApp::FrameMove</code> — <code>FrameMove()</code>
- <code>EditorD3DApp.h:183 CEditorD3DApp::Render</code> — <code>Render()</code>
- <code>EditorD3DApp.h:184 CEditorD3DApp::InvalidateDeviceObjects</code> — <code>InvalidateDeviceObjects()</code>
- <code>EditorD3DApp.h:185 CEditorD3DApp::DeleteDeviceObjects</code> — <code>DeleteDeviceObjects()</code>
- <code>EditorD3DApp.h:186 CEditorD3DApp::FinalCleanup</code> — <code>FinalCleanup()</code>
- <code>EditorD3DApp.h:198 CEditorD3DApp::GetHWnd</code> — <code>GetHWnd()</code>
- <code>EditorD3DApp.h:199 CEditorD3DApp::SetHWnd</code> — <code>SetHWnd(HWND hwnd)</code>
- <code>engine.h:83 CEngine::ShutdownRestartLoop</code> — <code>ShutdownRestartLoop()</code>
- <code>engine.h:116 CEngine::GetDefaultMesh</code> — <code>*GetDefaultMesh()</code>
- <code>engine.h:117 CEngine::GetGlobalMesh</code> — <code>*GetGlobalMesh(SINT num)</code>
- <code>engine.h:119 CEngine::GetCamera</code> — <code>*GetCamera()</code>
- <code>engine.h:120 CEngine::SetCamera</code> — <code>SetCamera(CCamera *c)</code>
- <code>engine.h:122 CEngine::ToggleDebugDraw</code> — <code>ToggleDebugDraw(ULONG num)</code>
- <code>engine.h:125 CEngine::GetHitEffectTexture</code> — <code>*GetHitEffectTexture()</code>
- <code>engine.h:126 CEngine::GetCloakTexture</code> — <code>*GetCloakTexture()</code>
- <code>engine.h:128 CEngine::ToggleParticles</code> — <code>ToggleParticles()</code>
- <code>engine.h:129 CEngine::DebugNoParticles</code> — <code>DebugNoParticles()</code>
- <code>engine.h:131 CEngine::GetDrawDebugStuff</code> — <code>GetDrawDebugStuff()</code>
- <code>engine.h:135 CEngine::GetNearZ</code> — <code>GetNearZ()</code>
- <code>engine.h:136 CEngine::GetFarZ</code> — <code>GetFarZ()</code>
- <code>engine.h:137 CEngine::SetNearZ</code> — <code>SetNearZ( const float aNearZ )</code>
- <code>engine.h:138 CEngine::SetFarZ</code> — <code>SetFarZ( const float aFarZ )</code>
- <code>engine.h:140 CEngine::SetCurrentViewport</code> — <code>SetCurrentViewport(CViewport *vp)</code>
- <code>engine.h:141 CEngine::GetCurrentViewport</code> — <code>GetCurrentViewport()</code>
- <code>engine.h:142 CEngine::GetCurrentViewportWidth</code> — <code>GetCurrentViewportWidth()</code>
- <code>engine.h:143 CEngine::GetCurrentViewportHeight</code> — <code>GetCurrentViewportHeight()</code>
- <code>engine.h:144 CEngine::GetCurrentViewportX</code> — <code>GetCurrentViewportX()</code>
- <code>engine.h:145 CEngine::GetCurrentViewportY</code> — <code>GetCurrentViewportY()</code>
- <code>engine.h:147 CEngine::GetCameraForViewpoint</code> — <code>*GetCameraForViewpoint(int n)</code>
- <code>engine.h:148 CEngine::GetPlayerForViewpoint</code> — <code>*GetPlayerForViewpoint(int n)</code>
- <code>engine.h:149 CEngine::GetViewportForViewpoint</code> — <code>*GetViewportForViewpoint(int n)</code>
- <code>engine.h:150 CEngine::GetNumViewpoints</code> — <code>GetNumViewpoints()</code>
- <code>engine.h:158 CEngine::GetHitEffectFactorR</code> — <code>GetHitEffectFactorR()</code>
- <code>engine.h:159 CEngine::GetHitEffectFactorG</code> — <code>GetHitEffectFactorG()</code>
- <code>engine.h:160 CEngine::GetHitEffectFactorB</code> — <code>GetHitEffectFactorB()</code>
- <code>engine.h:162 CEngine::GetLandscape</code> — <code>*GetLandscape()</code>
- <code>engine.h:171 CEngine::GetMapTex</code> — <code>* GetMapTex()</code>
- <code>engine.h:180 CEngine::AddDamage</code> — <code>AddDamage(float x, float y, int size)</code>
- <code>engine.h:181 CEngine::RemoveDamage</code> — <code>RemoveDamage(float x, float y, int size)</code>
- <code>engine.h:182 CEngine::LockCurrentDamage</code> — <code>LockCurrentDamage()</code>
- <code>engine.h:198 CEngine::ToggleHudAlphaMode</code> — <code>ToggleHudAlphaMode()</code>
- <code>engine.h:199 CEngine::HudAditive</code> — <code>HudAditive()</code>
- <code>engine.h:201 CEngine::GetLights</code> — <code>*GetLights()</code>
- <code>engine.h:205 CEngine::GetHilightTexture</code> — <code>* GetHilightTexture()</code>
- <code>engine.h:213 CEngine::LandscapeNavDisplay</code> — <code>LandscapeNavDisplay(BOOL onoff)</code>
- <code>engine.h:214 CEngine::GetNavDisplayMODE</code> — <code>GetNavDisplayMODE()</code>
- <code>event.h:16 CEvent::CEvent</code> — <code>CEvent()</code>
- <code>event.h:18 CEvent::SetNum</code> — <code>SetNum(const int event)</code>
- <code>event.h:19 CEvent::GetEventNum</code> — <code>GetEventNum()</code>
- <code>event.h:20 CEvent::SetToCall</code> — <code>SetToCall(CMonitor* to_call)</code>
- <code>event.h:21 CEvent::GetToCall</code> — <code>*  GetToCall()</code>
- <code>eventmanager.h:58 CEventManager::TotalEvents</code> — <code>TotalEvents()</code>
- <code>eventmanager.h:59 CEventManager::GetNumEventsProcessedInLastUpdate</code> — <code>GetNumEventsProcessedInLastUpdate()</code>
- <code>eventmanager.h:60 CEventManager::GetTime</code> — <code>&amp; GetTime()</code>
- <code>eventmanager.h:61 CEventManager::GetCurrentEventProcessNum</code> — <code>GetCurrentEventProcessNum()</code>
- <code>eventmanager.h:62 CEventManager::GetFrameCount</code> — <code>GetFrameCount()</code>
- <code>eventmanager.h:68 CEventManager::IsValid</code> — <code>IsValid()</code>
- <code>FEPGoodies.h:35 CGoodieData::GetNumber</code> — <code>GetNumber() const</code>
- <code>FEPGoodies.h:36 CGoodieData::GetNumber2</code> — <code>GetNumber2() const</code>
- <code>FrontEnd.cpp:32 CFrontEnd::CFrontEnd</code> — <code>CFrontEnd::CFrontEnd(void)</code>
- <code>Frontend.h:115 CFrontEnd::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>Frontend.h:116 CFrontEnd::GetControlType</code> — <code>GetControlType()</code>
- <code>Frontend.h:119 CFrontEnd::GetCounter</code> — <code>GetCounter()</code>
- <code>Frontend.h:120 CFrontEnd::SetQuit</code> — <code>SetQuit(SINT val)</code>
- <code>Frontend.h:123 CFrontEnd::GetCurrentPage</code> — <code>GetCurrentPage()</code>
- <code>Frontend.h:124 CFrontEnd::GetTransitionTo</code> — <code>GetTransitionTo()</code>
- <code>Frontend.h:125 CFrontEnd::GetTransitionFrom</code> — <code>GetTransitionFrom()</code>
- <code>Frontend.h:127 CFrontEnd::GetCommonPage</code> — <code>*GetCommonPage()</code>
- <code>Frontend.h:152 CFrontEnd::GetSaveMode</code> — <code>GetSaveMode()</code>
- <code>Frontend.h:162 CFrontEnd::GetAutoSave</code> — <code>GetAutoSave()</code>
- <code>Frontend.h:163 CFrontEnd::SetAutoSave</code> — <code>SetAutoSave(AutoSaveMode as)</code>
- <code>Frontend.h:165 CFrontEnd::GetMemoryCardNumber</code> — <code>GetMemoryCardNumber()</code>
- <code>Frontend.h:166 CFrontEnd::SetMemoryCardNumber</code> — <code>SetMemoryCardNumber(int num)</code>
- <code>Frontend.h:168 CFrontEnd::SetSaveMode</code> — <code>SetSaveMode(BOOL mode)</code>
- <code>Frontend.h:169 CFrontEnd::SetSuccessFEP</code> — <code>SetSuccessFEP(EFrontEndPage page, UINT time)</code>
- <code>Frontend.h:170 CFrontEnd::GetSuccessPage</code> — <code>GetSuccessPage()</code>
- <code>Frontend.h:171 CFrontEnd::GetSuccessTransTime</code> — <code>GetSuccessTransTime()</code>
- <code>Frontend.h:173 CFrontEnd::AllLevelsCheatActive</code> — <code>AllLevelsCheatActive()</code>
- <code>Frontend.h:258 CFrontEnd::GetController</code> — <code>* GetController(int which)</code>
- <code>Frontend.h:260 CFrontEnd::GetTextSet</code> — <code>*GetTextSet(SINT n)</code>
- <code>Frontend.h:263 CFrontEnd::ClearFirstRun</code> — <code>ClearFirstRun()</code>
- <code>game.cpp:1253 CWaitForStart::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>game.cpp:1254 CWaitForStart::GetControlType</code> — <code>GetControlType()</code>
- <code>game.cpp:4089 CGameCreditControlHandler::CGameCreditControlHandler</code> — <code>CGameCreditControlHandler()</code>
- <code>game.cpp:4091 CGameCreditControlHandler::ResetQuitFlag</code> — <code>ResetQuitFlag()</code>
- <code>game.cpp:4092 CGameCreditControlHandler::WantToQuit</code> — <code>WantToQuit()</code>
- <code>game.cpp:4099 CGameCreditControlHandler::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>game.cpp:4100 CGameCreditControlHandler::GetControlType</code> — <code>GetControlType()</code>
- <code>game.h:121 CGame::ToggleControlMethod</code> — <code>ToggleControlMethod()</code>
- <code>game.h:126 CGame::SetQuit</code> — <code>SetQuit(EQuitType quit)</code>
- <code>game.h:129 CGame::GetForsetiFearGrid</code> — <code>* GetForsetiFearGrid()</code>
- <code>game.h:130 CGame::GetMuspellFearGrid</code> — <code>* GetMuspellFearGrid()</code>
- <code>game.h:136 CGame::Random</code> — <code>Random()</code>
- <code>game.h:137 CGame::FloatRandom</code> — <code>FloatRandom()</code>
- <code>game.h:140 CGame::GetPlayer</code> — <code>* GetPlayer(SINT no)</code>
- <code>game.h:141 CGame::GetCurrentCamera</code> — <code>* GetCurrentCamera(int number)</code>
- <code>game.h:145 CGame::GetCurrentLevel</code> — <code>GetCurrentLevel()</code>
- <code>game.h:152 CGame::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>game.h:153 CGame::GetControlType</code> — <code>GetControlType()</code>
- <code>game.h:156 CGame::IsPaused</code> — <code>IsPaused()</code>
- <code>game.h:157 CGame::GetMessageBox</code> — <code>* GetMessageBox()</code>
- <code>game.h:158 CGame::GetMessageLog</code> — <code>* GetMessageLog()</code>
- <code>game.h:159 CGame::GetHelpTextDisplay</code> — <code>* GetHelpTextDisplay()</code>
- <code>game.h:160 CGame::GetLevelBriefingLog</code> — <code>* GetLevelBriefingLog()</code>
- <code>game.h:161 CGame::GetPauseMenu</code> — <code>* GetPauseMenu()</code>
- <code>game.h:166 CGame::GetNPlayers</code> — <code>GetNPlayers()</code>
- <code>game.h:172 CGame::GetGameState</code> — <code>GetGameState()</code>
- <code>game.h:173 CGame::IsFreeCameraOn</code> — <code>IsFreeCameraOn(int player)</code>
- <code>game.h:174 CGame::IsGameFinished</code> — <code>IsGameFinished()</code>
- <code>game.h:178 CGame::GetRenderFrameNumber</code> — <code>GetRenderFrameNumber()</code>
- <code>game.h:179 CGame::SetPrimaryObjectiveComplete</code> — <code>SetPrimaryObjectiveComplete(int num, int string_id)</code>
- <code>game.h:180 CGame::SetSecondaryObjectiveComplete</code> — <code>SetSecondaryObjectiveComplete(int num, int string_id)</code>
- <code>game.h:181 CGame::SetPrimaryObjectiveFailed</code> — <code>SetPrimaryObjectiveFailed(int num, int string_id)</code>
- <code>game.h:182 CGame::SetSecondaryObjectiveFailed</code> — <code>SetSecondaryObjectiveFailed(int num, int string_id)</code>
- <code>game.h:184 CGame::GetPrimaryObjective</code> — <code>* GetPrimaryObjective(int num)</code>
- <code>game.h:185 CGame::GetSecondaryObjective</code> — <code>* GetSecondaryObjective(int num)</code>
- <code>game.h:186 CGame::GetMaxPrimaryObjectives</code> — <code>GetMaxPrimaryObjectives()</code>
- <code>game.h:187 CGame::GetMaxSecondaryObjectives</code> — <code>GetMaxSecondaryObjectives()</code>
- <code>game.h:191 CGame::SetPanTime</code> — <code>SetPanTime(float time)</code>
- <code>game.h:192 CGame::SetPreRunTime</code> — <code>SetPreRunTime(float time)</code>
- <code>game.h:194 CGame::GetPreRunTime</code> — <code>GetPreRunTime()</code>
- <code>game.h:195 CGame::GetPanTime</code> — <code>GetPanTime()</code>
- <code>game.h:197 CGame::SetSGradeScore</code> — <code>SetSGradeScore(SINT score)</code>
- <code>game.h:198 CGame::SetDGradeScore</code> — <code>SetDGradeScore(SINT score)</code>
- <code>game.h:200 CGame::SetTimeLimit</code> — <code>SetTimeLimit(float time)</code>
- <code>game.h:201 CGame::SetFullScoreTime</code> — <code>SetFullScoreTime(float time)</code>
- <code>game.h:202 CGame::SetPercentageScoreTime</code> — <code>SetPercentageScoreTime(float time)</code>
- <code>game.h:203 CGame::SetScorePercentage</code> — <code>SetScorePercentage(float percentage)</code>
- <code>game.h:210 CGame::IncScore</code> — <code>IncScore(SINT inScore)</code>
- <code>game.h:211 CGame::GetAllowedAutoAim</code> — <code>GetAllowedAutoAim()</code>
- <code>game.h:212 CGame::SetAllowedAutoAim</code> — <code>SetAllowedAutoAim(BOOL val)</code>
- <code>game.h:215 CGame::InvertSides</code> — <code>InvertSides()</code>
- <code>game.h:222 CGame::GetSlots</code> — <code>&amp; GetSlots()</code>
- <code>game.h:226 CGame::GetLevelStartTime</code> — <code>GetLevelStartTime()</code>
- <code>game.h:227 CGame::SetLevelStartTime</code> — <code>SetLevelStartTime(float inTime)</code>
- <code>game.h:228 CGame::IsRestarting</code> — <code>IsRestarting()</code>
- <code>game.h:264 CGame::GetRenderFrameLength</code> — <code>GetRenderFrameLength()</code>
- <code>game.h:265 CGame::GetCurrentInterleavedScreen</code> — <code>GetCurrentInterleavedScreen()</code>
- <code>game.h:266 CGame::IsFirstFrame</code> — <code>IsFirstFrame()</code>
- <code>game.h:268 CGame::GetFrontEndSettings</code> — <code>* GetFrontEndSettings()</code>
- <code>game.h:269 CGame::GetCurrentlyRunningLevelNum</code> — <code>GetCurrentlyRunningLevelNum()</code>
- <code>game.h:270 CGame::GetFrameTime</code> — <code>GetFrameTime()</code>
- <code>game.h:271 CGame::GetBaseTime</code> — <code>GetBaseTime()</code>
- <code>InitThing.cpp:68 CInitThing::CInitThing</code> — <code>CInitThing::CInitThing()</code>
- <code>InitThing.h:94 CInitCSThing::CInitCSThing</code> — <code>CInitCSThing()</code>
- <code>InitThing.h:417 CSpawnerInitThing::CSpawnerInitThing</code> — <code>CSpawnerInitThing()</code>
- <code>InitThing.h:943 CAnimalInitThing::CAnimalInitThing</code> — <code>CAnimalInitThing()</code>
- <code>ltshell.cpp:774 PCLTShell::PCLTShell</code> — <code>PCLTShell::PCLTShell()</code>
- <code>ltshell.h:125 PCLTShell::GetMouseX</code> — <code>GetMouseX()</code>
- <code>ltshell.h:126 PCLTShell::GetMouseY</code> — <code>GetMouseY()</code>
- <code>ltshell.h:127 PCLTShell::GetMouseLButton</code> — <code>GetMouseLButton()</code>
- <code>ltshell.h:128 PCLTShell::GetMouseMButton</code> — <code>GetMouseMButton()</code>
- <code>ltshell.h:129 PCLTShell::GetMouseRButton</code> — <code>GetMouseRButton()</code>
- <code>ltshell.h:130 PCLTShell::ClearD3DErrorCount</code> — <code>ClearD3DErrorCount()</code>
- <code>ltshell.h:139 PCLTShell::MsgInfo</code> — <code>MsgInfo()</code>
- <code>ltshell.h:140 PCLTShell::WantsToQuit</code> — <code>WantsToQuit()</code>
- <code>ltshell.h:141 PCLTShell::IWantToQuit</code> — <code>IWantToQuit()</code>
- <code>ltshell.h:151 PCLTShell::SmallTexturesDisabled</code> — <code>SmallTexturesDisabled()</code>
- <code>ltshell.h:158 PCLTShell::TextureCompressionDisabled</code> — <code>TextureCompressionDisabled()</code>
- <code>ltshell.h:163 PCLTShell::D3DActive</code> — <code>D3DActive()</code>
- <code>ltshell.h:168 PCLTShell::DeviceForD3DXTextureLoad</code> — <code>DeviceForD3DXTextureLoad()</code>
- <code>ltshell.h:169 PCLTShell::GetDevice</code> — <code>GetDevice()</code>
- <code>ltshell.h:175 PCLTShell::SRS</code> — <code>SRS(D3DRENDERSTATETYPE state, DWORD value)</code>
- <code>ltshell.h:183 PCLTShell::RI_SRS</code> — <code>RI_SRS(D3DRENDERSTATETYPE state, DWORD value)</code>
- <code>ltshell.h:190 PCLTShell::STS</code> — <code>STS(DWORD stage, D3DTEXTURESTAGESTATETYPE type, DWORD val)</code>
- <code>ltshell.h:201 PCLTShell::ForceRS</code> — <code>ForceRS(D3DRENDERSTATETYPE state, DWORD value)</code>
- <code>ltshell.h:202 PCLTShell::ForceTS</code> — <code>ForceTS(DWORD stage, D3DTEXTURESTAGESTATETYPE type, DWORD val)</code>
- <code>ltshell.h:204 PCLTShell::ForceRS</code> — <code>ForceRS(D3DRENDERSTATETYPE state, DWORD value)</code>
- <code>ltshell.h:205 PCLTShell::ForceTS</code> — <code>ForceTS(DWORD stage, D3DTEXTURESTAGESTATETYPE type, DWORD val)</code>
- <code>ltshell.h:208 PCLTShell::SRS_Ret</code> — <code>SRS_Ret(D3DRENDERSTATETYPE state, DWORD value)</code>
- <code>ltshell.h:221 PCLTShell::D3D_SetTexture</code> — <code>D3D_SetTexture(  UINT Name, IDirect3DBaseTexture8* pTexture)</code>
- <code>ltshell.h:222 PCLTShell::D3D_SetVertexShader</code> — <code>D3D_SetVertexShader( DWORD Handle)</code>
- <code>ltshell.h:240 PCLTShell::D3D_CreateCubeTexture</code> — <code>D3D_CreateCubeTexture(  UINT EdgeLength, UINT Levels, DWORD Usage, D3DFORMAT Format, D3DPOOL Pool, IDirect3DCubeTexture8** ppCubeTexture)</code>
- <code>ltshell.h:243 PCLTShell::D3D_ReleaseTexture</code> — <code>D3D_ReleaseTexture(IDirect3DTexture8* pTexture, void *pData)</code>
- <code>ltshell.h:258 PCLTShell::D3D_SetGammaRamp</code> — <code>D3D_SetGammaRamp(DWORD flags,CONST D3DGAMMARAMP *pRamp)</code>
- <code>ltshell.h:259 PCLTShell::D3D_GetGammaRamp</code> — <code>D3D_GetGammaRamp(D3DGAMMARAMP *pRamp)</code>
- <code>ltshell.h:291 PCLTShell::xKeyOn</code> — <code>xKeyOn(int c)</code>
- <code>ltshell.h:292 PCLTShell::xKeyOnce</code> — <code>xKeyOnce(int c)</code>
- <code>ltshell.h:295 PCLTShell::AddDeviceObject</code> — <code>AddDeviceObject(DeviceObject* devob)</code>
- <code>ltshell.h:306 PCLTShell::JoyState</code> — <code>* JoyState(int padnumber)</code>
- <code>ltshell.h:307 PCLTShell::OldJoyState</code> — <code>* OldJoyState(int padnumber)</code>
- <code>ltshell.h:310 PCLTShell::JoyButtonOnce</code> — <code>JoyButtonOnce(int padnumber, int button)</code>
- <code>ltshell.h:314 PCLTShell::JoyButtonOn</code> — <code>JoyButtonOn(int padnumber, int button)</code>
- <code>ltshell.h:317 PCLTShell::JoyButtonRelease</code> — <code>JoyButtonRelease(int padnumber, int button)</code>
- <code>ltshell.h:323 PCLTShell::Running</code> — <code>Running()</code>
- <code>ltshell.h:324 PCLTShell::SetRunning</code> — <code>SetRunning(bool inRunning)</code>
- <code>ltshell.h:326 PCLTShell::GetWindowWidth</code> — <code>GetWindowWidth()</code>
- <code>ltshell.h:327 PCLTShell::GetWindowHeight</code> — <code>GetWindowHeight()</code>
- <code>membuffer.h:15 IMemBuffer::Read</code> — <code>Read(void *data, SINT size)</code>
- <code>membuffer.h:16 IMemBuffer::Write</code> — <code>Write(void *data, SINT size)</code>
- <code>membuffer.h:18 IMemBuffer::DeclareInvalidData</code> — <code>DeclareInvalidData(CThing *t)</code>
- <code>MemoryCard.h:58 CMemoryCard::TooManySavesHere</code> — <code>TooManySavesHere(int card)</code>
- <code>MemoryManager.cpp:81 CMutexGrabber::~dtor</code> — <code>~CMutexGrabber()</code>
- <code>MemoryManager.cpp:304 CMemoryHeap::Init</code> — <code>CMemoryHeap::Init( UINT aSize, UINT tinysize, char *name, BOOL bSupportSmallAllocs)</code>
- <code>MemoryManager.h:223 CMemoryBlock::GetSize</code> — <code>GetSize()</code>
- <code>MemoryManager.h:224 CMemoryBlock::GetMem</code> — <code>* GetMem()</code>
- <code>MemoryManager.h:225 CMemoryBlock::GetType</code> — <code>GetType()</code>
- <code>MemoryManager.h:226 CMemoryBlock::GetBlockSize</code> — <code>GetBlockSize()</code>
- <code>MemoryManager.h:228 CMemoryBlock::GetBlockBelow</code> — <code>* GetBlockBelow()</code>
- <code>MemoryManager.h:230 CMemoryBlock::GetBlock</code> — <code>* GetBlock( void * apMem )</code>
- <code>MemoryManager.h:232 CMemoryBlock::IsUsed</code> — <code>IsUsed()</code>
- <code>MemoryManager.h:233 CMemoryBlock::IsFree</code> — <code>IsFree()</code>
- <code>MemoryManager.h:235 CMemoryBlock::IsBaseSet</code> — <code>IsBaseSet()</code>
- <code>MemoryManager.h:243 CMemoryBlock::IsValid</code> — <code>IsValid()</code>
- <code>MemoryManager.h:278 CMemoryHeap::GetTypeSize</code> — <code>GetTypeSize(EMemoryType type)</code>
- <code>MemoryManager.h:295 CMemoryHeap::GetName</code> — <code>*GetName()</code>
- <code>MemoryManager.h:297 CMemoryHeap::GetSize</code> — <code>GetSize()</code>
- <code>MemoryManager.h:298 CMemoryHeap::GetPeakSize</code> — <code>GetPeakSize()</code>
- <code>MemoryManager.h:299 CMemoryHeap::GetUsedSize</code> — <code>GetUsedSize()</code>
- <code>MemoryManager.h:300 CMemoryHeap::GetFreeSize</code> — <code>GetFreeSize()</code>
- <code>MemoryManager.h:301 CMemoryHeap::GetTotalFreeSize</code> — <code>GetTotalFreeSize()</code>
- <code>MemoryManager.h:324 CMemoryHeap::IsLastBlock</code> — <code>IsLastBlock( CMemoryBlock * apBlock )</code>
- <code>MemoryManager.h:402 CMemoryManager::~dtor</code> — <code>~CMemoryManager()</code>
- <code>Music.h:32 CMusicMenu::GetName</code> — <code>GetName(char *name)</code>
- <code>Music.h:34 CMusicMenu::GetShowSubmenus</code> — <code>GetShowSubmenus()</code>
- <code>Music.h:68 CMusic::GetVolume</code> — <code>GetVolume()</code>
- <code>Music.h:69 CMusic::GetCurrentVolume</code> — <code>GetCurrentVolume()</code>
- <code>Music.h:78 CMusic::DeviceWarnOfStop</code> — <code>DeviceWarnOfStop()</code>
- <code>Music.h:102 CMusic::DeviceUpdateStatus</code> — <code>DeviceUpdateStatus()</code>
- <code>PCController.cpp:143 CPCController::CPCController</code> — <code>CPCController::CPCController(IController* to_control, int padnumber,int configuration, BOOL reverse_look_y_axis)</code>
- <code>PCController.h:21 CPCController::GetJoyButtonOnce</code> — <code>GetJoyButtonOnce(int pad_number, int button)</code>
- <code>PCController.h:22 CPCController::GetJoyButtonOn</code> — <code>GetJoyButtonOn(int pad_number, int button)</code>
- <code>PCController.h:23 CPCController::GetJoyButtonRelease</code> — <code>GetJoyButtonRelease(int pad_number, int button)</code>
- <code>PCController.h:25 CPCController::GetKeyOnce</code> — <code>GetKeyOnce(int pad_number, int key)</code>
- <code>PCController.h:26 CPCController::GetKeyOn</code> — <code>GetKeyOn(int pad_number, int key)</code>
- <code>PCController.h:27 CPCController::DeviceSetVibration</code> — <code>DeviceSetVibration(float)</code>
- <code>PCEngine.h:48 CPCEngine::GetSky</code> — <code>* GetSky()</code>
- <code>PCEngine.h:50 CPCEngine::GetSky</code> — <code>* GetSky()</code>
- <code>PCEngine.h:53 CPCEngine::GetDefaultTexture</code> — <code>*GetDefaultTexture()</code>
- <code>PCEngine.h:55 CPCEngine::GetScreenTexture</code> — <code>*GetScreenTexture()</code>
- <code>PCEngine.h:56 CPCEngine::TriggerScreenCapture</code> — <code>TriggerScreenCapture()</code>
- <code>PCEngine.h:57 CPCEngine::TriggerPartialScreenCapture</code> — <code>TriggerPartialScreenCapture(int top,int bottom)</code>
- <code>PCEngine.h:64 CPCEngine::ToggleHudAlphaMode</code> — <code>ToggleHudAlphaMode()</code>
- <code>PCEngine.h:65 CPCEngine::HudAditive</code> — <code>HudAditive()</code>
- <code>PCEngine.h:67 CPCEngine::GetOutlineTexture</code> — <code>* GetOutlineTexture()</code>
- <code>PCEngine.h:68 CPCEngine::GetOpaqueTexture</code> — <code>* GetOpaqueTexture()</code>
- <code>PCEngine.h:97 CPCEngine::GetWaterTexture</code> — <code>* GetWaterTexture()</code>
- <code>PCGame.h:17 CPCGame::SetBaseTime</code> — <code>SetBaseTime(float t)</code>
- <code>PCGame.h:18 CPCGame::SetFrameTime</code> — <code>SetFrameTime(float t)</code>
- <code>PCMemoryCard.h:15 CPCMemoryCard::IsHDDAvailable</code> — <code>IsHDDAvailable()</code>
- <code>PCMemoryCard.h:17 CPCMemoryCard::GetNumCards</code> — <code>GetNumCards(int *num)</code>
- <code>PCMemoryCard.h:97 CPCMemoryCard::Update</code> — <code>Update()</code>
- <code>PCPlatform.h:103 CPCPlatform::SetGeforce3</code> — <code>SetGeforce3(BOOL f)</code>
- <code>PCPlatform.h:104 CPCPlatform::IsGeforce3</code> — <code>IsGeforce3()</code>
- <code>PCPlatform.h:106 CPCPlatform::SetMemorySize</code> — <code>SetMemorySize(long size)</code>
- <code>PCPlatform.h:107 CPCPlatform::GetMemorySize</code> — <code>GetMemorySize()</code>
- <code>PCPlatform.h:119 CPCPlatform::Font</code> — <code>* Font()</code>
- <code>PCPlatform.h:120 CPCPlatform::DebugFont</code> — <code>* DebugFont()</code>
- <code>PCPlatform.h:121 CPCPlatform::SmallFont</code> — <code>* SmallFont()</code>
- <code>PCPlatform.h:122 CPCPlatform::TitleFont</code> — <code>* TitleFont()</code>
- <code>pcsoundmanager.h:58 CPCSoundManager::LoadSampleFromBuffer</code> — <code>*LoadSampleFromBuffer(CMEMBUFFER *mb,BOOL music)</code>
- <code>pcsoundmanager.h:75 CPCSoundManager::GetAvailableChannels</code> — <code>GetAvailableChannels()</code>
- <code>Player.cpp:24 CPlayer::CPlayer</code> — <code>CPlayer::CPlayer(int number)</code>
- <code>Player.h:65 CPlayer::CanBeControlledWhenInPause</code> — <code>CanBeControlledWhenInPause()</code>
- <code>Player.h:66 CPlayer::GetControlType</code> — <code>GetControlType()</code>
- <code>Player.h:68 CPlayer::GetNumber</code> — <code>GetNumber()</code>
- <code>Player.h:70 CPlayer::GetNumEnemyThingKilled</code> — <code>GetNumEnemyThingKilled(EKilledType type)</code>
- <code>Player.h:71 CPlayer::GetBattleEngine</code> — <code>* GetBattleEngine()</code>
- <code>Player.h:72 CPlayer::IsGod</code> — <code>IsGod()</code>
- <code>Player.h:73 CPlayer::ShouldRenderInternalCockpit</code> — <code>ShouldRenderInternalCockpit()</code>
- <code>Player.h:74 CPlayer::GetIsInFPV</code> — <code>GetIsInFPV()</code>
- <code>Player.h:75 CPlayer::GetPreferredCurrentViewMode</code> — <code>GetPreferredCurrentViewMode()</code>
- <code>Player.h:86 CPlayer::SetStat</code> — <code>SetStat(EPlayerStats s,int v)</code>
- <code>Player.h:87 CPlayer::GetStat</code> — <code>GetStat(EPlayerStats s)</code>
- <code>Player.h:88 CPlayer::IncStat</code> — <code>IncStat(EPlayerStats s,int v=1)</code>
- <code>Player.h:94 CPlayer::KilledThing</code> — <code>KilledThing(EKilledType type)</code>
- <code>Player.h:96 CPlayer::GetTimeoutTime</code> — <code>GetTimeoutTime()</code>
- <code>ResourceAccumulator.h:77 CResourceAccumulator::GetResourceID</code> — <code>GetResourceID()</code>
- <code>ResourceAccumulator.h:79 CResourceAccumulator::GetTargetPlatform</code> — <code>GetTargetPlatform()</code>
- <code>ResourceAccumulator.h:81 CResourceAccumulator::GetTargetLevel</code> — <code>GetTargetLevel()</code>
- <code>ResourceAccumulator.h:85 CResourceAccumulator::GetResourceFileHandle</code> — <code>GetResourceFileHandle()</code>
- <code>ResourceAccumulator.h:86 CResourceAccumulator::GetMasterPageFileHandle</code> — <code>GetMasterPageFileHandle()</code>
- <code>ResourceAccumulator.h:87 CResourceAccumulator::GetResourceFileName</code> — <code>*GetResourceFileName()</code>
- <code>ResourceAccumulator.h:89 CResourceAccumulator::GetLastGameLevelLoaded</code> — <code>GetLastGameLevelLoaded()</code>
- <code>ResourceAccumulator.h:91 CResourceAccumulator::GetOutputPageFile</code> — <code>*GetOutputPageFile()</code>
- <code>scheduledevent.h:16 CScheduledEvent::CScheduledEvent</code> — <code>CScheduledEvent()</code>
- <code>scheduledevent.h:20 CScheduledEvent::GetTime</code> — <code>&amp; GetTime()</code>
- <code>scheduledevent.h:21 CScheduledEvent::SetTime</code> — <code>SetTime(float new_time)</code>
- <code>scheduledevent.h:22 CScheduledEvent::SetReuse</code> — <code>SetReuse(BOOL val)</code>
- <code>scheduledevent.h:24 CScheduledEvent::GetReuse</code> — <code>GetReuse()</code>
- <code>scheduledevent.h:25 CScheduledEvent::GetData</code> — <code>*  GetData()</code>
- <code>scheduledevent.h:26 CScheduledEvent::SetData</code> — <code>SetData(CMonitor* data)</code>
- <code>scheduledevent.h:28 CScheduledEvent::GetNextFreeSE</code> — <code>* GetNextFreeSE()</code>
- <code>scheduledevent.h:29 CScheduledEvent::SetNextFreeSE</code> — <code>SetNextFreeSE(CScheduledEvent* se)</code>
- <code>scheduledevent.h:31 CScheduledEvent::GetNumCreated</code> — <code>GetNumCreated()</code>
- <code>SoundManager.h:53 CEffect::~dtor</code> — <code>~CEffect()</code>
- <code>SoundManager.h:164 CSoundManagerDebugMenu::GetName</code> — <code>GetName(char *name)</code>
- <code>SoundManager.h:166 CSoundManagerDebugMenu::GetShowSubmenus</code> — <code>GetShowSubmenus()</code>
- <code>SoundManager.h:222 CSoundManager::GetNumSoundEvents</code> — <code>GetNumSoundEvents()</code>
- <code>SoundManager.h:224 CSoundManager::GetFirstSoundEvent</code> — <code>*GetFirstSoundEvent()</code>
- <code>SoundManager.h:231 CSoundManager::GetFirstSample</code> — <code>*GetFirstSample()</code>
- <code>SoundManager.h:233 CSoundManager::IsInitialised</code> — <code>IsInitialised()</code>
- <code>SoundManager.h:235 CSoundManager::SetFirstSample</code> — <code>SetFirstSample(CSample *s)</code>
- <code>SoundManager.h:237 CSoundManager::GetMasterVolume</code> — <code>GetMasterVolume()</code>
- <code>SoundManager.h:240 CSoundManager::GetGameSoundsMasterVolume</code> — <code>GetGameSoundsMasterVolume()</code>
- <code>SoundManager.h:241 CSoundManager::SetGameSoundsMasterVolume</code> — <code>SetGameSoundsMasterVolume(float val)</code>
- <code>SoundManager.h:243 CSoundManager::GetMenuSoundsMasterVolume</code> — <code>GetMenuSoundsMasterVolume()</code>
- <code>SoundManager.h:244 CSoundManager::SetMenuSoundsMasterVolume</code> — <code>SetMenuSoundsMasterVolume(float val)</code>
- <code>SoundManager.h:247 CSoundManager::GetRadioMessageVolume</code> — <code>GetRadioMessageVolume()</code>
- <code>SoundManager.h:248 CSoundManager::GetHUDMessageVolume</code> — <code>GetHUDMessageVolume()</code>
- <code>SPtrSet.cpp:24 GenericSPtrSet::GenericSPtrSet</code> — <code>GenericSPtrSet::GenericSPtrSet()</code>
- <code>SPtrSet.cpp:35 GenericSPtrSet::GenericSPtrSet</code> — <code>GenericSPtrSet::GenericSPtrSet(const GenericSPtrSet&amp; copy)</code>
- <code>SPtrSet.cpp:53 GenericSPtrSet::operator=</code> — <code>&amp; GenericSPtrSet::operator = (GenericSPtrSet&amp; copy)</code>
- <code>SPtrSet.h:39 GenericSPtrSet::Size</code> — <code>Size()</code>
- <code>SPtrSet.h:40 GenericSPtrSet::First</code> — <code>* First()</code>
- <code>SPtrSet.h:41 GenericSPtrSet::Next</code> — <code>* Next()</code>
- <code>SPtrSet.h:43 GenericSPtrSet::Last</code> — <code>* Last()</code>
- <code>SPtrSet.h:70 SPtrSet::SPtrSet</code> — <code>SPtrSet()</code>
- <code>SPtrSet.h:71 SPtrSet::SPtrSet</code> — <code>SPtrSet(const SPtrSet&lt;T&gt;&amp; copy)</code>
- <code>SPtrSet.h:72 SPtrSet::operator=</code> — <code>&amp; operator = (SPtrSet&lt;T&gt;&amp; copy)</code>
- <code>SPtrSet.h:73 SPtrSet::Add</code> — <code>Add(T* ptr)</code>
- <code>SPtrSet.h:74 SPtrSet::Append</code> — <code>Append(T* ptr)</code>
- <code>SPtrSet.h:75 SPtrSet::Remove</code> — <code>Remove(T* ptr)</code>
- <code>SPtrSet.h:76 SPtrSet::RemoveAll</code> — <code>RemoveAll()</code>
- <code>SPtrSet.h:77 SPtrSet::DeleteAll</code> — <code>DeleteAll()</code>
- <code>SPtrSet.h:78 SPtrSet::Contains</code> — <code>Contains(T* ptr)</code>
- <code>SPtrSet.h:79 SPtrSet::Size</code> — <code>Size()</code>
- <code>SPtrSet.h:80 SPtrSet::At</code> — <code>* At(int val)</code>
- <code>SPtrSet.h:81 SPtrSet::First</code> — <code>* First()</code>
- <code>SPtrSet.h:82 SPtrSet::Next</code> — <code>* Next()</code>
- <code>SPtrSet.h:83 SPtrSet::Last</code> — <code>* Last()</code>
- <code>SPtrSet.h:93 GenericListIterator::GenericListIterator</code> — <code>GenericListIterator(GenericSPtrSet* list)</code>
- <code>SPtrSet.h:94 GenericListIterator::First</code> — <code>* First()</code>
- <code>SPtrSet.h:95 GenericListIterator::Next</code> — <code>* Next()</code>
- <code>SPtrSet.h:106 ListIterator::ListIterator</code> — <code>ListIterator(SPtrSet&lt;T&gt;* list)</code>
- <code>SPtrSet.h:107 ListIterator::First</code> — <code>* First()</code>
- <code>SPtrSet.h:108 ListIterator::Next</code> — <code>*      Next()</code>
- <code>thing.h:71 GetRenderPos</code> — <code>GetRenderPos()</code>
- <code>thing.h:72 GetRenderOrientation</code> — <code>GetRenderOrientation()</code>
- <code>thing.h:73 GetRenderSelected</code> — <code>GetRenderSelected()</code>
- <code>thing.h:74 GetRenderColourOffset</code> — <code>GetRenderColourOffset()</code>
- <code>thing.h:75 GetRenderColour</code> — <code>GetRenderColour()</code>
- <code>thing.h:76 GetRenderTurn</code> — <code>GetRenderTurn()</code>
- <code>thing.h:77 GetRenderFrame</code> — <code>GetRenderFrame()</code>
- <code>thing.h:78 GetRealAnimIndex</code> — <code>GetRealAnimIndex()</code>
- <code>thing.h:79 GetRenderRadius</code> — <code>GetRenderRadius()</code>
- <code>thing.h:80 GetRenderStartPos</code> — <code>GetRenderStartPos()</code>
- <code>thing.h:81 GetRenderEndPos</code> — <code>GetRenderEndPos()</code>
- <code>thing.h:82 GetRenderMesh</code> — <code>GetRenderMesh()</code>
- <code>thing.h:84 GetRenderRotateShadow</code> — <code>GetRenderRotateShadow()</code>
- <code>thing.h:85 GetRenderCanGoFlatShaded</code> — <code>GetRenderCanGoFlatShaded()</code>
- <code>thing.h:86 RenderUseHierarchy</code> — <code>RenderUseHierarchy(SINT pn)</code>
- <code>thing.h:87 GetShouldDoHitEffect</code> — <code>GetShouldDoHitEffect(SINT mesh_part_no)</code>
- <code>thing.h:88 GetRenderYaw</code> — <code>GetRenderYaw()</code>
- <code>thing.h:89 GetRenderScale</code> — <code>GetRenderScale()</code>
- <code>thing.h:90 GetRenderWithTransforms</code> — <code>GetRenderWithTransforms()</code>
- <code>thing.h:91 GetRenderImposterNo</code> — <code>GetRenderImposterNo()</code>
- <code>thing.h:92 GetRenderImposterBias</code> — <code>GetRenderImposterBias()</code>
- <code>thing.h:93 GetSnowDensity</code> — <code>GetSnowDensity()</code>
- <code>thing.h:94 GetCanBeStaticallyShadowed</code> — <code>GetCanBeStaticallyShadowed()</code>
- <code>thing.h:95 GetStaticShadow</code> — <code>*GetStaticShadow()</code>
- <code>thing.h:96 SetStaticShadow</code> — <code>SetStaticShadow(class CStaticShadow *shadow)</code>
- <code>thing.h:97 GetRequiresPolyBucket</code> — <code>GetRequiresPolyBucket()</code>
- <code>thing.h:99 GetSoundPos</code> — <code>GetSoundPos()</code>
- <code>thing.h:100 GetSoundOrientation</code> — <code>GetSoundOrientation()</code>
- <code>thing.h:101 GetSoundVelocity</code> — <code>GetSoundVelocity()</code>
- <code>thing.h:103 GetCueFactor</code> — <code>GetCueFactor()</code>
- <code>thing.h:107 SampleFinishedPlaying</code> — <code>SampleFinishedPlaying(CSoundEvent* event)</code>
- <code>thing.h:113 GetPos</code> — <code>&amp; GetPos()</code>
- <code>thing.h:116 SetPos</code> — <code>SetPos(FVector &amp;inPos)</code>
- <code>thing.h:118 GetMaxVelocity</code> — <code>GetMaxVelocity()</code>
- <code>thing.h:120 GetRadius</code> — <code>GetRadius()</code>
- <code>thing.h:133 TeleportOrientation</code> — <code>TeleportOrientation(const FMatrix&amp; orientation)</code>
- <code>thing.h:134 Activate</code> — <code>Activate()</code>
- <code>thing.h:135 Deactivate</code> — <code>Deactivate()</code>
- <code>thing.h:136 GetMoveMultiplier</code> — <code>GetMoveMultiplier()</code>
- <code>thing.h:138 GetLocalLastFrameMovement</code> — <code>GetLocalLastFrameMovement()</code>
- <code>thing.h:139 IsObjective</code> — <code>IsObjective()</code>
- <code>thing.h:142 GetVelocity</code> — <code>GetVelocity()</code>
- <code>thing.h:145 GetOldPos</code> — <code>GetOldPos()</code>
- <code>thing.h:146 GetOldOrientation</code> — <code>GetOldOrientation()</code>
- <code>thing.h:150 GetMapWhoEntry</code> — <code>*   GetMapWhoEntry()</code>
- <code>thing.h:151 SetRenderThing</code> — <code>SetRenderThing(CRenderThing* rtthing)</code>
- <code>thing.h:152 GetRenderThing</code> — <code>* GetRenderThing()</code>
- <code>thing.h:153 GetCST</code> — <code>* GetCST()</code>
- <code>thing.h:156 GetIsInvisible</code> — <code>GetIsInvisible()</code>
- <code>thing.h:157 MakeVisible</code> — <code>MakeVisible()</code>
- <code>thing.h:158 MakeInvisible</code> — <code>MakeInvisible()</code>
- <code>thing.h:163 GetCanBeImpostered</code> — <code>GetCanBeImpostered()</code>
- <code>thing.h:164 GetImposterFrames</code> — <code>GetImposterFrames()</code>
- <code>thing.h:165 GetImposterAnimMode</code> — <code>GetImposterAnimMode()</code>
- <code>thing.h:167 GetThing</code> — <code>* GetThing()</code>
- <code>thing.h:170 GetRTMesh</code> — <code>*GetRTMesh()</code>
- <code>thing.h:172 SetThingType</code> — <code>SetThingType(ULONG t)</code>
- <code>thing.h:173 GetThingType</code> — <code>&amp; GetThingType()</code>
- <code>thing.h:174 IsA</code> — <code>IsA(EThingType type) const</code>
- <code>thing.h:175 Hit</code> — <code>Hit(CThing* other_thing, CCollisionReport* report)</code>
- <code>thing.h:176 Damage</code> — <code>Damage(float amount,CThing *inByThis,BOOL inDamageShields=TRUE, int mesh_part_no = -1)</code>
- <code>thing.h:177 GetName</code> — <code>* GetName()</code>
- <code>thing.h:178 SetName</code> — <code>SetName(char *inName)</code>
- <code>thing.h:180 GetSoundMaterial</code> — <code>GetSoundMaterial()</code>
- <code>thing.h:186 ClipToGround</code> — <code>ClipToGround()</code>
- <code>thing.h:187 Gravity</code> — <code>Gravity()</code>
- <code>thing.h:188 ObeyGravity</code> — <code>ObeyGravity()</code>
- <code>thing.h:189 BounceFactor</code> — <code>BounceFactor()</code>
- <code>thing.h:190 COfGHeight</code> — <code>COfGHeight()</code>
- <code>thing.h:192 CanGoUnderWater</code> — <code>CanGoUnderWater()</code>
- <code>thing.h:194 GetFlags</code> — <code>GetFlags()</code>
- <code>thing.h:195 SetFlags</code> — <code>SetFlags(short val)</code>
- <code>thing.h:196 IsDying</code> — <code>IsDying()</code>
- <code>thing.h:197 IsShuttingDown</code> — <code>IsShuttingDown()</code>
- <code>thing.h:201 GetMotionController</code> — <code>*GetMotionController()</code>
- <code>thing.h:206 GetRenderAnimation</code> — <code>GetRenderAnimation()</code>
- <code>thing.h:209 GetAIState</code> — <code>GetAIState()</code>
- <code>thing.h:210 SetAIState</code> — <code>SetAIState(EAIState inAIState)</code>
- <code>thing.h:218 AccumulateScore</code> — <code>AccumulateScore()</code>
- <code>thing.h:220 ResetThingCounter</code> — <code>ResetThingCounter()</code>
- <code>thing.h:221 GetThingNumber</code> — <code>GetThingNumber()</code>
- <code>thing.h:223 SetVulnerable</code> — <code>SetVulnerable(BOOL val)</code>
- <code>thing.h:224 GetVulnerable</code> — <code>GetVulnerable()</code>
- <code>thing.h:268 GetRenderOrientation</code> — <code>GetRenderOrientation()</code>
- <code>thing.h:270 SetThingType</code> — <code>SetThingType(ULONG t)</code>
- <code>thing.h:271 GetRealAnimIndex</code> — <code>GetRealAnimIndex()</code>
- <code>thing.h:272 GetSoundOrientation</code> — <code>GetSoundOrientation()</code>
- <code>thing.h:273 GetOrientation</code> — <code>&amp; GetOrientation()</code>
- <code>thing.h:274 IsObjective</code> — <code>IsObjective()</code>
- <code>thing.h:275 GetOldOrientation</code> — <code>GetOldOrientation()</code>
- <code>thing.h:276 GetMotionController</code> — <code>*GetMotionController()</code>
- <code>thing.h:277 GetRenderAnimation</code> — <code>GetRenderAnimation()</code>
- <code>thing.h:278 GetName</code> — <code>* GetName()</code>
- <code>thing.h:280 GetMissionScript</code> — <code>* GetMissionScript()</code>
- <code>thing.h:293 GoToPoint</code> — <code>GoToPoint(FVector  point, BOOL inOverride=FALSE)</code>
- <code>thing.h:296 Stop</code> — <code>Stop()</code>
- <code>thing.h:297 GetContainedInside</code> — <code>* GetContainedInside()</code>

## Parser exclusions and bounded caveats

Tree-sitter produced 10 typeless non-constructor `function_definition` nodes. Each is named below and excluded because the source is a statement macro or SDK macro test, not a function definition.

- <code>Career.cpp:292 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(child_links, link)</code>
- <code>Career.cpp:430 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(next_links, link)</code>
- <code>Career.cpp:504 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(previous_links, previous_link)</code>
- <code>Career.cpp:1337 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(child_links, link)</code>
- <code>eventmanager.cpp:334 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(mEventListBuffer[next_bufffer][j], next_event)</code>
- <code>eventmanager.cpp:369 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(mEventListBuffer[next_bufffer][j], next_event)</code>
- <code>eventmanager.cpp:522 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(mEventListBuffer[buff][j], next_event)</code>
- <code>game.cpp:1417 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(unit_iterater,unit)</code>
- <code>ltshell.cpp:1199 FAILED</code> — <code>FAILED(hr)</code>
- <code>SPtrSet.cpp:299 FOR_ALL_ITEMS_IN</code> — <code>FOR_ALL_ITEMS_IN(iterator, item)</code>

The parser reported recoverable syntax errors in 26 files: <code>actor.cpp</code>, <code>actor.h</code>, <code>BattleEngine.h</code>, <code>BattleEngineDataManager.cpp</code>, <code>BattleEngineDataManager.h</code>, <code>Controller.cpp</code>, <code>d3dapp.cpp</code>, <code>d3dapp.h</code>, <code>DXEngine.cpp</code>, <code>DXMemoryManager.cpp</code>, <code>EditorD3DApp.cpp</code>, <code>EditorD3DApp.h</code>, <code>FEPGoodies.cpp</code>, <code>FEPLoadGame.cpp</code>, <code>FEPSaveGame.cpp</code>, <code>FrontEnd.cpp</code>, <code>game.cpp</code>, <code>ltshell.cpp</code>, <code>ltshell.h</code>, <code>MemoryManager.cpp</code>, <code>pcsoundmanager.h</code>, <code>scheduledevent.h</code>, <code>SPtrSet.cpp</code>, <code>SPtrSet.h</code>, <code>thing.cpp</code>, <code>thing.h</code>. The error nodes were inspected in the scratch receipt and are MSVC modifiers, inline assembly/string continuations, preprocessor placement, macro payloads, or declarations; the AST still recovers every one of the 1,149 valid crosswalk joins. The 1,783-definition count is therefore a deterministic parser-bounded inventory, not a compiler/linker claim about one selected build configuration.

The name table and closure are tracked authorities with different dates and populations. This audit compares their tracked rows only; it does not claim equality to an unmerged live Ghidra database. Name-table body ranges are bounding envelopes for multi-range functions, so size findings require a min/max disagreement rather than merely comparing `bodyBytes` to envelope width.

No pristine bytes were needed: the only authority size disagreement is already explicit between the two tracked tables. No binary or Ghidra project was opened or written.

## Evidence-path resolver fixture tests

- `PASS: markdown note resolves`
- `PASS: TSV row resolves`
- `PASS: dead path rejected`
- `PASS: unrelated existing file rejected`

## Validation

- PASS: two independent auditor runs are byte-identical for `row-audit.tsv`, `summary.json`, `inventory.tsv`, and `resolver-self-test.txt`.
- PASS: focused output validator confirms the 1,164-row schema/order mirror, exact `1,783 = 1,149 + 634` / `1,164 = 1,149 + 15` reconciliation, 106-file table, and 11+11 cold-read sample.
- PASS: `npm run test:doc-headers` reports zero violations, including this new report.
- PASS: `git diff --check` on the two audit outputs.
- Repository-wide `npm run test:docs` remains red before reaching the header gate because `tools/probe/README.md` points to ignored/missing `../../local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md`; this audit did not touch that owner.
- Direct downstream checks also expose existing out-of-scope baseline failures: `test:re-function-doc-names` names the zero-assertion `IScript__InitVariable_SetVariable_ShutdownVariable.md`, and `re_evidence_register_export.py --check-header-only` refuses the tracked header/current-authority mismatch. Neither audit output changes those inputs.

## Reproduction

Scratch parser (untracked by task boundary):

- `local-lab/source-crosswalk-audit-t_a103d4a7/audit_crosswalk.py` — SHA-256 `0f46e4c82d49f631fd264e4db5dfd1a33b35d81fbdc9c2fe820dff9fb9c980e3`
- tree-sitter `0.25.2`; tree-sitter-cpp `0.23.4`

Pinned inputs:

- `reverse-engineering/source-crosswalk/crosswalk.tsv` — SHA-256 `96ed0a7624c32b499e12403fd1062253c32a673738cba9345231950e85b7842a`
- `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv` — SHA-256 `4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213`
- `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv` — SHA-256 `cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974`
- `reverse-engineering/source-crosswalk/REPORT.md` — SHA-256 `9cfad83c0a62b9a09825af349a40f21e009045939d72ae179b4c63bac18f7c67`
- `references/Onslaught` submodule — `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`
- retail `.text` extent — `[0x00401000,0x005d7f9d)`

Exact command from the repository root (Git Bash):

```bash
python -m pip install tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
python local-lab/source-crosswalk-audit-t_a103d4a7/audit_crosswalk.py \
  --repo C:/Users/david/source/Onslaught-Career-Editor/.worktrees/t-sc-bea-crosswalk-audit \
  --output C:/Users/david/source/Onslaught-Career-Editor/.worktrees/t-sc-bea-crosswalk-audit/local-lab/source-crosswalk-audit-t_a103d4a7/repro-a \
  --source-commit 5352a81cdb838b145a57f7febc5d9fc4b0129ebb
python local-lab/source-crosswalk-audit-t_a103d4a7/audit_crosswalk.py \
  --repo C:/Users/david/source/Onslaught-Career-Editor/.worktrees/t-sc-bea-crosswalk-audit \
  --output C:/Users/david/source/Onslaught-Career-Editor/.worktrees/t-sc-bea-crosswalk-audit/local-lab/source-crosswalk-audit-t_a103d4a7/repro-b \
  --source-commit 5352a81cdb838b145a57f7febc5d9fc4b0129ebb
for f in row-audit.tsv summary.json inventory.tsv resolver-self-test.txt; do
  cmp local-lab/source-crosswalk-audit-t_a103d4a7/repro-a/$f local-lab/source-crosswalk-audit-t_a103d4a7/repro-b/$f
done
```

Two final runs were byte-identical. Sealed run-A outputs:

- `row-audit.tsv` — SHA-256 `6f110c6af3f234c16cc80d9dd80f859be6280e57cd1f4d8521dda863458449ea`
- `summary.json` — SHA-256 `1a325d2d021e68aec4cfeac28bae6e95e4323a66e5d2b936c76d2c396ce384f5`
- `inventory.tsv` — SHA-256 `91bfee284185379db52c7d044e42a59b3f5ba75306c1150a0e56bdbb33705912`
- `resolver-self-test.txt` — SHA-256 `eb865fc20c8e50df5c372cfb2dd9da0c8ce52142a74a4347c088627d3df6da4b`

Only `row-audit.tsv` and this report are tracked. Inventory, summary, fixtures, parser, and manual-sample working receipts remain under ignored `local-lab/` as required.
