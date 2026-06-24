# WinUI Control-Feel Telemetry Bundle Readiness Note

Status: complete local copied-runtime telemetry proof; not improved-feel proof
Date: 2026-06-19
Scope: `winui-control-feel-telemetry-bundle`

This slice adds a maintained checker for copied-runtime control telemetry and accepts one private ignored level-850 proof bundle. It is deliberately named telemetry, not control-feel improvement proof.

## Accepted Bundle

Accepted validator:

```powershell
py -3 tools\winui_control_feel_telemetry_bundle_check.py --artifact baseline_config1=<private-json> --artifact sharpened_config1=<private-json> --artifact swapped_config2=<private-json> --artifact alternate_config3=<private-json> --artifact swapped_alternate_config4=<private-json> --repeat-baseline <private-json> --no-input-control <private-json> --require-visual --require-files
```

Accepted schema: `winui-control-feel-telemetry-bundle.v1`.

Public-safe summary:

| Field | Value |
| --- | --- |
| Runtime profile | `original-binary-copied-local-control-telemetry` |
| Scenario count | `5` |
| Input-delta scenario count | `5` |
| Launch route | copied BEA, `-skipfmv -level 850`, controller configs `1,1,2,3,4` |
| Per scenario captures | `1` pre-input capture plus `3` post/after-input captures |
| Per scenario visual count | `4` |
| Per scenario input | one focused `down:UP,wait:700,up:UP` sequence |
| Repeat baseline | distinct process and distinct capture hash set |
| No-input control | one focused wait-only sequence, zero keyboard/mouse/window-message input events |
| Slot boundary | `slotCapacity=4`, `minimumArchitectureAcceptanceSlots=4`, `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4` |
| Online handoff boundary | `gameInputSentByNSlotScheduler=false`, `hostHelperInputSent=false` |
| N-player runtime proof | `nPlayerOriginalBinaryRuntimeProof=0` |
| Active P3/P4 gameplay proof | `activeP3P4OriginalBinaryGameplayProof=false` |

Accepted artifact hashes:

| Row | Hash |
| --- | --- |
| `baseline_config1` | `81944790b8fc1eca986f1dab9f9ec1063fe3d2cda68cd75fb5318bd1fdd025ec` |
| `sharpened_config1` | `a58fe4ba13a904592a4fe2ca3bc9927f9be132ccaa155470b1738850b8989fb9` |
| `swapped_config2` | `d3c6d69d8abde1140c92c459a27685018a76b944b545e8594c63fe9f89d705f1` |
| `alternate_config3` | `5bef40b23e2248e17331798b8375bf6d45cf18c8362542344940516db946d75d` |
| `swapped_alternate_config4` | `e6d84ef19cd113dc69f3d58d247339c7f4810378160b9618a8b3259e84667962` |
| `baseline_config1_repeat` | `039f1a257f25b47fa56cc71531bf870d1ca5ba1a2786bda19be74a1fb9502c75` |
| `baseline_config1_no_input_wait` | `d4a219d25bee5f5223470469686b1a1027eddc2c147abf77ca27aba481b759c0` |

The accepted bundle validates source safety, copied-executable/source-options/source-saves hash stability, no pre-existing BEA process, managed stop success, no remaining BEA process, focused scoped input where expected, visual proof metadata, and on-disk capture hashes.

## Rejected First Attempt

An earlier frontend/static-screen telemetry attempt under the same local work session was rejected by the new bundle checker because most scenarios had identical pre/post capture hashes. That failure is retained as useful negative evidence: static frontend frames are not enough for control telemetry.

## Boundary

This proves baseline plus four copied-control-options scenarios with scoped keyboard input/capture telemetry coverage, one distinct repeated baseline, and one wait-only no-input control. It does not prove improved control feel, analog deadzone behavior, look curves, camera response quality, physical gamepad behavior, online multiplayer, active P3/P4 original-binary gameplay, deterministic sync, gameplay parity, rebuild parity, or no-noticeable-difference parity.

The no-input control also recorded frame changes. That is expected for live level-850 rendering and is why this slice does not treat frame-hash delta as control causality or improved-feel evidence.

## Validation

- `py -3 -m py_compile tools\winui_control_input_delta_artifact_check.py tools\winui_control_feel_telemetry_bundle_check.py tools\winui_control_feel_telemetry_bundle_check_test.py` - passed.
- `py -3 tools\winui_control_input_delta_artifact_check.py --self-test` - passed.
- `py -3 tools\winui_control_feel_telemetry_bundle_check.py --self-test` - passed.
- `py -3 tools\winui_control_feel_telemetry_bundle_check_test.py` - passed, 2/2.
- Accepted live bundle validation command above - passed.

Next controls proof should add state-level or CDB-backed timing/causality before any default-visible deadzone/look-curve/control-feel byte patch is designed. Next online proof remains separate: second-host/private-LAN command-source proof or same-workstation N-slot telemetry with P3/P4 rejection timing, without claiming active P3/P4 gameplay.
