# WinUI DirectInput Deadzone Byte Export Readiness Note

Status: static clean-specimen byte export complete; runtime blocked
Date: 2026-06-19
Scope: `directinput-deadzone-byte-export`

This slice verifies the Wave848 `0x96` DirectInput deadzone note against the canonical clean Steam retail executable bytes. It does not add a Patch Bench row and does not claim improved control feel.

Evidence:

| Item | Value |
| --- | --- |
| Clean specimen SHA-256 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| Clean specimen size | `2506752` |
| Function | `0x00513120 PlatformInput__InitDirectInput` |
| Function file offset | `0x113120` |
| Candidate instruction | `0x00513167` / file offset `0x113167` |
| Candidate instruction bytes | `C7 85 E0 30 03 00 96 00 00 00` |
| Candidate instruction text | `MOV dword ptr [EBP + 0x330e0], 0x96` |
| Immediate | `0x0051316D` / file offset `0x11316D` |
| Immediate bytes | `96 00 00 00` |

Boundary flags:

- `addsPatchRow=false`
- `runtimeProof=false`
- `physicalGamepadProof=false`
- `improvedControlFeelProof=false`
- `directInputRuntimeProof=false`
- `copiedExecutablePatchProof=false`

Non-claims:

- no Patch Bench row
- no player-facing deadzone claim
- no physical gamepad proof
- no runtime DirectInput proof
- no improved control-feel proof
- no look-curve proof
- no all-controller claim
- no gameplay parity proof
- no rebuild parity proof
- no no-noticeable-difference parity proof

Next proof requirements before any visible deadzone patch row:

1. Copied-executable A/B byte verification and restore verification.
2. Physical gamepad or equivalent DirectInput runtime proof.
3. No-input negative control.
4. DirectInput poll/accessor evidence.
5. Downstream virtual-controller and player-state evidence.
6. Per-configuration regression across controller configs `1-4`.

Validation:

- `py -3 tools\winui_directinput_deadzone_byte_export_check.py --export`
- `npm run test:winui-directinput-deadzone-byte-export`
