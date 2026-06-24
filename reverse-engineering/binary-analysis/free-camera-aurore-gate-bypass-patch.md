# Free Camera Aurore Gate Bypass Patch

Status: byte/catalog proof plus copied-profile CDB toggle proof; Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, Q-pitch-up, and Q-pitch-down companion paths are now separately proven

This note records the copied-executable experimental patch row `free_camera_aurore_gate_bypass`.

## Static Evidence

`CGame__ReceiveButtonAction` is the debug-button dispatcher for button IDs `0..14`. The retail Steam binary includes an Aurore cheat gate before the `BUTTON_TOGGLE_FREE_CAMERA` path:

| Anchor | Evidence |
| --- | --- |
| Function | `0x0046f7e0 CGame__ReceiveButtonAction` |
| Gate call | `IsCheatActive(4)` at `0x0046f835` |
| Patch VA | `0x0046f83c` |
| File offset | `0x06f83c` |
| Clean bytes | `0F 84 58 02 00 00` |
| Patched bytes | `90 90 90 90 90 90` |

The patch NOPs the Aurore-inactive conditional branch so the existing free-camera debug button case can fall through to the toggle path.

## Runtime Evidence

An earlier private ignored runtime observation proved only that a copied clean-backup executable with `resolution_gate`, `force_windowed`, and `free_camera_aurore_gate_bypass` launched, produced one exact process/window loading-screen capture, stopped through the managed process path, and left the installed executable and clean backup hashes unchanged.

The accepted 2026-06-18 copied-runtime CDB pair strengthens this:

| Artifact | Result |
| --- | --- |
| Private ignored clean-branch toggle artifact | Clean copied branch with `resolution_gate` and `force_windowed` received `BUTTON_TOGGLE_FREE_CAMERA` (`button=1`) from scoped `F` input, showed clean gate bytes `0f 84 58 02 00 00`, and did not hit `CGame__ToggleFreeCameraOn` or `CGame__SetCurrentCamera`. |
| Private ignored patched-branch toggle artifact | Patched copied branch with `resolution_gate`, `force_windowed`, and `free_camera_aurore_gate_bypass` received two scoped `F` taps, showed patched gate bytes `90 90 90 90 90 90`, hit `CGame__ToggleFreeCameraOn`, called `CGame__SetCurrentCamera` for the on transition, observed `free0=1` on the second receive row, and called `CGame__SetCurrentCamera` with `releaseOld=1` to restore the original camera pointer. |

Focused checker: `tools/winui_safe_copy_free_camera_toggle_artifact_check.py`.

Readiness note: `release/readiness/winui_safe_copy_free_camera_toggle_2026-06-18.md`.

## Companion Q Movement And Orientation Hooks

Follow-up runtime work added separate experimental visible rows for one-key-path movement and orientation proofs:

- `free_camera_keyboard_forward_q_hook` plus hidden companion cave `free_camera_keyboard_forward_q_cave`: redirects the copied executable at `0x0041a980` / file offset `0x01a980` from the original prologue bytes `8B 44 24 08 81 EC C0 00 00 00` to `E9 90 90 18 00 90 90 90 90 90`. The cave lives at `0x005a3a15` / file offset `0x1a3a15`, remaps button `31` to button `38`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_backward_q_hook` plus hidden companion cave `free_camera_keyboard_backward_q_cave`: uses the same hook and cave offsets, remaps button `32` to button `39`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_strafe_left_q_hook` plus hidden companion cave `free_camera_keyboard_strafe_left_q_cave`: uses the same hook and cave offsets, remaps button `29` to button `40`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_strafe_right_q_hook` plus hidden companion cave `free_camera_keyboard_strafe_right_q_cave`: uses the same hook and cave offsets, remaps button `30` to button `41`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_yaw_left_q_hook` plus hidden companion cave `free_camera_keyboard_yaw_left_q_cave`: uses the same hook and cave offsets, remaps button `25` to button `36`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_yaw_right_q_hook` plus hidden companion cave `free_camera_keyboard_yaw_right_q_cave`: uses the same hook and cave offsets, remaps button `27` to button `37`, replays the displaced stack allocation, and jumps back to `0x0041a98a`.
- `free_camera_keyboard_pitch_up_q_hook` plus hidden `free_camera_keyboard_pitch_up_q_cave` maps copied-runtime config-2 `Q`/`E` look-up input (button `26`) to camera pitch-up (button `34`).
- `free_camera_keyboard_pitch_down_q_hook` plus hidden `free_camera_keyboard_pitch_down_q_cave` maps copied-runtime config-2 `Q`/`E` look-down input (button `28`) to camera pitch-down (button `35`).

The Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, Q-pitch-up, and Q-pitch-down remap variants are mutually exclusive because all eight patch the same hook and cave bytes.

The first diagnostic cave address `0x005a3955` was rejected for durable catalog use because it overlaps documented community widescreen/FOV cave space. The accepted catalog row uses `0x005a3a15`, which has clean `CC` padding on the canonical clean Steam specimen.

Accepted hardened Q-forward movement artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 20 scoped-Q cave hits, 20 post-cave button-38 read-backs, 20 camera-handler rows, 20 interpolation deltas, and no Q/button-31 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-backward movement artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 21 scoped-Q cave hits, 21 post-cave button-39 read-backs, 21 camera-handler rows, 21 interpolation deltas, and no Q/button-32 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-strafe-left movement artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 32 scoped-Q cave hits, 32 post-cave button-40 read-backs, 32 camera-handler rows, 32 interpolation deltas, and no Q/button-29 cave rows or interpolation deltas in adjacent wait windows. One earlier strafe-left timing diagnostic stayed source-safe but was rejected because the first free-camera toggle landed outside the expected first input window.

Accepted Q-strafe-right movement artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 31 scoped-Q cave hits, 31 post-cave button-41 read-backs, 31 camera-handler rows, 31 interpolation deltas, and no Q/button-30 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-yaw-left orientation artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 33 scoped-Q cave hits, 33 post-cave button-36 read-backs, 33 camera-handler rows, 33 orientation interpolation deltas, and no Q/button-25 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-yaw-right orientation artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 32 scoped-Q cave hits, 32 post-cave button-37 read-backs, 32 camera-handler rows, 32 orientation interpolation deltas, and no Q/button-27 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-pitch-up orientation artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 31 scoped-Q cave hits, 31 post-cave button-34 read-backs, 31 camera-handler rows, 31 orientation interpolation deltas, and no Q/button-26 cave rows or interpolation deltas in adjacent wait windows.

Accepted Q-pitch-down orientation artifact: private ignored copied-runtime CDB proof with exact `F`/wait/`Q`/wait/`F` ordering, full cave-byte read-back, 33 scoped-Q cave hits, 33 post-cave button-35 read-backs, 33 camera-handler rows, 33 orientation interpolation deltas, and no Q/button-28 cave rows or interpolation deltas in adjacent wait windows.

Movement checker: `tools/winui_safe_copy_free_camera_movement_artifact_check.py`.

Movement/orientation readiness notes: `release/readiness/winui_free_camera_q_forward_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_backward_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_strafe_left_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_strafe_right_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_yaw_left_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_yaw_right_runtime_2026-06-18.md`, `release/readiness/winui_free_camera_q_pitch_up_runtime_2026-06-18.md`, and `release/readiness/winui_free_camera_q_pitch_down_runtime_2026-06-18.md`.

Pause-context diagnostics: private ignored copied-runtime follow-ups attempted `Q`/`F`/`Q`/`O`/`Q`/`O`/`F`/`Q` with the Q-forward row active. The first run stayed source-safe, captured ten visual frames, and showed Q-forward movement in the active free-camera windows, but the two focused `O` windows produced zero `CController__SendButtonAction button=56`, zero `CGame__Pause`, and zero `CGame__UnPause` rows. A stricter held-`O` follow-up captured eleven visual-proof frames, used `down:O,wait:1000,up:O`, added `0x4f`-filtered upstream key-query breakpoints for `CPCController__GetKeyOnce`, `PlatformInput__GetKeyOnceCore`, and `PlatformInput__ConsumeKeyOnce`, and still produced zero CDB bytes in both `O` input windows while adjacent `Q`/`F` windows produced debugger output. A broader key-census follow-up then captured six visual-proof frames with an exact-PID F/O/Q/F observer and classified the held-`O` window as `o-key-state-latched-without-o-query`: `onceScanO=01`, `oKeyQueryCount=0`, no `BUTTON_PAUSE` dispatch, and no pause/unpause calls. `tools/winui_safe_copy_free_camera_pause_context_artifact_check.py` correctly rejects the held-`O` artifact with `pause window did not query CPCController::GetKeyOnce for O`, while `tools/winui_safe_copy_free_camera_key_census_artifact_check.py` accepts the broader key-census artifact as a diagnostic only. `release/readiness/winui_free_camera_pause_context_diagnostic_2026-06-18.md` records both negative pause diagnostics and the accepted key-census classification. This does not prove `O -> BUTTON_PAUSE` or any pause/menu behavior. The `O` mapping remains source/static-hypothesis plus open runtime proof; the documented runtime mapping table address is virtual `.data`/BSS-style state and cannot be verified by raw clean-executable bytes alone.

## Claim Boundary

This is free-camera toggle proof plus four bounded one-key companion movement proofs and four bounded one-key companion orientation proofs, not full free-camera behavior proof. It proves scoped `F` reaches `BUTTON_TOGGLE_FREE_CAMERA`, on/off camera-pointer transitions, scoped `Q` reaches the selected remap hook/cave paths, one copied-runtime Q-forward path, one copied-runtime Q-backward path, one copied-runtime Q-strafe-left path, one copied-runtime Q-strafe-right path with observed camera-position deltas, one copied-runtime Q-yaw-left path, one copied-runtime Q-yaw-right path, one copied-runtime Q-pitch-up path, and one copied-runtime Q-pitch-down path with observed camera-orientation deltas. It does not prove arbitrary key reachability, `O`/pause key reachability, camera-control feel, joystick/analog coverage, gameplay safety, pause/menu behavior, rendering behavior, visual parity, online/netcode, rebuild parity, or no-noticeable-difference parity. It must remain experimental until broader copied-profile runtime proof captures controllable camera behavior and safety boundaries.

The patch is for copied/app-owned `BEA.exe` profiles only. It must not be applied to the installed Steam executable.
