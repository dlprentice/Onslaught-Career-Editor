# Modding Reference

## Launch Options (PC Version)

From Dominating David (Discord #media, April 1, 2025):

### Confirmed Working

| Option | Effect |
|--------|--------|
| `-playabledemo` | Launches game as playable demo with 1 mission |
| `-nomusic` | Disables background music |
| `-nosound` | Disables all audio |
| `-skipfmv` | Skips intro video |

### Discovered (Effect Unknown/Untested)

| Option | Suspected Purpose |
|--------|-------------------|
| `-32bittextures` | Force 32-bit texture mode |
| `-autoconfigtest` | Auto-configuration testing |
| `-backbuffer2` | Alternate backbuffer config |
| `-cardid` | Graphics card ID override |
| `-defaultoptionsname` | Default options file |
| `-dxtntextures` | Force DXT texture compression |
| `-findbadwater` | Debug: find problematic water |
| `-findgoodwater` | Debug: find working water |
| `-forcewindowed` | Force windowed mode (didn't work in testing) |
| `-getversion` | Display version info |
| `-landscape0/1/2` | Landscape quality levels |
| `-level` | Jump directly to level (dev use) |
| `-showdebugtrace` | Show debug trace output |
| `-soundbuffers` | Sound buffer configuration |
| `-testeur` | Test EUR (European?) build |
| `-timeout` | Connection/load timeout |
| `-traceconsole` | Enable trace console |

Stuart noted: "These must of been used to help development. The --level one was important, because when you're coding and testing a particular level, you just want the game to start straight into the action and not keep going through the menus. I suspect many of these options won't work on the released version."

Historical context from preserved Discord extracts:
- `-forcewindowed` behavior discussions referenced a dev/release class split context (`CD3DApplication` vs `CEditorD3DApp`), which aligns with the two-gate startup behavior documented in `windowed-mode-analysis.md`.
- `cardid` handling in retail-era startup flow appears to post-date Stuart’s currently available source snapshot; treat retail binary evidence as authoritative when source and behavior differ.

---

## The cardid.txt Graphics Hack

**Location:** `game/cardid.txt` (18 KB)
**Authors:** Jan Svarovsky and Tom Forsyth (originally from StarTopia at Mucky Foot)
**Purpose:** Per-GPU graphics tweaks and compatibility fixes

### How It Works

The game reads `cardid.txt` on startup and applies tweaks based on your GPU's vendor/device ID. Modern GPUs aren't in the database, so the game uses conservative defaults that disable advanced features. By adding your GPU with the right tweaks, you can unlock all graphical options.

### Finding Your GPU IDs

1. Run `dxdiag` on Windows
2. Go to the "Display" tab
3. Note the **Vendor ID** and **Device ID** (in hex, e.g., `10DE` for NVIDIA)

Or check `game/setuphistory.txt` after running the game once - it logs detected adapters.

### Syntax

```
Vendor:XXXX VendorName
Device:YYYY DeviceName
Tweak:TWEAK_NAME value
Opt:OPTION_NAME button slider    // -1 = don't change
Driver:low_ver high_ver - low_ver high_ver driver_name    // version ranges
```

### Key Tweaks for Maximum Quality

Companion tooling (stable lane in this repo):

```bash
python3 tools/cardid_preset_manager.py --dry-run --input game/cardid.txt --preset modern
python3 tools/cardid_preset_manager.py --input game/cardid.txt --preset modern
python3 tools/cardid_preset_manager.py --input game/cardid.txt --restore
```

In-app note: the `cardid.txt` companion controls were intentionally shelved from active GUI surfaces. Use the binary patch lane in `Binary Patches`:
- `GEFORCE_FX_POWER` default-on patch (`0x0CDD40`)
- Optional cardid override-load bypass patch (`0x12AF3F`) to ignore `cardid.txt` tweak overrides entirely.

Add this block to the END of `cardid.txt` for modern NVIDIA GPUs:

```
// Modern NVIDIA GPUs (GTX 10xx, RTX 20xx/30xx/40xx)
Vendor:10DE nVidia
Device:2504 RTX_4080
Device:2684 RTX_4090
Device:2782 RTX_4060
// Add your specific Device ID here

// Enable all high-quality features
Tweak:GEFORCE_FX_POWER 1          // Unlock advanced shader effects
Tweak:SRT_ENABLE 1                // Screen-space rendering techniques
Tweak:IMPOSTOR_ENABLE 1           // Billboard rendering for distant objects
Tweak:LANDSCAPE_LIGHTING 1        // Full landscape lighting (not 0!)
Tweak:SNOW_ENABLE 1               // Weather effects
Tweak:GEFORCE_PARTICLE_FOG 1      // Particle fog effects
```

For AMD GPUs:
```
// Modern AMD GPUs (RX 5xxx/6xxx/7xxx)
Vendor:1002 ATI
Device:73DF RX_6700_XT
Device:744C RX_7900_XTX
// Add your specific Device ID here

Tweak:GEFORCE_FX_POWER 1
Tweak:SRT_ENABLE 1
Tweak:IMPOSTOR_ENABLE 1
Tweak:LANDSCAPE_LIGHTING 1
```

### All Available Tweaks

| Tweak | Values | Effect |
|-------|--------|--------|
| `GEFORCE_FX_POWER` | 0/1 | Enable high-end shader effects |
| `SRT_ENABLE` | 0/1 | Screen-space rendering |
| `IMPOSTOR_ENABLE` | 0/1 | Distant object billboards |
| `LANDSCAPE_LIGHTING` | 0/1 | Terrain lighting |
| `LANDSCAPE_METHOD` | 0/1/2 | Terrain rendering method |
| `LANDSCAPE_MAXLEVELS` | 1+ | Terrain LOD levels |
| `SHADOW_METHOD` | 0/1 | Shadow rendering method |
| `SUN_METHOD` | 0/1 | Sun/lighting method |
| `BATTLELINE_METHOD` | 0/1 | Battle line rendering |
| `SURF_METHOD` | 0/1 | Water surface method |
| `SNOW_ENABLE` | 0/1 | Weather snow effects |
| `DISABLE_SNOW` | 0/1 | Force disable snow |
| `GEFORCE_PARTICLE_FOG` | 0/1 | Particle fog effects |
| `MY_READABLE_Z_BUFFER` | 0/1 | Z-buffer read access |
| `DXSHADOWS_INVERSE` | 0/1 | Shadow direction fix |
| `FORCE_VSYNC` | 0/1 | Force vertical sync |
| `NOSCROLL_BACKGROUND` | 0/1 | Static menu background |
| `FASTER_INTERFACE` | 0/1 | Optimized UI rendering |

### Compatibility Tweaks (for old/problematic GPUs)

| Tweak | Effect |
|-------|--------|
| `RENDERSTATE_TWEAK_CARD_CANT_DO_TFACTOR` | Disable texture factor blending |
| `RENDERSTATE_TWEAK_CARD_CANT_DO_HWTNL` | Disable hardware T&L |
| `RENDERSTATE_TWEAK_CARD_CANT_DO_GLOSSMAP` | Disable gloss maps |
| `RENDERSTATE_DISALLOW_MULTITEXTURE` | Disable multi-texturing |
| `RENDERSTATE_DISALLOW_MIPMAPPING` | Disable mipmaps (1=partial, 2=full) |
| `SQUARE_TEXTURES_ONLY` | Force square textures |
| `TEXTURE_RES_LOSS_SHIFT` | Reduce texture resolution (shift bits) |

### In-Game Options (Opt:)

| Option | Button | Effect |
|--------|--------|--------|
| `OPT_SAFE_MODE` | 1 | Conservative graphics mode |
| `OPT_SAFE_MODE_NEW` | 1 | Updated safe mode |
| `OPT_FOGGING` | 1 | Enable distance fog |
| `OPT_MIPMAP_QUALITY` | 1 | Mipmap quality level |

---

## Widescreen Patch

**Location:** `media/patches/battleengineaqulawidescreenfix.zip`
**Source:** ModDB (2018)
**Effect:** Enables 1920x1080 and other widescreen resolutions

### Installation

1. Extract `battleengineaqulawidescreenfix.zip`
2. Replace `BEA.exe` with the patched version
3. Run the game - new resolutions appear in options

### Best Results: Widescreen + Binary Patch Gate Unlock

For the best visual experience on modern hardware:
1. Apply the widescreen patch (1080p support)
2. Apply the stable extra-graphics gate binary patch (`GEFORCE_FX_POWER` default-on)
3. Optionally layer `cardid.txt` tweaks for per-vendor experimentation
4. Enjoy 2003 graphics that still look surprisingly good!

---

## Modding Possibilities (from Stuart, May 2024)

### What's theoretically possible
- Modify AYA files for larger maps/more units (challenging)
- Small changes to .exe file

### What would require full source rebuild
- Better AI pathfinding
- Any significant game logic changes

**Stuart's assessment:**
> "Mods required to do the things you mentioned would be 'challenging'. Something maybe possible by modifying the AYA files and/or doing small changes to the .exe file. As for things like better AI pathfinding, then a complete rebuild of the C++ source would have to be done."

**Recommended approach for spiritual successor:**
> "If I was making battle engine aquila 2 (bigger and louder). I would probably just work from an engine like unreal or unity, and maybe port over some code from the original into c#."

**Precedent for open-sourcing**: Stuart mentioned (June 21, 2022) that Muckyfoot, a company Lost Toys was close to, recently open-sourced **Urban Chaos** while it's still on Steam. This establishes precedent for similar games being open-sourced.

---

## Readable Script Files (Accidentally Released)

From Stuart (May 2023):
> "If you look at files in 'Battle Engine Aquila\data\MissionScripts', then if you open any of these files in a text editor you'll see it's our readable script code. Much of this script code was actually written by the level designers which shows how good they were."

**Location**: `Battle Engine Aquila\data\MissionScripts\`
**Format**: Text-readable custom scripting language
**Authors**: Level designers (not programmers)
**Note**: Modifying these files does nothing - they're compiled into the AYA files

---

## In-House Level Editor

From Stuart (May 2024):
> "There was an 'In-house' editor for creating the islands like 'Landscape', 'Tree placement' and placing down units and buildings. I'm not sure a build of that editor exists anymore, but I seem to still have some of it's source code (C++/MFC)"

**Features**: Landscape editing, tree placement, unit/building placement
**Tech**: C++/MFC
**Status**: Build may not exist; Stuart has partial source code

---

## Asset Pipeline Notes (desimbr, February 15, 2026)

From desimbr (Discord, February 15, 2026):

> "I have various bits and pieces of code from some of the tools we used, mostly the world editor (using MFC). It's incomplete ... The code I do have builds the Xbox version and possibly the in-house PC version ... 3D models were created in 3D Studio Max, then exported with a custom plugin to our .msh format ... loading many .msh files was too slow ... so multiple raw .msh C++ structures were dumped directly from memory into a binary file and loaded back ... essentially part of the .aya files. The .tga textures were handled similarly. During development, game code could read either .aya or original .msh/.tga files. My extractor reverses this and converts to .fbx/.png."

**Key implications for RE/modding**:
- `.aya` loading is, at least in part, a performance-oriented runtime dump/reload path for mesh/texture structures, not only a clean high-level authoring format.
- The historical source/tooling split is expected: editor/source fragments can target Xbox/internal PC workflows while retail Steam behavior differs.
- A custom 3ds Max exporter existed in the original pipeline and is currently unavailable; this remains a hard blocker for fully-native asset re-authoring.
- Crash behavior on some levels with unlock-all patching remains an open runtime-behavior question and is not explained by this pipeline note alone.

---

## Dev-Build Precompute Pipeline Notes (Glenn, February 23, 2026)

From Glenn (Discord, February 23, 2026, paraphrased recollection):

> PC dev builds had at least some developer tooling built into the game runtime. Some heavy data was generated in-engine and then saved as files, while console/release PC loaded the precomputed outputs instead. The generation paths were conditionally compiled out of release builds.

Glenn called out three specific systems he remembers working on:

1. **Coastline generation**
   - Input: landscape heightmap.
   - Dev behavior: coastline mesh generated from heightmap relationship, then written out.
   - Release behavior: load previously saved coastline data file.
   - Build gating: generation code conditionally compiled out in release.

2. **Landscape LOD lookup-table generation**
   - Dev behavior: at least some landscape LOD lookup/precompute paths generated data and wrote it out.
   - Release behavior: precomputed tables loaded from file.
   - Build gating: same conditional-compilation pattern as coastline generation.

3. **Distance normal-mapped sprite (impostor-like) generation**
   - Dev behavior: create D3D render scenes, render meshes with normal-map color encoding, then save resulting sprites.
   - Release behavior: load saved sprite outputs.
   - Build gating: generation path likely disabled/removed from release build.

### Operational implications for current RE

- Expect a split between:
  - **authoring/precompute tooling paths** (likely present in internal/dev code),
  - and **runtime load-only paths** (dominant in retail Steam binary).
- This directly supports prior findings that many data formats in retail look like loaded cache artifacts rather than first-principles runtime generation.
- Missing CLI parameters likely existed for batch precompute/export runs (possibly all levels); exact flags remain unknown.
- Treat this as high-value historical guidance but still validate each claim against `BEA.exe` callsites/strings and any future public-source updates.

### Follow-up RE targets suggested by this note

- Search for file-write pathways adjacent to landscape/coastline/impostor systems in dev-path debug strings (`DXLandscape.cpp`, `DXPatchManager.cpp`, `imposter.cpp`, `bytesprite.cpp`, `rtmesh.cpp`).
- Trace command-line parsing paths for dormant precompute-style switches (particularly startup modes that iterate levels and emit files).
- Separate docs into:
  - `generation path (dev/internal, maybe stripped)`,
  - `consumption path (retail, confirmed)` for each subsystem.

---

## External Tools

### AYAResourceExtractor
- **Repo**: https://github.com/stuart73/AYAResourceExtractor
- **Author**: Stuart Gillam (desimbr)
- **Purpose**: Extract 3D models, textures from .aya files
- **Output**: FBX (binary and ASCII)
- **Note**: Animations not yet extractable
- **Blender import**: Turn off extra import options to avoid crash
- **Model scale**: Battle Engine is ~7.6m tall based on model calculations (April 2023)
- **Model quirks**: Models are asymmetrical - min473 noted "NOTHING is symmetrical in this model" when 3D printing
- **Use cases**: Gmod SNPCs, C&C Generals mods, 3D printing (thin parts break during support removal)
- **Pipeline context (2026-02-15)**: Extractor reverses an internal performance path where raw `.msh`-derived structures and `.tga` data were dumped/loaded via `.aya`-family binaries for faster startup.

### Onslaught Source Reference
- **Repo**: https://github.com/stuart73/Onslaught
- **Contents**: Career.cpp/h, d3dapp.cpp, FEPGoodies.cpp, etc.
- **Note**: Internal PC build, not console port

---

## Open Questions for Modding

1. ~~**EndLevelData structure**~~ - **SOLVED Dec 2025**: EndLevelData is runtime-only, never saved to file. It's consumed by `CCareer::Update()` after level completion and discarded.
2. **Exact offset of objective mask bits** in mBaseThingsExists for S-rank requirements
3. **Tech slot bit mapping** - Which bits enable which features? (Known: slots 61-62 control Mission 500 path choice)
4. ~~**PC cheat codes**~~ - **SOLVED Dec 2025**: Cheats use `strstr()` substring matching on save NAME. See [../game-mechanics/cheat-codes.md](../game-mechanics/cheat-codes.md)
