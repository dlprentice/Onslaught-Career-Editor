# WinUI Free-Camera Q-Pitch-Up Runtime Readiness Note

Status: accepted bounded copied-runtime CDB proof
Date: 2026-06-18
Scope: `free_camera_keyboard_pitch_up_q_hook` plus hidden companion `free_camera_keyboard_pitch_up_q_cave`

## Summary

The Q-pitch-up row is an experimental copied-executable patch pair. The visible row redirects `CControllableCamera::ReceiveButtonAction` at file offset `0x01A980` to a hidden companion cave at `0x1A3A15`. The cave maps config-2 `look-up` button `26` (`0x1a`) to free-camera pitch-up button `34` (`0x22`), then replays the displaced stack allocation and returns to `0x0041A98A`.

Accepted copied-runtime proof used a safe copied game folder only. The installed game folder, source clean backup executable, source options, and source assets were not mutated.

The Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, Q-pitch-up, and Q-pitch-down rows are mutually exclusive because the variants patch the same hook and cave bytes. The catalog records this with explicit conflicts plus the `free_camera_keyboard_q_remap` exclusive group on the visible rows.

## Evidence

| Evidence | Result |
| --- | --- |
| Static/source mapping | `BUTTON_MECH_PITCH_UP = 26`; `BUTTON_CAMERA_PITCH_UP = 34`; config-2 `look-up` materializes Q as button `26`; `CControllableCamera::ReceiveButtonAction` handles camera pitch-up as an orientation-delta path. |
| Private ignored accepted artifact | Safe-copy launch with `free_camera_aurore_gate_bypass`, `free_camera_keyboard_pitch_up_q_hook`, hidden companion cave, `resolution_gate`, and `force_windowed`; source/installed material unchanged; managed stop clean. |
| `tools/winui_safe_copy_free_camera_movement_artifact_check.py --mode pitch-up` | Validates source safety, copied patch keys, exact `F`/wait/`Q`/wait/`F` input-window ordering, Q-window isolation, hook JMP/displacement prefix bytes, full cave bytes, button `26` cave rows with negative vertical analogue value `0xbf800000`, post-cave button `34` read-back rows, camera-handler target consistency, changing free-camera orientations, interpolation orientation deltas, and no Q/button-26 cave rows or interpolation deltas in adjacent wait windows. |

## Accepted Artifact Summary

| Field | Value |
| --- | --- |
| Mode | `pitch-up` |
| Schema | `winui-safe-copy-free-camera-q-pitch-up-proof.v1` |
| Q input window | `down:Q,wait:1500,up:Q` |
| Q cave rows | `31` |
| Post-cave button-34 rows | `31` |
| Q camera-handler rows | `31` |
| Prepare-for-interpolation orientation deltas | `31` |
| Set-current-camera rows | `3` |
| Visual captures | `8` |

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --mode pitch-up --expect-q-count 31 <private ignored accepted artifact>
npm run test:winui-safe-copy-free-camera-movement-artifact
```

The package script self-test covers Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, Q-pitch-up, and Q-pitch-down synthetic proof modes, including expected-count failure checks. The private ignored accepted artifact was checked with the same focused checker in `--mode pitch-up`.

## Boundaries

- This proves one copied-runtime key path: after the Aurore gate patch toggles the free camera on, Q-bound pitch-up input reaches the hook/cave path and produces observed free-camera orientation deltas.
- This does not prove full free-camera controls, control feel, joystick/analog coverage, pause/menu safety, gameplay safety, rendering correctness, visual parity, online/netcode, rebuild parity, or no-noticeable-difference parity.
- This does not promote the patch into the Enhanced Profile Preview or any default preset.
- This row conflicts with the Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, and Q-pitch-down rows; use one remap variant per copied executable.
- This did not mutate Ghidra and did not produce a Ghidra backup.
