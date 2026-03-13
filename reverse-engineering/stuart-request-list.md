# Source Code Request List for Stuart

> Prioritized list of source files we'd love to have for game preservation and save editor development.
> Generated: December 2025

## Context

Stuart, thank you for the 52 .cpp files you've already shared! They've been invaluable for understanding the save file format and building the career editor. We've also done extensive reverse engineering of the PC port via Ghidra, including full-function naming coverage of the retail binary.

This list prioritizes files that would help us:
1. Complete the save file editor (unlock all features safely)
2. Understand unit/weapon systems for future modding potential
3. Preserve knowledge of this excellent game for the community

**Files already provided:** 52 .cpp files (see end of document)
**Files in binary we don't have:** 117 source files

---

## HIGH PRIORITY (14 files)

Core gameplay files critical for understanding game mechanics and save interactions.

### Unit System (Core Classes)
| File | Why We Need It |
|------|----------------|
| **Unit.cpp** | Base class for all units - need to understand damage, transforms, effects |
| **Mech.cpp** | Player vehicle - leg motion, cockpit, targeting systems |
| **Cannon.cpp** | Weapon system - firing, state machine, ammunition |
| **Missile.cpp** | Guided missiles - seeking behavior, damage |
| **Round.cpp** | Projectile base class - trajectory, collision |

### World & Level Loading
| File | Why We Need It |
|------|----------------|
| **world.cpp** | Level loading, script events - critical for understanding level state |

### Save-Related
| File | Why We Need It |
|------|----------------|
| **Hud.cpp** | HUD display - rank display, status indicators |
| **PauseMenu.cpp** | God mode toggle display logic |

### AI & Combat
| File | Why We Need It |
|------|----------------|
| **damage.cpp** | Damage system - how damage is applied and tracked |
| **InfluenceMap.cpp** | Territorial AI - strategic layer |
| **CollisionSeekingRound.cpp** | Homing projectiles - targeting logic |

### Bosses
| File | Why We Need It |
|------|----------------|
| **HiveBoss.cpp** | Boss encounter - state machine |
| **ThunderHead.cpp** | Boss mech - unique mechanics |
| **Warspite.cpp** | Naval AI controller |

---

## MEDIUM PRIORITY (23 files)

Would enhance our understanding but not critical for the save editor.

### Unit Subclasses
| File | Notes |
|------|-------|
| AirUnit.cpp | Aircraft base - trail/engine effects |
| Bomber.cpp | Bomber AI |
| DiveBomber.cpp | Dive bomber AI - targeting |
| Dropship.cpp | Transport aircraft |
| GroundUnit.cpp | Ground unit base |
| GroundVehicle.cpp | Wheeled vehicles |
| Infantry.cpp | Foot soldiers |
| Plane.cpp | Fighter aircraft |
| Submarine.cpp | Underwater vessels |
| Carrier.cpp | Transport vessel |
| Boat.cpp | Surface vessels |
| Sentinel.cpp | Turret enemy |
| Tentacle.cpp | Boss tentacles |
| WarspiteDome.cpp | Boss component |
| Mine.cpp | Explosive mines |

### Motion Controllers
| File | Notes |
|------|-------|
| MCMech.cpp | Procedural leg animation - already have good RE docs |
| MCBuggy.cpp | Wheeled vehicle physics |
| MCTentacle.cpp | Tentacle animation |
| GillM.cpp | Motion controller base |
| GillMHead.cpp | Head motion |

### Frontend Pages
| File | Notes |
|------|-------|
| FEPDebriefing.cpp | Mission results screen |
| FEPBEConfig.cpp | Weapon loadout config |
| MenuItem.cpp | Menu UI components |

---

## LOW PRIORITY (80 files)

We've already documented these well through reverse engineering, or they're rendering/utility code less relevant to gameplay.

### MissionScript System (7 files) - WELL DOCUMENTED
We've reverse engineered the bytecode VM thoroughly (27 opcodes, 272+ statement types).

| File | Our Documentation Status |
|------|-------------------------|
| AsmInstruction.cpp | Documented - VM opcodes |
| DataType.cpp | Documented - script data types |
| EventFunction.cpp | Documented - event triggers |
| IScript.cpp | Stub - script instructions |
| ScriptEventNB.cpp | Documented - non-blocking events |
| ScriptObjectCode.cpp | Documented - VM main loop |
| Symtab.cpp | Documented - symbol table |

### DirectX Rendering (18 files) - PARTIALLY DOCUMENTED
Rendering code is interesting but not needed for save editing.

| File | Our Documentation Status |
|------|-------------------------|
| DXLandscape.cpp | Full docs (20 functions) |
| DXTexture.cpp | Full docs (5 functions) |
| DXFont.cpp | Full docs (5 functions) |
| DXCompass.cpp | Full docs (7 functions) |
| DXMeshVB.cpp | Full docs (3 functions) |
| DXImposter.cpp | Full docs (2 functions) |
| DXClouds.cpp | Stub doc |
| DXFMV.cpp | Stub doc - Bink video |
| DXKempyCube.cpp | Stub doc - env mapping |
| DXShadows.cpp | Stub doc |
| DXSnow.cpp | Stub doc |
| DXSurf.cpp | Stub doc - water |
| DXTrees.cpp | Stub doc |
| DXBattleLine.cpp | Stub doc |
| DXFrontEndVideo.cpp | Stub doc |
| DXPalletizer.cpp | Stub doc |
| DXParticleTexture.cpp | Stub doc |
| DXPatchManager.cpp | Stub doc |

### Rendering Core (20 files) - WELL DOCUMENTED
| File | Status |
|------|--------|
| mesh.cpp | Full docs (6 functions) |
| MeshPart.cpp | Full docs (12 functions) |
| MeshRenderer.cpp | Full docs |
| MeshCollisionVolume.cpp | Full docs |
| texture.cpp | Full docs (5 functions) |
| tgaloader.cpp | Full docs |
| imageloader.cpp | Full docs (7 functions) |
| rtmesh.cpp | Full docs (7 functions) |
| StaticShadows.cpp | Full docs (8 functions) |
| VertexShader.cpp | Full docs (5 functions) |
| HeightField.cpp | Full docs |
| LandscapeTexture.cpp | Full docs (14 functions) |
| landscapeib.cpp | Full docs |
| maptex.cpp | Full docs (6 functions) |
| imposter.cpp | Full docs |
| vbuffer.cpp | Full docs (12 functions) |
| vbuftexture.cpp | Full docs (18 functions) |
| ibuffer.cpp | Full docs (9 functions) |
| FastVB.cpp | Full docs (7 functions) |
| gcgamut.cpp | Stub doc - view frustum |

### Managers & Systems (15 files) - WELL DOCUMENTED
| File | Status |
|------|--------|
| ParticleManager.cpp | Full docs (4 functions) |
| ParticleDescriptor.cpp | Full docs |
| ParticleSet.cpp | Full docs (7 functions) |
| SoundManager.cpp | Full docs |
| MemoryManager.cpp | Full docs (6 functions) |
| eventmanager.cpp | Full docs |
| WaypointManager.cpp | Full docs (3 functions) |
| Camera.cpp | Full docs (3 functions) |
| BSpline.cpp | Full docs (4 functions) |
| Cutscene.cpp | Full docs (3 functions) |
| RTCutscene.cpp | Full docs (6 functions) |
| SpawnerThng.cpp | Full docs (13 functions) |
| SphereTrigger.cpp | Full docs |
| WorldMeshList.cpp | Full docs |
| WorldPhysicsManager.cpp | Full docs (13 functions) |

### Spatial & Collision (3 files) - WELL DOCUMENTED
| File | Status |
|------|--------|
| mapwho.cpp | Full docs (22 functions) |
| PolyBucket.cpp | Full docs (16 functions) |
| collisionseekingthing.cpp | Needs documentation |

### Audio (3 files) - WELL DOCUMENTED
| File | Status |
|------|--------|
| wavread.cpp | Full docs (7 functions) |
| mixermap.cpp | Full docs (4 functions) |
| pcsoundmanager.cpp | Full docs (6 functions) |

### Utilities (14 files) - WELL DOCUMENTED
| File | Status |
|------|--------|
| bytesprite.cpp | Full docs (11 functions) |
| console.cpp | Full docs (4 functions) |
| text.cpp | Full docs |
| TokenArchive.cpp | Full docs (8 functions) |
| triangulate.cpp | Full docs |
| Component.cpp | Full docs (3 functions) |
| thing.cpp | Full docs (4 functions) |
| InitThing.cpp | Full docs |
| oids.cpp | Full docs (5 functions) |
| flexarray.cpp | Stub doc |
| SPtrSet.cpp | Full docs |
| RadarWarningReceiver.cpp | Full docs (4 functions) |
| PCPlatform.cpp | Full docs (10 functions) |
| PCRTID.cpp | Full docs (3 functions) |

---

## Summary

| Priority | Count | Description |
|----------|-------|-------------|
| **HIGH** | 14 | Core gameplay, units, weapons, world loading |
| **MEDIUM** | 23 | Unit subclasses, motion, frontend |
| **LOW** | 80 | Already documented via RE, or rendering code |
| **Total Needed** | **117** | Files in binary but not provided |

---

## Files Already Provided (52 files)

For reference, these are the files Stuart has already shared (in `references/Onslaught/`):

### In Binary (~30 files)
- BattleEngine.cpp, BattleEngineConfigurations.cpp, BattleEngineDataManager.cpp
- Camera.cpp, chunker.cpp, Controller.cpp
- DXMemBuffer.cpp, engine.cpp, eventmanager.cpp
- FEPGoodies.cpp, FEPLoadGame.cpp, FEPSaveGame.cpp, FrontEnd.cpp
- game.cpp, InitThing.cpp, ltshell.cpp
- MemoryManager.cpp, Music.cpp
- PCPlatform.cpp, pcsoundmanager.cpp, Platform.cpp, Player.cpp
- ResourceAccumulator.cpp, SoundManager.cpp, SPtrSet.cpp, thing.cpp

### Not in Binary (~22 files - internal tools, console-only, different architecture)
- activereader.cpp, actor.cpp, Array.cpp
- BattleEngineJetPart.cpp, BattleEngineWalkerPart.cpp
- Career.cpp (functions exist but no debug path)
- CLIParams.cpp, d3dapp.cpp
- DXEngine.cpp, DXFrontend.cpp, DXGame.cpp, DXMemoryManager.cpp
- EditorD3DApp.cpp, EndLevelData.cpp, event.cpp
- MemoryCard.cpp, PCController.cpp, PCEngine.cpp
- PCFEPLoadGame.cpp, PCFEPSaveGame.cpp, PCFrontend.cpp, PCGame.cpp
- PCMemoryCard.cpp, scheduledevent.cpp, storage.cpp, XBoxMemoryCard.cpp

---

## Thank You!

The files you've already shared have made the save editor possible. The Career.cpp, FEPGoodies.cpp, and Player.cpp files were especially valuable for understanding the save file format, goodies unlock conditions, and kill tracking.

Any additional files you can share would help preserve Battle Engine Aquila for future generations. The game deserves to be remembered!

---

*Document maintained by the Onslaught Career Editor project*
*https://github.com/dlprentice/Onslaught-Career-Editor*
