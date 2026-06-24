# WinUI Free-Camera Q-Yaw-Left Runtime Readiness Note

Status: accepted bounded copied-runtime CDB proof
Date: 2026-06-18
Scope: `free_camera_keyboard_yaw_left_q_hook` plus hidden companion `free_camera_keyboard_yaw_left_q_cave`

## Summary

The Q-yaw-left row is an experimental copied-executable patch pair. The visible row redirects `CControllableCamera::ReceiveButtonAction` at file offset `0x01A980` to a hidden companion cave at `0x1A3A15`. The cave maps config-2 `look-left` button `25` (`0x19`) to free-camera yaw-left button `36` (`0x24`), then replays the displaced stack allocation and returns to `0x0041A98A`.

Accepted copied-runtime proof used a safe copied game folder only. The installed game folder, source clean backup executable, source options, and source assets were not mutated.

The Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, and Q-yaw-right rows are mutually exclusive because the variants patch the same hook and cave bytes. The catalog records this with explicit conflicts plus the `free_camera_keyboard_q_remap` exclusive group on the visible rows.

## Evidence

| Evidence | Result |
| --- | --- |
| Static/source mapping | `BUTTON_CAMERA_YAW_LEFT = 36`; config-2 `look-left` materializes Q as button `25`; `CControllableCamera::ReceiveButtonAction` handles camera yaw-left as an orientation-delta path. |
| Private ignored accepted artifact | Safe-copy launch with `free_camera_aurore_gate_bypass`, `free_camera_keyboard_yaw_left_q_hook`, hidden companion cave, `resolution_gate`, and `force_windowed`; source/installed material unchanged; managed stop clean. |
| `tools/winui_safe_copy_free_camera_movement_artifact_check.py --mode yaw-left` | Validates source safety, copied patch keys, exact `F`/wait/`Q`/wait/`F` input-window ordering, Q-window isolation, hook JMP/displacement prefix bytes, full cave bytes, button `25` cave rows, post-cave button `36` read-back rows, camera-handler target consistency, changing free-camera orientations, interpolation orientation deltas, and no Q/button-25 cave rows or interpolation deltas in adjacent wait windows. |

## Accepted Artifact Summary

| Field | Value |
| --- | --- |
| Mode | `yaw-left` |
| Schema | `winui-safe-copy-free-camera-q-yaw-left-proof.v1` |
| Q input window | `down:Q,wait:1500,up:Q` |
| Q cave rows | `33` |
| Post-cave button-36 rows | `33` |
| Q camera-handler rows | `33` |
| Prepare-for-interpolation orientation deltas | `33` |
| Set-current-camera rows | `3` |
| Visual captures | `8` |

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_movement_artifact_check.py --mode yaw-left --expect-q-count 33 <private ignored accepted artifact>
npm run test:winui-safe-copy-free-camera-movement-artifact
```

The package script self-test covers Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, and Q-yaw-right synthetic proof modes, including expected-count failure checks. The private ignored accepted artifact was checked with the same focused checker in `--mode yaw-left --expect-q-count 33`. The broader closeout also reruns WinUI build, filtered Patch Bench regression tests, docsync, markdown-link, public-allowlist, release-profile, curated-manifest, repo-hygiene, JSON parse, and whitespace gates before commit.

## Boundaries

- This proves one copied-runtime key path: after the Aurore gate patch toggles the free camera on, Q-bound yaw-left input reaches the hook/cave path and produces observed free-camera orientation deltas.
- This does not prove control feel, pitch axes, joystick/analog coverage, pause/menu safety, gameplay safety, rendering correctness, visual parity, online/netcode, rebuild parity, or no-noticeable-difference parity.
- This does not promote the patch into the Enhanced Profile Preview or any default preset.
- This row conflicts with the Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, and Q-yaw-right rows; use one remap variant per copied executable.
- This did not mutate Ghidra and did not produce a Ghidra backup.
