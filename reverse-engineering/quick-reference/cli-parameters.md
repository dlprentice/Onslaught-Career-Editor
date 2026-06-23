Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Command-line parameter lookup.
# Onslaught CLI Parameter Reference

Complete command-line parameter documentation for the Onslaught engine.

## Graphics Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-geforce2` | Flag | Force GeForce2-level rendering |
| `-geforce3` | Flag | Force GeForce3-level rendering |
| `-vshaders` | Flag | Enable vertex shaders |
| `-novshaders` | Flag | Disable vertex shaders |
| `-forcewindowed` | Flag | Run in windowed mode |
| `-hidetail` | Flag | Enable high detail mode |
| `-nostaticshadows` | Flag | Disable static shadows |
| `-textureramlimit N` | Integer | Limit texture RAM to N bytes |
| `-decimatemeshes` | Flag | Enable mesh decimation |
| `-nomeshpartreduction` | Flag | Disable mesh part reduction |
| `-pure` | Flag | Use pure Direct3D device |
| `-impure` | Flag | Use non-pure Direct3D device |

## Audio Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-nomusic` | Flag | Disable music playback |
| `-nosound` | Flag | Disable all audio |
| `-norumble` | Flag | Disable controller vibration |

## Development Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-devmode` | Flag | Enable developer mode (debug features) |
| `-artists` | Flag | Enable artist test mode |
| `-killhud` | Flag | Hide the HUD (DEV_VERSION only) |
| `-modelviewer` | Flag | Launch model viewer (DEV_VERSION, sets 64MB heap) |
| `-cutsceneeditor` | Flag | Launch cutscene editor (DEV_VERSION) |
| `-buildmodelinfo` | Flag | Build model info (DEV_VERSION) |
| `-showdebugtrace` | Flag | Show debug trace output |
| `-traceconsole` | Flag | Enable console tracing |

## Resource Building Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-buildresources [platforms]` | Multi | Build resources for PC, PS2, and/or XBOX (sets 256MB heap) |
| `-nobaseresources` | Flag | Skip base resource building |
| `-buildgoodies` | Flag | Build goodies/unlockables |
| `-resbuildermode` | Flag | Resource builder mode |
| `-quickcompression` | Flag | Use fast (lower quality) compression |

Example: `-buildresources PC PS2` builds for both PC and PS2.

## Gameplay Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-level N` | Integer | Start at level N directly |
| `-configuration N` | Integer | Use controller configuration N (1-4) |
| `-skipfmv` | Flag | Skip FMV video playback |
| `-attractmode` | Flag | Enable attract/demo mode |
| `-pal` | Flag | Use PAL video mode |
| `-ntsc` | Flag | Use NTSC video mode |

## Demo Recording Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-record filename` | String | Record demo to filename |
| `-play filename` | String | Playback demo from filename |
| `-stresstest N` | Integer | Run stress test mode N |

## Memory Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-mem N` | Integer | Set heap size to N megabytes |
| `-largeram` | Flag | Enable large RAM mode |

## Platform-Specific Parameters

### PC Only

| Parameter | Type | Description |
|-----------|------|-------------|
| `-emulatedvd` | Flag | Emulate DVD loading behavior |
| `-nocodeoffcd` | Flag | Don't load code from CD |

### Xbox Only

| Parameter | Type | Description |
|-----------|------|-------------|
| `-devkit` | Flag | Running on development kit |
| `-clearutility` | Flag | Clear utility data |
| `-reboot N` | Integer | Reboot Xbox after N attract cycles |

## Default Values

| Parameter | Default Value |
|-----------|---------------|
| `mMusic` | TRUE |
| `mSound` | TRUE |
| `mPureDevice` | TRUE |
| `mPal` | TRUE |
| `mLevelNo` | -1 (use normal progression) |
| `mConfigurationNo` | 0 |
| `mTextureRAMLimit` | 0x7FFFFFFF (2GB) |
| `mLanguage` | LANG_ENGLISH |

## Usage Examples

```bash
# Development testing - skip videos, use dev mode, start at level 5
onslaught.exe -devmode -skipfmv -level 5

# Artist testing with model viewer
onslaught.exe -modelviewer -artists

# Build PC and Xbox resources
onslaught.exe -buildresources PC XBOX

# Demo recording
onslaught.exe -record mydemo.dem -level 1

# Demo playback
onslaught.exe -play mydemo.dem

# Low-end PC settings
onslaught.exe -geforce2 -novshaders -nostaticshadows -textureramlimit 33554432

# Force windowed mode with specific controller config
onslaught.exe -forcewindowed -configuration 2

# Stress testing
onslaught.exe -stresstest 100 -attractmode
```

## Notes

- Parameters are case-insensitive
- Parameters can be passed via command line or in a text string
- DEV_VERSION parameters require a development build
- Model viewer and cutscene editor are mutually exclusive
- Resource building sets heap size to 256MB automatically
- Model viewer sets heap size to 64MB automatically
