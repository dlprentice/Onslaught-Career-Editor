# WinUI Controller Mapping Table Diagnostic

Status: accepted bounded copied-runtime diagnostic
Date: 2026-06-18
Scope: `controller-mapping-table-20260618`

This slice followed the rejected free-camera `O -> BUTTON_PAUSE` diagnostics by dumping the active retail controller mapping table from a real copied `BEA.exe` runtime. The run used only an app-owned copied game folder derived from `BEA.exe.original.backup`, applied only the base copied-profile windowed rows (`resolution_gate` and `force_windowed`), attached exact-PID CDB with observer-only commands, captured one bounded frame, stopped the managed copied process, and left the installed game, clean backup executable, source `defaultoptions.bea`, source saves, and Ghidra database unchanged.

## Evidence

| Evidence Class | Result |
| --- | --- |
| Source/static consults | Source `ControllerMaping` is a four-field internal/source struct with `O -> BUTTON_PAUSE`, but retail `CController__DoMappings` decompile scans an 8-dword live row window at `0x008892dc`; each decoded row has one button/entry id plus two runtime slots consumed as `inputCode`, `pushType`, and `keyArg`. Both Codex read-only consults recommended treating the runtime table/options path as the active question, not assuming a bad static function identity. |
| `tools/runtime-probes/controller-mapping-table-observer.cdb.txt` | Observer-only CDB script: disassembles `CController__DoMappings` / `CController__GetMappedInputValue`, dumps both adjacent views (`dd 008892d8 L90` and `dd 008892dc L220`), then continues. |
| `tools/winui_safe_copy_controller_mapping_table_artifact_check.py` | Decodes the live `0x008892dc` `CController__DoMappings` row window, verifies source-safety and CDB cleanup, requires the table sentinel, exposes slot `inputCode` / `pushType` / `keyArg`, and classifies the `BUTTON_PAUSE` row. |
| Accepted live artifact | Decoded `47` rows before sentinel. Found one `BUTTON_PAUSE` row at row index `34`, raw words `00000038 00000000 00000008 00000001 ffffffff 00000000 00000000 00000000`. Slot0 is `inputCode=0`, `pushType=8`, `keyArg=1`; slot1 is disabled/sentinel-like (`inputCode=-1`, `pushType=0`, `keyArg=0`). No `O` key argument (`0x4f` or `0x18`) slot was present for the pause row. |

Diagnostic summary:

| Field | Value |
| --- | --- |
| Decoded row count | `47` |
| Sentinel found | `true` |
| Pause row count | `1` |
| Pause row index | `34` |
| Pause row slot0 | `inputCode=0`, `pushType=8`, `keyArg=1` |
| Pause row slot1 | disabled/sentinel-like (`inputCode=-1`, `pushType=0`, `keyArg=0`) |
| O pause slots | `0` |
| Classification | `runtime-table-pause-row-present-without-o-slot` |

## Interpretation

The copied runtime did have a pause mapping row, but it was not bound to `O` in the observed row window. The observed active slot is a `KEY_ONCE`-style slot with `keyArg=1`, not `O` (`keyArg=0x18` or `0x4f`). This explains the prior F/O/Q/F key-census result: the `O` scancode could latch in the platform key table, while the active controller mapping path never queried `O` and therefore never dispatched `BUTTON_PAUSE`.

This does not indicate a bad static owner/name/signature for `CController__DoMappings`, `CPCController__GetKeyOnce`, or `PlatformInput__GetKeyOnceCore`. The live decompile/table evidence instead supports a runtime mapping/default-binding gap between Stuart's source/internal mapping and the observed Steam copied-runtime row window. It does not by itself prove defaultoptions/save persistence, other control schemes/profiles, or exact source parity.

## Validation

```powershell
py -3 tools\winui_safe_copy_controller_mapping_table_artifact_check_test.py
py -3 tools\winui_safe_copy_controller_mapping_table_artifact_check.py --self-test
py -3 tools\winui_safe_copy_controller_mapping_table_artifact_check.py <private-runtime-artifact.json>
```

## Boundaries

- This is not an accepted `O -> BUTTON_PAUSE` proof.
- This does not prove free-camera pause/unpause, pause-menu suppression, normal pause-menu behavior, control feel, gameplay safety, rendering behavior, visual parity, rebuild parity, or no-noticeable-difference parity.
- This does not prove defaultoptions/save persistence, other control schemes/profiles, or exact source parity.
- This did not mutate Ghidra and did not produce a Ghidra backup.
- Future pause-context work should trace or materialize copied-options/default binding changes before treating an `O` pause path as a product feature.
