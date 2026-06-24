# Binary String Dump

> Systematic dump of strings from BEA.exe for function discovery
> Phase 1 completed: 2025-12-15

## Overview

This file catalogs strings found in BEA.exe used to locate functions via xrefs.

**Phase 1 Historical Results (2025 snapshot):**
- **196 debug path strings** found
- **50+ error/warning strings** found
- **30+ RTTI class names** found

---

## Debug Path Strings (196 total, historical snapshot)

Format: `C:\dev\ONSLAUGHT2\[filename]`

### High Priority (Not Yet Processed)

| Address | Source File | Priority | Notes |
|---------|-------------|----------|-------|
| 0x00631690 | Player.cpp | HIGH | Kill tracking, god mode |
| 0x006230bc | BattleEngine.cpp | HIGH | Combat system |
| 0x006243bc | Carrier.cpp | HIGH | Carrier mechanics |
| 0x00633b6c | Unit.cpp | HIGH | Base unit class |
| 0x0062e0e0 | Mech.cpp | HIGH | Mech/player vehicle |
| 0x0062d4a8 | Infantry.cpp | MEDIUM | Infantry units |
| 0x00623a78 | Bomber.cpp | MEDIUM | Bomber aircraft |
| 0x00628b40 | engine.cpp | MEDIUM | Core engine |
| 0x0062f590 | MemoryManager.cpp | MEDIUM | Memory system |
| 0x00632428 | SoundManager.cpp | MEDIUM | Audio system |

### Already Processed (Migrated to functions/)

| Address | Source File | Status |
|---------|-------------|--------|
| 0x0062bba4 | game.cpp | MIGRATED |
| 0x006314dc | PauseMenu.cpp | MIGRATED |
| 0x0062913c | FEPDebriefing.cpp | MIGRATED |
| 0x00629318 | FEPGoodies.cpp | MIGRATED |
| 0x006293c0 | FEPLoadGame.cpp | MIGRATED |
| 0x00629a78 | FEPSaveGame.cpp | MIGRATED |

### Complete Debug Path List (Alphabetical)

| Address | Source File |
|---------|-------------|
| 0x00622cf4 | AirUnit.cpp |
| 0x00622ec4 | Atmospherics.cpp |
| 0x006230bc | BattleEngine.cpp |
| 0x006235a8 | BattleEngineConfigurations.cpp |
| 0x00623674 | BattleEngineDataManager.cpp |
| 0x00623990 | Boat.cpp |
| 0x00623a78 | Bomber.cpp |
| 0x00623ab8 | BSpline.cpp |
| 0x00623af4 | Building.cpp |
| 0x00623c18 | bytesprite.cpp |
| 0x00623c90 | Camera.cpp |
| 0x00623dd4 | Cannon.cpp |
| 0x006243bc | Carrier.cpp |
| 0x00624400 | Carver.cpp |
| 0x00624464 | chunker.cpp |
| 0x00624630 | CollisionSeekingRound.cpp |
| 0x006246d8 | collisionseekingthing.cpp |
| 0x006247f8 | Component.cpp |
| 0x00624d0c | console.cpp |
| 0x00625538 | Controller.cpp |
| 0x0062568c | CPhysicsScript.cpp |
| 0x00625818 | CPhysicsScriptStatements.cpp |
| 0x0062811c | Cutscene.cpp |
| 0x006282dc | damage.cpp |
| 0x006287b4 | DestructableSegmentsController.cpp |
| 0x006289c0 | DiveBomber.cpp |
| 0x00628a54 | Dropship.cpp |
| 0x00628b40 | engine.cpp |
| 0x00628d3c | eventmanager.cpp |
| 0x00628fac | FEPBEConfig.cpp |
| 0x0062913c | FEPDebriefing.cpp |
| 0x0062921c | FEPDevelopment.cpp |
| 0x00629318 | FEPGoodies.cpp |
| 0x006293c0 | FEPLoadGame.cpp |
| 0x00629414 | FEPMain.cpp |
| 0x00629a78 | FEPSaveGame.cpp |
| 0x00629a9c | flexarray.cpp |
| 0x00629df0 | FrontEnd.cpp |
| 0x0062bba4 | game.cpp |
| 0x0062c968 | gcgamut.cpp |
| 0x0062c9e8 | GillM.cpp |
| 0x0062ca6c | GillMHead.cpp |
| 0x0062cadc | GroundAttackAircraft.cpp |
| 0x0062cb0c | GroundUnit.cpp |
| 0x0062cb30 | GroundVehicle.cpp |
| 0x0062cbd0 | HeightField.cpp |
| 0x0062cc98 | HiveBoss.cpp |
| 0x0062ce76 | Hud.cpp |
| 0x0062d390 | ibuffer.cpp |
| 0x0062d3cc | imageloader.cpp |
| 0x0062d3f0 | imposter.cpp |
| 0x0062d4a8 | Infantry.cpp |
| 0x0062d61c | InfluenceMap.cpp |
| 0x0062d7b0 | InitThing.cpp |
| 0x0062d824 | landscapeib.cpp |
| 0x0062d8e0 | LandscapeTexture.cpp |
| 0x0062db04 | maptex.cpp |
| 0x0062db88 | mapwho.cpp |
| 0x0062dc80 | MCBuggy.cpp |
| 0x0062df60 | MCMech.cpp |
| 0x0062e06c | MCTentacle.cpp |
| 0x0062e0e0 | Mech.cpp |
| 0x0062f590 | MemoryManager.cpp |
| 0x0062f7d8 | MenuItem.cpp |
| 0x0062f8e8 | mesh.cpp |
| 0x0062fe40 | MeshCollisionVolume.cpp |
| 0x0062fe70 | MeshPart.cpp |
| 0x00630178 | MeshRenderer.cpp |
| 0x006309a4 | Mine.cpp |
| 0x006309c0 | Missile.cpp |
| 0x00630a4c | Music.cpp |
| 0x00630c20 | oids.cpp |
| 0x00630cd8 | ParticleDescriptor.cpp |
| 0x00630e60 | ParticleManager.cpp |
| 0x00630fb0 | ParticleSet.cpp |
| 0x006314dc | PauseMenu.cpp |
| 0x00631630 | Plane.cpp |
| 0x00631654 | Platform.cpp |
| 0x00631690 | Player.cpp |
| 0x006316bb | PolyBucket.cpp |
| 0x00631784 | RadarWarningReceiver.cpp |
| 0x00631b7c | ResourceAccumulator.cpp |
| 0x00631d38 | Round.cpp |
| 0x00631e2c | RTCutscene.cpp |
| 0x00631f28 | rtmesh.cpp |
| 0x0063221c | Sentinel.cpp |
| 0x00632428 | SoundManager.cpp |
| 0x00632650 | SpawnerThng.cpp |
| 0x0063270c | SphereTrigger.cpp |
| 0x00632730 | SPtrSet.cpp |
| 0x0063283c | SquadNormal.cpp |
| 0x00632918 | SquadRelaxed.cpp |
| 0x006329f8 | StaticShadows.cpp |
| 0x00632abc | Submarine.cpp |
| 0x00632ccc | Tentacle.cpp |
| 0x00632dd8 | text.cpp |
| 0x00632ef0 | texture.cpp |
| 0x0063314c | tgaloader.cpp |
| 0x006331c0 | thing.cpp |
| 0x00633240 | ThunderHead.cpp |
| 0x00633a00 | TokenArchive.cpp |
| 0x00633a84 | tree.cpp |
| 0x00633ab8 | triangulate.cpp |
| 0x00633b6c | Unit.cpp |
| 0x00633d08 | vbuffer.cpp |
| 0x00633d5c | vbuftexture.cpp |
| 0x0063cf78 | VertexShader.cpp |
| 0x0063d12c | Warspite.cpp |
| 0x0063d170 | WarspiteDome.cpp |
| 0x0063d1b0 | wavread.cpp |
| 0x0063d1f8 | WaypointManager.cpp |
| 0x0063d2ac | world.cpp |
| 0x0063d488 | WorldMeshList.cpp |
| 0x0063d798 | WorldPhysicsManager.cpp |
| 0x0063dd8c | ltshell.cpp |
| 0x0063e03c | PCPlatform.cpp |
| 0x0063e284 | PCRTID.cpp |
| 0x0063e46c | pcsoundmanager.cpp |
| 0x0063fb24 | FastVB.cpp |
| 0x0063fb4c | FEPDirectory.cpp |
| 0x0063fc24 | FEPMultiplayerStart.cpp |
| 0x0063fc88 | FEPOptions.cpp |
| 0x0063fd4c | FEPWingmen.cpp |
| 0x00640030 | mixermap.cpp |

### MissionScript Subfolder

| Address | Source File |
|---------|-------------|
| 0x0064c5c4 | MissionScript/AsmInstruction.cpp |
| 0x0064cc80 | MissionScript/DataType.cpp |
| 0x0064cce0 | MissionScript/EventFunction.cpp |
| 0x0064fa40 | MissionScript/IScript.cpp |
| 0x0064fe98 | MissionScript/ScriptEventNB.cpp |
| 0x00650040 | MissionScript/ScriptObjectCode.cpp |
| 0x00650134 | MissionScript/Symtab.cpp |

### DirectX Files (DX prefix)

| Address | Source File |
|---------|-------------|
| 0x00650324 | DXBattleLine.cpp |
| 0x006503d4 | DXClouds.cpp |
| 0x00650454 | DXCompass.cpp |
| 0x00650644 | DXFMV.CPP |
| 0x00650670 | DXFont.cpp |
| 0x00650744 | DXFrontEndVideo.cpp |
| 0x006508cc | DXImposter.cpp |
| 0x00650a88 | DXKempyCube.cpp |
| 0x00650bdc | DXLandscape.cpp |
| 0x00650fd0 | DXMemBuffer.cpp |
| 0x00651244 | DXMeshVB.cpp |
| 0x00651d60 | DXPalletizer.cpp |
| 0x00651dcc | DXParticleTexture.cpp |
| 0x0065211c | DXPatchManager.cpp |
| 0x00652410 | DXShadows.cpp |
| 0x00652534 | DXSnow.cpp |
| 0x006525a0 | DXSurf.cpp |
| 0x0065269c | DXTexture.cpp |
| 0x006529b0 | DXTrees.cpp |

---

## Error/Warning Strings (Function Anchors)

### Career System

| Address | String | Likely Function |
|---------|--------|-----------------|
| 0x006241b4 | "WARNING: Could not find career node from world number %d" | CCareer::GetNodeFromWorld |
| 0x006241f0 | "FATAL ERROR: Can't update career because can't find node for world %d" | CCareer::UpdateOnWorldComplete |
| 0x00624238 | "Updating career (world %d completed)" | CCareer::UpdateOnWorldComplete |
| 0x00624288 | "%-15s killed this level %d, Total %d" | Kill counter display |
| 0x006242ec | "Error: no career node for world %d" | CCareer::GetNodeFromWorld |
| 0x00624318 | "Error: Outside slot range (%d) in call to GetSlot" | CCareer::GetSlotBit |
| 0x0062434c | "Error: Outside slot range (%d) in call to SetSlot" | CCareer::SetSlotBit |

### Memory/Resource Management

| Address | String | Likely Function |
|---------|--------|-----------------|
| 0x0062c368 | "WARNING : THING HEAP NEARLY FULL!" | Memory manager |
| 0x0062f938 | "Mesh '%s' leaked : refcount=%d\n" | Resource leak detection |
| 0x0062f7b8 | "Writing memory dump '%s'\n" | Memory dump function |

### Model/Asset Loading

| Address | String | Likely Function |
|---------|--------|-----------------|
| 0x0062864c | "FATAL ERROR: Could not find segment for '%s" | Segment lookup |
| 0x00628614 | "WARNING: '%s', building part not found!!!!!! part = %d" | Building part lookup |
| 0x0062faec | "Loading mesh %s" | Mesh loader |
| 0x0062fc80 | "Mesh '%s' not found in level resource file" | Mesh lookup |

### Physics/Collision

| Address | String | Likely Function |
|---------|--------|-----------------|
| 0x00622c68 | "Warning object %s travelling beyond max velocity" | Velocity validation |
| 0x0062cdec | "WARNING: Unexpected collision check already done" | Collision system |
| 0x0062ce20 | "WARNING: Object colliding with too many objects %08x" | Collision overflow |

---

## RTTI Class Names

### Core Game Classes

| Address | Decoded Name |
|---------|--------------|
| 0x0062bc28 | CGame |
| 0x00631680 | CPlayer |
| 0x00623248 | CBattleEngine |
| 0x00633ae0 | CUnit |
| 0x00631cf8 | CRound |
| 0x0063d260 | CWeapon |
| 0x006327f0 | CSquad |

### Frontend Classes (CFE*)

| Address | Decoded Name |
|---------|--------------|
| 0x00629c18 | CFEPGoodies |
| 0x00629cf8 | CFEPSaveGame |
| 0x00629d60 | CFEPLoadGame |
| 0x00629d40 | CFEPDebriefing |
| 0x00629cb8 | CFEPOptions |
| 0x00629d80 | CFEPMain |

---

## Statistics

- **Total debug paths:** 169
- **Source files processed:** 10
- **Source files remaining:** ~159
- **Error strings found:** 50+
- **RTTI classes found:** 30+

---

## Next Steps (Phase 1 continued)

1. [ ] Find xrefs to Player.cpp debug path (0x00631690)
2. [ ] Find xrefs to BattleEngine.cpp debug path (0x006230bc)
3. [ ] Find xrefs to Unit.cpp debug path (0x00633b6c)
4. [ ] Map functions discovered via xrefs
5. [ ] Create new source file folders as needed
