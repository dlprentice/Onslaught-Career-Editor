# Function Mappings - Master Index

> Binary-to-source function mappings for BEA.exe (Steam version)
> Last updated: 2026-02-13

## Overview

This directory contains per-source-file documentation of all functions mapped from Stuart's source code to the compiled binary.

For binary-wide `% mapped` metrics (total function objects, named coverage, remaining `FUN_`), see [`FUNCTION_COVERAGE_STATE.md`](FUNCTION_COVERAGE_STATE.md).

**Structure:**
```
functions/
  _index.md                 # This file - master index
  FUNCTION_COVERAGE_STATE.md # Binary-wide function coverage tracker
  Career.cpp/               # One folder per source file
    _index.md               # Source file overview + function list
    CCareer__Blank.md       # Individual function analysis
    ...
```

---

## Key Functions (Save/Cheat)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00421200 | CCareer__Load | Reads 16-bit version word, loads data from `source + 2`. `flag==0` applies options entries + tail; `flag!=0` preserves Sound/Music floats and skips options entries/tail. |
| 0x00421350 | CCareer__Save | Writes 16-bit version word, copies `0x24BC` bytes into `dest + 2` |
| 0x00421430 | CCareer__GetSaveSize | Returns `0x2514 + 0x20 * N` (N from `DAT_008892d8`; Steam retail observed `N=16` => `0x2714` fixed) |
| 0x00420b10 | OptionsTail_Write | Writes `0x56`-byte globals/options tail block |
| 0x00420d70 | OptionsTail_Read | Reads `0x56`-byte globals/options tail block |
| 0x00465490 | IsCheatActive | XOR decrypt + `strstr()` cheat check |

## Key Functions (Kill Counters)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00421900 | CCareer__GetKillCounterTopByte_23F8 | Returns top byte (biased) for 0x23F8 counter |
| 0x00421910 | CCareer__SetKillCounterTopByte_23F4 | Sets top byte for 0x23F4 counter |
| 0x00421940 | CCareer__SetKillCounterTopByte_23F8 | Sets top byte for 0x23F8 counter |
| 0x00421980 | CCareer__GetGoodiePtr | Returns pointer into `CGoodie[300]` (ECX = base) |

## Key Functions (Frontend/Options)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00461a50 | Career_IsWorldUnlocked | Unlock gate: world 100 always unlocked; otherwise any parent link `mLinkType==CN_COMPLETE`; bypassed by IsCheatActive(1) (TURKEY) |
| 0x0042db10 | OptionsEntries__FindById | Finds a persisted 0x20-byte “options entry” (control binding) by `entry_id` |
| 0x00453460 | OptionsEntries__InitDefaultDualBindingsTable | Initializes default dual-binding options-entry table (`DAT_00677af0` range) |
| 0x00514210 | OptionsEntries__InitDefaultSingleBindingsTable | Initializes default single-binding options-entry table (`DAT_008892d8` range) |
| 0x00453970 | CControllerDefinition__InitDefaults | Initializes control-definition defaults and vtable prior to remap lifecycle |
| 0x004539b0 | CControllerDefinition__scalar_deleting_dtor | Scalar deleting dtor wrapper for control-definition helper object |
| 0x004539d0 | CControllerDefinition__dtor | Control-definition destructor path (key-sink gate reset + owned pointer release) |
| 0x00453780 | Controls__ApplyPreset | Applies control scheme preset; sets `g_ControlSchemeIndex` and remaps inputs |
| 0x00453f50 | Controls__DispatchRemap | Maps action_code to one or more `(entry_id, binding_type)` pairs (control remap) |
| 0x00454e90 | Controls__ClearDuplicateBinding | Clears duplicate bindings across entries/slots |
| 0x00456080 | Controls__BeginRemapCapture | Starts remap input capture; schedules callback at code label `0x00456190` |
| 0x004565d0 | OptionsEntries__SetBindingSlot | Writes one binding slot into an options entry |
| 0x004ceef0 | LandscapeDetail_SetLevel | Sets landscape detail enum (writes g_LandscapeDetailLevel1/2) |
| 0x004cef30 | LandscapeDetail_GetLevel | Returns detail level (2 if level2 set, else level1 flag) |
| 0x00528aa0 | CVar__Init | CVar constructor/init for options CVars |
| 0x00528ad0 | CVar__SetValueRounded | Sets CVar numeric value (rounded) at +0xC |

## Key Functions (Console Loading / Script UI)

| Address | Function | Notes |
|---------|----------|-------|
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Recomputes console layout fields from current window height (`+0x2384/+0x2388/+0xb3cc`) |
| 0x0042ad30 | CConsole__ExecScript | Executes a script file (`Exec`) by reading lines and dispatching each command |
| 0x0042a460 | CConsole__ListBinds | Enumerates current key bindings and prints formatted bind lines |
| 0x0042a540 | CConsoleVar__GetTypeName | Maps cvar type enum (`+0xa0`) to printable type label |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Formats cvar value text using type (`+0xa0`) and value ptr (`+0xa4`) |
| 0x0042a770 | CConsole__FindCommandByName | Linked-list command lookup (`this+0x2394`, `stricmp`) |
| 0x0042a7b0 | CConsole__SetVariableByName | `Set` command helper with variable lookup + typed value parsing/writes |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full console teardown helper (command/var lists + owned aux pointers) |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Clears/frees command and variable lists only |
| 0x0042a4f0 | CConsole__ExecuteBufferedCommandSlot | Executes buffered command/output slot (`this+0x23BC`) if line is non-empty |
| 0x0042b120 | CConsole__HandleBind | Console input/bind key handler (toggle/history/tab-complete/dispatch paths) |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status-line rewrite helper used by status/progress completion flows |
| 0x0042b9c0 | CConsole__ExecuteCommandLine | Parses first token and dispatches a command callback from console command list |
| 0x0042ba90 | CConsole__MenuUp | Console menu selection up (decrement/clamp index) |
| 0x0042bac0 | CConsole__MenuDown | Console menu selection down (increment/clamp index) |
| 0x0042bb30 | CConsole__MenuSelect | Console menu select/activate current entry |
| 0x0042bbc0 | CConsole__SetLoading | Enables/disables loading-screen mode and resets/releases loading resources/progress state |
| 0x0042c810 | CConsole__RenderLoadingScreen | Loading-screen renderer used by FrontEnd/Game load flows and progress updates |
| 0x0042cf40 | CConsole__SetLoadingRange | Sets loading interpolation range (`min/max`) and refreshes loading UI |
| 0x0042cf70 | CConsole__SetLoadingFraction | Sets loading progress fraction (`t`) inside active range and refreshes loading UI |
| 0x0042c750 | FatalError__ExitWithLocalizedPrefix_A | Localized fatal wrapper used by load/resource paths; formats prefix (`string id 0xCC`) + message and exits |
| 0x0042d0b0 | FatalError__ExitWithLocalizedPrefix_B | Same localized fatal wrapper semantics in mesh/resource deserialize paths |
| 0x0042d260 | OptionsEntries__InitSingleBindingEntry | Initializes one persisted options/control-binding entry slot (single-binding variant) |
| 0x0042d2b0 | OptionsEntries__InitDualBindingEntry | Initializes one persisted options/control-binding entry with dual-binding metadata |
| 0x0042d300 | OptionsEntries__InitSentinelEntry | Sentinel/reset helper used by the options-entry initialization table setup |
| 0x0042d310 | PlatformInput__InitMouse | DirectInput mouse init/acquire path used at gameplay/pause transitions |
| 0x0042d3b0 | PlatformInput__ShutdownMouse | Mouse unacquire/release path used on pause/shutdown transitions |
| 0x0042d420 | PlatformInput__PollMouseMotion | Mouse motion poll + delta accumulation (reacquire on input loss) |
| 0x0042d4d0 | PlatformInput__PollMouseState | Motion + button edge/hold poll used in `CGame__Update` |

## Key Functions (Physics Script Statements)

| Address | Function | Notes |
|---------|----------|-------|
| 0x0042f5f0 | CWeaponStatement__Create | Allocates/initializes weapon-statement node and appends to statement set |
| 0x0042f750 | CWeaponStatement__GetSerializedSize | Recursive size accumulator for weapon-statement tree |
| 0x0042fa80 | CWeaponModeStatement__Create | Allocates/initializes weapon-mode statement node and appends to statement set |
| 0x0042fc70 | CWeaponModeStatement__GetSerializedSize | Recursive size accumulator for weapon-mode statement tree |
| 0x0042ffa0 | CRoundStatement__Create | Allocates/initializes round statement and appends to statement set |
| 0x004301e0 | CRoundStatement__GetSerializedSize | Recursive size accumulator for round-statement tree |
| 0x00433390 | CComponentBasedOn__CopyFrom | Deep-copy helper for component-based statement resources/strings |

## Key Functions (ActiveReader / Monitor)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00401000 | CGenericActiveReader__SetReader | Core ActiveReader helper (remove from old deletion list, assign, register with new monitor) |
| 0x00401040 | CMonitor__AddDeletionEvent | monitor.h helper: allocate/init `CSPtrSet` at `monitor+0x04` (if NULL) and add reader cell |
| 0x0042d9b0 | CMonitor__DeleteDeletionEvent | monitor.h helper: remove `reader_cell` from `monitor+0x04` deletion list when present |
| 0x00419a20 | CMonitor__scalar_deleting_dtor | Scalar deleting dtor wrapper (shutdown + optional free when delete flag is set) |
| 0x0044b1d0 | CGenericActiveReader__dtor | Unregister helper used before freeing/destroying an ActiveReader (removes from `mToRead+0x04`) |
| 0x00466120 | CMonitor__ctor | Monitor base ctor: initializes monitor vtable and `monitor+0x04` deletion-list pointer |
| 0x0046dbc0 | CMonitor__Shutdown_Thunk | Thin compiler thunk forwarding to `CMonitor__Shutdown` |
| 0x004bac40 | CMonitor__Shutdown | Monitor shutdown/destructor path: nulls registered reader cells, then clears/frees `monitor+0x04` deletion list |
| 0x004bacb0 | CMonitor__Shutdown_Core | Shared monitor cleanup implementation used in many monitor-derived vtables |
| 0x00505d00 | CSPtrSet__ctor | Thin ctor wrapper used by monitor allocation paths; calls `CSPtrSet__Init(this)` and returns `this` |

## Key Functions (HUD Component)

| Address | Function | Notes |
|---------|----------|-------|
| 0x004de3a0 | CHudComponent__ctor | 0x68-byte HUD component ctor used by `CHud__SetHudComponent`; builds mesh name and initializes Effect/resource handles |
| 0x004de730 | CHudComponent__scalar_deleting_dtor | Scalar deleting dtor wrapper (`dtor` + conditional free) |
| 0x004de760 | CHudComponent__dtor | Destructor body (owned object release + `CMonitor__Shutdown`) |
| 0x004de850 | CHudComponent__RequestDestroy | Deferred-destroy mark helper (`+0x64/+0x65`) used by HUD slot switch/render path |
| 0x004de860 | CHudComponent__RenderPass | Per-component render/update pass (iterates sub-item table, calls `CHudComponent__RenderPassEntry`) |

## Key Functions (Random Helpers)

| Address | Function | Notes |
|---------|----------|-------|
| 0x004de8c0 | RandomSeedPair__Set | Initializes a 2-dword seed pair to the same value (current/base) |
| 0x004de8d0 | Random__NextLCGAbs | LCG step helper (Schrage-style constants), updates `*seed`, returns absolute value |

## Key Functions (Memory / Static Shadow Helpers)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00549270 | MEM_MANAGER__Cleanup | Source-level `MEM_MANAGER.Cleanup()` wrapper used in load/restart cleanup paths (double coalesce pass) |
| 0x004ebc00 | CStaticShadows__Reattach | Rebinds static-shadow entries to live things and refreshes visibility during restart-loop prep |

## Key Functions (Rendering State Helpers)

| Address | Function | Notes |
|---------|----------|-------|
| 0x00513bc0 | RenderState_Set | Cached render-state setter; forwards to device vtable call and swaps cull mode (2/3) when winding-flip flag is active |

## Key Functions (MSVC Runtime Helpers)

| Address | Function | Notes |
|---------|----------|-------|
| 0x0055dc20 | eh_vector_constructor_iterator | MSVC array-construction helper used by many class/vector initialization paths |
| 0x0055db8a | eh_vector_destructor_iterator | MSVC array-destruction helper used for cleanup/unwind paths |
 
## Source File Index

### Core Career System
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Career.cpp](Career.cpp/_index.md) | 35 | DOCUMENTED | Save/load, graph recalculation, goodies, grade helpers, and inline accessors |

### Frontend (FEP) Classes
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [FEPSaveGame.cpp](FEPSaveGame.cpp/_index.md) | 1 | MIGRATED | IsCheatActive, cheat system |
| [FEPGoodies.cpp](FEPGoodies.cpp/_index.md) | 7 | DOCUMENTED | Goodies gallery UI with resource deserialize/load/poll/release helpers |
| [FEPLoadGame.cpp](FEPLoadGame.cpp/_index.md) | 1 | MIGRATED | Save file loading |
| [FEPLevelSelect.cpp](FEPLevelSelect.cpp/_index.md) | 12 | DOCUMENTED | Level-select wheel page: world gating, selection logic, input/process/render + mouse-edge slide helper |
| [FEPDebriefing.cpp](FEPDebriefing.cpp/_index.md) | 1 | MIGRATED | Mission results |
| [FEPDirectory.cpp](FEPDirectory.cpp/_index.md) | 1 | DOCUMENTED | Save file directory browser |
| [FEPOptions.cpp](FEPOptions.cpp/_index.md) | 10 | DOCUMENTED | Options menu, defaultoptions.bea, sound/music floats + kill-counter meta usage |
| [FEPWingmen.cpp](FEPWingmen.cpp/_index.md) | 4 | DOCUMENTED | Wingmen selection screen, CRelaxedSquad |
| [FEPMultiplayerStart.cpp](FEPMultiplayerStart.cpp/_index.md) | 16 | DOCUMENTED | Multiplayer start screen. Primary vtable `0x005db8d0` is mapped, and embedded subobject vtable `0x005db4fc` entries were recovered/mapped headlessly on 2026-02-25 (`Init/ActiveNotification/Process/ButtonPressed/RenderPreCommon/Render/TransitionNotification`). |
| [FEPLanguageTest.cpp](FEPLanguageTest.cpp/_index.md) | 6 | DOCUMENTED | Developer/debug language test page ("LANGUAGE TEST"). Recovered via manual `F` + MCP rename/signature; previously misattributed as MultiplayerStart due to vtable mix-up. |
| [FEPVirtualKeyboard.cpp](FEPVirtualKeyboard.cpp/_index.md) | 6 | DOCUMENTED | Save-name virtual keyboard page (vtable `0x005db830`) recovered via manual `F` + serialized direct-HTTP rename/signature read-back. |
| [FEPScreenPos.cpp](FEPScreenPos.cpp/_index.md) | 5 | DOCUMENTED | Screen-position calibration page (RTTI `.?AVCFEPScreenPos@@`); core vtable (`Init/ButtonPressed/RenderPreCommon/Render/TransitionNotification`) mapped. |
| [FEPCredits.cpp](FEPCredits.cpp/_index.md) | 5 | DOCUMENTED | Credits frontend page (RTTI `.?AVCFEPCredits@@`); `Process/ButtonPressed/RenderPreCommon/Render/TransitionNotification` vtable core mapped |
| [FEPMain.cpp](FEPMain.cpp.md) | 10 | DOCUMENTED | Main menu page: process/button/render/transition + navigation/page IDs |
| [FEPBEConfig.cpp](FEPBEConfig.cpp/_index.md) | 8 | DOCUMENTED | Battle Engine weapon loadout config |
| [MenuItem.cpp](MenuItem.cpp/_index.md) | 34 | DOCUMENTED | Menu UI components - CMenuItem, Dropdown, Slider, Range |

### Game Core
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [ltshell.cpp](ltshell.cpp/_index.md) | 1 | DOCUMENTED | WinMain entry point, Lost Toys Shell |
| [Credits.cpp](Credits.cpp/_index.md) | 3 | DOCUMENTED | Credits table-build + entry-writer helpers + shared renderer used by outro/FE credits paths |
| [game.cpp](game.cpp/_index.md) | 38 | DOCUMENTED | Game lifecycle/render/event core: initialize/restart/render, pause/unpause, intro/outro FMV flow, credits loop driver, level win/loss, respawn, camera/debug helpers, music/cutscene helpers, wait-helper ctor, and console command handlers |
| [PauseMenu.cpp](PauseMenu.cpp/_index.md) | 1 | MIGRATED | Pause menu, god mode toggle |
| [CLIParams.cpp](CLIParams.cpp/_index.md) | 1 | MIGRATED | Command line parsing (no debug path - identified via other means) |
| [monitor.h](monitor.h/_index.md) | 4 | DOCUMENTED | ActiveReader deletion-event system (safe pointer null-on-delete) |

### Script & World
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Script.cpp](Script.cpp/_index.md) | 2 | DOCUMENTED | Runtime slot-bit API (`CGame__SetSlot` / `CGame__GetSlot`) used by MissionScripts |
| [world.cpp](world.cpp/_index.md) | 1 | MIGRATED | World/level loading |

### Unit System (Phase 1 Xref Discovery - Batch 1)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Player.cpp](Player.cpp/_index.md) | 3 | DOCUMENTED | ctor, dtor, GotoPanView |
| [BattleEngine.cpp](BattleEngine.cpp/_index.md) | 3 | DOCUMENTED | Init, UpdateWeaponEffect, AddProjectile |
| [Unit.cpp](Unit.cpp/_index.md) | 4 | DOCUMENTED | Init, ApplyDamage, UpdateTransform, TriggerEffect |
| [Mech.cpp](Mech.cpp/_index.md) | 3 | DOCUMENTED | InitLegMotion, InitCockpit, InitTargeting |

### Unit Types (Phase 1 Xref Discovery - Batch 2)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Carrier.cpp](Carrier.cpp/_index.md) | 1 | DOCUMENTED | Init - transport vessel |
| [Infantry.cpp](Infantry.cpp/_index.md) | 1 | DOCUMENTED | Init - foot soldiers |
| [Bomber.cpp](Bomber.cpp/_index.md) | 0* | PARTIAL | *Constructor inline, NOT in Stuart's source |

### Aircraft Classes (Phase 1 Xref Discovery - Batch 3)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [AirUnit.cpp](AirUnit.cpp/_index.md) | 1 | DOCUMENTED | Init - Trail/Engine effects |
| [DiveBomber.cpp](DiveBomber.cpp/_index.md) | 1 | DOCUMENTED | SelectTarget - AI targeting |
| [GroundAttackAircraft.cpp](GroundAttackAircraft.cpp/_index.md) | 1 | DOCUMENTED | Constructor recovered and mapped (`CGroundAttackAircraft__Constructor`) |

### Water & Ground Vehicles (Phase 1 Xref Discovery - Batch 4)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Boat.cpp](Boat.cpp/_index.md) | 1 | DOCUMENTED | Init - surface vessel |
| [Submarine.cpp](Submarine.cpp/_index.md) | 1 | DOCUMENTED | Init - underwater vessel |
| [GroundUnit.cpp](GroundUnit.cpp/_index.md) | 2 | DOCUMENTED | Init, CreateCollisionSphere |
| [GroundVehicle.cpp](GroundVehicle.cpp/_index.md) | 1 | DOCUMENTED | Init - wheeled vehicles |

### Weapons & Projectiles (Phase 1 Xref Discovery - Batch 5)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Missile.cpp](Missile.cpp/_index.md) | 1 | DOCUMENTED | Init - guided missiles |
| [Round.cpp](Round.cpp/_index.md) | 1 | DOCUMENTED | Init - projectile base class |
| [Mine.cpp](Mine.cpp/_index.md) | 1 | DOCUMENTED | Init - explosive mines |
| [CollisionSeekingRound.cpp](CollisionSeekingRound.cpp/_index.md) | 9 | DOCUMENTED | Seeking projectiles with collision avoidance (also covers collisionseekingthing.cpp) |

### Weapons, Structures & Systems (Phase 1 Xref Discovery - Batch 6)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Cannon.cpp](Cannon.cpp/_index.md) | 6 | DOCUMENTED | State machine, firing, init/update/transition helpers |
| [Building.cpp](Building.cpp/_index.md) | 1 | DOCUMENTED | CreateRepairPadAI, repair pads |
| [Camera.cpp](Camera.cpp/_index.md) | 12 | DOCUMENTED | CThing3rdPersonCamera + CPanCamera mappings (includes orphan accessor/handler blocks) |
| [BSpline.cpp](BSpline.cpp/_index.md) | 4 | DOCUMENTED | B-spline curves for camera paths |
| [Dropship.cpp](Dropship.cpp/_index.md) | 1 | DOCUMENTED | Init - transport aircraft with thrusters |

### Core Systems & Bosses (Phase 1 Xref Discovery - Batch 7)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [engine.cpp](engine.cpp/_index.md) | 5 | DOCUMENTED | Init, SetCamera, CVar system + DX render pipeline (`CDXEngine__PreRender/Render/PostRender`) |
| [Cutscene.cpp](Cutscene.cpp/_index.md) | 4 | DOCUMENTED | Load, AddAnimation, Update, InitAnimations |
| [HiveBoss.cpp](HiveBoss.cpp/_index.md) | 1 | DOCUMENTED | Init - boss enemy, "core2" model |
| [Sentinel.cpp](Sentinel.cpp.md) | 7* | DOCUMENTED | Activate/Deactivate, flamethrowers, *Constructor needs manual Ghidra creation |
| [world.cpp](world.cpp/_index.md) | 7 | DOCUMENTED | CWorld - level loading, script events, LOD lists |

### Environment & Weather (Phase 1 Xref Discovery - Batch 14)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Atmospherics.cpp](Atmospherics.cpp/_index.md) | 6 | DOCUMENTED | Weather system - rain, snow, lightning, wind cvars |

### Managers & Systems (Phase 1 Xref Discovery - Batch 8, 25)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Warspite.cpp](Warspite.cpp/_index.md) | 4 | DOCUMENTED | Naval AI - Create, Init, Destructor, Update |
| [WarspiteDome.cpp](WarspiteDome.cpp/_index.md) | 3 | DOCUMENTED | CWarspiteDome - boss dome component, CGroundUnit subclass |
| [MemoryManager.cpp](MemoryManager.cpp/_index.md) | 7 | DOCUMENTED | Init, Alloc, Free, Realloc, Coalesce, DumpStats, global cleanup wrapper |
| [SoundManager.cpp](SoundManager.cpp/_index.md) | 2 | DOCUMENTED | Init, LoadSoundDefinitions, cvars |
| [ParticleManager.cpp](ParticleManager.cpp/_index.md) | 4 | DOCUMENTED | Init, CreateEffect, AllocateParticle, LOD system |
| [ParticleDescriptor.cpp](ParticleDescriptor.cpp/_index.md) | 2 | DOCUMENTED | Update, Load - particle effect definitions |
| [eventmanager.cpp](eventmanager.cpp/_index.md) | 12 | DOCUMENTED | Event scheduling system (ctor/dtor/init/shutdown/add-event/update/flush), 20K event pool |
| [scheduledevent.cpp](scheduledevent.cpp/_index.md) | 2 | DOCUMENTED | Scheduled event object used by EventManager (`Set`, dtor) |
| [Music.cpp](Music.cpp/_index.md) | 11 | DOCUMENTED | Music playback, playlist, volume control |

### Frontend, Input & UI (Phase 1 Xref Discovery - Batch 9)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [FrontEnd.cpp](FrontEnd.cpp/_index.md) | 6 | DOCUMENTED | CFrontEnd__Init, SetPage, Process, Render, Run, PlaySound - 24 FEP pages, transitions, UI sounds |
| [Hud.cpp](Hud.cpp/_index.md) | 7 | DOCUMENTED | CHud core + CHudComponent lifecycle/render helpers |
| [Controller.cpp](Controller.cpp/_index.md) | 23 | DOCUMENTED | CController stack/control dispatch + mapping engine + PC joystick/key/analogue helpers (vtable `0x005e48e0`) |
| [DestructableSegmentsController.cpp](DestructableSegmentsController.cpp/_index.md) | 7 | DOCUMENTED | Segment destruction, hierarchical damage |

### Base Classes & Core Systems (Phase 1 Xref Discovery - Batch 10)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [thing.cpp](thing.cpp/_index.md) | 4 | DOCUMENTED | CThing base class - collision, name, sound, trails |
| [damage.cpp](damage.cpp/_index.md) | 3 | DOCUMENTED | CDamage__Init, LoadDamageTexture, CreateTextureBuffer |

### Rendering & 3D Systems (Phase 1 Xref Discovery - Batch 11-12, 15-16)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [mesh.cpp](mesh.cpp/_index.md) | 6 | DOCUMENTED | CMesh - mesh loading, caching, AYA archive |
| [texture.cpp](texture.cpp/_index.md) | 5 | DOCUMENTED | CTexture - texture lookup, caching, 248 callers |
| [tgaloader.cpp](tgaloader.cpp/_index.md) | 4 | DOCUMENTED | CTGALoader - TGA texture loading, RLE decompression |
| [Component.cpp](Component.cpp/_index.md) | 3 | DOCUMENTED | CComponent factory - Fenrir/Carrier weapon components |
| [imposter.cpp](imposter.cpp/_index.md) | 2 | DOCUMENTED | CImposter - billboard sprites for distant objects |
| [MeshPart.cpp](MeshPart.cpp/_index.md) | 12 | DOCUMENTED | CMeshPart - mesh geometry, vertices, skinning |
| [MeshRenderer.cpp](MeshRenderer.cpp/_index.md) | 1 | DOCUMENTED | CMeshRenderer - rendering dispatch, LOD handling |
| [MeshCollisionVolume.cpp](MeshCollisionVolume.cpp/_index.md) | 2 | DOCUMENTED | CMeshCollisionVolume - collision bounds for mesh parts |
| [DXFont.cpp](DXFont.cpp/_index.md) | 5 | DOCUMENTED | CDXFont - DirectX font rendering, GDI font creation |
| [DXCompass.cpp](DXCompass.cpp/_index.md) | 7 | DOCUMENTED | CDXCompass - compass HUD, threat markers, split-screen |
| [DXClouds.cpp](DXClouds.cpp.md) | 2 | DOCUMENTED | CDXClouds - cloud rendering, cg_cloudwidth cvar |
| [DXMeshVB.cpp](DXMeshVB.cpp/_index.md) | 3 | DOCUMENTED | CDXMeshVB - DirectX vertex/index buffer management |
| [DXTexture.cpp](DXTexture.cpp/_index.md) | 5 | DOCUMENTED | CDXTexture - texture loading, mipmaps, DXT compression |
| [DXLandscape.cpp](DXLandscape.cpp/_index.md) | 20 | DOCUMENTED | CDXLandscape - terrain rendering, LOD, shadow maps |
| [DXShadows.cpp](DXShadows.cpp.md) | 3 | DOCUMENTED | CDXShadows - shadow system, blob shadows |
| [DXImposter.cpp](DXImposter.cpp/_index.md) | 2 | DOCUMENTED | CDXImposter - imposter rendering, vertex buffers |
| [DXFrontEndVideo.cpp](DXFrontEndVideo.cpp.md) | 12 | DOCUMENTED | CDXFrontEndVideo - Bink video playback for menus |
| [DXBattleLine.cpp](DXBattleLine.cpp.md) | 10 | DOCUMENTED | CDXBattleLine - battle line HUD, territory visualization |
| [DXFMV.CPP](DXFMV.cpp.md) | 8 | DOCUMENTED | CDXFMV, CBinkOpenThread - Bink video playback, async loading |
| [DXPalletizer.cpp](DXPalletizer.cpp.md) | 9 | DOCUMENTED | Color quantization - octree palette, texture swizzling |
| [DXParticleTexture.cpp](DXParticleTexture.cpp.md) | 8 | DOCUMENTED | Particle texture manager - factory, batch rendering, shaders |
| [DXMemBuffer.cpp](DXMemBuffer.cpp.md) | 9 | DOCUMENTED | Buffered file I/O with zlib compression support |
| [DXKempyCube.cpp](DXKempyCube.cpp.md) | 5 | DOCUMENTED | CDXKempyCube - environment cube mapping, skybox rendering |
| [DXTrees.cpp](DXTrees.cpp.md) | 9 | DOCUMENTED | CDXTrees - tree billboard rendering, quadtree queries |
| [DXSurf.cpp](DXSurf.cpp.md) | 12 | DOCUMENTED | CDXSurf - water/wave surface rendering, sine geometry |
| [DXPatchManager.cpp](DXPatchManager.cpp.md) | 8 | DOCUMENTED | CDXPatchManager - terrain LOD patch pools, vertex buffers |
| [gcgamut.cpp](gcgamut.cpp.md) | 4 | DOCUMENTED | CGamut - view frustum visibility culling, 64x64 grid |

### Terrain Systems (Phase 1 Xref Discovery - Batch 12)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [HeightField.cpp](HeightField.cpp/_index.md) | 2 | DOCUMENTED | CHeightField - terrain loading, 663KB height buffer |

### AI & Navigation (Phase 1 Xref Discovery - Batch 11+14)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [InfluenceMap.cpp](InfluenceMap.cpp/_index.md) | 13 | DOCUMENTED | CInfluenceMap/Manager - territorial AI, faction control |
| [WaypointManager.cpp](WaypointManager.cpp/_index.md) | 3 | DOCUMENTED | CWaypointManager - waypoint loading, entity linking |
| [SquadNormal.cpp](SquadNormal.cpp/_index.md) | 7 | DOCUMENTED | CSquadNormal - squad AI, member spawning, linked list |

### Developer Console (Phase 1 Xref Discovery - Batch 11)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [console.cpp](console.cpp/_index.md) | 4 | DOCUMENTED | CConsole - developer console, commands, cvars |

### Text & Localization (Phase 1 Xref Discovery - Batch 12)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [text.cpp](text.cpp/_index.md) | 9 | DOCUMENTED | CText - language file loading + lookup (UTF-16 + audio IDs) |

### Cutscene Systems (Phase 1 Xref Discovery - Batch 13)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [RTCutscene.cpp](RTCutscene.cpp/_index.md) | 6 | DOCUMENTED | CRTCutscene - real-time cutscenes, vtable 0x005dea38 |

### Unit Types (Phase 1 Xref Discovery - Batch 13)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [ThunderHead.cpp](ThunderHead.cpp/_index.md) | 3 | DOCUMENTED | CThunderHead - boss mech, leg motion, Warspite AI |
| [Tentacle.cpp](Tentacle.cpp/_index.md) | 3 | DOCUMENTED | CTentacle - boss enemy, factory methods for Guide/AI |

### Motion Controllers (Phase 1 Xref Discovery - Batch 14-15, 24-25)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [GillM.cpp](GillM.cpp/_index.md) | 3 | DOCUMENTED | CGillM - motion controller, leg motion, Warspite component |
| [GillMHead.cpp](GillMHead.cpp/_index.md) | 7 | DOCUMENTED | CGillMHead - head motion, position offset 100 units from parent |
| [MCBuggy.cpp](MCBuggy.cpp/_index.md) | 12 | DOCUMENTED | CMCBuggy - wheeled vehicle wheel physics and animation |
| [MCMech.cpp](MCMech.cpp.md) | 11 | DOCUMENTED | CMCMech - procedural leg animation, 24 hydraulic cylinders |
| [MCTentacle.cpp](MCTentacle.cpp.md) | 8 | DOCUMENTED | CMCTentacle - Bezier spline tentacle animation |

### Image Loading (Phase 1 Xref Discovery - Batch 15)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [imageloader.cpp](imageloader.cpp/_index.md) | 7 | DOCUMENTED | CImageLoader - base class for image loading, width/height buffers |

### Object Initialization (Phase 1 Xref Discovery - Batch 15)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [InitThing.cpp](InitThing.cpp/_index.md) | 2 | DOCUMENTED | CInitThing factory - object spawning, 13 subclasses |

### Particles (Phase 1 Xref Discovery - Batch 17)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [ParticleSet.cpp](ParticleSet.cpp/_index.md) | 7 | DOCUMENTED | CParticleSet - 13 particle types, .par file loading |

### Real-Time Systems (Phase 1 Xref Discovery - Batch 17)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [rtmesh.cpp](rtmesh.cpp/_index.md) | 7 | DOCUMENTED | CRTMesh - LOD, imposters, 10 console variables |

### Spawning & Triggers (Phase 1 Xref Discovery - Batch 17)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [SpawnerThng.cpp](SpawnerThng.cpp/_index.md) | 13 | DOCUMENTED | CSpawnerThng - wave spawning, collision checks |
| [SphereTrigger.cpp](SphereTrigger.cpp/_index.md) | 2 | DOCUMENTED | CSphereTrigger - spherical trigger volumes |

### Containers & Utilities (Phase 1 Xref Discovery - Batch 18, 29)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [SPtrSet.cpp](SPtrSet.cpp/_index.md) | 3 | DOCUMENTED | CSPtrSet - smart pointer list, free pool pattern |
| [flexarray.cpp](flexarray.cpp.md) | 8 | DOCUMENTED | CFlexArray - dynamic array with growth factor |
| [chunker.cpp](chunker.cpp/_index.md) | 3 | DOCUMENTED | CChunker - chunked resource loading, 308 bytes |

### Rendering & Shadows (Phase 1 Xref Discovery - Batch 18, 29)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [StaticShadows.cpp](StaticShadows.cpp/_index.md) | 9 | DOCUMENTED | CStaticShadows - shadow maps, reattach/update visibility, ray-triangle intersect |
| [bytesprite.cpp](bytesprite.cpp/_index.md) | 11 | DOCUMENTED | CByteSprite - RLE sprites, compass HUD |

### AI Squad States (Phase 1 Xref Discovery - Batch 18)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [SquadRelaxed.cpp](SquadRelaxed.cpp/_index.md) | 2 | DOCUMENTED | CRelaxedSquad - idle/patrol AI state |

### Aircraft Units (Phase 1 Xref Discovery - Batch 18)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Plane.cpp](Plane.cpp/_index.md) | 1 | DOCUMENTED | CPlane - fighter aircraft, CAirUnit subclass |

### Spatial Systems (Phase 1 Xref Discovery - Batch 19, 28)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [PolyBucket.cpp](PolyBucket.cpp/_index.md) | 16 | DOCUMENTED | Spatial partitioning, collision detection, line search |
| [mapwho.cpp](mapwho.cpp/_index.md) | 22 | DOCUMENTED | Quadtree spatial partitioning (64x64 to 4x4), radius/line queries |

### Resource Systems (Phase 1 Xref Discovery - Batch 19)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [ResourceAccumulator.cpp](ResourceAccumulator.cpp/_index.md) | 2 | DOCUMENTED | AYA archive loading, chunk parsing |

### Radar Warning System (Phase 1 Xref Discovery - Batch 20)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [RadarWarningReceiver.cpp](RadarWarningReceiver.cpp/_index.md) | 4 | DOCUMENTED | RWR threat detection, bearing calculation, alerts |

### Platform Abstraction (Phase 1 Xref Discovery - Batch 19, 28)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Platform.cpp](Platform.cpp/_index.md) | 5+7 | DOCUMENTED | Platform abstraction wrappers (`Process/BeginScene/ClearScreen/EndScene/GetSysTimeFloat`) + PCPlatform save file ops |
| [PCPlatform.cpp](PCPlatform.cpp/_index.md) | 10 | DOCUMENTED | PC platform - save files, fonts, D3D init |

### Serialization (Phase 1 Xref Discovery - Batch 20)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [TokenArchive.cpp](TokenArchive.cpp/_index.md) | 8 | DOCUMENTED | Particle config parsing, 124 token types |

### Environment (Phase 1 Xref Discovery - Batch 20)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [tree.cpp](tree.cpp/_index.md) | 3 | DOCUMENTED | Environmental trees, falling physics, bounce |

### Mesh Generation (Phase 1 Xref Discovery - Batch 20)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [triangulate.cpp](triangulate.cpp/_index.md) | 1 | DOCUMENTED | Quad mesh triangulation, subdivision modes |

### Vertex Buffers (Phase 1 Xref Discovery - Batch 20-21, 27)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [vbuffer.cpp](vbuffer.cpp/_index.md) | 12 | DOCUMENTED | D3D vertex buffer wrapping, lock/unlock, streaming |
| [vbuftexture.cpp](vbuftexture.cpp/_index.md) | 18 | DOCUMENTED | Vertex buffer + texture, batched rendering |
| [ibuffer.cpp](ibuffer.cpp/_index.md) | 9 | DOCUMENTED | D3D index buffer, static/dynamic, shadow buffer |
| [FastVB.cpp](FastVB.cpp/_index.md) | 7 | DOCUMENTED | Fast quad rendering, auto-flush, shared index buffer |

### Landscape Rendering (Phase 1 Xref Discovery - Batch 27-28)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [landscapeib.cpp](landscapeib.cpp/_index.md) | 1 | DOCUMENTED | Terrain grid index buffer generation |
| [LandscapeTexture.cpp](LandscapeTexture.cpp/_index.md) | 14 | DOCUMENTED | Tile-based terrain texturing, RGB565 blending |
| [maptex.cpp](maptex.cpp/_index.md) | 6 | DOCUMENTED | Terrain textures (grass, rock, sand, etc), height encoding |

### Shaders (Phase 1 Xref Discovery - Batch 21)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [VertexShader.cpp](VertexShader.cpp/_index.md) | 5 | DOCUMENTED | D3D8 vertex shader compilation, caching |

### Audio (Phase 1 Xref Discovery - Batch 21-23)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [wavread.cpp](wavread.cpp/_index.md) | 7 | DOCUMENTED | RIFF WAVE audio file parsing, mmio API |
| [mixermap.cpp](mixermap.cpp/_index.md) | 4 | DOCUMENTED | Audio mixer map, 4096 channel slots |

### World Systems (Phase 1 Xref Discovery - Batch 21-22)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [WorldMeshList.cpp](WorldMeshList.cpp/_index.md) | 3 | DOCUMENTED | World mesh tracking, child mesh recursion |
| [WorldPhysicsManager.cpp](WorldPhysicsManager.cpp/_index.md) | 13 | DOCUMENTED | Entity factory, 26 physics object types |

### PC Sound System (Phase 1 Xref Discovery - Batch 22)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [pcsoundmanager.cpp](pcsoundmanager.cpp/_index.md) | 6 | DOCUMENTED | DirectSound, ADPCM decoding, quality levels |

### Configuration & Serialization (Phase 1 Xref Discovery - Batch 24)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [BattleEngineConfigurations.cpp](BattleEngineConfigurations.cpp/_index.md) | 2 | DOCUMENTED | Config name loading/skipping |
| [BattleEngineDataManager.cpp](BattleEngineDataManager.cpp/_index.md) | 3 | DOCUMENTED | Weapon loadouts, versioned serialization (12+ versions) |

### Object Factory Systems (Phase 1 Xref Discovery - Batch 28-29)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [PCRTID.cpp](PCRTID.cpp/_index.md) | 3 | DOCUMENTED | CRT object factory - CRTMesh, CRTTree, CRTBuilding, CRTCutscene |
| [oids.cpp](oids.cpp/_index.md) | 5 | DOCUMENTED | OID object factory - 20+ game object types |

### Mission Scripting (Phase 1 Xref Discovery - Batch 36-39)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [AsmInstruction.cpp](AsmInstruction.cpp.md) | 13 | DOCUMENTED | CAsmInstruction - bytecode VM, 27 opcodes, stack machine |
| [EventFunction.cpp](EventFunction.cpp.md) | 5 | DOCUMENTED | CEventFunction - event-triggered script functions |
| [ScriptEventNB.cpp](ScriptEventNB.cpp.md) | 15 | DOCUMENTED | CScriptEventNB - non-blocking events, waypoints |
| [IScript.cpp](IScript.cpp.md) | 28 | DOCUMENTED | Script instruction handlers - cameras, sounds, vectors, slots, goodies, level outcome |
| [DataType.cpp](DataType.cpp.md) | 38 | DOCUMENTED | Script data types - int, float, string, position, thing ptr |
| [Symtab.cpp](Symtab.cpp.md) | 2 | DOCUMENTED | CSymtab - script symbol table, variable names/types |
| [ScriptObjectCode.cpp](ScriptObjectCode.cpp.md) | 17 | DOCUMENTED | CScriptObjectCode - bytecode VM, stack ops, main Run loop |

### Physics Scripting (Phase 1 Xref Discovery - Batch 30+35)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [CPhysicsScript.cpp](CPhysicsScript.cpp.md) | 5 | DOCUMENTED | Physics script manager - singleton, 9 statement types |
| [CPhysicsScriptStatements.cpp](CPhysicsScriptStatements.cpp.md) | 7+ | PARTIAL | Recovered statement helper set (`CWeaponStatement*`, `CWeaponModeStatement*`, `CRoundStatement*`, `CComponentBasedOn__CopyFrom`); full subtype family still in progress |

### Rendering & Culling (Phase 1 Xref Discovery - Batch 35)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [gcgamut.cpp](gcgamut.cpp.md) | 4 | DOCUMENTED | CGamut - view frustum culling, 64x64 visibility grid |

### Enemy AI (Phase 1 Xref Discovery - Batch 35)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [Carver.cpp](Carver.cpp.md) | 12 | DOCUMENTED | CCarverAI, CCarverGuide - flying mech with folding wings |

### Frontend (FEP) - Additional (Phase 1 Xref Discovery - Batch 39)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [FEPDevelopment.cpp](FEPDevelopment.cpp.md) | 1 | DOCUMENTED | CFEPDevelopment__EnumerateWorldFiles - world file enumeration |

### Weather Effects (Phase 1 Xref Discovery - Batch 39)
| Source File | Functions | Status | Notes |
|-------------|-----------|--------|-------|
| [DXSnow.cpp](DXSnow.cpp.md) | 1 | DOCUMENTED | CDXSnow__Init - 1000 snowflake particles, 4 cvars |

### Not Processed (No Functions Found)
| Source File | Status | Notes |
|-------------|--------|-------|
| Actor.cpp | NO_DEBUG_PATH | No debug path string found in binary |

### Files Not In Binary (Stripped/Internal)
| Source File | Notes |
|-------------|-------|
| EditorD3DApp.cpp | Internal dev tool - stripped from release |
| CreditMenu.cpp | RTTI exists but no debug path |
| EndLevelData.cpp | Runtime-only struct |
| Crc.cpp | Inlined into DXMemBuffer.cpp |

---

## Statistics

- **Total Functions in Binary:** 5,861
- **Named Functions:** 5,861 (100.00%)
- **Source-file entries tracked (`Functions` numeric rows):** 158
- **Functions represented in source-file corpus (`Functions` numeric sum):** 1,059
- **Source-file directories with index docs:** 131
- **Canonical live metrics:** see `FUNCTION_COVERAGE_STATE.md`

---

## Reference Documentation

Cross-cutting topics that span multiple source files or document system-level functionality.

| Document | Topic | Notes |
|----------|-------|-------|
| [display-settings.md](display-settings.md) | Display & Video Settings | CD3DApplication, -forcewindowed/-res CLI, Video Options menu |
| [globals.md](globals.md) | Global Variables | g_bDevModeEnabled, cheat table, physics script singleton |

---

## Global Variables

See [globals.md](globals.md) for global variable mappings.

| Address | Name | Notes |
|---------|------|-------|
| 0x00662df4 | g_bDevModeEnabled | Dev mode flag |
| 0x00679ec1 | g_bAllCheatsEnabled | All cheats flag (BSS) |
| 0x00662ab4 | g_bGodModeEnabled | God mode state |
| 0x00629464 | Cheat table | XOR-encrypted codes |
| 0x00629a64 | XOR key | "HELP ME!!" |
| 0x0066e99c | g_pPhysicsScript | Physics script manager singleton |

---

## Migration Status

- [x] Backup created: `BACKUP/ghidra-analysis.md.bak`
- [x] Career.cpp migrated (23 functions)
- [x] FEP* files migrated (4 functions)
- [x] Other files migrated (6 functions)
- [x] Verification complete (2025-12-15)
- [x] Phase 1 xref discovery (13 functions) - 2025-12-15

**Phase 0 Verification Results:**
- Career.cpp: PASS - All 23 functions verified
- FEP/Other: PASS - All 10 functions verified
- Globals: PASS - All variables documented
- No data loss detected

**Phase 1 Discovery Results (Batch 1):**
- Player.cpp: 3 functions via xref to debug path 0x00631690
- BattleEngine.cpp: 3 functions via xref to debug path 0x006230bc
- Unit.cpp: 4 functions via xref to debug path 0x00633b6c
- Mech.cpp: 3 functions via xref to debug path 0x0062e0e0
- All 13 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 2):**
- Carrier.cpp: 1 function via xref to debug path 0x006243bc
- Infantry.cpp: 1 function via xref to debug path 0x0062d4a8
- Bomber.cpp: 0 functions (constructor inline) via xref to 0x00623a78
- Note: Bomber.cpp NOT in Stuart's source dump - binary-only discovery
- All 2 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 3):**
- AirUnit.cpp: 1 function (CAirUnit__Init) via xref to debug path 0x00622cf4
- DiveBomber.cpp: 1 function (CDiveBomber__SelectTarget) via xref to 0x006289c0
- GroundAttackAircraft.cpp: constructor recovered at 0x0047bbf0 and mapped as `CGroundAttackAircraft__Constructor`
- All 3 functions renamed/recovered in Ghidra and documented

**Phase 1 Discovery Results (Batch 4):**
- Boat.cpp: 1 function (CBoat__Init) via xref to debug path 0x00623990
- Submarine.cpp: 1 function (CSubmarine__Init) via xref to 0x00632abc
- GroundUnit.cpp: 2 functions (CGroundUnit__Init, CGroundUnit__CreateCollisionSphere) via xref to 0x0062cb0c
- GroundVehicle.cpp: 1 function (CGroundVehicle__Init) via xref to 0x0062cb30
- All 5 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 5):**
- Missile.cpp: 1 function (CMissile__Init) via xref to debug path 0x006309c0
- Round.cpp: 1 function (CRound__Init) via xref to 0x00631d38
- Mine.cpp: 1 function (CMine__Init) via xref to 0x006309a4
- All 3 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 6):**
- Cannon.cpp: 6 functions via xref to debug path 0x00623dd4 (includes `CCannon__Init` at 0x0041b1a0)
  - State machine: Active/Inactive/Activating/Deactivating
- Building.cpp: 1 function (CBuilding__CreateRepairPadAI) via xref to 0x00623af4
  - Creates CRepairPadAI for "Forseti Repair Pad" buildings
- Camera.cpp: 3 functions via xref to debug path 0x00623c90
  - `CThing3rdPersonCamera__ctor` @ `0x00418ef0`
  - `CThing3rdPersonCamera__dtor` @ `0x00419140`
  - `CThing3rdPersonCamera__scalar_deleting_dtor` @ `0x00419120`
  - Uses `CBSpline` for smooth 3rd-person camera movement
  - Also mapped: `CPanCamera__ctor` @ `0x004198d0` (discovered via monitor.h deletion-list string)
- BSpline.cpp: 4 functions via xref to debug path 0x00623ab8
  - CBSpline__ctor, CBSpline__dtor, CBSpline__BasisFunction, CBSpline__GetPoint
  - Cox-de Boor recursion for B-spline basis functions
  - Used by CCamera and CPlayer for smooth interpolation
- Dropship.cpp: 1 function (CDropship__Init) via xref to 0x00628a54
  - Inherits CAirUnit, has thruster system with "Thruster Dust Effect"
- All 14 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 7):**
- engine.cpp: 5 functions via xref to debug path 0x00628b40
  - CEngine__Init (0x004499d0), CEngine__SetViewpoint (0x0044a020), CEngine__SetNumViewpoints (0x00528b50)
  - Has CVar system for hit effect colors (cg_hiteffectfactor*)
- Cutscene.cpp: 3 functions via xref to 0x0062811c
  - CCutscene__Load, CCutscene__AddAnimation, CCutscene__Update
  - `CCutscene__InitAnimations` recovered at 0x0043f510
  - Loads .cut files from data\cutscenes\, frame-based playback
- HiveBoss.cpp: 1 function (CHiveBoss__Init) via xref to 0x0062cc98
  - Boss enemy, inherits CUnit, uses "core2" model
- Sentinel.cpp: 7 functions (6 renamed, 1 needs manual creation at 0x004dea50)
- All 6 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 8):**
- Warspite.cpp: 4 functions via xref to debug path 0x0063d12c
  - CWarspite__Create, Init, Destructor, Update
  - Naval AI controller for battleships, state machine with Fighting/Waypoint/Target modes
- MemoryManager.cpp: 6 functions via xref to 0x0062f590 (13 total in file)
  - CMemoryManager__Init, Alloc, Free, Realloc, Coalesce, DumpStats
  - Thread-safe heap with bucketed free lists, 16-byte alignment, magic sentinel 0x4f69ea21
- SoundManager.cpp: 2 functions via xref to 0x00632428
  - CSoundManager__Init, LoadSoundDefinitions
  - 256 sound event pool, cvars (snd_frozen, snd_visible), 3D attenuation (50m range)
- ParticleManager.cpp: 4 functions via xref to 0x00630e60
  - CParticleManager__SetParticleResource, Init, CreateEffect, AllocateParticle
  - 512 particles per pool, LOD-based culling for performance
- All 16 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 9):**
- FrontEnd.cpp: 6 functions via xref/callsite mapping to debug path 0x00629df0
  - CFrontEnd__Init (0x004662a0) - Main initialization, loads 24 FEP pages, allocates player objects
  - CFrontEnd__Process (0x00466ba0) - Per-frame frontend update (event manager/pages/controllers/message box)
  - CFrontEnd__Render (0x00468200) - Frontend render pass used by `CFrontEnd__Run` transition wait loop
  - CFrontEnd__Run (0x004684d0) - Main loop, state machine (-2=running, -1=exit, >=0=world ID)
  - References g_bDevModeEnabled and g_bAllCheatsEnabled for conditional pages
- Hud.cpp: 2 functions via xref to debug path 0x0062ce78
  - CHud__Init (0x00481450) - Initializes HUD, allocates buffers, loads 8 texture resources
  - CHud__SetHudComponent (0x00481f40) - Creates/destroys HUD component objects
- Controller.cpp: 23 functions via xref/vtable mapping to debug path 0x00625538
  - CController stack/control helpers: Init, GetToControl, SetToControl, RelinquishControl, SendButtonAction, inactivity timeout guard
  - Mapping pipeline: Flush -> DoMappings (push_type switch)
  - PC/Steam vtable helpers (`0x005e48e0`): joystick buttons, keyboard state, analogue axes, POV hat, record/read controller state
- DestructableSegmentsController.cpp: 7 functions via xref to debug path 0x006287b4
  - CDestructableSegmentsController__Init (0x00444660) - Initialize controller
  - CDestructableSegmentsController__CreateSegment (0x004449c0) - Factory for 4 segment types
  - CDestructableSegmentsController__ProcessNode (0x00444c10) - Recursive node processor
  - CDestructableSegment__InitPrimary (0x00443480) - Primary/core segment init
  - CDestructableSegment__Init (0x004425a0) - Base segment initialization
  - CDestructableSegment__Register (0x00442700) - Register with monitor system
  - CDestructableSegment__GetTotalHealth (0x00442900) - Recursive health calculation
- All 13 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 10):**
- damage.cpp: 3 functions via xref to debug path 0x006282dc
  - CDamage__Init (0x00440b90) - Initialize damage system, load default texture
  - CDamage__LoadDamageTexture (0x00440c70) - TGA loader with mipmap generation
  - CDamage__CreateTextureBuffer (0x00441000) - Allocate texture buffer memory
- eventmanager.cpp: 12 functions mapped (core scheduler flow)
  - CEventManager__ctor / dtor / scalar_deleting_dtor / Init / Shutdown / GetNextFreeEvent
  - CEventManager__AddEvent_TimeFromNow / AddEvent_ScheduledEvent / AddEvent_AtTime
  - CEventManager__Update / AdvanceTime / Flush
- scheduledevent.cpp: 2 functions mapped (scheduled event object)
  - CScheduledEvent__Set
  - CScheduledEvent__dtor
- thing.cpp: 4 functions via xref to debug path 0x006331c0
  - CThing__AddCollision (0x004f39c0) - Creates collision object at this+0x38
  - CThing__SetName (0x004f4120) - Sets object name string at this+0x78
  - CThing__SetSound (0x004f4230) - Attaches sound/FX at this+0x74
  - CThing__AddTrail (0x004f44a0) - Adds visual trail effect at this+0x6c
  - CThing is the base class for all game objects
- Music.cpp: 11 functions via xref to debug path 0x00630a4c
  - CMusic__Init (0x004bb380) - Initialize music system
  - CMusic__Shutdown (0x004bb400) - Stop and free resources
  - CMusic__Play/Stop (0x004bb450/0x004bb490) - Playback control
  - CMusic__UpdateVolumeFade (0x004bb4b0) - Smooth volume transitions
  - CMusic__Update (0x004bb530) - Main loop, playlist cycling
  - CMusic__AddToPlaylist (0x004bb6b0) - Add track to playlist
  - CMusic__LoadPlaylistFromDir (0x004bb7c0) - Load directory of tracks
  - CMusic__PlayTrack (0x004bb7e0) - Play specific or random track
  - CMusic__PlayTrackByType (0x004bb8c0) - Play by game state
  - CMusic__SetMasterVolume (0x004bba10) - Set volume (0-127)
  - Dev mode forces "BEA 08(Master).wma" for testing
- All 19 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 11):**
- Component.cpp: 3 functions via xref to debug path 0x006247f8
  - CComponent__CreateSubComponent1 (0x00427cd0) - Creates small component at this+0x70
  - CComponent__CreateSubComponent2 (0x00427d50) - Creates component at this+0x208
  - CComponent__CreateWeaponComponent (0x00427dd0) - Factory for Fenrir/Carrier weapons
  - Factory pattern with string matching for "Fenrir Bomb Launcher", "Fenrir Main Gun", "Carrier Health Pad"
- All 3 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 12):**
- console.cpp: 4 functions via xref to debug path 0x00624d0c
  - CConsole__Init (0x00429bc0) - Initialize console system, buffers, linked lists
  - CConsole__RegisterBuiltinCommands (0x00429ef0) - Register ShowCmds, ShowVars, Bind, Set, Get, Exec, etc.
  - CConsole__RegisterCommand (0x0042af80) - Register single command with callback
  - CConsole__RegisterVariable (0x0042b040) - Register single cvar with storage pointer
  - Developer console with command/variable system, key bindings, script execution
  - Built-in commands: ?, ShowCmds, ShowVars, Get, Set, Bind, ListBinds, Echo, Exec, UseConfiguration, Exit, Quit, ToggleMenu, MemStats, DumpMem
  - Built-in cvar: cg_consolealpha (background transparency, default 200)
- All 4 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 13):**
- text.cpp: 9 functions via xref to debug path 0x00632dd8
  - CText__ResetCoreFields (0x004f2140) - Reset core fields (keeps language id)
  - CText__Ctor (0x004f2150) - Lightweight ctor/reset
  - CText__FreeBuffer (0x004f2170) - Free mBuffer
  - CText__GetLanguageName (0x004f2190) - Return language name string
  - CText__Init (0x004f21f0) - Load language file, parse text format versions 0-3
  - CText__GetAudioNameById (0x004f24b0) - v2/v3 audio-id lookup (ASCII)
  - CText__GetStringByIdAfter (0x004f2500) - v1/v2/v3 grouped-string lookup
  - CText__GetStringById (0x004f2580) - v1/v2/v3 string lookup by text_id (UTF-16)
  - CText__CopyFrom (0x004f2660) - Deep copy (alloc + adjust pool pointers)
  - Supports 5 languages: English, French, German, Spanish, Italian (+ American English variant)
  - Text file format has magic 0xFFFFFFBB (`bb ff ff ff` in file bytes) for newer versions (v1/v2/v3)
- All 9 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 14):**
- SquadNormal.cpp: 7 functions via xref to debug path 0x0063283c
  - CSquadNormal__Constructor (0x004e6870) - Initialize squad, set vtables
  - CSquadNormal__ScalarDestructor (0x004e6ac0) - Scalar deleting destructor
  - CSquadNormal__Destructor (0x004e6ae0) - Clean up resources, member lists
  - CSquadNormal__Init (0x004e6bb0) - Initialize with spawn point position
  - CSquadNormal__RemoveMember (0x004e6f70) - Remove unit from squad
  - CSquadNormal__CreateIterator (0x004e8ed0) - Create iterator for member list
  - CSquadNormal__SpawnMembers (0x004e91f0) - Spawn squad members with timeout
  - Manages AI squad members via linked list, dual vtables, multiple position vectors
  - Orphan code at 0x004e6ce0 (virtual method not recognized by Ghidra)
- All 7 functions renamed in Ghidra and documented

**Phase 1 Discovery Results (Batch 15):**
- InitThing.cpp: 2 functions via xref to debug path 0x0062d7b0
  - InitThing__CreateThingByType (0x0048c650) - Factory function for CInitThing subclasses
  - CInfluenceMap__Init (0x0048dcf0) - Base initializer (already named)
  - Factory creates 13 different CInitThing subclasses based on Object ID (OID)
  - Object types: CTreeInitThing, CUnitInitThing, CStartInitThing, CSpawnerInitThing, CCutsceneInitThing, CSquadInitThing, CWallInitThing, CFeatureInitThing, CSphereTriggerInitThing, CHazardInitThing
  - Called from CWorld__LoadWorld (7 times) during level loading
  - 13 Unwind@* exception handlers are compiler-generated, not source functions
- All 2 functions renamed in Ghidra and documented
