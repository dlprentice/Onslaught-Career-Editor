# Windowed Mode Analysis

> Investigation of `-forcewindowed` parsing and startup-flow behavior across Steam baselines
> Generated: December 2025

Status: **partially superseded 2026-07-28** — the `DAT_00662f3e` guard-byte claim
and the hex-edit instruction built on it are **withdrawn as false**. The two-gate
model, the startup-flow patch guidance, and the wrapper workarounds stand
unchanged. See "Correction 2026-07-28" immediately below.
Last updated: 2026-07-28
Verdict: `-forcewindowed` is real and reachable, but its parser gate
`DAT_00662f3e` is **BSS — zero at load** and is set only by the `-testeur`
switch appearing **earlier on the same command line**. So `-forcewindowed` alone
does nothing on a stock invocation, and the byte cannot be normalised with a hex
editor because it has no file byte to edit. The startup-flow byte patch at file
offset `0x12A644` remains the operational path.
Evidence: MEASURED — PE section table, `tools/pe_read_va.py`,
`tools/operand_scan.py` and `tools/disasm_va.py` read over the pristine specimen
on 2026-07-28; corroborated by the runtime run recorded in
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md).
Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
2,506,752 bytes (`local-lab/safe-copy-bea-pristine/`, read-only). Image base
`0x00400000`. `BEA.exe` was not launched by this pass and the Ghidra database was
not opened or mutated.

## Correction 2026-07-28 — the guard-byte claim was false, and its hex edit was harmful

**What this document previously said, quoted so the record survives:**

> | Guard Flag | Current canonical Steam hash (`74154bfa...`) has `DAT_00662f3e` = 0x01; some historical baselines were observed at 0x00 |
>
> - In current canonical Steam hash (`74154bfa...`), this byte is already `0x01`.
>
> **Validation note (2026-03)**: In current repo binaries, the guard is already `0x01` …
>
> ### Option 3: Binary Patch (Guard-byte Normalization)
>
> Normalize the guard byte so `-forcewindowed` is parsed:
>
> 1. Open BEA.exe in a hex editor
> 2. Go to file offset 0x262F3E
> 3. If the byte is `0x00`, change it to `0x01`
> 4. Save and run with `-forcewindowed`
>
> 3. **Baseline normalization (optional):** ensure file offset `0x262F3E` is `0x01` so the parser gate does not block `-forcewindowed`.

**All of that is wrong. Measured on the pristine specimen named in the header:**

1. **`DAT_00662f3e` has no file byte at all.** VA `0x00662f3e` is RVA `0x262f3e`.
   `.data` has virtual extent RVA `0x222000`–`0x5d4614` but **raw** extent
   `0x222000`–`0x261000` (raw size `0x3f000`), and `0x262f3e` is `0x40f3e` into
   the section — past the raw size. It is **BSS: zero at image load, not `0x01`**.
   `tools/pe_read_va.py <specimen> 0x00662f3e --count 4` refuses the address with
   `ValueError: VA 0x00662f3e is in uninitialised part of .data`.

2. **File offset `0x262F3E` belongs to `.rsrc`,** whose raw extent is
   `0x261000`–`0x264000`. The `0x01` that earlier passes read there is a
   **resource byte**, which is exactly why the false claim looked confirmed.
   Following the old step 3 would have corrupted a resource and left the parser
   gate untouched. This is the same failure class the project has already
   recorded elsewhere: a `.data` VA whose naive file offset lands on unrelated
   content.

3. **The mechanism is the opposite of what was described.** `tools/operand_scan.py`
   finds exactly **two** absolute references to `0x00662f3e` in the image, and
   **both are reads** — `0x00424150` and `0x004714f0`, each `mov al, byte ptr
   [0x662f3e]`. There is **no absolute write**. The only writer is object-relative:

   ```
   00423c6b  68 18 46 62 00             push      0x624618            ; "-testeur"
   00423c70  55                         push      ebp                 ; current token
   00423c71  e8 1a 47 14 00             call      0x568390            ; stricmp
   00423c79  85 c0                      test      eax, eax
   00423c7b  75 07                      jne       0x423c84
   00423c7d  c6 83 86 01 00 00 01       mov       byte ptr [ebx + 0x186], 1
   ```

   `ebx` is the `CCLIParams` `this` pointer (`mov ebx, ecx` at `0x00423bd4`;
   `mov ecx, 0x662db8` at `0x004239c0`), and `0x00662DB8 + 0x186 = 0x00662F3E`
   exactly. So the guard is a **member of the CLI-parameter object that
   `-testeur` sets at runtime**, not a shipped constant.

4. **Ordering matters, and it is structural.** `0x0042418d` is
   `jl 0x423c6b` — the token comparisons are one pass per argument, with the
   `-testeur` compare at the loop head and the guarded `-forcewindowed` compare
   at `0x00424150` in the same pass. The guard can therefore only be set by a
   `-testeur` that appears **before** `-forcewindowed` on the command line.

5. **Corroborated by running it, on a different day and by a different method.**
   [`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md)
   records that the pristine binary launched with `-testeur -forcewindowed`
   presents windowed at client 640x480 with the desktop untouched, and derives
   the same `ebx = 0x00662DB8` from the `[ebx+0x38]` store at `0x0042416b`
   (`0x00662DB8 + 0x38 = 0x00662DF0`).

**UNKNOWN, and what would settle it:** the "some historical baselines were
observed at `0x00`" report is unresolvable and is withdrawn as evidence rather
than restated. The address it names has no file byte in *any* PE built this way,
so the reports were almost certainly reading file offset `0x262F3E` — a `.rsrc`
byte that legitimately differs between builds. Settling it would need one of
those historical binaries hashed and its section table parsed; none is held here.

**What is unchanged:** the two-gate model, the `mForceWindowed` offset `0x38`,
the `d3dapp.cpp` source context, the DxWnd and dgVoodoo2 workarounds, and the
operational guidance to use the startup-flow patch at `0x12A644` (with
`0x129696` as the resolution gate). None of those rest on the guard byte.

## Summary

| Finding | Details |
|---------|---------|
| CLI Parameter | `-forcewindowed` exists in binary |
| Guard Flag | `DAT_00662f3e` is **BSS — zero at load** in the pristine specimen (`74154bfa…`), and is set to `1` at runtime only by `-testeur` appearing earlier on the command line. *(Corrected 2026-07-28 — see above; previously read "Current canonical Steam hash (`74154bfa...`) has `DAT_00662f3e` = 0x01".)* |
| Flag Storage | `CLIParams.mForceWindowed` at offset 0x38 |
| Root Cause | Launch behavior depends on both CLI parse gating and startup fullscreen-flow gates |
| Practical path | Use the AppCore safe-copy profile with catalog rows at `0x12A644` and `0x12BB97`. **Guard-byte normalization is not an alternative** — the guard has no file byte. *(Corrected 2026-07-28.)* |

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
- *(Corrected 2026-07-28. This previously read: "In current canonical Steam hash
  (`74154bfa...`), this byte is already `0x01`." It is **zero at load** — the
  address is BSS. It reaches `1` only when `-testeur` is parsed first, via
  `mov byte ptr [ebx + 0x186], 1` at `0x00423c7d`. See "Correction 2026-07-28".)*
- *(Corrected 2026-07-28. This previously read: "Historical baseline reports with
  `0x00` explain why some users saw the parser path skipped." Withdrawn — the
  parser path is skipped on **every** stock command line, in every build,
  because the guard starts at zero. The historical `0x00`/`0x01` reports are
  UNKNOWN in origin and are no longer offered as an explanation.)*

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

### Option 0: Isolated safe-copy testing

Use the Windowed & Mods custom profile to select the resolution gate and
windowed-startup rows independently. AppCore verifies the supported specimen
and mutates only the copied executable.

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

### Option 3: ~~Binary Patch (Guard-byte Normalization)~~ — WITHDRAWN 2026-07-28

**Do not do this.** The four steps that stood here are quoted in
"Correction 2026-07-28" above and are not repeated as instructions, because
file offset `0x262F3E` is inside `.rsrc`, not `.data`. Editing it changes a
**resource byte** and does nothing to the parser gate, which is BSS and has no
file byte at all.

The **2026-03 validation note** that stood here — "In current repo binaries, the
guard is already `0x01`" — was reading that same `.rsrc` byte and is withdrawn.

The half of that note which was correct still holds: primary operational
guidance is the startup-flow patch set (`0x12A644`, optional `0x12BB97`) exposed
by Binary Patches.

### Option 4: `-testeur -forcewindowed` on the command line (no patching)

MEASURED, on pristine: the shipped parser accepts `-forcewindowed` once
`-testeur` has already been seen in the same argument sweep, and the game then
presents windowed at client 640x480 with the desktop untouched — see
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md).
Order matters: `-testeur` must come **first**.

## Key Addresses

| Address | Purpose |
|---------|---------|
| 0x00423bc0 | `CLIParams__ParseCommandLine` - CLI parsing |
| 0x00424150 | Guard flag check (`DAT_00662f3e`) |
| 0x00424168 | Set `mForceWindowed = 1` |
| 0x006244a0 | String `"-forcewindowed"` |
| 0x00662f3e | Guard flag — `CCLIParams` member `this+0x186`, **BSS, zero at load**; set to `1` at `0x00423c7d` only on the `-testeur` path. No file byte exists for it. *(Corrected 2026-07-28; previously read "current canonical Steam hash `74154bfa...` = 0x01; some historical baselines reported 0x00".)* |
| 0x00423c7d | `mov byte ptr [ebx + 0x186], 1` — the only writer of the guard, on `-testeur` |
| 0x00624618 | String `"-testeur"` |
| 0x00662db8 | The `CCLIParams` singleton; `+0x186` is the guard, `+0x38` is `mForceWindowed` |
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

The `-forcewindowed` launch outcome is controlled by both parser gating (`DAT_00662f3e`) and startup fullscreen flow. *(Corrected 2026-07-28. The sentence that followed here previously read: "In current repo binaries, the guard byte is already `0x01`, but startup-flow patches remain the reliable path for consistent windowed startup." The guard byte is **zero at load in every build** — it is BSS. Only the second clause survives.)* Startup-flow patches remain the reliable path for consistent windowed startup; the guard is opened at runtime by `-testeur`, not by the image.

**To enable windowed mode in current app workflow:**
1. **Primary stable path:** apply the stable startup-flow patch `0x12A644`, with resolution gate patch `0x129696` as desired.
2. **Optional experimental follow-up:** use `0x12BB97` only if the stable set is already verified and startup still flips to fullscreen on that setup.
3. ~~**Baseline normalization (optional):** ensure file offset `0x262F3E` is `0x01` so the parser gate does not block `-forcewindowed`.~~ **WITHDRAWN 2026-07-28** — quoted here struck through rather than deleted, because it was a live instruction that would corrupt `.rsrc`. Use `-testeur -forcewindowed` on the command line instead if an unpatched route is wanted; see Option 4.
4. **Wrapper fallback:** use wrapper/translation help only when system-specific behavior still bypasses the verified byte-patch path.

---

*Analysis performed December 2025*
*Binary analysis via Ghidra + GhydraMCP*
