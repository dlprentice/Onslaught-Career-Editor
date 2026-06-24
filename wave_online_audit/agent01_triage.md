# Semantic Audit Online Pass 2026-02-12 - Mismatch Triage

Scope: canonical `reverse-engineering/` paths only (ignored `lore-book/`).

## Summary Counts

- Doc should change to match Ghidra name: 30
- Ghidra likely missing rename (doc correct target): 32
- Function object missing / address is callsite (audit false positive): 35
- Requires manual function-create in UI: 27

## Prioritized Table

| Priority | Category | Addr | Expected | Actual | Source |
|---|---|---|---|---|---|
| 1 | Requires manual function-create in UI | `0x004f7a80` | `CScriptObjectCode__Run` | `` | `reverse-engineering/binary-analysis/README.md` |
| 1 | Requires manual function-create in UI | `0x005e4e4c` | `CStringDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 1 | Requires manual function-create in UI | `0x005e4df8` | `CThingPtrDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 1 | Requires manual function-create in UI | `0x0045d7e0` | `CFEPGoodies__Process` | `` | `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x0043f510` | `CCutscene__InitAnimations` | `` | `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x004d2f19` | `CPlayer__GotoPanView` | `` | `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x00533e20` | `IScript__Create3PointPanCamera` | `` | `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x0053421e` | `IScript__Create4PointPanCamera` | `` | `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x00426ad3` | `CCollisionSeekingRound__CreateEffect` | `` | `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x004160e4` | `CBomber__Constructor_1` | `` | `reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x0041611d` | `CBomber__Constructor_2` | `` | `reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x0046cfe2` | `CGame__LoadLevel` | `` | `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md` |
| 1 | Requires manual function-create in UI | `0x0055aa2e` | `CDXTrees__Render` | `` | `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md` |
| 1 | Requires manual function-create in UI | `0x0041b1a0` | `CCannon__Init` | `` | `reverse-engineering/binary-analysis/functions/Cannon.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x005507b5` | `CDXPatch__LoadFromFile` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 1 | Requires manual function-create in UI | `0x0041bcd0` | `CCareer__UpdateOnWorldComplete` | `` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 1 | Requires manual function-create in UI | `0x004684ef` | `CFrontEnd__Run` | `` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 1 | Requires manual function-create in UI | `0x0047bbe4` | `CGroundAttackAircraft__Constructor` | `` | `reverse-engineering/binary-analysis/functions/GroundAttackAircraft.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x00464520` | `CFEPMain__Init` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 1 | Requires manual function-create in UI | `0x004621e0` | `CFEPMain__GetActionCount` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 1 | Requires manual function-create in UI | `0x004621d0` | `CFEPMain__GetMenuType` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 1 | Requires manual function-create in UI | `0x00466140` | `CFEPMain__Cleanup` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 1 | Requires manual function-create in UI | `0x00488460` | `CIBuffer__CreateDynamic` | `` | `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x004884f0` | `CIBuffer__CreateStatic` | `` | `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x00440cb8` | `CDamage__LoadDamageTexture` | `` | `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md` |
| 1 | Requires manual function-create in UI | `0x0047f7ea` | `CHeightField__Load` | `` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__InitColorGradient.md` |
| 1 | Requires manual function-create in UI | `0x004dea50` | `CSentinel::Constructor` | `` | `reverse-engineering/binary-analysis/functions/Sentinel.cpp.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00465490` | `prologue` | `IsCheatActive` | `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0043f340` | `CCutscene__Start` | `FUN_0043f340` | `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0043f420` | `CCutscene__Stop` | `FUN_0043f420` | `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0043fa70` | `CCutscene__PrepareAnimations` | `FUN_0043fa70` | `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0043fcd0` | `CCutscene__ForceEnd` | `FUN_0043fcd0` | `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00404960` | `CAtmospheric__Unlink` | `FUN_00404960` | `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00404920` | `CAtmospheric__Link` | `FUN_00404920` | `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004046d0` | `CAtmospheric__Constructor` | `FUN_004046d0` | `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00404010` | `CAtmospheric__Destructor` | `FUN_00404010` | `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0052f670` | `CEventFunctionParam__ScalarDeletingDestructor` | `CDataType__ScalarDeletingDestructor` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0048e310` | `CLandscapeIB__ReleaseBuffer` | `CLandscapeTexture__FreeTexture` | `reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x0048e360` | `CLandscapeIB__SetParameters` | `CLandscapeTexture__SetupMipLevel` | `reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00533aa0` | `IScript__GetEnumValue` | `IScript__GetGoodieState` | `reverse-engineering/binary-analysis/functions/IScript.cpp.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a15a0` | `CMemoryManager__ReallocFromPool` | `FUN_004a15a0` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a1d60` | `CMemoryManager__AddToFreeList` | `FUN_004a1d60` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a1ea0` | `CMemoryManager__EnableCoalescing` | `FUN_004a1ea0` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a2660` | `CMemoryManager__DumpHeapBlocks` | `FUN_004a2660` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a2a80` | `CMemoryManager__DumpMemoryReport` | `FUN_004a2a80` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a2ff0` | `CMemoryManager__SetBlockFlag` | `FUN_004a2ff0` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004a1f60` | `CMemoryManager__DumpStatsToFile` | `FUN_004a1f60` | `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00423910` | `StreamReader::GetTag` | `FUN_00423910` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x00423960` | `StreamReader::Read` | `FUN_00423960` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cae50` | `CParticle__Destroy` | `FUN_004cae50` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cb050` | `CParticleManager__RemoveFromGlobalList` | `FUN_004cb050` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cb1b0` | `CParticleManager__Shutdown` | `FUN_004cb1b0` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cb210` | `CParticleManager__Update` | `FUN_004cb210` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cb300` | `CParticleManager__InterpolatePositions` | `FUN_004cb300` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cbca0` | `CParticleManager__UpdateParticles` | `FUN_004cbca0` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004cbe30` | `CParticleManager__PruneDeadParticles` | `FUN_004cbe30` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004caf60` | `CParticleManager__CleanupHandles` | `FUN_004caf60` | `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004fe710` | `CSubmarineAI__CSubmarineAI` | `CWarspite__Init` | `reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md` |
| 2 | Ghidra likely missing rename (doc correct target) | `0x004ef570` | `CSubmarineGuide__CSubmarineGuide` | `FUN_004ef570` | `reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md` |
| 3 | Doc should change to match Ghidra name | `0x004213c0` | `CCareer::SaveToFile` | `CCareer__SaveWithFlag` | `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` |
| 3 | Doc should change to match Ghidra name | `0x00421200` | `CCareer::LoadFromFile` | `CCareer__Load` | `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` |
| 3 | Doc should change to match Ghidra name | `0x00421430` | `CCareer::GetSaveSize` | `CCareer__GetSaveSize` | `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` |
| 3 | Doc should change to match Ghidra name | `0x00421350` | `CCareer::Save` | `CCareer__Save` | `reverse-engineering/binary-analysis/executable-analysis.md` |
| 3 | Doc should change to match Ghidra name | `0x004213c0` | `CCareer::SaveWithFlag` | `CCareer__SaveWithFlag` | `reverse-engineering/binary-analysis/executable-analysis.md` |
| 3 | Doc should change to match Ghidra name | `0x00421200` | `CCareer::LoadFromFile` | `CCareer__Load` | `reverse-engineering/binary-analysis/executable-analysis.md` |
| 3 | Doc should change to match Ghidra name | `0x00421430` | `CCareer::GetSaveSize` | `CCareer__GetSaveSize` | `reverse-engineering/binary-analysis/executable-analysis.md` |
| 3 | Doc should change to match Ghidra name | `0x00539760` | `FUN_00539760` | `CScriptObjectCode__GetInstruction` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x00539a60` | `FUN_00539a60` | `CScriptObjectCode__CallEventDirect` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x00541220` | `CDXFrontEndVideo::~CDXFrontEndVideo` | `CDXFrontEndVideo__dtor` | `reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x00541f30` | `CFrontEndVideo::scalar_deleting_dtor` | `CFrontEndVideo__scalar_dtor` | `reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x0053a120` | `scalar_deleting_dtor` | `CDXBattleLine__scalar_deleting_dtor` | `reverse-engineering/binary-analysis/functions/DXBattleLine.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x0044b060` | `FUN_0044b060` | `CEventManager__Init` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 3 | Doc should change to match Ghidra name | `0x00541240` | `FUN_00541240` | `CDXFrontEndVideo__SetDefaultSize` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 3 | Doc should change to match Ghidra name | `0x004f2150` | `FUN_004f2150` | `CText__Ctor` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 3 | Doc should change to match Ghidra name | `0x004f21f0` | `FUN_004f21f0` | `CText__Init` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 3 | Doc should change to match Ghidra name | `0x004bb8c0` | `FUN_004bb8c0` | `CMusic__PlayTrackByType` | `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md` |
| 3 | Doc should change to match Ghidra name | `0x00528f80` | `CD3DApplication::Init` | `CD3DApplication__Init` | `reverse-engineering/binary-analysis/functions/display-settings.md` |
| 3 | Doc should change to match Ghidra name | `0x005290a0` | `CD3DApplication::Create` | `CD3DApplication__Create` | `reverse-engineering/binary-analysis/functions/display-settings.md` |
| 3 | Doc should change to match Ghidra name | `0x00529350` | `CD3DApplication::BuildDeviceList` | `CD3DApplication__BuildDeviceList` | `reverse-engineering/binary-analysis/functions/display-settings.md` |
| 3 | Doc should change to match Ghidra name | `0x0052af00` | `CD3DApplication::Initialize3DEnvironment` | `CD3DApplication__Initialize3DEnvironment` | `reverse-engineering/binary-analysis/functions/display-settings.md` |
| 3 | Doc should change to match Ghidra name | `0x0052c730` | `CD3DApplication::SetResolution` | `CD3DApplication__SetResolution` | `reverse-engineering/binary-analysis/functions/display-settings.md` |
| 3 | Doc should change to match Ghidra name | `0x004f2c90` | `scalar_deleting_destructor` | `CTGALoader__scalar_deleting_destructor` | `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md` |
| 3 | Doc should change to match Ghidra name | `0x00488620` | `CTextureLoader::CTextureLoader` | `CImageLoader__Constructor` | `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md` |
| 3 | Doc should change to match Ghidra name | `0x00488700` | `CTextureLoader::~CTextureLoader` | `CImageLoader__Destructor` | `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md` |
| 3 | Doc should change to match Ghidra name | `0x00549220` | `CMemoryManager::Free` | `OID__FreeObject` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md` |
| 3 | Doc should change to match Ghidra name | `0x005490e0` | `CMemoryManager::Alloc` | `OID__AllocObject` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md` |
| 3 | Doc should change to match Ghidra name | `0x004ded30` | `CSentinel::Activate` | `CSentinel__Activate` | `reverse-engineering/binary-analysis/functions/Sentinel.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x004dec00` | `CSentinel::scalar_deleting_dtor` | `CSentinel__scalar_deleting_dtor` | `reverse-engineering/binary-analysis/functions/Sentinel.cpp.md` |
| 3 | Doc should change to match Ghidra name | `0x0044b370` | `FUN_0044b370` | `CEventManager__AddEvent_AtTime` | `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4af8` | `CDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4ea4` | `CDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4d50` | `CDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4da4` | `CDataType__ScalarDeletingDestructor` | `` | `reverse-engineering/binary-analysis/functions/DataType.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x004261be` | `CCollisionSeekingRound__Init` | `` | `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0042627a` | `CCollisionSeekingRound__Init` | `` | `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4ef8` | `CEventFunction__vtable` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4d50` | `CEventFunctionParam__vtable` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005d92d4` | `CRelaxedSquad__vtable` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00538fe4` | `FUN_00538ec0` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0053913f` | `FUN_00539040` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00538c3b` | `FUN_00538b70` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00538d68` | `FUN_00538c70` | `` | `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0055044d` | `CDXPatchManager__Init` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00550479` | `CDXPatchManager__Init` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005504f4` | `CDXPatchManager__Init` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0055057d` | `CDXPatchManager__Init` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005505f1` | `CDXPatchManager__Init` | `` | `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x004741b5` | `CGamut__Init` | `` | `reverse-engineering/binary-analysis/functions/gcgamut.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x004741db` | `CGamut__Init` | `` | `reverse-engineering/binary-analysis/functions/gcgamut.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00462c90` | `CFEPMain__Update` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00462638` | `CFEPMain__Update` | `` | `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050bc92` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050bdd8` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050bfc8` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050c1dd` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050c29e` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050c9ab` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050caac` | `CWorld__LoadWorld` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x0050dd75` | `FUN_0050dcb0` | `` | `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x00491203` | `FUN_004911c0` | `` | `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x004910d6` | `FUN_00491060` | `` | `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4f34` | `CScriptEventNB__vtable_base` | `` | `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4f44` | `CScriptEventNB__vtable` | `` | `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md` |
| 4 | Function object missing / address is callsite (audit false positive) | `0x005e4f54` | `CScriptEventNB__vtable_derived` | `` | `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md` |

## Details

### Doc should change to match Ghidra name

- `0x004213c0` `expected=CCareer::SaveToFile` `actual=CCareer__SaveWithFlag` `source=reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `0x00421200` `expected=CCareer::LoadFromFile` `actual=CCareer__Load` `source=reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `0x00421430` `expected=CCareer::GetSaveSize` `actual=CCareer__GetSaveSize` `source=reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `0x00421350` `expected=CCareer::Save` `actual=CCareer__Save` `source=reverse-engineering/binary-analysis/executable-analysis.md`
- `0x004213c0` `expected=CCareer::SaveWithFlag` `actual=CCareer__SaveWithFlag` `source=reverse-engineering/binary-analysis/executable-analysis.md`
- `0x00421200` `expected=CCareer::LoadFromFile` `actual=CCareer__Load` `source=reverse-engineering/binary-analysis/executable-analysis.md`
- `0x00421430` `expected=CCareer::GetSaveSize` `actual=CCareer__GetSaveSize` `source=reverse-engineering/binary-analysis/executable-analysis.md`
- `0x00539760` `expected=FUN_00539760` `actual=CScriptObjectCode__GetInstruction` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x00539a60` `expected=FUN_00539a60` `actual=CScriptObjectCode__CallEventDirect` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x00541220` `expected=CDXFrontEndVideo::~CDXFrontEndVideo` `actual=CDXFrontEndVideo__dtor` `source=reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md`
- `0x00541f30` `expected=CFrontEndVideo::scalar_deleting_dtor` `actual=CFrontEndVideo__scalar_dtor` `source=reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md`
- `0x0053a120` `expected=scalar_deleting_dtor` `actual=CDXBattleLine__scalar_deleting_dtor` `source=reverse-engineering/binary-analysis/functions/DXBattleLine.cpp.md`
- `0x0044b060` `expected=FUN_0044b060` `actual=CEventManager__Init` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x00541240` `expected=FUN_00541240` `actual=CDXFrontEndVideo__SetDefaultSize` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x004f2150` `expected=FUN_004f2150` `actual=CText__Ctor` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x004f21f0` `expected=FUN_004f21f0` `actual=CText__Init` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x004bb8c0` `expected=FUN_004bb8c0` `actual=CMusic__PlayTrackByType` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x00528f80` `expected=CD3DApplication::Init` `actual=CD3DApplication__Init` `source=reverse-engineering/binary-analysis/functions/display-settings.md`
- `0x005290a0` `expected=CD3DApplication::Create` `actual=CD3DApplication__Create` `source=reverse-engineering/binary-analysis/functions/display-settings.md`
- `0x00529350` `expected=CD3DApplication::BuildDeviceList` `actual=CD3DApplication__BuildDeviceList` `source=reverse-engineering/binary-analysis/functions/display-settings.md`
- `0x0052af00` `expected=CD3DApplication::Initialize3DEnvironment` `actual=CD3DApplication__Initialize3DEnvironment` `source=reverse-engineering/binary-analysis/functions/display-settings.md`
- `0x0052c730` `expected=CD3DApplication::SetResolution` `actual=CD3DApplication__SetResolution` `source=reverse-engineering/binary-analysis/functions/display-settings.md`
- `0x004f2c90` `expected=scalar_deleting_destructor` `actual=CTGALoader__scalar_deleting_destructor` `source=reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `0x00488620` `expected=CTextureLoader::CTextureLoader` `actual=CImageLoader__Constructor` `source=reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `0x00488700` `expected=CTextureLoader::~CTextureLoader` `actual=CImageLoader__Destructor` `source=reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `0x00549220` `expected=CMemoryManager::Free` `actual=OID__FreeObject` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `0x005490e0` `expected=CMemoryManager::Alloc` `actual=OID__AllocObject` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `0x004ded30` `expected=CSentinel::Activate` `actual=CSentinel__Activate` `source=reverse-engineering/binary-analysis/functions/Sentinel.cpp.md`
- `0x004dec00` `expected=CSentinel::scalar_deleting_dtor` `actual=CSentinel__scalar_deleting_dtor` `source=reverse-engineering/binary-analysis/functions/Sentinel.cpp.md`
- `0x0044b370` `expected=FUN_0044b370` `actual=CEventManager__AddEvent_AtTime` `source=reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`

### Ghidra likely missing rename (doc correct target)

- `0x00465490` `expected=prologue` `actual=IsCheatActive` `source=reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `0x0043f340` `expected=CCutscene__Start` `actual=FUN_0043f340` `source=reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `0x0043f420` `expected=CCutscene__Stop` `actual=FUN_0043f420` `source=reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `0x0043fa70` `expected=CCutscene__PrepareAnimations` `actual=FUN_0043fa70` `source=reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `0x0043fcd0` `expected=CCutscene__ForceEnd` `actual=FUN_0043fcd0` `source=reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `0x00404960` `expected=CAtmospheric__Unlink` `actual=FUN_00404960` `source=reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `0x00404920` `expected=CAtmospheric__Link` `actual=FUN_00404920` `source=reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `0x004046d0` `expected=CAtmospheric__Constructor` `actual=FUN_004046d0` `source=reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `0x00404010` `expected=CAtmospheric__Destructor` `actual=FUN_00404010` `source=reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `0x0052f670` `expected=CEventFunctionParam__ScalarDeletingDestructor` `actual=CDataType__ScalarDeletingDestructor` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x0048e310` `expected=CLandscapeIB__ReleaseBuffer` `actual=CLandscapeTexture__FreeTexture` `source=reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md`
- `0x0048e360` `expected=CLandscapeIB__SetParameters` `actual=CLandscapeTexture__SetupMipLevel` `source=reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md`
- `0x00533aa0` `expected=IScript__GetEnumValue` `actual=IScript__GetGoodieState` `source=reverse-engineering/binary-analysis/functions/IScript.cpp.md`
- `0x004a15a0` `expected=CMemoryManager__ReallocFromPool` `actual=FUN_004a15a0` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a1d60` `expected=CMemoryManager__AddToFreeList` `actual=FUN_004a1d60` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a1ea0` `expected=CMemoryManager__EnableCoalescing` `actual=FUN_004a1ea0` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a2660` `expected=CMemoryManager__DumpHeapBlocks` `actual=FUN_004a2660` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a2a80` `expected=CMemoryManager__DumpMemoryReport` `actual=FUN_004a2a80` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a2ff0` `expected=CMemoryManager__SetBlockFlag` `actual=FUN_004a2ff0` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x004a1f60` `expected=CMemoryManager__DumpStatsToFile` `actual=FUN_004a1f60` `source=reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `0x00423910` `expected=StreamReader::GetTag` `actual=FUN_00423910` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `0x00423960` `expected=StreamReader::Read` `actual=FUN_00423960` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `0x004cae50` `expected=CParticle__Destroy` `actual=FUN_004cae50` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cb050` `expected=CParticleManager__RemoveFromGlobalList` `actual=FUN_004cb050` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cb1b0` `expected=CParticleManager__Shutdown` `actual=FUN_004cb1b0` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cb210` `expected=CParticleManager__Update` `actual=FUN_004cb210` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cb300` `expected=CParticleManager__InterpolatePositions` `actual=FUN_004cb300` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cbca0` `expected=CParticleManager__UpdateParticles` `actual=FUN_004cbca0` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004cbe30` `expected=CParticleManager__PruneDeadParticles` `actual=FUN_004cbe30` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004caf60` `expected=CParticleManager__CleanupHandles` `actual=FUN_004caf60` `source=reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `0x004fe710` `expected=CSubmarineAI__CSubmarineAI` `actual=CWarspite__Init` `source=reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md`
- `0x004ef570` `expected=CSubmarineGuide__CSubmarineGuide` `actual=FUN_004ef570` `source=reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md`

### Function object missing / address is callsite (audit false positive)

- `0x005e4af8` `expected=CDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x005e4ea4` `expected=CDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x005e4d50` `expected=CDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x005e4da4` `expected=CDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x004261be` `expected=CCollisionSeekingRound__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md`
- `0x0042627a` `expected=CCollisionSeekingRound__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md`
- `0x005e4ef8` `expected=CEventFunction__vtable` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x005e4d50` `expected=CEventFunctionParam__vtable` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x005d92d4` `expected=CRelaxedSquad__vtable` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x00538fe4` `expected=FUN_00538ec0` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x0053913f` `expected=FUN_00539040` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x00538c3b` `expected=FUN_00538b70` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x00538d68` `expected=FUN_00538c70` `actual=missing` `source=reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `0x0055044d` `expected=CDXPatchManager__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x00550479` `expected=CDXPatchManager__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x005504f4` `expected=CDXPatchManager__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x0055057d` `expected=CDXPatchManager__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x005505f1` `expected=CDXPatchManager__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x004741b5` `expected=CGamut__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/gcgamut.cpp.md`
- `0x004741db` `expected=CGamut__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/gcgamut.cpp.md`
- `0x00462c90` `expected=CFEPMain__Update` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x00462638` `expected=CFEPMain__Update` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x0050bc92` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050bdd8` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050bfc8` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050c1dd` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050c29e` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050c9ab` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050caac` `expected=CWorld__LoadWorld` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x0050dd75` `expected=FUN_0050dcb0` `actual=missing` `source=reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `0x00491203` `expected=FUN_004911c0` `actual=missing` `source=reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `0x004910d6` `expected=FUN_00491060` `actual=missing` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `0x005e4f34` `expected=CScriptEventNB__vtable_base` `actual=missing` `source=reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`
- `0x005e4f44` `expected=CScriptEventNB__vtable` `actual=missing` `source=reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`
- `0x005e4f54` `expected=CScriptEventNB__vtable_derived` `actual=missing` `source=reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`

### Requires manual function-create in UI

- `0x004f7a80` `expected=CScriptObjectCode__Run` `actual=missing` `source=reverse-engineering/binary-analysis/README.md`
- `0x005e4e4c` `expected=CStringDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x005e4df8` `expected=CThingPtrDataType__ScalarDeletingDestructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `0x0045d7e0` `expected=CFEPGoodies__Process` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/_index.md`
- `0x0043f510` `expected=CCutscene__InitAnimations` `actual=missing` `source=reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `0x004d2f19` `expected=CPlayer__GotoPanView` `actual=missing` `source=reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md`
- `0x00533e20` `expected=IScript__Create3PointPanCamera` `actual=missing` `source=reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md`
- `0x0053421e` `expected=IScript__Create4PointPanCamera` `actual=missing` `source=reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md`
- `0x00426ad3` `expected=CCollisionSeekingRound__CreateEffect` `actual=missing` `source=reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md`
- `0x004160e4` `expected=CBomber__Constructor_1` `actual=missing` `source=reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md`
- `0x0041611d` `expected=CBomber__Constructor_2` `actual=missing` `source=reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md`
- `0x0046cfe2` `expected=CGame__LoadLevel` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`
- `0x0055aa2e` `expected=CDXTrees__Render` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`
- `0x0041b1a0` `expected=CCannon__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/Cannon.cpp/_index.md`
- `0x005507b5` `expected=CDXPatch__LoadFromFile` `actual=missing` `source=reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `0x0041bcd0` `expected=CCareer__UpdateOnWorldComplete` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x004684ef` `expected=CFrontEnd__Run` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `0x0047bbe4` `expected=CGroundAttackAircraft__Constructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/GroundAttackAircraft.cpp/_index.md`
- `0x00464520` `expected=CFEPMain__Init` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x004621e0` `expected=CFEPMain__GetActionCount` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x004621d0` `expected=CFEPMain__GetMenuType` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x00466140` `expected=CFEPMain__Cleanup` `actual=missing` `source=reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `0x00488460` `expected=CIBuffer__CreateDynamic` `actual=missing` `source=reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md`
- `0x004884f0` `expected=CIBuffer__CreateStatic` `actual=missing` `source=reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md`
- `0x00440cb8` `expected=CDamage__LoadDamageTexture` `actual=missing` `source=reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `0x0047f7ea` `expected=CHeightField__Load` `actual=missing` `source=reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__InitColorGradient.md`
- `0x004dea50` `expected=CSentinel::Constructor` `actual=missing` `source=reverse-engineering/binary-analysis/functions/Sentinel.cpp.md`
