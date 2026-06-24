# WinUI DirectInput Deadzone Runtime A/B Readiness Note

Status: readiness gate complete; runtime blocked
Date: 2026-06-23
Scope: `directinput-deadzone-runtime-a-b-readiness`

This slice makes the next DirectInput deadzone proof gate explicit after the static byte export. It does not add a Patch Bench row and does not claim improved control feel.

Evidence:

| Item | Value |
| --- | --- |
| Contract | `roadmap/original-binary-directinput-deadzone-runtime-ab-readiness.v1.json` |
| Static byte-export proof | `winui-directinput-deadzone-byte-export.v1` |
| Candidate function | `0x00513120 PlatformInput__InitDirectInput` |
| Candidate instruction | `0x00513167` / file offset `0x113167` |
| Candidate immediate | `0x0051316D` / file offset `0x11316D` |
| Baseline immediate | `0x96` |
| Baseline instruction bytes | `C7 85 E0 30 03 00 96 00 00 00` |
| Latest local gamepad preflight | `blocked_no_present_gamepad` |
| Present gamepad candidates | `0` |
| Registry gamepad candidates | `0` |

Required before any visible deadzone patch row:

1. Fresh clean-specimen byte export still matches `0x00513167 / 0x113167`.
2. Copied-executable A/B byte verification under an app-owned proof root.
3. Restore verification before and after any attempted alternate immediate.
4. Physical gamepad or equivalent DirectInput runtime device present on the host.
5. Exact managed copied `BEA.exe` PID and CDB attachment.
6. DirectInput poll/accessor rows at `0x00513370 PlatformInput__PollPadState` and CPCController joy accessors.
7. Zero keyboard `SendInput` / `keybd_event` / `PostMessage` positive-stimulus counters for the DirectInput stimulus window.
8. No-input negative control.
9. Downstream `CController__SendButtonAction` and `CPlayer__ReceiveButtonActionState` evidence.
10. Per-configuration regression across controller configs `1-4`.

Boundary flags:

- `addsPatchRow=false`
- `visiblePatchRowAdded=false`
- `runtimeAbProof=false`
- `runtimeProof=false`
- `physicalGamepadProof=false`
- `directInputRuntimeProof=false`
- `improvedControlFeelProof=false`
- `copiedExecutablePatchProof=false`
- `installedGameMutation=false`
- `originalExecutableMutation=false`

Non-claims:

- not a Patch Bench row
- not a player-facing deadzone option
- not runtime DirectInput proof
- not physical gamepad proof
- not improved control-feel proof
- not proof that `0x96` causes floaty controls
- not proof that lowering the immediate improves controls
- not online multiplayer proof
- not rebuild parity proof

Validation:

- `py -3 tools\winui_directinput_deadzone_runtime_ab_readiness.py --self-test`
- `py -3 tools\winui_directinput_deadzone_runtime_ab_readiness.py --check`
- `py -3 tools\winui_directinput_deadzone_runtime_ab_readiness.py --gamepad-artifact subagents\winui-control-feel\gamepad-readiness-live-20260623\gamepad-readiness-summary.json`
- `npm run test:winui-directinput-deadzone-runtime-ab-readiness`
