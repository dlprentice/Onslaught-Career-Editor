# WinUI Safe-Copy Free-Camera Toggle Readiness Note

Status: accepted copied-runtime CDB toggle proof
Date: 2026-06-18
Scope: `free_camera_aurore_gate_bypass`

This slice validates the experimental copied-executable free-camera gate patch against a real app-owned copied `BEA.exe` launch. The patch was applied only to copied game folders under ignored runtime evidence roots. It did not mutate the installed Steam game folder, the original `BEA.exe`, source `defaultoptions.bea`, source `savegames`, or the Ghidra database.

## Evidence

| Evidence Class | Result |
| --- | --- |
| Private ignored baseline copied-runtime artifact | Clean copied branch with `resolution_gate` and `force_windowed` received `BUTTON_TOGGLE_FREE_CAMERA` (`button=1`) from scoped `F` input, showed clean gate bytes `0f 84 58 02 00 00`, and did not hit `CGame__ToggleFreeCameraOn` or `CGame__SetCurrentCamera`. |
| Private ignored patched copied-runtime artifact | Patched copied branch with `resolution_gate`, `force_windowed`, and `free_camera_aurore_gate_bypass` received two scoped `F` taps, showed patched gate bytes `90 90 90 90 90 90`, hit `CGame__ToggleFreeCameraOn`, called `CGame__SetCurrentCamera` for the on transition, observed `free0=1` on the second receive row, and called `CGame__SetCurrentCamera` with `releaseOld=1` to restore the original camera pointer. |
| `tools/runtime-probes/free-camera-toggle-observer.cdb.txt` | Exact-PID CDB observer for `CGame__ReceiveButtonAction`, the free-camera case/gate site, `CGame__ToggleFreeCameraOn`, and `CGame__SetCurrentCamera`. |
| `tools/winui_safe_copy_free_camera_toggle_artifact_check.py` | Validates source safety, copied patch keys, scoped input, visual captures, CDB attach/cleanup, clean-vs-patched gate bytes, toggle reachability, `free0` transition, and original-camera restore. |

Accepted checker summary:

| Field | Value |
| --- | --- |
| Baseline receive rows | `1` |
| Baseline toggle/set-camera rows | `0 / 0` |
| Patched receive rows | `2` |
| Patched toggle/set-camera rows | `1 / 2` |
| Patched free-camera transition | `free0: 0 -> 1` |
| Camera pointer transition | Original and free-camera pointers were nonzero, distinct, and restored on the second toggle. |
| Visual captures | `3 baseline + 3 patched` |

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_toggle_artifact_check.py --self-test
npm run test:winui-safe-copy-free-camera-toggle-artifact
```

The private ignored baseline/patched artifacts were checked with the same focused checker and minimum three-capture gate. The package script is also included in `test:winui-copied-profile-runtime`.

## Boundaries

- This proves copied-runtime debug input reaches the existing free-camera toggle path when the Aurore gate branch is bypassed.
- This proves the first toggle installs a different camera pointer and the second toggle restores the original camera pointer.
- This does not prove free-camera movement, camera control feel, camera usability, pause/menu behavior, gameplay safety, rendering correctness, visual parity, rebuild parity, or no-noticeable-difference parity.
- This does not promote the patch into the Enhanced Profile Preview or any default preset.
- No Ghidra mutation or Ghidra backup was produced by this runtime slice.
