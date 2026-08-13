# Coordinate-covered functions: the long tail

Status: active static function map
Last updated: 2026-08-13
Source File: various, each named per section by the shipped image | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

The PC-native source-coordinate instrument covers 827 functions. The largest
files were documented individually; what remains here is a **long tail of 148
function/file rows covering 141 unique functions across 93 source files**, at
most a handful each. Seven addresses occur under two source-file spellings or
coordinate groups and must not be counted twice. Per-file documents are the
wrong shape for that tail, so the rows are consolidated here.

Rows are **measured** only: entry address, current Ghidra name, body size,
callee-popped argument count from `ret imm`, the compiler's own
`__FILE__`/`__LINE__` coordinates, and the heaviest direct callees. **No purpose
is invented anywhere in this document.** Where a current name already describes
the function, that name is the claim and the evidence is consistent or silent;
nothing here contradicts one.

Argument counts are callee-popped stack arguments; `this` travels in ECX and is
not counted. A comma-separated count means the body has several `ret imm` forms.

## Measurement notes

- The instrument is **factory-biased** — coordinates are emitted only at
  debug-allocator call sites, so allocating functions are over-represented and
  pure logic, rendering and math are largely invisible. See the
  [instrument report](../pc-native-source-coordinates-2026-08-12.md).
- `monitor.h` and `Monitor.h` appear as separate sections because the shipped
  image spells the include both ways. They are one file; the split is a property
  of the binary's strings, not of this document.
- Documented here means tabled with measured facts. It does **not** mean
  contracted: none of these has a behaviour contract.

### `Array.h` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0047D590` | `CGroundVehicleGuide__Constructor` | 187 | 1 | 18 | `CDXMemoryManager__Alloc` x2; `CGuide__ctor_base` x1 |
| `0x004A0A20` | `CMechGuide__ctor` | 228 | 1 | 18 | `CDXMemoryManager__Alloc` x2; `CGuide__ctor_base` x1 |

### `array.h` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0048A3C0` | `CInfantryGuide__ctor` | 228 | 1 | 18 | `CDXMemoryManager__Alloc` x2; `CGuide__ctor_base` x1 |
| `0x004D40D0` | `CPolyBucket__Build` | 2502 | 1 | 18 | `CDXMemoryManager__Alloc` x6; `CRT__RoundDoubleWithFpuChecks` x6 |
| `0x004E6870` | `CNormalSquad__Constructor` | 241 | 0 | 18 | `CDXMemoryManager__Alloc` x2; `CSquad__Constructor` x1 |

### `Atmospherics.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00404A00` | `Atmospherics__Init` | 386 | 0 | 112–115 | `CConsole__RegisterVariable` x4; `CDXMemoryManager__Alloc` x2 |

### `BattleEngineDataManager.h` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00510800` | `CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData` | 642 | 0 | 263–310 | `CSPtrSet__Clear` x4; `CDXMemBuffer__InitFromFile` x2 |

### `Boat.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00414E50` | `CBoat__Init` | 336 | 1 | 31 | `CDXMemoryManager__Alloc` x2; `CGroundUnit__Init` x1 |

### `Building.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00417190` | `CBuilding__VFunc_9_00417190` | 439 | ? | 50–51 | `CDXMemoryManager__Alloc` x2; `CMesh__FindAnimationIndexByName` x2 |
| `0x00417390` | `CBuilding__CreateRepairPadAI` | 231 | 1 | 100–104 | `CDXMemoryManager__Alloc` x2; `CWarspite__Init` x2 |

### `bytesprite.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004184C0` | `CByteSprite__Load` | 604 | 5 | 29–191 | `CDXMemoryManager__Alloc` x6; `CDXMemoryManager__Free` x4 |

### `Camera.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00418EF0` | `CThing3rdPersonCamera__ctor` | 440 | 1 | 158–169 | `CDXMemoryManager__Alloc` x5; `CSPtrSet__AddToTail` x3 |

### `Cannon.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0041B1A0` | `CCannon__Init` | 456 | 1 | 34–35 | `CDXMemoryManager__Alloc` x3; `CMesh__FindAnimationIndexByName` x2 |

### `CollisionSeekingRound.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00425B50` | `CCollisionSeekingRound__InitCollisionLineAndSound` | 265 | 1 | 27 | `CConsole__Printf` x1; `CDXMemoryManager__Alloc` x1 |

### `collisionseekingthing.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00426A40` | `CCSRay__CreateEffect` | 482 | 1 | 314 | `CCollisionSeekingThing__Init` x1; `CDXMemoryManager__Alloc` x1 |

### `Component.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00427DD0` | `CComponent__CreateWeaponComponent` | 439 | 1 | 92–99 | `CDXMemoryManager__Alloc` x4; `CWarspite__Init` x4 |

### `console.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00429EF0` | `CConsole__RegisterBuiltinCommands` | 1307 | 0 | 805 | `CConsole__RegisterCommand` x8; `CConsole__FindCommandByName` x7 |
| `0x0042AF80` | `CConsole__RegisterCommand` | 189 | 4 | 805 | `stricmp` x1; `CDXMemoryManager__Alloc` x1 |
| `0x0042B040` | `CConsole__RegisterVariable` | 209 | 6 | 830 | `stricmp` x1; `CDXMemoryManager__Alloc` x1 |

### `Controller.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0042D640` | `CController__Init` | 308 | 3 | 967 | `CSPtrSet__Init` x2; `CDXMemoryManager__Alloc` x2 |

### `Cutscene.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0043F510` | `CCutscene__InitAnimations` | 360 | 1 | 501 | `CDXMemoryManager__Alloc` x2; `stricmp` x1 |
| `0x0043F690` | `CCutscene__Update` | 988 | 0 | 549 | `CCutscene__PrepareAnimations` x1; `CDXMemoryManager__Alloc` x1 |

### `damage.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00440B90` | `CDamage__Init` | 108 | 0 | 22 | `CDXMemoryManager__Alloc` x1; `CDamage__LoadDamageTexture` x1 |
| `0x00440C70` | `CDamage__LoadDamageTexture` | 483 | 1 | 78 | `CTGALoader__CTGALoader` x1; `CTGALoader__Load` x1 |
| `0x00441000` | `CDamage__CreateTextureBuffer` | 132 | 1 | 117 | `CDXMemoryManager__Alloc` x2; `CChunkReader__Read` x2 |

### `DataType.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0052F820` | `CPositionDataType__VFunc_1_0052f820` | 128 | 1 | 135 | `CDXMemoryManager__Alloc` x1 |

### `DestructableSegmentsController.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00444660` | `CDestructableSegmentsController__Init` | 732 | 0 | 388–424 | `CConsole__Printf` x4; `CDXMemoryManager__Alloc` x3 |
| `0x004449C0` | `CDestructableSegmentsController__CreateSegment` | 525 | 4 | 488–498 | `CDXMemoryManager__Alloc` x4; `CDestructableSegment__Init` x3 |

### `DiveBomber.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00445250` | `CDiveBomber__VFunc_9_00445250` | 302 | 1 | 18–19 | `CDXMemoryManager__Alloc` x2; `CAirUnit__Init` x1 |

### `Dropship.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00446D70` | `CDropship__Init` | 720 | 1 | 44–55 | `CDXMemoryManager__Alloc` x4; `CMCDropship__Ctor` x2 |

### `DXBattleLine.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0053A150` | `CDXBattleLine__LoadTextures` | 292 | 0 | 132–151 | `CTexture__FindTexture` x2; `CDXMemoryManager__Alloc` x2 |
| `0x0053A5E0` | `CDXBattleLine__BuildMesh` | 841 | 0 | 325–368 | `CDXMemoryManager__Alloc` x4; `CHeightField__RecomputeGridExtentsAndHeightRange` x1 |

### `DXCompass.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0053BE40` | `CDXCompass__Init` | 902 | 0 | 91–104 | `CDXMemoryManager__Alloc` x5; `FatalError_LocalizedStringId` x3 |

### `DXFont.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0053FB00` | `CDXFont__CreateGDIFont` | 1281 | 0 | 264 | `StringScratch__CopyToRotating4KBufferA` x2; `CDXTexture__GetAnimatedFrame` x2 |

### `DXFrontEndVideo.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00541430` | `CDXFrontEndVideo__InitVideo` | 541 | 0 | 256 | `CBinkOpenThread__Unlock` x3; `DebugTrace` x2 |

### `DXImposter.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00543D90` | `CDXImposter__Deserialize` | 439 | 0 | 1857–1858 | `CChunkReader__GetNext` x4; `CChunkReader__Read` x3 |
| `0x00543F50` | `CDXImposter__Create` | 232 | 0 | 2019–2055 | `CChunkReader__GetNext` x4; `CChunkReader__Read` x3 |

### `DXLandscape.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005447E0` | `CDXLandscape__CreateMipLevels` | 442 | 1 | 95–115 | `CDXMemoryManager__Alloc` x4; `eh_vector_constructor_iterator` x2 |
| `0x00544AF0` | `CDXLandscape__Init` | 457 | 1 | 169–179 | `CDXMemoryManager__Alloc` x3; `CLandscapeTexture__ResetUpdateQueue` x1 |
| `0x00545070` | `CDXLandscape__Reset` | 851 | 0 | 434–443 | `CDXLandscape__CreateMipLevels` x3; `CDXMemoryManager__Alloc` x2 |

### `DXLandscape.h` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005447E0` | `CDXLandscape__CreateMipLevels` | 442 | 1 | 170 | `CDXMemoryManager__Alloc` x4; `eh_vector_constructor_iterator` x2 |

### `DXMeshVB.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0054C0A0` | `CDXMeshVB__BuildStaticVB` | 2162 | 0 | 81–186 | `CDXMemoryManager__Alloc` x4; `CDXMemoryManager__Free` x4 |
| `0x0054C920` | `CDXMeshVB__BuildSkeletalVB` | 2254 | 0 | 425–534 | `CDXMemoryManager__Alloc` x5; `CDXMemoryManager__Free` x4 |
| `0x0054E160` | `CDXMeshVB__Load` | 920 | 2 | 1742–1756 | `CChunkReader__Read` x10; `CChunkReader__GetNext` x6 |

### `DXTexture.cpp` (4)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00557300` | `CDXTexture__LoadTextureFromFile` | 1650 | 1 | 418 | `CDXTexture__IsResourceHandleValid` x12; `CDXMemBuffer__dtor_base` x2 |
| `0x005586E0` | `CDXTexture__DumpTextureToRGBA` | 398 | 1 | 929 | `CDXMemoryManager__Alloc` x1; `DebugTrace` x1 |
| `0x00559BE0` | `CDXTexture__Deserialize` | 1154 | 0 | 3109 | `CChunkReader__GetNext` x4; `CChunkReader__Read` x3 |
| `0x005D7DC0` | `CDXTexture__Deserialize_Unwind` | 28 | 0 | 3109 | `OID__FreeObject_Callback` x1 |

### `DXTrees.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0055A420` | `CDXTrees__BuildTreeGeometry` | 1505 | 0 | 94–106 | `CVBufTexture__dtor` x2; `CDXMemoryManager__Free` x2 |

### `FastVB.cpp` (4)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0051A270` | `CFastVB__Create` | 201 | 0 | 41 | `CDXMemoryManager__Alloc` x1; `CVBuffer__ctor_base` x1 |
| `0x0051A510` | `CFastVB__Render` | 387 | 0 | 195 | `CVBuffer__Unlock` x1; `CDXMemoryManager__Alloc` x1 |
| `0x005D6820` | `CFastVB__Create__Unwind` | 22 | 0 | 41 | `OID__FreeObject_Callback` x1 |
| `0x005D6840` | `CFastVB__Render__Unwind` | 25 | 0 | 195 | `OID__FreeObject_Callback` x1 |

### `FEPBEConfig.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0044FA90` | `CFEPBEConfig__Init` | 633 | 0 | 320 | `DebugTrace` x7; `CDXMemBuffer__Close` x2 |
| `0x0044FE70` | `CFEPBEConfig__Load` | 415 | 1 | 423 | `CDXMemBuffer__Read` x10; `CDXMemoryManager__Alloc` x3 |

### `FEPDirectory.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0051AD30` | `CFEPDirectory__RefreshSaveFileList` | 283 | 1 | 208 | `CMovieCamera__GetShowHUD` x1; `PCPlatform__GetStorageDeviceInfo` x1 |

### `FEPMultiplayerStart.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0051DBA0` | `CFEPMultiplayerStart__Init` | 487 | 0 | 56–73 | `CDXMemoryManager__Alloc` x2; `CFEPMultiplayerStart__LoadPreviewMeshFromConfig` x2 |

### `FEPOptions.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0051F7E0` | `CFEPOptions__EnsureOptionsContext` | 253 | 1 | 406 | `PLATFORM__GetSysTimeFloat` x1; `CCareer__GetKillCounterTopByte_23F4` x1 |

### `FEPWingmen.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00521AE0` | `CFEPWingmen__Load` | 415 | 1 | 235 | `CDXMemBuffer__Read` x10; `CDXMemoryManager__Alloc` x3 |

### `game.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004726B0` | `CGame__RollCredits` | 480 | 0 | 4542–4543 | `PLATFORM__GetSysTimeFloat` x2; `CDXMemoryManager__Alloc` x2 |

### `GillM.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00479A50` | `CGillM__InitLegMotion` | 237 | 1 | 45 | `CMesh__FindAnimationIndexByName` x1; `CDXMemoryManager__Alloc` x1 |

### `GroundAttackAircraft.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0047BBF0` | `CGroundAttackAircraft__Init` | 376 | 1 | 19–21 | `CDXMemoryManager__Alloc` x3; `CAirUnit__Init` x1 |

### `GroundUnit.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0047C730` | `CGroundUnit__Init` | 379 | 1 | 35 | `CUnit__Init` x1; `CDXMemoryManager__Alloc` x1 |
| `0x0047C8E0` | `CGroundUnit__CreateCollisionSphere` | 132 | 1 | 67 | `CThing__InitCollisionSeekingThing` x2; `CDXMemoryManager__Alloc` x1 |

### `GroundVehicle.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0047CFD0` | `CGroundVehicle__Init` | 490 | 1 | 28–37 | `CDXMemoryManager__Alloc` x4; `CMCBuggy__CMCBuggy` x2 |

### `HiveBoss.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0047FE30` | `CHiveBoss__Init` | 463 | 1 | 34–40 | `CDXMemoryManager__Alloc` x3; `CDestructableSegmentsController__Ctor` x1 |

### `imageloader.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00488780` | `CImageLoader__LoadWidthBuffer` | 51 | 1 | 43 | `CDXMemoryManager__Alloc` x1 |
| `0x004887C0` | `CImageLoader__LoadHeightBuffer` | 51 | 1 | 50 | `CDXMemoryManager__Alloc` x1 |

### `imposter.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004888F0` | `CImposter__FindOrCreate` | 369 | 0 | 41 | `stricmp` x1; `DebugTrace` x1 |

### `InfluenceMap.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0048B010` | `CInfluenceMapManager__Load` | 1500 | 1 | 70–116 | `CDXMemBuffer__Read` x17; `CSPtrSet__First` x8 |

### `InfluenceMap.h` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0048B010` | `CInfluenceMapManager__Load` | 1500 | 1 | 115 | `CDXMemBuffer__Read` x17; `CSPtrSet__First` x8 |

### `InitThing.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0048C650` | `InitThing__CreateThingByType` | 1267 | 0 | 15–63 | `CDXMemoryManager__Alloc` x13; `CInitThing__ctor` x11 |

### `ltshell.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005126F0` | `PCLTShell__VFunc_8_005126f0` | 630 | 0 | 1152–1153 | `CEngine__InvokeCallbackIfStateMinusOne` x5; `CConsole__RenderLoadingScreen` x4 |

### `maptex.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004914B0` | `CMapTex__LoadMixerTextureSet` | 275 | 3 | 151 | `sprintf` x2; `CDXMemoryManager__Free` x2 |

### `mapwho.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004919B0` | `CMapWho__Init` | 667 | 0 | 100 | `CDXMemoryManager__Alloc` x3; `eh_vector_constructor_iterator` x1 |

### `MCBuggy.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00493190` | `CMCBuggy__Init` | 862 | 1 | 69–83 | `CDXMemoryManager__Alloc` x9; `CMesh__FindPartField40ByNameAndOwner` x3 |

### `Mech.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0049FB00` | `CMech__VFunc_35_0049fb00` | 153 | 1 | 87 | `CDXMemoryManager__Alloc` x1; `CCylinder__ctor` x1 |

### `MemoryManager.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004A13B0` | `CMemoryHeap__Init` | 446 | 4 | 379 | `_malloc` x1; `CMemoryHeap__Alloc` x1 |
| `0x004A2A80` | `CMemoryManager__DumpMemory` | 1385 | 1 | 1800–1914 | `sprintf` x17; `CDXMemBuffer__WriteBytes` x15 |

### `MeshCollisionVolume.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004AD600` | `CMeshCollisionVolume__SetPartBounds` | 495 | 3 | 553 | `vector_constructor_iterator_nothrow` x2; `CDXMemoryManager__Alloc` x1 |
| `0x005D3980` | `CMeshCollisionVolume__SetPartBounds_Unwind` | 25 | 0 | 553 | `OID__FreeObject_Callback` x1 |

### `meshpose.h` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004DC370` | `CRTMesh__Init` | 1502 | 1 | 33–36 | `CDXMemoryManager__Alloc` x12; `CConsole__RegisterVariable` x10 |

### `MeshRenderer.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004B6350` | `CMeshRenderer__RenderMesh` | 2134 | 0 | 519 | `CMeshRenderer__CopyBasisAndRefreshTime` x8; `CDXMemoryManager__Alloc` x1 |

### `Mine.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004BA150` | `CMine__Init` | 821 | 1 | 31 | `Vec3__SetXYZ` x3; `CMCMine__Constructor` x2 |
| `0x004BA4D0` | `CMine__VFunc_66_004ba4d0` | 799 | 0 | 88 | `CMapWho__GetFirstEntryWithinRadius` x1; `CMapWhoEntry__GetOwner` x1 |

### `Missile.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004BAAE0` | `CMissile__Init` | 303 | 1 | 11 | `CDXMemoryManager__Alloc` x1; `eh_vector_constructor_iterator` x1 |

### `mixermap.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00523190` | `CMixerMap__InitSlot` | 106 | 1 | 134 | `CChunkReader__GetNext` x3; `CChunkReader__Read` x2 |
| `0x005232B0` | `CMixerMap__Init` | 270 | 1 | 246–247 | `CDXMemoryManager__Alloc` x2; `CChunkReader__GetNext` x2 |

### `Monitor.h` (4)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004198D0` | `CPanCamera__ctor` | 327 | 3 | 24 | `CDXMemoryManager__Alloc` x1; `CSPtrSet__ctor` x1 |
| `0x0041A210` | `CMovieCamera__ctor` | 337 | 1 | 24 | `CDXMemoryManager__Alloc` x1; `CSPtrSet__ctor` x1 |
| `0x004A3510` | `CMenuItem__Init` | 252 | 6 | 24 | `CDXMemoryManager__Alloc` x1; `CSPtrSet__Init` x1 |
| `0x004A3630` | `CMenuItem__InitWithIcon` | 252 | 6 | 24 | `CDXMemoryManager__Alloc` x1; `CSPtrSet__Init` x1 |

### `monitor.h` (5)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0042D640` | `CController__Init` | 308 | 3 | 24 | `CSPtrSet__Init` x2; `CDXMemoryManager__Alloc` x2 |
| `0x0042E610` | `CController__SetToControl` | 204 | 1 | 24 | `CDXMemoryManager__Alloc` x2; `CSPtrSet__AddToHead` x2 |
| `0x00444660` | `CDestructableSegmentsController__Init` | 732 | 0 | 24 | `CConsole__Printf` x4; `CDXMemoryManager__Alloc` x3 |
| `0x004D28C0` | `CPlayer__GotoFPView` | 246 | 0 | 24 | `CDXMemoryManager__Alloc` x2; `CSPtrSet__Init` x1 |
| `0x004E5700` | `CSphereTrigger__Hit` | 315 | 2 | 24 | `CDXMemoryManager__Alloc` x2; `CComplexThing__Hit` x1 |

### `Music.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004BB6B0` | `CMusic__AddToPlayList` | 265 | 1 | 318 | `stricmp` x2; `CDXMemoryManager__Alloc` x1 |

### `oids.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004BF090` | `OID__CreateObject` | 2203 | 0 | 40–72 | `CDXMemoryManager__Alloc` x20; `CComplexThing__ctor_base` x10 |

### `ParticleDescriptor.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004C5410` | `CPDFoR__Update` | 741 | 1 | 2025 | `CParticleDescriptor__Load12DwordsAndMarkDirty` x2; `CDXMemoryManager__Alloc` x1 |

### `ParticleManager.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004CAED0` | `CParticle__SetParticleResource` | 93 | 1 | 194 | `CDXMemoryManager__Free` x1; `CDXMemoryManager__Alloc` x1 |
| `0x004CB3D0` | `CParticleManager__CreateEffect` | 485 | 8 | 704 | `vector_constructor_iterator_nothrow` x2; `CParticleManager__AllocateParticle` x1 |
| `0x004CB5C0` | `CParticleManager__AllocateParticle` | 823 | 2 | 738 | `CGame__IsMultiplayer` x2; `CDXMemoryManager__Alloc` x1 |

### `PauseMenu.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004D0810` | `CPauseMenu__ButtonPressed` | 1325 | 2 | 1633–2290 | `CGame__GetController` x9; `CDXMemoryManager__Alloc` x5 |

### `PCPlatform.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005154E0` | `PCPlatform__Init` | 253 | 0 | 27 | `CConsole__Printf` x3; `CDXMemoryManager__Alloc` x1 |
| `0x005155E0` | `PCPlatform__LoadFonts` | 457 | 0 | 79–103 | `DebugTrace` x4; `CDXMemoryManager__Alloc` x4 |

### `PCRTID.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00516580` | `PCRTID__CreateObject` | 285 | 0 | 17–21 | `CDXMemoryManager__Alloc` x4; `CRTCutscene__CRTCutscene` x1 |

### `pcsoundmanager.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005169B0` | `CPCSoundManager__Init` | 1300 | 0 | 229 | `CConsole__Printf` x13; `CDXMemoryManager__Alloc` x1 |
| `0x005172A0` | `CPCSoundManager__CreateSampleFromFile` | 411 | 3 | 679–714 | `CDXMemoryManager__Free` x4; `CDXMemoryManager__Alloc` x3 |
| `0x005176D0` | `CPCSoundManager__CreateSampleFromData` | 184 | 4 | 753 | `CDXMemoryManager__Free` x1; `CDXMemoryManager__Alloc` x1 |

### `Player.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004D28C0` | `CPlayer__GotoFPView` | 246 | 0 | 58 | `CDXMemoryManager__Alloc` x2; `CSPtrSet__Init` x1 |
| `0x004D29C0` | `CPlayer__Goto3rdPersonView` | 133 | 0 | 67 | `CDXMemoryManager__Alloc` x1; `CThing3rdPersonCamera__ctor` x1 |

### `RadarWarningReceiver.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004D66B0` | `CRadarWarningReceiver__Update` | 851 | 0 | 65 | `LinkedPtrCursor__MoveFirstAndGet` x3; `LinkedPtrCursor__MoveNextAndGet` x3 |

### `ResourceAccumulator.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004D7200` | `CResourceAccumulator__ReadResourceFile` | 2071 | 0 | 768–816 | `CChunkReader__Read` x7; `sprintf` x7 |

### `RTCutscene.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004DBD80` | `CRTCutscene__Init` | 208 | 1 | 42–50 | `CDXMemoryManager__Alloc` x3; `CRenderThing__Init` x1 |

### `rtmesh.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004DC370` | `CRTMesh__Init` | 1502 | 1 | 90–178 | `CDXMemoryManager__Alloc` x12; `CConsole__RegisterVariable` x10 |

### `SoundManager.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004E00D0` | `CSoundManager__Init` | 503 | 0 | 81–90 | `CConsole__RegisterVariable` x4; `CDXMemoryManager__Alloc` x2 |

### `SphereTrigger.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004E5700` | `CSphereTrigger__Hit` | 315 | 2 | 83 | `CDXMemoryManager__Alloc` x2; `CComplexThing__Hit` x1 |

### `SPtrSet.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004E59F0` | `CSPtrSet__Initialise` | 131 | 0 | 137 | `CConsole__Printf` x1; `CDXMemoryManager__Alloc` x1 |

### `SquadNormal.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004E91F0` | `CSquadNormal__SpawnMembers` | 577 | 0 | 1163 | `CStaticShadows__SampleShadowHeightBilinear` x3; `LinkedPtrCursor__MoveFirstAndGet` x1 |

### `SquadRelaxed.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004EA780` | `CRelaxedSquad__VFunc_67_004ea780` | 191 | 4 | 100 | `CDXMemoryManager__Alloc` x1; `CGenericActiveReader__SetReader` x1 |

### `StaticShadows.cpp` (4)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004EBE40` | `CStaticShadows__UpdateLightVectorAndRebuild` | 366 | 0 | 193 | `CDXMemoryManager__Alloc` x1; `CStaticShadows__BuildShadowMaps` x1 |
| `0x004EC2F0` | `CStaticShadows__BuildShadowMaps` | 7620 | 0 | 394–623 | `Vec3__SetXYZ` x18; `CStaticShadows__SampleShadowHeightBilinear` x17 |
| `0x004EE0F0` | `CStaticShadows__ApplyShadowsToGrid` | 799 | 4 | 839 | `sprintf` x1; `DebugTrace` x1 |
| `0x004EE8F0` | `CStaticShadows__Load` | 662 | 0 | 1074–1122 | `CChunkReader__Read` x13; `CDXMemoryManager__Alloc` x4 |

### `Submarine.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004EEC80` | `CSubmarine__Init` | 305 | 1 | 29–30 | `CDXMemoryManager__Alloc` x2; `CUnit__Init` x1 |

### `tgaloader.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004F2CE0` | `CTGALoader__Load` | 1071 | 0 | 119 | `CDXMemBuffer__Read` x14; `CDXMemBuffer__Close` x4 |

### `thing.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004F39C0` | `CThing__InitCollisionSeekingThing` | 137 | 1 | 310 | `CDXMemoryManager__Alloc` x1; `CConsole__Printf` x1 |
| `0x004F44A0` | `CComplexThing__SetAnimMode` | 136 | 3 | 767 | `CDXMemoryManager__Alloc` x1; `CAnimation__ctor` x1 |

### `TokenArchive.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004F57B0` | `CTokenArchive__ReadNextToken` | 789 | 4 | 362 | `CRT__SscanfFromString` x3; `CDXMemoryManager__Alloc` x2 |
| `0x004F5BA0` | `CTokenArchive__ResolveReferences` | 205 | 1 | 450 | `CDXMemoryManager__Free` x2; `CDXMemoryManager__Alloc` x1 |

### `tree.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004F6480` | `CTree__VFunc_35_004f6480` | 180 | 1 | 143 | `CDXMemoryManager__Alloc` x1; `CThing__InitCollisionSeekingThing` x1 |

### `vbuftexture.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005005E0` | `CVBufTexture__ResizeVertexBuffer` | 522 | 1 | 182 | `FatalError_LocalizedStringId` x3; `CVBuffer__EnsureLock` x2 |
| `0x005007F0` | `CVBufTexture__ResizeIndexBuffer` | 457 | 1 | 251 | `FatalError_LocalizedStringId` x3; `CIBuffer__LockDirect` x2 |
| `0x00501280` | `CVBufTexture__GetOrCreate` | 139 | 0 | 750 | `CDXMemoryManager__Alloc` x1; `CVBufTexture__CVBufTexture` x1 |

### `VertexShader.cpp` (4)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00502060` | `CVertexShader__Create` | 549 | 0 | 701 | `CDXMemoryManager__Alloc` x2; `stricmp` x1 |
| `0x005022A0` | `CVertexShader__LoadFromFile` | 378 | 4 | 797 | `CVertexShader__CompileScriptWithDirectiveParser` x1; `DebugTrace` x1 |
| `0x00502420` | `CVertexShader__CompileShader` | 968 | 0 | 941–996 | `_strstr` x7; `CDXMemoryManager__Free` x3 |
| `0x00503F90` | `CVertexShader__Clone` | 862 | 0 | 2458–2590 | `CDXMemoryManager__Alloc` x8; `CChunkReader__GetNext` x7 |

### `WarspiteDome.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x005047E0` | `CWarspiteDome__Init` | 417 | 1 | 25–29 | `CDXMemoryManager__Alloc` x3; `CMCWarspiteDome__Constructor` x2 |

### `wavread.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00505210` | `WavRead__ReadMMIO` | 435 | 0 | 61 | `CDXMemoryManager__Alloc` x2; `CDXMemoryManager__Free` x1 |

### `WaypointManager.cpp` (2)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x00505AE0` | `CWaypointManager__LoadWaypoints` | 198 | 0 | 114 | `CDXMemBuffer__Read` x1; `CDXMemoryManager__Alloc` x1 |
| `0x005D5860` | `CWaypointManager__LoadWaypoints_unwind` | 22 | 0 | 114 | `OID__FreeObject_Callback` x1 |

### `world.cpp` (3)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0050AC70` | `CWorld__LoadScriptEvents` | 294 | 1 | 192–197 | `CDXMemoryManager__Alloc` x3; `CDXMemBuffer__Read` x2 |
| `0x0050B780` | `CWorld__DeserializeWorld` | 423 | 1 | 644–646 | `CChunkReader__GetNext` x4; `CConsole__Status` x3 |
| `0x0050D580` | `CWorld__InitLODLists` | 252 | 0 | 1335–1336 | `CDXMemoryManager__Alloc` x3; `CWorld__InitOccupancyBitplanes` x3 |

### `WorldMeshList.cpp` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0050D9E0` | `CWorldMeshList__Add` | 572 | 0 | 46 | `CDXMemoryManager__Alloc` x2; `CGame__IsRunningResources` x1 |

### `WorldPhysicsManager.h` (1)

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0042EE90` | `CUnitAI__CreateAndRegisterByName` | 305 | 0 | 1623–2417 | `CSPtrSet__Init` x4; `CDXMemoryManager__Alloc` x2 |
