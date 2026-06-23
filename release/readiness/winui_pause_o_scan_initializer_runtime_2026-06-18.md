# WinUI Pause O-Scan Initializer Runtime Proof

Status: accepted bounded copied-runtime CDB proof
Date: 2026-06-18

This note records the accepted runtime boundary for `pause_o_scan_initializer_experiment`.

## Accepted Evidence

The accepted local run is stored only in private ignored evidence. The public-safe summary is that it launched an app-owned copied profile from the clean backup specimen, applied `resolution_gate`, `force_windowed`, `free_camera_aurore_gate_bypass`, and `pause_o_scan_initializer_experiment`, attached CDB to the exact managed copied `BEA.exe` PID, sent focused input only, captured nine bounded target-window frames, stopped the managed process, and left the installed game, clean backup executable, source `defaultoptions.bea`, source saves, and Ghidra database unchanged.

The focused checker passed in strict positive mode:

```powershell
py -3 tools\winui_pause_o_scan_initializer_runtime_artifact_check.py <private-runtime-artifact.json> --require-positive
```

Accepted checker summary:

| Field | Value |
| --- | --- |
| Copied patch byte | `0x005144CD == 0x18` |
| Live pause row | row `34`, `entryId=56`, `slot0 inputCode=0`, `pushType=8`, `keyArg=24` (`0x18`) |
| Table classification | `runtime-table-o-pause-slot-present` |
| O input classification | `ordered-o-window-pause-and-unpause-observed` |
| Exact PID match | CDB target PID matched the launched copied `BEA.exe` PID |
| Safe-copy path binding | CDB log referenced the exact copied `BEA.exe` path from the live-smoke artifact |
| First O window | ordered O-key query, `CController__SendButtonAction` button `56`, `CControllableCamera` button `56`, and `CGame__Pause` count `1` |
| Second O window | ordered O-key query, `CController__SendButtonAction` button `56`, `CControllableCamera` button `56`, and `CGame__UnPause` count `1` |
| Visual captures | `9` |

## Boundary

This promotes the row beyond byte-only: in this bounded copied-profile free-camera context, the patched initializer byte produced a live `BUTTON_PAUSE` row for scan `0x18`, and the CDB log contains ordered same-window evidence for `O` query, `BUTTON_PAUSE` dispatch, and one pause/unpause pair.

## Follow-Up Level-100 Diagnostic

A later level-100 normal-gameplay diagnostic launched a clean-backup-derived copied game with only `resolution_gate`, `force_windowed`, and `pause_o_scan_initializer_experiment`. It attached CDB to the exact managed copied `BEA.exe` PID, sent two scoped `O` taps, captured six bounded target-window frames, stopped the managed process, and left the installed game, clean backup executable, source `defaultoptions.bea`, and source saves unchanged.

The strict positive checker rejected this diagnostic in `--require-positive` mode. Non-strict evidence still recorded copied byte `0x18`, live row `34` keyArg `0x18`, ordered first-window `O` query, `BUTTON_PAUSE` dispatch, `CGame__Pause`, and pause-menu init. The second `O` window observed `O` and button `56` dispatch but did not observe `CGame__UnPause`. This counts as a launch/capture/stop diagnostic and pause-only reachability evidence, not accepted normal-gameplay pause/unpause proof.

## Follow-Up Normal-Gameplay O/Enter Proof

A 2026-06-19 level-100 normal-gameplay follow-up launched a clean-backup-derived copied game with only `resolution_gate`, `force_windowed`, and `pause_o_scan_initializer_experiment`. It attached CDB to the exact managed copied `BEA.exe` PID, sent scoped `O`, then scoped `ENTER`, captured five bounded target-window frames, stopped the managed process, and left the installed game, clean backup executable, source `defaultoptions.bea`, and source saves unchanged.

The focused checker now has a separate normal-gameplay gate:

```powershell
py -3 tools\winui_pause_o_scan_initializer_runtime_artifact_check.py <private-runtime-artifact.json> --require-normal-gameplay-positive
```

Accepted normal-gameplay checker summary:

| Field | Value |
| --- | --- |
| Patch set | exactly `resolution_gate`, `force_windowed`, `pause_o_scan_initializer_experiment` |
| Copied patch byte | `0x005144CD == 0x18` |
| Live pause row | row `34`, `entryId=56`, `slot0 inputCode=0`, `pushType=8`, `keyArg=24` (`0x18`) |
| Level | copied runtime launched with `-level 100` |
| O window | ordered `O` query, `BUTTON_PAUSE` dispatch, `CGame__Pause`, and `PauseMenuInit`; free-camera flags were `0/0`; no camera receive row |
| Resume window | `PauseMenuResumePersist` and `CGame__UnPause`; free-camera flags were `0/0`; no camera receive row |
| Visual captures | `5` |

This proves one bounded normal-gameplay copied-runtime path: the patch makes `O` open the pause menu on level 100, and `ENTER` resumes from that pause menu. It still does not prove second-`O` normal-gameplay unpause, all pause/menu contexts, gameplay safety, control feel, all controller/profile combinations, long-session behavior, render parity, online/netcode, rebuild parity, or no-noticeable-difference parity. The row remains experimental, custom-only, and copied-profile-only.

This is not a Ghidra correction. The runtime result is consistent with the existing static contract: the retail initializer row used keyArg `1`; this copied-executable patch changes that initializer byte to keyArg `0x18`.

## Validation

```powershell
py -3 tools\winui_pause_o_scan_initializer_runtime_artifact_check.py --self-test
npm run test:winui-pause-o-scan-initializer-runtime-artifact
py -3 tools\winui_safe_copy_live_runtime_smoke_test.py
```
