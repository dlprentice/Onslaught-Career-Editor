# WinUI Pause O-Scan Normal-Gameplay Resume Proof

Status: accepted bounded copied-runtime CDB proof
Date: 2026-06-19

This note records the normal-gameplay follow-up for `pause_o_scan_initializer_experiment`. The private ignored runtime artifact label is `pause-o-normal-enter-resume-level100-20260619-053747`.

## Evidence

The local run launched an app-owned copied game from the clean backup specimen, applied exactly `resolution_gate`, `force_windowed`, and `pause_o_scan_initializer_experiment`, attached CDB to the exact managed copied `BEA.exe` PID, sent scoped `O`, then scoped `ENTER`, captured five bounded target-window frames, stopped the managed process, and left the installed game, clean backup executable, source `defaultoptions.bea`, source saves, and Ghidra database unchanged.

The focused checker passed:

```powershell
py -3 tools\winui_pause_o_scan_initializer_runtime_artifact_check.py <private-runtime-artifact.json> --require-normal-gameplay-positive
```

Accepted checker summary:

| Field | Value |
| --- | --- |
| Patch set | exactly `resolution_gate`, `force_windowed`, `pause_o_scan_initializer_experiment` |
| Copied patch byte | `0x005144CD == 0x18` |
| Live pause row | row `34`, `entryId=56`, `slot0 inputCode=0`, `pushType=8`, `keyArg=24` (`0x18`) |
| Table classification | `runtime-table-o-pause-slot-present` |
| Launch arguments | `-skipfmv -level 100` |
| O window | ordered `O` query, `BUTTON_PAUSE` dispatch, `CGame__Pause`, and `PauseMenuInit`; free-camera flags were `0/0`; no camera receive row |
| Resume window | `PauseMenuResumePersist` and `CGame__UnPause`; free-camera flags were `0/0`; no camera receive row |
| Visual captures | `5` |

## Boundary

This promotes the patch from the earlier level-100 pause-only diagnostic to one accepted normal-gameplay copied-runtime proof for `O` opening the pause menu and `ENTER` resuming from that pause menu. It does not prove second-`O` normal-gameplay unpause, all pause/menu contexts, gameplay safety, control feel, all controller/profile combinations, long-session behavior, render parity, online/netcode, rebuild parity, or no-noticeable-difference parity.

This is not a Ghidra correction. The runtime result is consistent with the existing static contract: the retail initializer row used keyArg `1`; this copied-executable patch changes that initializer byte to keyArg `0x18`.

## Validation

```powershell
py -3 tools\winui_pause_o_scan_initializer_runtime_artifact_check.py --self-test
npm run test:winui-pause-o-scan-initializer-runtime-artifact
```
