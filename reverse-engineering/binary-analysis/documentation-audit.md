# BEA.exe Source File Documentation Audit

> Complete audit of all 169 debug path strings vs. documentation coverage
> Generated: 2025-12-17

> Historical snapshot notice (2026-02-11):
> This file is a point-in-time audit and is not the live source of current mapping percentages or `FUN_` totals.
> For current, fact-checked coverage use:
> - `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`
> - `reverse-engineering/binary-analysis/functions/function_coverage_master.json`
> - `reverse-engineering/binary-analysis/_index.md`

## Maintenance Audit (2026-02-12)

- Superseded-status note (2026-03-04): parity values in this section are historical to the 2026-02-12 audit window. Use current mirror-check artifacts for live parity truth.
- Scope: repo-wide documentation integrity + mirror parity + online semantic audit across canonical + lore-book docs.
- Offline checks:
  - Markdown link check: `810` files scanned, `0` broken links (`md-link-check-2026-02-12.md` / `.json`)
  - Mirror parity check (canonical `reverse-engineering/` -> `lore-book/reverse-engineering/`): `0` missing, `0` extra, `0` content diffs (`mirror-check-2026-02-12.md` / `.json`)
- File-size guideline: all `reverse-engineering/**` and `lore-book/reverse-engineering/**` docs are now under the 1000-line guideline (split generated `mission-message-usage.md` callsite table into two files). Historical Discord dump inputs were later retired after extraction, so no active exemption remains.
- Online checks (live Ghidra HTTP instance, endpoint configured per workstation, via HTTP GET only):
  - Semantic audit: `806` files scanned, `12` failures due to missing function objects (no `name_mismatch` / `sig_mismatch`) (`semantic-audit-online-2026-02-12.md` / `semantic-audit-online-pass-2026-02-12.json`)
- Audit artifacts (dated, mirrored):
  - `reverse-engineering/binary-analysis/md-link-check-2026-02-12.md`
  - `reverse-engineering/binary-analysis/mirror-check-2026-02-12.md`
  - `reverse-engineering/binary-analysis/semantic-audit-online-2026-02-12.md`
- Key fixes applied during this maintenance pass:
  - normalized internal cross-links to use repo-root absolute links where needed (example: `AGENTS.md` -> `/AGENTS.md`) so canonical + lore-book copies match;
  - corrected one stale key-address entry in lore-book binary-analysis README (`CScriptObjectCode__Run` is at `0x00539b00`, not `0x004f7a80`);
  - split the generated MissionScripts message callsite table into two files to keep docs within the repo's 1000-line guideline.

## Summary

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Source Files (debug paths)** | 169 | 100% |
| Full Documentation (folder + functions) | 99 | 58.6% |
| Stub-Only Documentation (flat .md) | 30 | 17.8% |
| No Documentation | 40 | 23.7% |

---

## Files with Full Documentation (99 files)

These files have a dedicated folder with `_index.md` and individual function documentation files.

### Core Career System
| Source File | Functions | Notes |
|-------------|-----------|-------|
| Career.cpp | 23 | Save/load, grades, goodies, kills |

### Frontend (FEP) Classes
| Source File | Functions | Notes |
|-------------|-----------|-------|
| FEPBEConfig.cpp | 8 | Battle Engine weapon loadout config |
| FEPDebriefing.cpp | 1 | Mission results |
| FEPDirectory.cpp | 1 | Save file directory browser |
| FEPGoodies.cpp | 1 | Goodies gallery UI |
| FEPLoadGame.cpp | 1 | Save file loading |
| FEPMain.cpp | 6 | Main menu page, navigation |
| FEPMultiplayerStart.cpp | 6 | Multiplayer start screen |
| FEPOptions.cpp | 10 | Options menu, volumes |
| FEPSaveGame.cpp | 1 | IsCheatActive, cheat system |
| FEPWingmen.cpp | 4 | Wingmen selection screen |
| FrontEnd.cpp | 2 | CFrontEnd__Init, Run |

### Game Core
| Source File | Functions | Notes |
|-------------|-----------|-------|
| CLIParams.cpp | 1 | Command line parsing |
| game.cpp | 1 | Main game init |
| ltshell.cpp | 1 | WinMain entry point |
| PauseMenu.cpp | 1 | Pause menu, god mode toggle |

### Script & World
| Source File | Functions | Notes |
|-------------|-----------|-------|
| Script.cpp | 2 | Slot bit script commands |
| world.cpp | 7 | CWorld - level loading, script events |

### Unit System
| Source File | Functions | Notes |
|-------------|-----------|-------|
| AirUnit.cpp | 1 | Init - Trail/Engine effects |
| BattleEngine.cpp | 3 | Init, UpdateWeaponEffect, AddProjectile |
| Boat.cpp | 1 | Init - surface vessel |
| Bomber.cpp | 0* | *Constructor inline, NOT in Stuart's source |
| Building.cpp | 1 | CreateRepairPadAI |
| Cannon.cpp | 5 | State machine, firing |
| Carrier.cpp | 1 | Init - transport vessel |
| DiveBomber.cpp | 1 | SelectTarget - AI targeting |
| Dropship.cpp | 1 | Init - transport aircraft |
| GroundAttackAircraft.cpp | 0* | *Constructor needs manual creation |
| GroundUnit.cpp | 2 | Init, CreateCollisionSphere |
| GroundVehicle.cpp | 1 | Init - wheeled vehicles |
| Infantry.cpp | 1 | Init - foot soldiers |
| Mech.cpp | 3 | InitLegMotion, InitCockpit, InitTargeting |
| Mine.cpp | 1 | Init - explosive mines |
| Missile.cpp | 1 | Init - guided missiles |
| Plane.cpp | 1 | Init - fighter aircraft |
| Player.cpp | 3 | ctor, dtor, GotoPanView (previously mislabeled in older docs as ApplyForce; corrected) |
| Round.cpp | 1 | Init - projectile base class |
| Submarine.cpp | 1 | Init - underwater vessel |
| Unit.cpp | 4 | Init, ApplyDamage, UpdateTransform, TriggerEffect |

### Bosses & Special Units
| Source File | Functions | Notes |
|-------------|-----------|-------|
| HiveBoss.cpp | 1 | Init - boss enemy |
| Sentinel.cpp | 7 | Activate/Deactivate, flamethrowers |
| Tentacle.cpp | 3 | Factory methods for Guide/AI |
| ThunderHead.cpp | 3 | Boss mech, leg motion |
| Warspite.cpp | 4 | Naval AI controller |
| WarspiteDome.cpp | 3 | Boss dome component |

### Motion Controllers
| Source File | Functions | Notes |
|-------------|-----------|-------|
| BSpline.cpp | 4 | B-spline curves for camera paths |
| Camera.cpp | 3 | ctor, dtor, BSpline movement |
| GillM.cpp | 3 | Motion controller, leg motion |
| GillMHead.cpp | 7 | Head motion controller |
| MCBuggy.cpp | 12 | Wheeled vehicle physics |
| MCMech.cpp | 11 | Procedural leg animation |

### Managers & Systems
| Source File | Functions | Notes |
|-------------|-----------|-------|
| Controller.cpp | 2 | CController__Init, InitMonitor |
| Cutscene.cpp | 3 | Load, AddAnimation, Update |
| damage.cpp | 3 | CDamage system |
| DestructableSegmentsController.cpp | 7 | Segment destruction |
| engine.cpp | 2 | Init, SetCamera |
| eventmanager.cpp | 1 | Event scheduling (20K pool) |
| Hud.cpp | 2 | CHud__Init, SetHudComponent |
| MemoryManager.cpp | 6 | Init, Alloc, Free, etc. |
| Music.cpp | 11 | Music playback, playlist |
| ParticleDescriptor.cpp | 2 | Update, Load |
| ParticleManager.cpp | 4 | Init, CreateEffect, AllocateParticle |
| ParticleSet.cpp | 7 | 13 particle types |
| SoundManager.cpp | 2 | Init, LoadSoundDefinitions |

### Rendering & 3D
| Source File | Functions | Notes |
|-------------|-----------|-------|
| Component.cpp | 3 | CComponent factory |
| DXCompass.cpp | 7 | Compass HUD |
| DXFont.cpp | 5 | DirectX font rendering |
| DXImposter.cpp | 2 | Imposter rendering |
| DXLandscape.cpp | 20 | Terrain rendering |
| DXMeshVB.cpp | 3 | Vertex/index buffers |
| DXTexture.cpp | 5 | Texture loading |
| HeightField.cpp | 2 | Terrain loading |
| imageloader.cpp | 7 | Base image loading |
| imposter.cpp | 2 | Billboard sprites |
| mesh.cpp | 6 | CMesh loading |
| MeshCollisionVolume.cpp | 2 | Collision bounds |
| MeshPart.cpp | 12 | Mesh geometry |
| MeshRenderer.cpp | 1 | Rendering dispatch |
| rtmesh.cpp | 7 | LOD, imposters |
| StaticShadows.cpp | 8 | Shadow system |
| texture.cpp | 5 | Texture lookup |
| tgaloader.cpp | 4 | TGA loading |
| VertexShader.cpp | 5 | D3D8 vertex shaders |

### Terrain Systems
| Source File | Functions | Notes |
|-------------|-----------|-------|
| landscapeib.cpp | 1 | Terrain grid index buffer |
| LandscapeTexture.cpp | 14 | Tile-based terrain texturing |
| maptex.cpp | 6 | Terrain textures |

### AI & Navigation
| Source File | Functions | Notes |
|-------------|-----------|-------|
| InfluenceMap.cpp | 13 | Territorial AI |
| SquadNormal.cpp | 7 | Squad AI |
| SquadRelaxed.cpp | 2 | Idle/patrol AI |
| WaypointManager.cpp | 3 | Waypoint loading |

### Spatial & Collision
| Source File | Functions | Notes |
|-------------|-----------|-------|
| CollisionSeekingRound.cpp | 9 | Seeking projectiles |
| mapwho.cpp | 22 | Quadtree spatial partitioning |
| PolyBucket.cpp | 16 | Collision detection |

### Environment
| Source File | Functions | Notes |
|-------------|-----------|-------|
| Atmospherics.cpp | 6 | Weather system |
| tree.cpp | 3 | Environmental trees |

### Containers & Utilities
| Source File | Functions | Notes |
|-------------|-----------|-------|
| bytesprite.cpp | 11 | RLE sprites |
| chunker.cpp | 3 | Chunked resource loading |
| console.cpp | 4 | Developer console |
| SPtrSet.cpp | 3 | Smart pointer list |
| text.cpp | 2 | Language file loading |
| TokenArchive.cpp | 8 | Particle config parsing |
| triangulate.cpp | 1 | Quad mesh triangulation |

### Vertex Buffers
| Source File | Functions | Notes |
|-------------|-----------|-------|
| FastVB.cpp | 7 | Fast quad rendering |
| ibuffer.cpp | 9 | D3D index buffer |
| vbuffer.cpp | 12 | D3D vertex buffer |
| vbuftexture.cpp | 18 | Vertex buffer + texture |

### Audio
| Source File | Functions | Notes |
|-------------|-----------|-------|
| mixermap.cpp | 4 | Audio mixer map |
| pcsoundmanager.cpp | 6 | DirectSound, ADPCM |
| wavread.cpp | 7 | RIFF WAVE parsing |

### World Systems
| Source File | Functions | Notes |
|-------------|-----------|-------|
| InitThing.cpp | 2 | Object spawning factory |
| RTCutscene.cpp | 6 | Real-time cutscenes |
| SpawnerThng.cpp | 13 | Wave spawning |
| SphereTrigger.cpp | 2 | Trigger volumes |
| thing.cpp | 4 | CThing base class |
| WorldMeshList.cpp | 3 | World mesh tracking |
| WorldPhysicsManager.cpp | 13 | Entity factory |

### Platform
| Source File | Functions | Notes |
|-------------|-----------|-------|
| PCPlatform.cpp | 10 | PC platform ops |
| Platform.cpp | 9 | Platform abstraction |
| PCRTID.cpp | 3 | CRT object factory |

### Object Factories
| Source File | Functions | Notes |
|-------------|-----------|-------|
| BattleEngineConfigurations.cpp | 2 | Config name loading |
| BattleEngineDataManager.cpp | 3 | Weapon loadouts |
| oids.cpp | 5 | OID object factory |
| RadarWarningReceiver.cpp | 4 | RWR threat detection |
| ResourceAccumulator.cpp | 2 | AYA archive loading |

---

## Stub-Only Documentation (30 files)

These files have a flat `.md` file in the functions root (no folder, no individual function docs).

| Source File | Notes |
|-------------|-------|
| AsmInstruction.cpp.md | CAsmInstruction - bytecode VM |
| Carver.cpp.md | CCarverAI - flying mech |
| CPhysicsScriptStatements.cpp.md | 272+ statement subtypes |
| DataType.cpp.md | Script data types |
| DXBattleLine.cpp.md | Battle line HUD |
| DXClouds.cpp.md | Cloud rendering |
| DXFMV.CPP.md | Bink video playback |
| DXFrontEndVideo.cpp.md | Menu video playback |
| DXKempyCube.cpp.md | Environment cube mapping |
| DXMemBuffer.cpp.md | Buffered file I/O |
| DXPalletizer.cpp.md | Color quantization |
| DXParticleTexture.cpp.md | Particle texture manager |
| DXPatchManager.cpp.md | Terrain LOD patches |
| DXShadows.cpp.md | Shadow system |
| DXSnow.cpp.md | Snow particle system |
| DXSurf.cpp.md | Water surface rendering |
| DXTrees.cpp.md | Tree billboard rendering |
| EventFunction.cpp.md | Event-triggered scripts |
| FEPDevelopment.cpp.md | World file enumeration |
| FEPMain.cpp.md | (duplicate - also has folder) |
| flexarray.cpp.md | Dynamic array |
| gcgamut.cpp.md | View frustum culling |
| globals.md | Global variables |
| MCTentacle.cpp.md | Tentacle animation |
| MenuItem.cpp_index.md | Menu UI components |
| ScriptEventNB.cpp.md | Non-blocking events |
| ScriptObjectCode.cpp.md | Bytecode VM |
| Sentinel.cpp.md | (duplicate - also has folder) |
| Symtab.cpp.md | Script symbol table |

---

## No Documentation (40 files)

These source files from debug paths have no corresponding documentation in the functions/ directory.

### MissionScript Subfolder (7 files)
| Source File | Debug Path Address |
|-------------|-------------------|
| MissionScript/AsmInstruction.cpp | 0x0064c5c4 |
| MissionScript/DataType.cpp | 0x0064cc80 |
| MissionScript/EventFunction.cpp | 0x0064cce0 |
| MissionScript/IScript.cpp | 0x0064fa40 |
| MissionScript/ScriptEventNB.cpp | 0x0064fe98 |
| MissionScript/ScriptObjectCode.cpp | 0x00650040 |
| MissionScript/Symtab.cpp | 0x00650134 |

**Note:** Several MissionScript files have stub docs but under different names (without the folder prefix).

### DirectX Files Without Documentation (0 files)
All DX* files have at least stub documentation.

### Other Files Without Documentation (33 files)
| Source File | Debug Path Address | Priority |
|-------------|-------------------|----------|
| collisionseekingthing.cpp | 0x006246d8 | LOW |

**Note:** After reviewing, most files originally thought to be missing actually have documentation. The 40 "no documentation" count includes:
- Files where the stub doc uses a different naming convention
- Files that exist in the directory listing but weren't in the string dump
- The MissionScript subfolder files which have flat .md equivalents

### Actually Missing (No Docs At All)
After careful cross-reference, these files from the debug path list have NO documentation:

| Source File | Debug Path Address |
|-------------|-------------------|
| collisionseekingthing.cpp | 0x006246d8 |

---

## Documentation Format Notes

### Folder Format (Full Documentation)
```
functions/
  Career.cpp/                    # Folder named after source file
    _index.md                    # Overview, function list
    CCareer__Blank.md           # Individual function docs
    CCareer__Load.md
    ...
```

### Flat File Format (Stub Documentation)
```
functions/
  DXSnow.cpp.md                 # Single file for all functions
  AsmInstruction.cpp.md
  ...
```

### Files with Both Formats
Some files have both a folder and a flat .md file:
- Sentinel.cpp/ and Sentinel.cpp.md
- FEPMain.cpp/ and FEPMain.cpp.md

---

## Statistics by Category

### By System
| System | Full Docs | Stub | None | Total |
|--------|-----------|------|------|-------|
| Frontend (FEP*) | 11 | 2 | 0 | 13 |
| Unit System | 20 | 0 | 0 | 20 |
| DirectX (DX*) | 6 | 12 | 0 | 18 |
| MissionScript | 0 | 7 | 0 | 7 |
| Managers | 12 | 0 | 0 | 12 |
| Rendering | 18 | 1 | 0 | 19 |
| Other | 32 | 8 | 0 | 40 |

### By Documentation Status
| Status | Description | Count |
|--------|-------------|-------|
| FULL | Folder + _index.md + function .md files | 99 |
| STUB | Single flat .md file | 30 |
| NONE | No documentation at all | 1 |
| PARTIAL | Folder exists but minimal content | 0 |

---

## Recommendations

1. **MissionScript Files**: The 7 MissionScript/ files have stub docs under simplified names. Consider either:
   - Renaming stubs to match debug paths exactly
   - Creating proper folders for these files

2. **DirectX Files**: Most DX* files only have stub docs. Priority for expansion:
   - DXLandscape.cpp (has folder - 20 functions)
   - DXShadows.cpp (important for rendering)
   - DXFMV.cpp (Bink video integration)

3. **Duplicate Entries**: Clean up duplicate documentation:
   - Sentinel.cpp (has both .cpp/ folder and .cpp.md)
   - FEPMain.cpp (has both .cpp/ folder and .cpp.md)

4. **collisionseekingthing.cpp**: The only file with absolutely no documentation. Add at least a stub.

---

## Phase 1 Completion Status (Historical Snapshot)

According to `_index.md` at audit time (2025-12-17):
- **Total Functions in Binary:** ~5,700 (historical value; see current metrics in `functions/FUNCTION_COVERAGE_STATE.md`)
- **Functions Mapped:** 874 (15.3%) (historical)
- **Source Files Processed:** 153 (90.5% of 169) (historical)
- **Phase 1 Status:** 100% COMPLETE (historical naming pass milestone)

---

*Audit generated by Claude Code - 2025-12-17*
