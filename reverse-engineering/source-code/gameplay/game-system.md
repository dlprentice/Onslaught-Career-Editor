# Game System

> Analysis from game.cpp/h, DXGame.cpp/h, PCGame.cpp/h, EndLevelData.cpp/h, Music.cpp/h, and SoundManager.cpp/h - December 2025

## Overview

The game loop system provides the core execution framework through a class hierarchy that abstracts platform-specific main loops.

---

## Class Hierarchy

```
CGame (base class - abstract interface)
    ├── CDXGame (DirectX 8 implementation)
    │       └── CPCGame (PC-specific extensions)
    └── CPS2Game (PlayStation 2 - not in provided source)
```

**Platform Selection:**
- PC builds use `CPCGame` extending `CDXGame`
- Xbox builds use `CDXGame` directly
- PS2 builds use `CPS2Game` (not provided)

---

## Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `MAX_UPDATE_TIME` | 1.0f/40.0f | Game logic cap (40 FPS max) |
| `CLOCK_TICK` | 0.05f | 50ms per tick = 20 ticks/second |
| `MAX_PLAYERS` | 4 | Maximum simultaneous players |
| `GAME_COUNT_WHEN_LOST_OR_DRAW` | 5.0f | Delay before returning to menu on loss |
| `GAME_COUNT_WHEN_WON` | 5.0f | Delay before returning to menu on win |
| `TIMERECORDS` | 1000 | Profiler sample buffer size |

### Timing Architecture

- **Game logic updates**: Maximum 40 FPS (`MAX_UPDATE_TIME = 0.025s`)
- **Fixed time step events**: `CLOCK_TICK` intervals (50ms = 20 FPS physics)
- **Rendering**: Runs as fast as possible (uncapped)

---

## Game States (EGameState)

| State | Value | Description |
|-------|-------|-------------|
| `NOT_RUNNING` | 0 | Game not initialized |
| `PRE_RUNNING` | 1 | Loading/initializing |
| `PANNING` | 2 | Intro camera pan |
| `PLAYING` | 3 | Normal gameplay |
| `LEVEL_LOST` | 4 | Single-player: mission failed |
| `LEVEL_WON` | 5 | Single-player: mission completed |
| `PLAYER_1_WON` | 6 | Multiplayer: Player 1 victory |
| `PLAYER_2_WON` | 7 | Multiplayer: Player 2 victory |
| `GAME_DRAWN` | 8 | Multiplayer: draw |
| `QUIT` | 9 | Exiting level |

---

## Quit Types (EQuitType)

| Type | Value | Description |
|------|-------|-------------|
| `NONE` | 0 | No quit requested |
| `QUIT_TO_FRONTEND` | 1 | Return to main menu |
| `QUIT_TO_SYSTEM` | 2 | Exit to OS (PC only) |
| `LOAD_ERROR` | 3 | Asset loading failure |
| `RESTART_LEVEL` | 4 | Restart current mission |
| `QUIT_TIMEOUT` | 5 | Inactivity timeout |
| `USER_QUIT_TO_FRONTEND` | 6 | User-initiated menu exit |
| `USER_QUIT_TO_TITLE_SCREEN` | 7 | User-initiated title exit |

---

## Main Loop Architecture

The game uses a nested loop structure:

```
RunLevel()
    ├── Init()                 // One-time level initialization
    ├── InitRestartLoop()      // Per-attempt initialization
    ├── LoadResources()        // Asset loading
    └── RestartLoopRunLevel()  // Main gameplay
            └── MainLoop()     // Frame-by-frame execution
                    ├── ProcessInput()
                    ├── Update(deltaTime)
                    └── Render()
```

**Key Methods:**
- `RunLevel()` - Entry point, handles level lifecycle
- `InitRestartLoop()` - Reset state for level restart
- `MainLoop()` - Core frame processing with timing management

---

## Career Integration Points

The game loop directly interfaces with the career system at several critical points:

| Location | Code | Purpose |
|----------|------|---------|
| Line 319 | `mSlots = CAREER.GetSlots()` | Load tech slot state |
| Line 737 | `CAREER.GetControllerConfigurationNum(i)` | Per-player controller config |
| Lines 1139-1143 | FMV goodie unlocking | Auto-unlock goodies when watching cutscenes |

### Tech Slot Loading (Line 319)

```cpp
mSlots = CAREER.GetSlots();
// Used to check mission branching (SLOT_500_ROCKET, SLOT_500_SUB)
```

### Controller Configuration (Line 737)

```cpp
for (int i = 0; i < MAX_PLAYERS; i++) {
    int config = CAREER.GetControllerConfigurationNum(i);
    // Apply per-player control scheme
}
```

---

## B4K42 Cheat Mechanism

**Scope note:** This section documents the **internal/source build** cheat strings. The Steam PC port uses different codes (`MALLOY`, `TURKEY`, `Maladim`) and Maladim shows **no visible effect** in user testing (Dec 2025).

**Source/internal finding:** The B4K42 god mode cheat check uses `strstr()` against the **save game NAME** at runtime (substring match):

```cpp
// From FEPSaveGame.cpp - IsCheatActive()
if (strstr(saveName, "B4K42") != NULL) {
    // God mode enabled - "MyB4K42Save" would also work
}
```

### Why B4K42 Cheat Works

- The game checks if the save NAME **contains** "B4K42" (substring match, not exact)
- If found, god mode is enabled for Player 1
- In the internal build, god mode is runtime state (`CPlayer::mIsGod`) and the career also has a per-player `CCareer::mIsGod[2]` array in the source.
- **Steam build correction (Feb 2026):** In the retail PC port, the save offsets previously written up as `mIsGod[]` are used by the Controls UI for per-player invert-Y toggles; the only persisted god-related field we track is `g_bGodModeEnabled` (CCareer `+0x2494`, file `0x2496`), and behavior remains cheat-gated.

---

## FMV Goodie System

FMV (Full Motion Video) goodies are automatically unlocked when watching cutscenes:

| Goodie ID Range | Content |
|-----------------|---------|
| 200-232 | FMV/cutscene unlocks |

### Auto-Unlock Logic (Lines 1139-1143)

```cpp
// When FMV playback completes:
if (fmv_goodie_id >= 200 && fmv_goodie_id <= 232) {
    CAREER.UnlockGoodie(fmv_goodie_id);
}
```

This explains why goodies 200-232 appear as "empty placeholders" in `FEPGoodies.cpp` - they're unlocked via the FMV system rather than kill counts or grades.

---

## Debug Keys

| Key | Function | Notes |
|-----|----------|-------|
| `~` (tilde) | Toggle console | Debug console overlay |
| `T` | MAP_WHO | Unknown debug display |
| `C` | Toggle cockpit view | First-person camera |
| `P` | Toggle profiler | Performance overlay |
| `R` | Restart level | Immediate level restart |
| `ESC` | Quit to menu | Standard quit |
| `V` | Toggle god mode | Via `BUTTON_TOGGLE_GOD_MODE` |
| `U` | Win level | Debug instant-win |
| `I` | Lose level | Debug instant-lose |
| `7` | Complete all objectives | Debug skip |
| `A` / `F` | Free camera | Two key bindings |
| `8` / `9` | Debug squad cycling | Forward/backward |
| `4` / `5` | Debug unit cycling | Forward/backward |
| `Space` | Skip cutscene | During cinematics |
| `O` | Pause | Keyboard alternative |

**Note:** These debug keys only function in development builds with `-devmode` enabled.

---

## God Mode Toggle

God mode is toggled via `BUTTON_TOGGLE_GOD_MODE` (virtual button 0):

```cpp
// When V key pressed in dev mode:
if (BUTTON_TOGGLE_GOD_MODE pressed) {
    for (int n = 0; n < num_players; n++) {
        BOOL current = mPlayer[n]->IsGod();
        mPlayer[n]->SetIsGod(!current);
    }
}
```

**Important:** This is the runtime toggle path. In the internal/source build it calls `SetIsGod`, which also writes career state. In Steam/retail, the persisted god-related field we track is `g_bGodModeEnabled` (file `0x2496`), while actual invincibility behavior remains runtime/cheat-gated.

---

## Multiplayer Detection

Levels are identified as multiplayer based on their world number:

| Range | Type |
|-------|------|
| 100-799 | Single-player campaign |
| 850-899 | Multiplayer levels |
| 900-905 | Special multiplayer modes |

### Detection Logic

```cpp
BOOL IsMultiplayerLevel(int worldNumber) {
    return (worldNumber >= 850 && worldNumber <= 899);
}
```

This explains why multiplayer modes (and per-player state) are handled differently from single-player.

---

## Player Death and Respawn System

The respawn system handles player death differently based on game mode:

### DeclarePlayerDead(int number)

Called when a player's battle engine is destroyed:

```cpp
void CGame::DeclarePlayerDead(int number) {
    CBattleEngine* engine = mPlayer[number-1]->GetBattleEngine();
    FVector pos = engine->GetPos();

    // Disable free camera if active
    if (mFreeCameraOn[number])
        ToggleFreeCameraOff(number);

    // Create death view camera
    SetCurrentCamera(number-1, new CViewPointCamera(pos, 0.5f, 0.0f, 6.0f, 3.0f));

    // Stop message box sounds in single-player
    if (!GAME.IsMultiplayer() && mMessageBox)
        mMessageBox->StopCurrentPlayingSound();

    switch (WORLD.GetType()) {
        case CWorld::kSinglePlayer:
            if (engine->IsInWater())
                DeclareLevelLost(GAME_OVER_WATER, TRUE);
            else
                DeclareLevelLost(GAME_OVER_DEATH, TRUE);
            break;

        case CWorld::kCooperativeMultiplayer:
        case CWorld::kVersusMultiplayer:
            // Schedule respawn after 5 seconds
            EVENT_MANAGER.AddEvent(5.0f, RESPAWN_PLAYER_N, this, START_OF_FRAME);
            break;
    }
}
```

### Level Lost Reasons

| Constant | Trigger |
|----------|---------|
| `GAME_OVER_DEATH` | Player health reached zero |
| `GAME_OVER_WATER` | Player fell into water |
| `P1_OUT_OF_LIVES` | Player 1 has no lives remaining (co-op) |
| `P2_OUT_OF_LIVES` | Player 2 has no lives remaining (co-op) |

### RespawnPlayer(SINT inNumber)

Handles player respawn in multiplayer modes:

```cpp
void CGame::RespawnPlayer(SINT inNumber) {
    // Check lives in different modes
    switch (WORLD.GetType()) {
        case CWorld::kCooperativeMultiplayer:
            if (mPlayerLives[inNumber] == 0) {
                DeclareLevelLost(P_OUT_OF_LIVES, TRUE);
                return;
            }
            break;

        case CWorld::kVersusMultiplayer:
            if (mPlayerLives[inNumber] == 0) {
                MPDeclarePlayerWon(otherPlayer);  // Other player wins
                return;
            }
            break;
    }

    // Decrement lives
    if (mPlayerLives[inNumber] > 0)
        mPlayerLives[inNumber]--;

    // Find spawn point (CSpawnPoint preferred, CStart fallback)
    // ...spawn logic...

    // If spawn fails, retry after 1 second
    if (!spawned) {
        mPlayerLives[inNumber]++;  // Restore life
        EVENT_MANAGER.AddEvent(1.0f, RESPAWN_PLAYER_N, this, START_OF_FRAME);
    }
}
```

### Player Lives

- **Default lives per player**: 2 (`mPlayer1Lives = 2`, `mPlayer2Lives = 2`)
- Lives decrement on each death/respawn
- When lives reach 0:
  - **Co-op**: Triggers `DeclareLevelLost()` with `P1_OUT_OF_LIVES` or `P2_OUT_OF_LIVES`
  - **Versus**: Triggers `MPDeclarePlayerWon()` for the surviving player

### Spawn Point Types

| Class | Priority | Purpose |
|-------|----------|---------|
| `CSpawnPoint` | Primary | Level-designed respawn locations |
| `CStart` | Fallback | Initial spawn locations (if no CSpawnPoint available) |

Spawn points are player-specific (`GetPlayerNumber()` returns 1 or 2) and can be marked as unavailable.

---

## World Types (CWorld)

| Type | Constant | Description |
|------|----------|-------------|
| Single Player | `kSinglePlayer` | Standard campaign missions |
| Co-op Multiplayer | `kCooperativeMultiplayer` | 2 players vs AI |
| Versus Multiplayer | `kVersusMultiplayer` | 1v1 PvP combat |

---

## PC Game Implementation (PCGame.cpp/h)

### Frame Timing System

From `PCGame.cpp`:

| Feature | Value |
|---------|-------|
| FPS Cap | 40 FPS maximum game logic updates |
| Render FPS | Uncapped (runs as fast as possible) |
| Physics tick | 20 FPS fixed (CLOCK_TICK = 0.05s) |

### Screen Capture System

F8 key captures screenshots:
- Saves to `grabs\scrNNNN.tga` (sequential numbering)
- TGA format (uncompressed)
- Full resolution (game's current resolution)

### Debug Features (DrawGameStuff)

Debug overlay showing:
- FPS counter
- Memory usage
- Profiler data
- Event queue statistics

### Time Recording System (DEBUG_TIMERECORDS)

Performance profiling via `TIME_THIS_FUNCTION()` macro:
- 1000 sample buffer (`TIMERECORDS`)
- Tracks function execution time
- Displayed via profiler overlay (P key)

---

## EndLevelData Runtime System (EndLevelData.cpp/h)

### CRITICAL: Runtime-Only Structure

**In the source/internal path, and consistent with current Steam tracing, EndLevelData is treated as runtime-only (not directly serialized to `.bes`).** It is a struct that:
1. Gets populated when a level ends (win or lose)
2. Is consumed by `CCareer::Update()` to update the persistent career
3. Is discarded after career update completes

This invalidates earlier hypotheses that the historically labeled "mystery region" at 0x24CC-0x2714 contained "cached EndLevelData". That region contains remaining CCareer members (per-player settings, configuration).

### Struct Members

| Member | Type | Saved? | Destination |
|--------|------|--------|-------------|
| `mBaseThingsLeft` | BOOL[288] | ✅ Yes | `CCareerNode::mBaseThingsExists` (compressed to 36 bytes) |
| `mPrimaryObjectives` | CMissionObjective[10] | ❌ No | Runtime display only |
| `mSecondaryObjectives` | CMissionObjective[10] | ❌ No | Runtime display only |
| `mWorldFinished` | int | ❌ No | Used for routing (100, 211, 500, etc.) |
| `mFinalState` | EGameState | ❌ No | WIN/LOSE determination |
| `mRanking` | float (0.0-1.0) | ✅ Yes* | `CCareerNode::mRanking` (only if better) |
| `mScore` | SINT | ❌ No | Displayed on results screen |
| `mTimeTaken` | float (seconds) | ❌ No | Displayed on results screen |
| `mThingsKilled` | int[5] | ✅ Yes** | **Added to** `CCareer::mKilledThings` |
| `mSlots` | int[32] | ✅ Yes*** | **Copied to** `CCareer::mSlots` |

\* Rankings only update if the new ranking is BETTER than the existing saved ranking.
\*\* Kill counts are **cumulative** - added to existing totals, not replaced.
\*\*\* Tech slots are **overwritten** - the level's slot state replaces career slots entirely.

### Ranking Calculation System

The ranking (grade) is calculated based on score relative to level-specific thresholds:

```cpp
// Conceptual logic from EndLevelData.cpp
float CalculateRanking(int score, int time_taken) {
    // Base ranking from score thresholds
    if (score >= mSGradeScore) ranking = 1.0f;      // S-rank
    else if (score >= mDGradeScore) {
        // Linear interpolation between D and S
        ranking = (score - mDGradeScore) / (mSGradeScore - mDGradeScore);
    }
    else ranking = 0.0f;  // E-rank

    // Time multiplier: faster completion = higher score
    ranking *= time_multiplier;

    return clamp(ranking, 0.0f, 1.0f);
}
```

**CRITICAL: Secondary Objectives Gate Ranking**

Secondary objective completion directly affects achievable ranking:

| Secondary Status | Minimum Rank | Maximum Rank | Notes |
|------------------|--------------|--------------|-------|
| ALL completed | C (0.4) | S (1.0) | Full ranking range available |
| ANY failed | E (0.0) | B (0.6) | **Cannot achieve S or A rank!** |

This explains why some players report being "stuck at B-rank" despite high scores - failing ANY secondary objective caps the maximum achievable grade at B (0.6).

### Data Flow: EndLevelData → Career

```
Level Ends
    │
    ▼
EndLevelData populated
    │
    ▼
CCareer::Update() called
    │
    ├─── Check mFinalState
    │         │
    │         ├─── GAME_STATE_LEVEL_WON: Process updates
    │         │
    │         └─── GAME_STATE_LEVEL_LOST: Discard (no updates)
    │
    ├─── Update mBaseThingsExists (base objectives)
    │
    ├─── Update mRanking (only if better)
    │
    ├─── Add mThingsKilled to mKilledThings (cumulative)
    │
    ├─── Copy mSlots to mSlots (overwrite)
    │
    ├─── Update node links (unlock next missions)
    │
    └─── Save career to .bes file
```

**Key Behaviors:**

1. **GAME_STATE_LEVEL_WON only**: Career updates ONLY trigger on level victory. Level losses do not modify the save file.

2. **Rankings only improve**: If current save has A-rank (0.8) and you finish with B-rank (0.6), the save retains A-rank. Rankings never decrease.

3. **Kill counts are cumulative**: Every kill adds to your total. Replaying missions continues to add to kill counts (for goodie unlocks).

4. **Slots are overwritten**: Unlike kills, tech slots are replaced entirely. This is used for branching (SLOT_500_ROCKET vs SLOT_500_SUB).

### Confirmation: Reserved/Unmapped Region is NOT EndLevelData

The historically labeled mystery region at file offsets 0x24CC-0x2714 was previously hypothesized to contain cached EndLevelData. For the Steam build analyzed here, current evidence argues against that theory:

- EndLevelData is never serialized to disk
- EndLevelData is a transient runtime structure
- The reserved/unmapped region contains remaining CCareer members:
  - Per-player settings (invert Y-axis, vibration, controller config)
  - Unknown padding/reserved fields
  - Possibly platform-specific data

---

## Music System (Music.cpp/h)

Music playback with playlist support.

### Playback Types (EMusicPlayType)

| Type | Behavior |
|------|----------|
| `MPT_SINGLE` | Play once |
| `MPT_LINEAR` | Play in order |
| `MPT_RANDOM` | Random shuffle |
| `MPT_SELECTION` | Player-selected |

### Music Selections (EMusicSelection)

| Selection | Context |
|-----------|---------|
| `MUS_FRONTEND` | Menu music |
| `MUS_CREDITS` | Credits roll |
| `MUS_TUTORIAL` | Tutorial levels |
| `MUS_STEALTH` | Stealth missions |
| `MUS_INGAME` | General gameplay |

### Volume Persistence

In the Steam build analyzed for this repo, `CAREER.GetMusicVolume()` maps to retail `.bes` offset **0x2492** (true-view mapping); re-verify on other retail variants.

### Platform Audio Formats

- PC: MP3/WAV
- Xbox: WMA

### Bug Found

Line 448 has assignment (`=`) instead of comparison (`==`) - classic C bug.

---

## Sound System (SoundManager.cpp/h, pcsoundmanager.cpp/h)

The sound system handles 3D positional audio, volume management, and platform-specific audio output.

### Class Hierarchy

| Class | Platform | Backend |
|-------|----------|---------|
| `CSoundManager` | Base class | Abstract interface |
| `CPCSoundManager` | PC | DirectSound |
| `CPS2SoundManager` | PlayStation 2 | Sony SPU |
| `CXBOXSoundManager` | Xbox | DirectSound/Xbox Audio |

### Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `FAR_SOUND` | 50 | Max audible distance (units) |
| `NEAR_SOUND` | 3 | Full volume distance (units) |
| `MAX_SOUND_EVENTS` | 256 | Max concurrent sound events |
| `MAX_SOUND_BUFFERS` | 32 | PC DirectSound buffers |
| Default sample rate | 44100 Hz | All platforms |
| Default format | 16-bit mono | Standard audio format |

### Volume Categories

Multiple volume channels with independent control:

| Member | Purpose | Default |
|--------|---------|---------|
| `mMasterVolume` | Global volume multiplier | 1.0 |
| `mGameSoundsMasterVolume` | In-game effects | 1.0 |
| `mMenuSoundsMasterVolume` | Menu/UI sounds | 1.0 |
| `mRadioMessageVolume` | Radio voice comms | PS2: 0.70, PC: 0.42 |
| `mHUDMessageVolume` | HUD feedback | 0.45 |

**Note:** Radio message volume is lower on PC (0.42 vs 0.70) - likely tuned for different speaker setups.

### Sound Tracking Types (ESoundTrackingType)

Controls how 3D sounds follow their sources:

| Type | Behavior | Use Case |
|------|----------|----------|
| `ST_NOTRACKING` | Fixed position | Camera-relative sounds |
| `ST_SETINITIALPOSITION` | Set once, don't follow | Explosion at location |
| `ST_FOLLOWANDDIE` | Follow source, stop when source dies | Engine sounds |
| `ST_FOLLOWDONTDIE` | Follow source, continue after death | Ambient loops |

### Career Integration

Volume settings persisted in .bes save files:

| Setting | Career Offset | File Offset | Format |
|---------|---------------|-------------|--------|
| Sound Volume | `mSoundVolume` | 0x248E | Raw IEEE-754 float |
| Music Volume | `mMusicVolume` | 0x2492 | Raw IEEE-754 float |

Note: Retail file offsets use the true view mapping `file_off = 0x0002 + career_off`. In the legacy 4-byte-aligned view, these floats can look scrambled due to 2-byte misalignment.

### PC Volume Curve (CPCSoundManager)

PC uses a non-linear volume curve for better perceptual scaling:

```cpp
// Simplified from CPCSoundManager::SetVolume()
float adjustedVolume = tan(linearVolume * PI/4);  // Non-linear curve
```

- PS2 uses linear volume mapping
- PC's tan() curve provides better perceived volume at low settings

### Localization System

Language-dependent voice samples loaded from subdirectories:

```
sounds\
  english\     - English voice samples
  french\      - French voice samples
  german\      - German voice samples
  spanish\     - Spanish voice samples
  italian\     - Italian voice samples
```

Sample names are language-agnostic; the system prepends the language path.

### Debug Console Commands

| Command/Variable | Purpose |
|------------------|---------|
| `playsound <name>` | Play named sound sample |
| `snd_visible` | Toggle sound debug visualization |
| `snd_frozen` | Freeze sound system for debugging |

---

## Special Pan Camera Levels

8 levels have the player starting "on something" requiring a different intro camera:
- 221, 222, 231, 232, 331, 332, 523, 524

These levels use a panning camera intro instead of the standard fixed camera, as the player starts on a moving platform (carrier ship).

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `game.cpp` | Main game loop, career integration, B4K42 cheat, player death/respawn |
| `game.h` | Game states, quit types, constants |
| `DXGame.cpp` | DirectX game loop implementation |
| `DXGame.h` | CDXGame class definition |
| `PCGame.cpp` | PC-specific game loop (40 FPS cap, F8 screenshots) |
| `PCGame.h` | CPCGame class definition |
| `EndLevelData.cpp` | Runtime level completion data (NOT saved) |
| `EndLevelData.h` | EndLevelData struct definition |
| `Music.cpp` | Music playback system |
| `Music.h` | Music enums, playback types |
| `SoundManager.cpp` | Base sound manager implementation |
| `SoundManager.h` | Sound system interface, tracking types |
| `pcsoundmanager.cpp` | PC DirectSound implementation |
| `pcsoundmanager.h` | PC-specific sound declarations |

---

## See Also

- [career-system.md](career-system.md) - Career integration details
- [battle-system.md](battle-system.md) - Battle Engine mechanics, god mode implementation
- [../frontend/fep-systems.md](../frontend/fep-systems.md) - Cheat code implementation
- [../../game-mechanics/god-mode.md](../../game-mechanics/god-mode.md) - God mode investigation

---

*Last updated: December 2025*
