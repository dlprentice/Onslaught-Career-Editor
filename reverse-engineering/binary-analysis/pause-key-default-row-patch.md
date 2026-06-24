# Pause Key Default Row Patch

Status: accepted bounded copied-runtime CDB ordered-window proof for one pause/unpause context
Date: 2026-06-18

This note records the bounded evidence for `pause_o_scan_initializer_experiment`, an experimental Patch Bench row that changes the retail default single-binding initializer for `BUTTON_PAUSE` in a copied `BEA.exe`.

## Evidence

| Item | Value |
| --- | --- |
| Retail function | `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable` |
| Runtime table row | `DAT_00889718`, button `0x38` (`BUTTON_PAUSE`) |
| Patch VA | `0x005144CD` |
| File offset | `0x1144CD` |
| Original byte | `01` |
| Patched byte | `18` |
| Patch id | `pause_o_scan_initializer_experiment` |

Wave851 static read-back decompile records the retail pause default row as:

```c
OptionsEntries__InitSingleBindingEntry(&DAT_00889718,0,0x38,8,1,0);
```

The local clean Steam specimen bytes around `0x005144CA` read back as:

```text
6A 00 6A 01 6A 08 6A 38 6A 00 B9 18 97 88 00 E8 ...
```

The patch changes only the `6A 01` immediate payload byte for the pause row candidate from `0x01` to `0x18`. `0x18` is the DirectInput scan-code candidate for `O`, matching Stuart source's `O -> BUTTON_PAUSE` mapping hypothesis. The baseline retail runtime diagnostic did not show that mapping active: the accepted controller-table artifact found one pause row with `keyArg=1` and no `O` key argument (`0x18` or `0x4f`).

## Runtime Proof

The follow-up copied-runtime proof in `release/readiness/winui_pause_o_scan_initializer_runtime_2026-06-18.md` accepted the patch in one bounded context. The app-owned copied profile was launched from the clean backup specimen with `resolution_gate`, `force_windowed`, `free_camera_aurore_gate_bypass`, and `pause_o_scan_initializer_experiment`; exact-PID CDB observed:

- copied byte `0x005144CD == 0x18`,
- live mapping row `34` as `entryId=56`, `pushType=8`, `keyArg=0x18`,
- scoped `O` input querying key `0x18`,
- ordered same-window `CController__SendButtonAction` dispatching button `56`,
- `CControllableCamera` receiving button `56`,
- first `O` window continuing to `CGame__Pause`,
- second `O` window continuing to `CGame__UnPause`.

A later level-100 normal-gameplay diagnostic used only `resolution_gate`, `force_windowed`, and `pause_o_scan_initializer_experiment` on a clean-backup-derived copied game. It re-observed copied byte `0x18`, live row `34` keyArg `0x18`, ordered first-window `O` query, `BUTTON_PAUSE` dispatch, `CGame__Pause`, and pause-menu init. It did not observe `CGame__UnPause` in the second `O` window and was rejected by the original strict positive checker, so it is pause-only reachability evidence rather than second-`O` normal-gameplay unpause proof.

A 2026-06-19 follow-up used the same exact three-patch level-100 setup and a stricter normal-gameplay checker. The first window sent `O` and observed ordered `O` query, `BUTTON_PAUSE` dispatch, `CGame__Pause`, and `PauseMenuInit` with free-camera flags `0/0` and no camera receive row. The second window sent `ENTER` and observed `PauseMenuResumePersist` plus `CGame__UnPause` with free-camera flags `0/0` and no camera receive row. This is accepted proof for `O` opening the pause menu and `ENTER` resuming from it in one copied-runtime level-100 context.

## Boundary

This is not a Ghidra correction. Current static names/comments still match the bounded evidence: the retail binary initializes a pause row with keyArg `1`, and the copied-executable patch changes that initializer byte so the accepted proof context has ordered same-window `O` query, `BUTTON_PAUSE` dispatch, and pause/unpause evidence.

This patch does not edit `defaultoptions.bea`, save files, persisted options entries, controller configuration rows, the installed Steam executable, or the original clean backup. The persisted `defaultoptions.bea` options-entry model currently covers the 16 configurable UI rows and does not include `BUTTON_PAUSE` (`0x38`), so pause should not be forced into that fixed persisted-options lane.

The accepted proof is still narrow. It does not prove a full debugger call-chain, second-`O` normal-gameplay unpause, broad pause/menu safety, gameplay safety, control feel, all controller/profile combinations, long-session behavior, render parity, online/netcode, rebuild parity, or no-noticeable-difference parity. The row remains experimental, custom-only, copied-profile-only, and outside all default presets.
