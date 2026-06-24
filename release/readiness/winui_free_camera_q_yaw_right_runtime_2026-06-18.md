# WinUI Free-Camera Q-Yaw-Right Runtime Readiness Note

Status: accepted bounded copied-runtime CDB proof
Date: 2026-06-18
Scope: `free_camera_keyboard_yaw_right_q_hook` plus hidden companion `free_camera_keyboard_yaw_right_q_cave`

## Summary

The Q-yaw-right row is an experimental copied-executable patch pair. The visible row redirects `CControllableCamera::ReceiveButtonAction` at file offset `0x01A980` to a hidden companion cave at `0x1A3A15`. The cave maps config-2 `look-right` button `27` (`0x1b`) to free-camera yaw-right button `37` (`0x25`), then replays the displaced stack allocation and returns to `0x0041A98A`.

Accepted copied-runtime proof used a safe copied game folder only. The installed game folder, source clean backup executable, source options, and source assets were not mutated.

The Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, and Q-yaw-right rows are mutually exclusive because the variants patch the same hook and cave bytes. The catalog records this with explicit conflicts plus the `free_camera_keyboard_q_remap` exclusive group on the visible rows.

## Evidence

| Evidence | Result |
| --- | --- |
| Static/source mapping | `BUTTON_CAMERA_YAW_RIGHT = 37`; config-2 `look-right` materializes Q as button `27`; `CControllableCamera::ReceiveButtonAction` handles camera yaw-right as an orientation-delta path. |
| Private ignored accepted artifact | Safe-copy launch with `free_camera_aurore_gate_bypass`, `free_camera_keyboard_yaw_right_q_hook`, hidden companion cave, `resolution_gate`, and `force_windowed`; source/installed material unchanged; managed stop clean. |
| `tools/winui_safe_copy_free_camera_movement_artifact_check.py --mode yaw-right` | Validates source safety, copied patch keys, exact `F`/wait/`Q`/wait/`F` input-window ordering, Q-window isolation, hook JMP/displacement prefix bytes, full cave bytes, button `27` cave rows, post-cave button `37` read-back rows, camera-handler target consistency, changing free-camera orientations, interpolation orientation deltas, and no Q/button-27 cave rows or interpolation deltas in adjacent wait windows. |

## Accepted Artifact Summary

| Field | Value |
| --- | --- |
| Mode | `yaw-right` |
| Schema | `winui-safe-copy-free-camera-q-yaw-right-proof.v1` |
| Q input window | `down:Q,wait:1500,up:Q` |
| Q cave rows | `32` |
| Post-cave button-37 rows | `32` |
| Q camera-handler rows | `32` |
| Prepare-for-interpolation orientation deltas | `32` |
| Set-current-camera rows | `3` |
| Visual captures | `8` |

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --mode yaw-right --expect-q-count 32 <private ignored accepted artifact>
npm run test:winui-safe-copy-free-camera-movement-artifact
```

The package script self-test covers Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, and Q-yaw-right synthetic proof modes, including expected-count failure checks. The private ignored accepted artifact was checked with the same focused checker in `--mode yaw-right --expect-q-count 32`. The broader closeout also reruns WinUI build, filtered Patch Bench regression tests, docsync, markdown-link, public-allowlist, release-profile, curated-manifest, repo-hygiene, JSON parse, and whitespace gates before commit.

## Boundaries

- This proves one copied-runtime key path: after the Aurore gate patch toggles the free camera on, Q-bound yaw-right input reaches the hook/cave path and produces observed free-camera orientation deltas.
- This does not prove control feel, all camera axes, joystick/analog coverage, pause/menu safety, gameplay safety, rendering correctness, visual parity, online/netcode, rebuild parity, or no-noticeable-difference parity.
- This does not promote the patch into the Enhanced Profile Preview or any default preset.
- This row conflicts with the Q-forward, Q-backward, Q-strafe-left, and Q-strafe-right rows; use one remap variant per copied executable.
- This did not mutate Ghidra and did not produce a Ghidra backup.
