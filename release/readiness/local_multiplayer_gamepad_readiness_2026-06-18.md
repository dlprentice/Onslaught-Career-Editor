# Local Multiplayer Physical Gamepad Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0042e4d0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: readiness preflight blocked on missing present physical controller
Date: 2026-06-18
Scope: `local-multiplayer-gamepad-readiness`

Current measured state: `1 readiness/preflight artifact; 0 physical DirectInput/gamepad runtime proof artifacts`.

`tools\winui_safe_copy_local_multiplayer_gamepad_readiness.py --inventory --output subagents\winui-safe-copy-live-runtime\local-multiplayer-gamepad-readiness-20260618\gamepad-readiness.json` collected live Windows device and joystick registry inventory on this workstation. The summary reported `status=blocked_no_present_gamepad`, `presentGamepadCandidateCount=0`, and `registryGamepadCandidateCount=0`. Several joystick OEM registry keys were present, but their `OEMName` values were blank; that is not treated as usable hardware proof.

This is a preflight only: hardware detection is a precondition, not BEA polling proof, virtual-controller routing proof, visible movement proof, or online multiplayer proof.

## Static Anchors

| Address | Role |
| --- | --- |
| `0x00513120 PlatformInput__InitDirectInput` | DirectInput startup/enumeration path; static evidence records `DirectInput8Create`, joypad enumeration, deadzone setup, and four-pad cap. |
| `0x00513370 PlatformInput__PollPadState` | Per-pad DirectInput poll/reacquire/state update path. |
| `0x005147f0 CPCController__GetJoyButtonOn` | Joy button held-state accessor over the current pad-state table. |
| `0x00514640 CPCController__GetJoyAnalogueLeftX` | Left-stick X accessor; paired with `0x00514670 CPCController__GetJoyAnalogueLeftY` for config-1/config-3 movement. |
| `0x0042e4d0 CController__SendButtonAction` | Virtual button dispatch bridge used by current CDB keyboard proof. |
| `0x004d3110 CPlayer__ReceiveButtonActionState` | Existing runtime observer label for downstream player receive/state rows. |

## Next Positive Claim Bar

A future physical-controller proof must use a copied profile and exact managed BEA PID, attach CDB to that process, and observe all of the following in one bounded run:

1. `0x00513370 PlatformInput__PollPadState` rows for a present pad.
2. A CPCController joy accessor row, such as `0x005147f0 CPCController__GetJoyButtonOn` or `0x00514640..0x005146d0` analogue accessors, changing during documented physical-controller stimulus.
3. Downstream rows at `0x0042e4d0 CController__SendButtonAction` and `0x004d3110 CPlayer__ReceiveButtonActionState`.
4. Matching BattleEngine/WalkerPart or JetPart state rows if the claim reaches gameplay-state routing.
5. A no-input negative control.
6. `zero keyboard SendInput/keybd_event/PostMessage positive-stimulus counters`.
7. Installed game, original executable, source `defaultoptions.bea`, and source saves unchanged after managed stop.

The acceptable positive wording after that future slice is bounded to: one copied-profile host/device/config/action path shows BEA DirectInput pad polling reaches the virtual controller and state path. It must not claim all controllers, all configs, control-feel improvement, online/network behavior, deterministic sync, exact DirectInput layout, rebuild parity, or no-noticeable-difference parity.

## Validation

- `py -3 tools\winui_safe_copy_local_multiplayer_gamepad_readiness.py --self-test`
- `py -3 tools\winui_safe_copy_local_multiplayer_gamepad_readiness.py --inventory --output subagents\winui-safe-copy-live-runtime\local-multiplayer-gamepad-readiness-20260618\gamepad-readiness.json`

Boundary: no copied BEA launch, no installed-game mutation, no original `BEA.exe` mutation, no Ghidra mutation, no executable-byte change, and not online multiplayer proof.
