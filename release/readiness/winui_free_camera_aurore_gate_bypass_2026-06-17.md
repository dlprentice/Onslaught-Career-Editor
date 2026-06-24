# WinUI Free Camera Aurore Gate Bypass Readiness Note

Status: byte/catalog proof plus accepted copied-runtime CDB toggle proof; movement proof lives in a separate companion row

The WinUI Windowed & Mods patch catalog now includes the experimental visible row `free_camera_aurore_gate_bypass`.

| Field | Value |
| --- | --- |
| Function | `0x0046f7e0 CGame__ReceiveButtonAction` |
| Patch VA | `0x0046f83c` |
| File offset | `0x06f83c` |
| Expected original bytes | `0F 84 58 02 00 00` |
| Patched bytes | `90 90 90 90 90 90` |
| Target specimen | Clean Steam retail `BEA.exe` SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, size `2506752` |

Purpose: NOP the retail Aurore-inactive branch before the existing free-camera debug toggle path in copied `BEA.exe` profiles.

Local ignored runtime observation:

| Artifact | Evidence |
| --- | --- |
| `subagents/winui-safe-copy-live-runtime/20260617-055140/live-safe-copy-runtime-smoke.json` | Used installed game folder as read-only source material and `BEA.exe.original.backup` as clean executable override; applied `resolution_gate`, `force_windowed`, and `free_camera_aurore_gate_bypass` to the copied executable only; launched copied `BEA.exe` with `-skipfmv`; captured one exact managed process/window frame; stopped the managed process; verified installed `BEA.exe` hash and clean-backup hash unchanged. |
| `subagents/winui-safe-copy-live-runtime/20260617-055140/capture/safe-copy-frame.png` | Captured a loading-screen frame only. |

Follow-up accepted toggle proof: `release/readiness/winui_safe_copy_free_camera_toggle_2026-06-18.md` records the clean-vs-patched CDB pair where scoped `F` reaches `BUTTON_TOGGLE_FREE_CAMERA`, the clean gate blocks, the patched gate reaches `CGame__ToggleFreeCameraOn`, the first toggle installs a different camera pointer, and the second toggle restores the original camera pointer.

Companion movement proof: `release/readiness/winui_free_camera_q_forward_runtime_2026-06-18.md` records the separate experimental `free_camera_keyboard_forward_q_hook` / hidden cave row where scoped `Q` reaches the hook/cave path and produces free-camera position deltas in a copied runtime.

Boundary: this Aurore row proves byte shape, static/source intent, copied-profile launch/capture/stop safety, and the free-camera on/off toggle path. The companion Q-forward row proves one bounded movement key path. Control feel, all axes, joystick/analog coverage, pause/menu safety, gameplay safety, rendering behavior, installed-game patching behavior, rebuild parity, and no-noticeable-difference parity remain unproven.
