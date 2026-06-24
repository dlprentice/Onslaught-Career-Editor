# Source File Inventory

> Complete inventory of all source files in BEA.exe vs what Stuart provided
> Generated: December 2025
> Refresh note: 2026-02-11 inventory refresh added below

## 2026-02-11 Refresh (Authoritative Counts)

Inventory-level parse completed for both reference repos:

- `references/Onslaught`: **111 files** total (`52 .cpp`, `53 .h`, plus ancillary files)
- `references/AYAResourceExtractor`: **75 files** total (`54` source files in `.cs/.cpp/.c/.h`)

Authoritative artifact manifests:

- `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv`
- `reverse-engineering/source-code/aya-resourceextractor-file-manifest-2026-02-11.tsv`

For methodology and metrics, see:

- `reverse-engineering/source-code/full-source-parse-2026-02-11.md`

## Summary

| Category | Count |
|----------|-------|
| Debug paths in binary | **169** |
| Stuart provided (.cpp) | **52** |
| Stuart NOT provided (.cpp strict request delta) | **124** |
| Stuart provided (.h) | 53 |

---

## Files Stuart PROVIDED (52 .cpp files)

These files are in `references/Onslaught/`:

| File | In Binary | Notes |
|------|-----------|-------|
| activereader.cpp | NO | Not in binary debug paths |
| actor.cpp | NO | Not in binary debug paths |
| Array.cpp | NO | Not in binary debug paths |
| BattleEngine.cpp | YES | Core combat system |
| BattleEngineConfigurations.cpp | YES | Config loading |
| BattleEngineDataManager.cpp | YES | Weapon loadouts |
| BattleEngineJetPart.cpp | NO | Not in binary debug paths |
| BattleEngineWalkerPart.cpp | NO | Not in binary debug paths |
| Camera.cpp | YES | Camera system |
| Career.cpp | NO* | Career.cpp not in debug paths, but functions exist |
| chunker.cpp | YES | Resource chunking |
| CLIParams.cpp | NO* | Functions exist but no debug path |
| Controller.cpp | YES | Input handling |
| d3dapp.cpp | NO | Internal dev tool |
| DXEngine.cpp | NO | Not in binary - different architecture |
| DXFrontend.cpp | NO | Not in binary |
| DXGame.cpp | NO | Not in binary |
| DXMemBuffer.cpp | YES | Buffered file I/O |
| DXMemoryManager.cpp | NO | Not in binary |
| EditorD3DApp.cpp | NO | Internal dev tool - stripped |
| EndLevelData.cpp | NO | Runtime-only, never saved |
| engine.cpp | YES | Core engine |
| event.cpp | NO | Not in binary debug paths |
| eventmanager.cpp | YES | Event scheduling |
| FEPGoodies.cpp | YES | Goodies gallery |
| FEPLoadGame.cpp | YES | Save loading |
| FEPSaveGame.cpp | YES | Save saving, cheat codes |
| FrontEnd.cpp | YES | Main menu system |
| game.cpp | YES | Main game init |
| InitThing.cpp | YES | Object factory |
| ltshell.cpp | YES | WinMain entry point |
| MemoryCard.cpp | NO | Console-only |
| MemoryManager.cpp | YES | Heap management |
| Music.cpp | YES | Music playback |
| PCController.cpp | NO | Not in binary debug paths |
| PCEngine.cpp | NO | Not in binary debug paths |
| PCFEPLoadGame.cpp | NO | Not in binary debug paths |
| PCFEPSaveGame.cpp | NO | Not in binary debug paths |
| PCFrontend.cpp | NO | Not in binary debug paths |
| PCGame.cpp | NO | Not in binary debug paths |
| PCMemoryCard.cpp | NO | Not in binary debug paths |
| PCPlatform.cpp | YES | Save file operations |
| pcsoundmanager.cpp | YES | DirectSound |
| Platform.cpp | YES | Platform abstraction |
| Player.cpp | YES | Player entity |
| ResourceAccumulator.cpp | YES | AYA archive loading |
| scheduledevent.cpp | NO* | No direct debug path string in retail build; key methods mapped via event-manager callsites (`CScheduledEvent__Set` @ 0x004de1f0, `CScheduledEvent__dtor` @ 0x004de230) |
| SoundManager.cpp | YES | Audio system |
| SPtrSet.cpp | YES | Smart pointer list |
| storage.cpp | NO | Not in binary debug paths |
| thing.cpp | YES | Base game object |
| XBoxMemoryCard.cpp | NO | Xbox-only |

**Stuart's files IN binary:** ~30
**Stuart's files NOT in binary:** ~22 (internal tools, console-only, different architecture)

---

## Files Stuart DID NOT PROVIDE (124 .cpp request-delta files)

These debug paths exist in BEA.exe but Stuart has not provided the source:

### Core Gameplay (Not Provided)

| Address | File | Description (from RE) |
|---------|------|----------------------|
| 0x00622cf4 | AirUnit.cpp | Aircraft base class |
| 0x00622ec4 | Atmospherics.cpp | Weather system - rain, snow, lightning |
| 0x00623990 | Boat.cpp | Surface vessel |
| 0x00623a78 | Bomber.cpp | Bomber aircraft |
| 0x00623ab8 | BSpline.cpp | B-spline curves for camera |
| 0x00623af4 | Building.cpp | Static structures |
| 0x00623c18 | bytesprite.cpp | RLE sprite rendering |
| 0x00623dd4 | Cannon.cpp | Weapon system |
| 0x006243bc | Carrier.cpp | Transport vessel |
| 0x00624400 | Carver.cpp | Flying mech enemy |
| 0x00624630 | CollisionSeekingRound.cpp | Homing projectiles |
| 0x006246d8 | collisionseekingthing.cpp | Collision avoidance |
| 0x006247f8 | Component.cpp | Entity components |
| 0x00624d0c | console.cpp | Developer console |
| 0x0062568c | CPhysicsScript.cpp | Physics scripting |
| 0x00625818 | CPhysicsScriptStatements.cpp | 272+ statement types |
| 0x0062811c | Cutscene.cpp | Cutscene playback |
| 0x006282dc | damage.cpp | Damage system |
| 0x006287b4 | DestructableSegmentsController.cpp | Destructible parts |
| 0x006289c0 | DiveBomber.cpp | Dive bomber AI |
| 0x00628a54 | Dropship.cpp | Transport aircraft |
| 0x0062cadc | GroundAttackAircraft.cpp | Ground attack AI |
| 0x0062cb0c | GroundUnit.cpp | Ground unit base |
| 0x0062cb30 | GroundVehicle.cpp | Wheeled vehicles |
| 0x0062cc98 | HiveBoss.cpp | Boss enemy |
| 0x0062d4a8 | Infantry.cpp | Foot soldiers |
| 0x0062e0e0 | Mech.cpp | Player mech |
| 0x006309a4 | Mine.cpp | Explosive mines |
| 0x006309c0 | Missile.cpp | Guided missiles |
| 0x00631630 | Plane.cpp | Fighter aircraft |
| 0x00631d38 | Round.cpp | Projectile base |
| 0x0063221c | Sentinel.cpp | Turret enemy |
| 0x00632abc | Submarine.cpp | Underwater vessel |
| 0x00632ccc | Tentacle.cpp | Boss tentacles |
| 0x00633240 | ThunderHead.cpp | Boss mech |
| 0x00633b6c | Unit.cpp | Unit base class |
| 0x0063d12c | Warspite.cpp | Naval AI |
| 0x0063d170 | WarspiteDome.cpp | Boss dome component |

### Frontend Pages (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x00628fac | FEPBEConfig.cpp | Weapon loadout config |
| 0x0062913c | FEPDebriefing.cpp | Mission results |
| 0x0062921c | FEPDevelopment.cpp | Dev menu (level select) |
| 0x00629414 | FEPMain.cpp | Main menu |
| 0x0063fb4c | FEPDirectory.cpp | Save directory browser |
| 0x0063fc24 | FEPMultiplayerStart.cpp | Multiplayer start |
| 0x0063fc88 | FEPOptions.cpp | Options menu |
| 0x0063fd4c | FEPWingmen.cpp | Wingmen selection |
| 0x0062f7d8 | MenuItem.cpp | Menu UI components |
| 0x006314dc | PauseMenu.cpp | Pause menu |
| 0x0062ce76 | Hud.cpp | HUD display |

### Rendering System (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x0062c968 | gcgamut.cpp | View frustum culling |
| 0x0062cbd0 | HeightField.cpp | Terrain height data |
| 0x0062d390 | ibuffer.cpp | Index buffers |
| 0x0062d3cc | imageloader.cpp | Image loading base |
| 0x0062d3f0 | imposter.cpp | Billboard sprites |
| 0x0062d824 | landscapeib.cpp | Terrain index buffers |
| 0x0062d8e0 | LandscapeTexture.cpp | Terrain texturing |
| 0x0062db04 | maptex.cpp | Map textures |
| 0x0062db88 | mapwho.cpp | Quadtree spatial |
| 0x0062f8e8 | mesh.cpp | Mesh loading |
| 0x0062fe40 | MeshCollisionVolume.cpp | Mesh collision |
| 0x0062fe70 | MeshPart.cpp | Mesh geometry |
| 0x00630178 | MeshRenderer.cpp | Mesh rendering |
| 0x006316bc | PolyBucket.cpp | Spatial partitioning |
| 0x00631e2c | RTCutscene.cpp | Real-time cutscenes |
| 0x00631f28 | rtmesh.cpp | Runtime mesh LOD |
| 0x006329f8 | StaticShadows.cpp | Shadow mapping |
| 0x00632ef0 | texture.cpp | Texture system |
| 0x0063314c | tgaloader.cpp | TGA loading |
| 0x00633d08 | vbuffer.cpp | Vertex buffers |
| 0x00633d5c | vbuftexture.cpp | VB + texture batching |
| 0x0063cf78 | VertexShader.cpp | Shader compilation |
| 0x0063fb24 | FastVB.cpp | Fast quad rendering |

### DirectX Rendering (Not Provided - 18 files)

| Address | File | Description |
|---------|------|-------------|
| 0x00650324 | DXBattleLine.cpp | Battle line HUD |
| 0x006503d4 | DXClouds.cpp | Cloud rendering |
| 0x00650454 | DXCompass.cpp | Compass HUD |
| 0x00650644 | DXFMV.CPP | Bink video playback |
| 0x00650670 | DXFont.cpp | Font rendering |
| 0x00650744 | DXFrontEndVideo.cpp | Menu video |
| 0x006508cc | DXImposter.cpp | Imposter rendering |
| 0x00650a88 | DXKempyCube.cpp | Environment mapping |
| 0x00650bdc | DXLandscape.cpp | Terrain rendering |
| 0x00651244 | DXMeshVB.cpp | Mesh vertex buffers |
| 0x00651d60 | DXPalletizer.cpp | Color quantization |
| 0x00651dcc | DXParticleTexture.cpp | Particle textures |
| 0x0065211c | DXPatchManager.cpp | Terrain LOD patches |
| 0x00652410 | DXShadows.cpp | Shadow system |
| 0x00652534 | DXSnow.cpp | Snow particles |
| 0x006525a0 | DXSurf.cpp | Water/wave surface |
| 0x0065269c | DXTexture.cpp | Texture management |
| 0x006529b0 | DXTrees.cpp | Tree billboards |

### MissionScript System (Not Provided - 7 files)

| Address | File | Description |
|---------|------|-------------|
| 0x0064c5c4 | MissionScript/AsmInstruction.cpp | Bytecode VM, 27 opcodes |
| 0x0064cc80 | MissionScript/DataType.cpp | Script data types |
| 0x0064cce0 | MissionScript/EventFunction.cpp | Event triggers |
| 0x0064fa40 | MissionScript/IScript.cpp | Script instructions |
| 0x0064fe98 | MissionScript/ScriptEventNB.cpp | Non-blocking events |
| 0x00650040 | MissionScript/ScriptObjectCode.cpp | Bytecode VM main loop |
| 0x00650134 | MissionScript/Symtab.cpp | Symbol table |

### Motion Controllers (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x0062c9e8 | GillM.cpp | Motion controller |
| 0x0062ca6c | GillMHead.cpp | Head motion |
| 0x0062dc80 | MCBuggy.cpp | Wheeled vehicle physics |
| 0x0062df60 | MCMech.cpp | Mech leg animation |
| 0x0062e06c | MCTentacle.cpp | Tentacle animation |

### AI & Navigation (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x0062d61c | InfluenceMap.cpp | Territorial AI |
| 0x0063283c | SquadNormal.cpp | Squad AI |
| 0x00632918 | SquadRelaxed.cpp | Idle AI state |
| 0x0063d1f8 | WaypointManager.cpp | Waypoint system |

### World & Particles (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x00630cd8 | ParticleDescriptor.cpp | Particle definitions |
| 0x00630e60 | ParticleManager.cpp | Particle system |
| 0x00630fb0 | ParticleSet.cpp | Particle types |
| 0x00632650 | SpawnerThng.cpp | Wave spawning |
| 0x0063270c | SphereTrigger.cpp | Trigger volumes |
| 0x00633a84 | tree.cpp | Environmental trees |
| 0x0063d2ac | world.cpp | Level loading |
| 0x0063d488 | WorldMeshList.cpp | World mesh tracking |
| 0x0063d798 | WorldPhysicsManager.cpp | Physics object factory |

### Other Systems (Not Provided)

| Address | File | Description |
|---------|------|-------------|
| 0x00629a9c | flexarray.cpp | Dynamic arrays |
| 0x00630c20 | oids.cpp | Object allocation |
| 0x00631784 | RadarWarningReceiver.cpp | RWR threat detection |
| 0x00632dd8 | text.cpp | Localization |
| 0x00633a00 | TokenArchive.cpp | Config parsing |
| 0x00633ab8 | triangulate.cpp | Mesh triangulation |
| 0x0063d1b0 | wavread.cpp | WAVE audio loading |
| 0x00640030 | mixermap.cpp | Audio mixer |
| 0x0063e284 | PCRTID.cpp | Runtime ID factory |

---

## Files to Request from Stuart

**High Priority (Current Static-Validation Blockers):**
1. AirUnit.cpp - Air-vehicle base behavior contracts
2. Carrier.cpp - Carrier behavior/path contracts
3. DiveBomber.cpp - Air attack behavior contracts
4. FEPDebriefing.cpp - Career/debrief frontend path parity
5. HeightField.cpp - Terrain/height queries and collision assumptions
6. Infantry.cpp - Infantry behavior contracts
7. Mech.cpp - Player vehicle behavior contracts
8. PauseMenu.cpp - Frontend pause/debug/menu flow parity
9. ThunderHead.cpp - Boss/system behavior contracts
10. Unit.cpp - Core unit ownership/type contracts
11. world.cpp - Level/world lifecycle contracts
12. text.cpp - Localization/runtime text behavior contracts

**Medium Priority (Rendering):**
1. mesh.cpp - Mesh loading
2. texture.cpp - Texture system
3. DXLandscape.cpp - Terrain

**Low Priority (Already RE'd):**
- MissionScript/*.cpp - We've documented the bytecode VM
- Most DX*.cpp files - We've documented rendering

---

## Statistics

- **Total debug paths in binary:** 169
- **Stuart provided:** 52 files (31%)
- **Stuart NOT provided:** 124 files (73%)
- **Files we've documented (Phase 1):** 155 (includes 7 new stubs)
- **Files with stub documentation:** 7 (pending xref discovery)
- **Files covered by related files:** 2 (collisionseekingthing.cpp in CollisionSeekingRound.cpp, MenuItem.cpp as MenuItem.cpp_index.md)
- **Files not yet documented:** ~12

---

## Stub Files Created (Dec 2025)

The following files have stub documentation noting "0 xrefs found":

| File | Debug Path | Notes |
|------|------------|-------|
| AsmInstruction.cpp | 0x0064c5c4 | MissionScript VM, claimed 13 functions |
| Carver.cpp | 0x00624400 | Flying mech AI, claimed 12 functions |
| CPhysicsScriptStatements.cpp | 0x00625818 | 272+ statement types, claimed 15 factories |
| DXClouds.cpp | 0x006503d4 | Cloud rendering, claimed 2 functions |
| DXFMV.cpp | 0x00650644 | Bink video playback, claimed 8 functions |
| DXKempyCube.cpp | 0x00650a88 | Environment cube mapping, claimed 5 functions |
| DXShadows.cpp | 0x00652410 | Shadow system, claimed 3 functions |

These were referenced in `_index.md` as documented but the actual files were missing.

---

*Generated from Phase 1 reverse engineering (Dec 2025)*
*Updated: 2025-12-16 - Added stub files for undocumented source files*
