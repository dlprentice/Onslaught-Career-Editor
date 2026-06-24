# WinUI Free-Camera Q-Strafe-Left Runtime Readiness Note

Status: accepted copied-runtime CDB movement proof for one bounded key path
Date: 2026-06-18
Scope: `free_camera_keyboard_strafe_left_q_hook` plus hidden companion `free_camera_keyboard_strafe_left_q_cave`

This slice validates a third experimental copied-executable companion hook for the existing free-camera toggle patch. The patch was applied only to an app-owned copied `BEA.exe` under ignored runtime evidence roots. It did not mutate the installed Steam game folder, the original `BEA.exe`, source `defaultoptions.bea`, source `savegames`, or the Ghidra database.

## Patch Shape

| Row | VA / file offset | Bytes |
| --- | --- | --- |
| Visible hook `free_camera_keyboard_strafe_left_q_hook` | `0x0041a980` / `0x01a980` | `8B 44 24 08 81 EC C0 00 00 00` -> `E9 90 90 18 00 90 90 90 90 90` |
| Hidden companion cave `free_camera_keyboard_strafe_left_q_cave` | `0x005a3a15` / `0x1a3a15` | `CC` x29 -> load button argument, map button `29` to button `40`, replay the displaced stack allocation, and jump back to `0x0041a98a` |

The Q-forward, Q-backward, Q-strafe-left, and Q-strafe-right rows are mutually exclusive because the variants patch the same hook and cave bytes. The catalog records that with explicit conflicts plus the `free_camera_keyboard_q_remap` exclusive group on the visible rows.

## Evidence

| Evidence Class | Result |
| --- | --- |
| Private ignored rejected diagnostic artifact | The first strafe-left attempt stayed source-safe and stopped cleanly, but the strict checker rejected it because the initial free-camera toggle landed outside the expected first input window. It is timing/readiness evidence only. |
| Private ignored accepted copied-runtime artifact | Applied `resolution_gate`, `force_windowed`, `free_camera_aurore_gate_bypass`, `free_camera_keyboard_strafe_left_q_hook`, and hidden `free_camera_keyboard_strafe_left_q_cave` to the copied executable only; launched copied level `100`; sent scoped `F`, wait, `Q` hold, wait, `F`; captured eight bounded target-window frames; stopped the managed copied process; left source material unchanged. |
| `tools/runtime-probes/free-camera-movement-observer.cdb.txt` | Exact-PID CDB observer for the gate/toggle path, controller dispatch, hook/cave bytes, `CControllableCamera` movement handler, and `PrepareForInterpolation` position deltas. |
| `tools/winui_safe_copy_free_camera_movement_artifact_check.py --mode strafe-left` | Validates source safety, copied patch keys, exact `F`/wait/`Q`/wait/`F` input-window ordering, Q-window isolation, hook JMP/displacement prefix bytes, full cave bytes, button `29` cave rows, post-cave button `40` read-back rows, camera-handler target consistency, changing free-camera positions, interpolation deltas, and no Q/button-29 cave rows or interpolation deltas in adjacent wait windows. |

Accepted checker summary:

| Field | Value |
| --- | --- |
| Q input window | `down:Q,wait:1500,up:Q` |
| Q cave rows | `32` |
| Post-cave button-40 rows | `32` |
| Q camera-handler rows | `32` |
| Prepare-for-interpolation deltas | `32` |
| Set-current-camera rows | `3` |
| Visual captures | `8` |

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --mode strafe-left <private ignored accepted artifact>
npm run test:winui-safe-copy-free-camera-movement-artifact
```

The package script self-test covers Q-forward, Q-backward, Q-strafe-left, and Q-strafe-right synthetic proof modes. The private ignored accepted artifact was checked with the same focused checker in `--mode strafe-left`. The broader closeout also reran WinUI build, filtered Patch Bench regression tests, docsync, markdown-link, public-allowlist, release-profile, curated-manifest, repo-hygiene, JSON parse, and whitespace gates.

## Boundaries

- This proves one copied-runtime key path: after the Aurore gate patch toggles the free camera on, Q-bound strafe-left input reaches the hook/cave path and produces observed free-camera position deltas.
- This does not prove control feel, all camera axes, joystick/analog coverage, pause/menu safety, gameplay safety, rendering correctness, visual parity, rebuild parity, or no-noticeable-difference parity. The later Q-strafe-right readiness note separately proves one copied-runtime right-strafe key path.
- This does not promote the patch into the Enhanced Profile Preview or any default preset.
- This row conflicts with the Q-forward, Q-backward, and Q-strafe-right rows; use one remap variant per copied executable.
- No Ghidra mutation or Ghidra backup was produced by this runtime slice.
