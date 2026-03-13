# Windowed Mode Analysis

> Investigation of `-forcewindowed` parsing and startup-flow behavior across Steam baselines
> Generated: December 2025

## Summary

| Finding | Details |
|---------|---------|
| CLI Parameter | `-forcewindowed` exists in binary |
| Guard Flag | Current canonical Steam hash (`74154bfa...`) has `DAT_00662f3e` = 0x01; some historical baselines were observed at 0x00 |
| Flag Storage | `CLIParams.mForceWindowed` at offset 0x38 |
| Root Cause | Launch behavior depends on both CLI parse gating and startup fullscreen-flow gates |
| Practical path | Use `patches/patch_display_mode_flow.py` windowed patches (`0x12A644`, optional `0x12BB97`); guard-byte normalization is an alternate baseline tweak |

## The Mystery

Users historically reported inconsistent `-forcewindowed` behavior across Steam binaries/setups. The parameter exists in code, but startup flow determines whether launch remains fullscreen.

**Root Cause (combined flow)**: `-forcewindowed` parsing and startup fullscreen toggles are separate gates. Even when parsing is reachable, startup flow can still force fullscreen without additional display-flow patches.

## Technical Analysis

### CLI Parsing (GUARD-GATED)

In `CLIParams__ParseCommandLine` at `0x00423bc0`:

```c
// At 0x00424150-0x00424168
if ((DAT_00662f3e != '\0') &&                              // Guard check
   (iVar3 = stricmp(pcVar9, "-forcewindowed"), iVar3 == 0)) {
  extraout_ECX[0xe] = 1;  // Sets mForceWindowed = TRUE when guard path is reachable
}
```

- The parser requires non-zero `DAT_00662f3e` to process `-forcewindowed`.
- In current canonical Steam hash (`74154bfa...`), this byte is already `0x01`.
- Historical baseline reports with `0x00` explain why some users saw the parser path skipped.

### D3D Initialization (Startup Fullscreen Gate)

From Stuart's source code (`d3dapp.cpp` line 162-170):

```cpp
#ifndef _DEBUG
#ifndef OPTIMISED_DEBUG
#ifdef DEV_VERSION
    if ((!CLIPARAMS.mModelViewer) && (!CLIPARAMS.mCutsceneEditor))
#endif
    if (!CLIPARAMS.mForceWindowed)
        ToggleFullscreen();  // <-- Should be skipped if mForceWindowed=TRUE
#endif
#endif
```

If `mForceWindowed` is not set (or later startup flow forces fullscreen), this path falls through to fullscreen mode.

### Evidence

1. **String exists**: `"-forcewindowed"` at `0x006244a0`
2. **Guard-gated parser path**: `DAT_00662f3e` gates whether `-forcewindowed` is parsed
3. **Startup fullscreen flow**: startup code can still force fullscreen if display-flow patches are not applied
4. **Source-snapshot split context**: preserved source discussions reference `CD3DApplication`/`CEditorD3DApp` split behavior, so source parity is guidance while retail branch behavior is confirmed from BEA.exe evidence.
5. **Result**: launch behavior depends on both parser gate and startup flow

### Root Cause

Current evidence supports a two-gate model: parser gate (`DAT_00662f3e`) plus startup fullscreen flow. This explains inconsistent field reports and aligns with the current Binary Patches implementation.

## Workarounds

### Option 0: Isolated patch-branch testing (recommended before deeper surgery)

Use `patches/patch_display_mode_flow.py` with split controls:

- `--apply --resolution-only`
- `--apply --windowed-only`

This allows clean A/B testing of resolution-gate vs windowed-startup mutations without coupling both changes in a single run.

### Option 1: DxWnd (Recommended)

DxWnd intercepts DirectX calls and forces windowed mode at the API level.

1. Download DxWnd from https://sourceforge.net/projects/dxwnd/
2. Add BEA.exe to DxWnd
3. Configure windowed mode settings
4. Launch game through DxWnd

### Option 2: dgVoodoo2

dgVoodoo2 is a DirectX wrapper that provides windowed mode support.

1. Download from http://dege.freeweb.hu/dgVoodoo2/dgVoodoo2/
2. Extract to game directory
3. Configure via dgVoodooCpl.exe
4. Enable windowed mode in settings

### Option 3: Binary Patch (Guard-byte Normalization)

Normalize the guard byte so `-forcewindowed` is parsed:

1. Open BEA.exe in a hex editor
2. Go to file offset 0x262F3E
3. If the byte is `0x00`, change it to `0x01`
4. Save and run with `-forcewindowed`

**Validation note (2026-03)**: In current repo binaries, the guard is already `0x01`; primary operational guidance is still the startup-flow patch set (`0x12A644`, optional `0x12BB97`) exposed by Binary Patches.

## Key Addresses

| Address | Purpose |
|---------|---------|
| 0x00423bc0 | `CLIParams__ParseCommandLine` - CLI parsing |
| 0x00424150 | Guard flag check (`DAT_00662f3e`) |
| 0x00424168 | Set `mForceWindowed = 1` |
| 0x006244a0 | String `"-forcewindowed"` |
| 0x00662f3e | Guard flag (current canonical Steam hash `74154bfa...` = 0x01; some historical baselines reported 0x00) |
| 0x005290a0 | D3D window/device creation (suspected) |

## Source Code Reference

From `CLIParams.h`:
```cpp
class CCLIParams {
public:
    // ... other fields ...
    BOOL mForceWindowed;  // offset 0x38 (index 0xe)
    // ...
};
```

From `d3dapp.cpp`:
```cpp
// The code that SHOULD check mForceWindowed before going fullscreen
if (!CLIPARAMS.mForceWindowed)
    ToggleFullscreen();
```

## Conclusion

The `-forcewindowed` launch outcome is controlled by both parser gating (`DAT_00662f3e`) and startup fullscreen flow. In current repo binaries, the guard byte is already `0x01`, but startup-flow patches remain the reliable path for consistent windowed startup.

**To enable windowed mode in current app workflow:**
1. **Primary stable path:** apply the stable startup-flow patch `0x12A644`, with resolution gate patch `0x129696` as desired.
2. **Optional experimental follow-up:** use `0x12BB97` only if the stable set is already verified and startup still flips to fullscreen on that setup.
3. **Baseline normalization (optional):** ensure file offset `0x262F3E` is `0x01` so the parser gate does not block `-forcewindowed`.
4. **Wrapper fallback:** use wrapper/translation help only when system-specific behavior still bypasses the verified byte-patch path.

---

*Analysis performed December 2025*
*Binary analysis via Ghidra + GhydraMCP*
