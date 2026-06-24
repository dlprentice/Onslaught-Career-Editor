# WinUI Debug Camera Preview Proof Matrix

Status: proof-boundary guard validated
Date: 2026-06-22
Scope: `debug-camera-preview`

This slice adds a machine-checked public proof-boundary consistency matrix around the existing Debug Camera Preview profile and the already cataloged free-camera rows. It does not revalidate private runtime artifacts. It adds no executable bytes, no BEA launch, no CDB attach, no Ghidra mutation, and no new runtime artifact.

## Matrix Counts

| Counter | Value |
| --- | --- |
| `movementProofRows` | 8 |
| `pauseContextProofRows` | 2 |
| `keyCensusProofRows` | 1 |

Guard tokens: `movementProofRows=8`; `pauseContextProofRows=2`; `keyCensusProofRows=1`.

## Preset-selected rows

Debug Camera Preview still selects only:

- `resolution_gate`
- `force_windowed`
- `free_camera_aurore_gate_bypass`
- `free_camera_keyboard_forward_q_hook`

AppCore expands the hidden companion `free_camera_keyboard_forward_q_cave` during copied-executable preparation.

## Manual-only rows

The other proven Q remap rows remain manual/custom-only because the rows share the same hook/cave bytes and are mutually exclusive:

- `free_camera_keyboard_backward_q_hook`
- `free_camera_keyboard_strafe_left_q_hook`
- `free_camera_keyboard_strafe_right_q_hook`
- `free_camera_keyboard_yaw_left_q_hook`
- `free_camera_keyboard_yaw_right_q_hook`
- `free_camera_keyboard_pitch_up_q_hook`
- `free_camera_keyboard_pitch_down_q_hook`

## Boundaries

The matrix records that eight individual Q remap rows have separate accepted copied-runtime CDB movement/orientation proof. It is not private runtime artifact revalidation. It does not say the preset is a full free-camera mode and is not a full free-camera control scheme.

Still not proven: full camera controls, joystick/analog camera input, pause/menu safety, gameplay safety, rendering behavior, render parity, online play, rebuild parity, or no-noticeable-difference parity.

Validation target: `npm run test:winui-debug-camera-preview-proof-matrix`.
