# WinUI Control-Feel Candidate Map Readiness Note

Status: complete read-only candidate map
Date: 2026-06-19
Scope: `winui-control-feel-candidate-map`

`roadmap/original-binary-control-feel-candidate-map.v1.json` records six bounded original-binary control-feel candidates for copied-profile work. It adds no visible Patch Bench row, performs no runtime proof, performs no Ghidra mutation, and does not mutate the installed game or original `BEA.exe`.

Accepted candidate classes:

| Candidate | Classification | Boundary |
| --- | --- | --- |
| `copied_defaultoptions_mouse_sensitivity` | `already_materialized_options_edit` | Safe-copy options baseline; not analog deadzone, look-curve, or improved-feel proof. |
| `copied_defaultoptions_controller_config` | `already_materialized_options_edit` | Safe-copy options/config baseline; not a binary patch or best-feel proof. |
| `platform_input_directinput_deadzone_0x96` | `file_backed_static_candidate_runtime_blocked` | File-backed byte-export target at `0x00513167` / `0x113167`; not patchable yet, and physical DirectInput/gamepad proof is still required before any player-facing deadzone claim. |
| `controller_mapping_engine` | `needs_runtime_trace` | Trace/provenance anchor around `0x0042db40 CController__DoMappings`; not a current patch target. |
| `mouse_look_angle_update` | `needs_runtime_trace` | Camera-response trace target around `0x00407540 CGame__UpdateMouseLookAngles` and `0x006254f4 g_MouseSensitivity`; not improved mouse-look proof. |
| `player_receive_button_action_observer` | `observer_only` | Runtime CDB observer anchor at `0x004d3110 CPlayer__ReceiveButtonAction`; not a recommended patch target yet. |

The recorded risk model keeps broad dispatcher/accessor hooks highest risk, DirectInput/deadzone work high risk until physical device proof exists, camera/movement constants medium-high risk because they can change gameplay balance, and copied-options presets lower risk because they are reversible safe-copy edits.

Completed next rung: `directinput-deadzone-byte-export`. It verifies exact clean-specimen instruction bytes `C7 85 E0 30 03 00 96 00 00 00` at `0x00513167` / `0x113167`, with the `0x96` immediate at `0x0051316D` / `0x11316D`, and preserves no-improved-feel/no-gamepad-proof boundaries. It does not add a Patch Bench row.

Current next rung: `directinput-deadzone-runtime-a-b-proof`. This remains blocked on copied-runtime DirectInput/gamepad evidence, copied-executable A/B byte verification, restore verification, a no-input negative control, downstream virtual-controller/player-state evidence, and per-configuration regression across controller configs `1-4`.

Validation:

- `py -3 tools\winui_control_feel_candidate_map_probe_test.py`
- `py -3 tools\winui_control_feel_candidate_map_probe.py --self-test`
- `py -3 tools\winui_control_feel_candidate_map_probe.py --check`

Non-claims:

- No improved control-feel proof.
- No physical gamepad proof.
- No wall-clock latency proof.
- No true online multiplayer proof.
- No active P3/P4 original-binary gameplay proof.
- No rebuild parity or no-noticeable-difference parity proof.
