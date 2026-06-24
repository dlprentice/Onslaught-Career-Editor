# Executable Modding

> BEA.exe modifications for windowed mode, settings, and resolution

## Binary Patching Discoveries (Dec 2025, archival)

Historical candidate patch notes from early RE passes. Treat these as archival hypotheses unless re-validated against current canonical binary-analysis docs.

See [re-investigation.md - Binary Patching](re-investigation.md#binary-patching-new-dec-2025-archival) for full details.

| Patch | Address | Change | Effect |
|-------|---------|--------|--------|
| **All Cheats (candidate)** | 0x004654a0 | `75` → `EB` | Candidate force-true path in `IsCheatActive` (revalidation required) |
| Dev Mode Flag | 0x00662df4 | Set to `01` | Alternative: set flag in .data |

**Status**: Archived notes only. Do not treat as a current shipping recommendation.

## Desired Features (from LinkedIn conversation)

1. **Windowed mode support** - Currently fullscreen only
2. **Settings improvements** - Remove cardid.txt dependency for advanced options
3. **Resolution options** - Better widescreen support

## Action Items

### Research

1. [ ] Get graphics/settings code from Stuart (`d3dapp.cpp`, `PCPlatform.cpp` already have some)
2. [x] Identify entry points in exe for display mode - **DONE Dec 2025**: Found `CLIParams__ParseCommandLine` at 0x00423bc0
3. [ ] Document existing widescreen patch (in `media/patches/`)
4. [x] Search for `-forcewindowed` implementation in Ghidra - **DONE Dec 2025**: Found but GUARDED by dev flag!

### Windowed Mode Discovery (Dec 2025)

**CRITICAL FINDING**: The `-forcewindowed` parameter EXISTS in BEA.exe but was thought to be **GUARDED** by `DAT_00662f3e`:

```c
// From CLIParams__ParseCommandLine (0x00423bc0)
if ((DAT_00662f3e != '\\0') && strcmp(param, "-forcewindowed") == 0) {
    extraout_ECX[0xe] = 1;  // Enable windowed mode
}
```

**Corrected (Dec 2025)**: The guard flag `DAT_00662f3e` is `0x00` (disabled) in the Steam version. Even after patching it to `0x01`:
- The CLI parameter IS parsed correctly
- The windowed flag IS set in the params struct
- But the actual D3D/DirectX initialization **ignores the flag** or has hardcoded fullscreen behavior

**Status (archival note)**: superseded by later patch-analysis work. Canonical current status for widescreen/windowed behavior lives in:
- `reverse-engineering/binary-analysis/widescreen-patch-analysis.md`
- `reverse-engineering/binary-analysis/windowed-mode-analysis.md`

### Implementation

1. [x] ~~Create windowed mode patch~~ - **BLOCKED**: Guard can be enabled but deeper D3D issue prevents windowed mode
2. [ ] Document all working launch options
3. [ ] Create cardid.txt presets for modern GPUs (done - see modding-reference.md)
4. [ ] Investigate D3D initialization to find actual fullscreen enforcement (low priority)

## Source Code Files Needed

**Files we have:**
- Career.cpp/h
- FEPGoodies.cpp/h
- Controller, Player, Platform, etc.
- d3dapp.cpp/h
- PCPlatform.cpp/h

**Files that would help:**
- [ ] `cliparams.h` - Command-line parameter definitions (mForceWindowed, mForcedCard, etc.)
- [ ] Display initialization code
- [ ] Graphics options menu code

## Related Resources

- **Widescreen patch**: `media/patches/battleengineaqulawidescreenfix.zip` (ModDB 2018)
- **cardid.txt hack**: [../reverse-engineering/game-assets/modding-reference.md](../reverse-engineering/game-assets/modding-reference.md)
- **Ghidra analysis**: [../reverse-engineering/binary-analysis/executable-analysis.md](../reverse-engineering/binary-analysis/executable-analysis.md)

## Alternative Contact

Ben Carter (Lead Programmer, wrote GDM post-mortem) worked on PS2/Xbox engine code and may have insights into display code. Last known email: `ben@sailune.net` (2003).

## Notes

- Encore Software was the **publisher** for the Windows release.
- Per Stuart (Discord, Dec 2025), the Windows retail work was done **in-house at Lost Toys** by Jan (ex-Mucky Foot) and possibly others.
- Stuart's uploaded source reflects the internal PC development build, not the final retail/Steam binary. Treat it as a reference for struct layouts and logic, but validate retail behaviors (especially persistence) against `BEA.exe`.

---

*Priority 3 investigation item*
