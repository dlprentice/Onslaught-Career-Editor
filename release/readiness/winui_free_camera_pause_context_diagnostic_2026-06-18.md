# WinUI Free-Camera Pause-Context Diagnostic Note

Status: rejected copied-runtime pause reachability diagnostics; key-census shows O scancode latch without O query
Date: 2026-06-18
Scope: `free_camera_keyboard_forward_q_hook` pause-context follow-up

This slice tested whether the existing copied-runtime free-camera Q-forward proof could also validate the source-indicated `O -> BUTTON_PAUSE` path while free camera is active. The diagnostics used only app-owned copied `BEA.exe` instances under ignored runtime evidence roots. They did not mutate the installed Steam game folder, the original `BEA.exe`, source `defaultoptions.bea`, source `savegames`, or the Ghidra database.

## Evidence

| Evidence Class | Result |
| --- | --- |
| Private ignored copied-runtime diagnostic artifact | Applied `resolution_gate`, `force_windowed`, `free_camera_aurore_gate_bypass`, `free_camera_keyboard_forward_q_hook`, and hidden `free_camera_keyboard_forward_q_cave` to the copied executable only; launched copied level `100`; sent scoped `Q`, `F`, active `Q`, `O`, active `Q`, `O`, `F`, and post-toggle `Q`; captured ten bounded target-window frames; stopped the managed copied process; left installed/source material unchanged. |
| Held-`O` upstream-key diagnostic artifact | Repeated the copied level `100` flow with `down:O,wait:1000,up:O` windows, `11` visual-proof captures, exact-PID CDB attachment, `8/8` focused input windows, `16` scan-code key events, and `0` background/PostMessage events. Adjacent `Q` and `F` windows produced debugger output; both held-`O` byte windows produced `0` bytes of CDB output. |
| `tools/runtime-probes/free-camera-pause-context-observer.cdb.txt` | Exact-PID CDB observer for the free-camera toggle path, pause/unpause entrypoints, pause-menu/game-interface dispatch sentinels, controller dispatch, hook/cave bytes, `CControllableCamera`, camera interpolation deltas, and upstream `O`-key rows at `CPCController__GetKeyOnce`, `PlatformInput__GetKeyOnceCore`, and `PlatformInput__ConsumeKeyOnce`. |
| `tools/winui_safe_copy_free_camera_pause_context_artifact_check.py --mode forward` | Correctly rejects the held-`O` diagnostic artifact before the old pause-dispatch checks because neither focused `O` input window queried `CPCController__GetKeyOnce` for key `0x4f`. |
| Key-census diagnostic artifact | Repeated the copied level `100` flow with `F`, held `O`, held `Q`, and `F` windows, `6` visual-proof captures, exact-PID CDB attachment, `4/4` focused input windows, `8` scan-code key events, and `0` background/PostMessage events. The held-`O` window produced CDB polling output and `onceScanO=01`, but `oKeyQueryCount=0`, `pauseButtonDispatched=false`, `CGame__Pause=0`, and `CGame__UnPause=0`. |
| `tools/runtime-probes/free-camera-key-census-observer.cdb.txt` | Exact-PID CDB observer for unfiltered key polling/dispatch census around `CPCController__GetKeyOnce`, `PlatformInput__GetKeyOnceCore`, `PlatformInput__ConsumeKeyOnce`, `CController__SendButtonAction`, `CControllableCamera`, `CGame__Pause`, and `CGame__UnPause`. |
| `tools/winui_safe_copy_free_camera_key_census_artifact_check.py` | Accepts the key-census artifact as a diagnostic and classifies the held-`O` window as `o-key-state-latched-without-o-query`. |
| Controller mapping-table diagnostic artifact | Follow-up copied-runtime CDB table dump decoded `47` rows from the active retail `CController__DoMappings` row window at `0x008892dc`, found one `BUTTON_PAUSE` row at index `34`, and classified it as `runtime-table-pause-row-present-without-o-slot`. |
| `tools/winui_safe_copy_controller_mapping_table_artifact_check.py` | Accepts the mapping-table artifact as bounded diagnostic evidence only when source hashes are unchanged, CDB cleanup is recorded, the sentinel is present, and the pause-row classification is stable. |

Diagnostic summary:

| Field | Value |
| --- | --- |
| Focused input windows | `8/8` |
| Visual captures | `10` in the first diagnostic; `11` in the held-`O` diagnostic |
| Key-census visual captures | `6` |
| Source executable/source save-options safety | unchanged |
| Active Q cave rows | `21` then `22` across the two active Q windows |
| `O` windows with `BUTTON_PAUSE` | `0/2` |
| `CGame__Pause` / `CGame__UnPause` rows | `0 / 0` |
| Held-`O` windows querying `CPCController__GetKeyOnce` for `0x4f` | `0/2` |
| Held-`O` windows querying `PlatformInput__GetKeyOnceCore` for `0x4f` | `0/2` |
| Held-`O` CDB byte windows | `0` bytes then `0` bytes |
| Key-census held-`O` classification | `o-key-state-latched-without-o-query` |
| Key-census held-`O` `onceVkO` / `onceScanO` | `00 / 01` |
| Key-census held-`O` O-specific key-query count | `0` |
| Key-census held-`O` sent buttons | `25`, `26`, `27`, `28`; no `56` |
| Mapping-table decoded rows / sentinel | `47 / true` |
| Mapping-table pause row | row index `34`; raw words `00000038 00000000 00000008 00000001 ffffffff 00000000 00000000 00000000`; slot0 `inputCode=0`, `pushType=8`, `keyArg=1`; slot1 disabled/sentinel-like (`inputCode=-1`, `pushType=0`, `keyArg=0`) |
| Mapping-table `O` pause slots | `0` |
| Mapping-table classification | `runtime-table-pause-row-present-without-o-slot` |

## Interpretation

The diagnostics prove the harness can safely send and isolate the `O` key attempt, and that the strict checker will reject missing upstream key-query or pause-dispatch evidence. The key-census follow-up adds the important split: the copied runtime saw an `O` scancode state latch, but the active polling/mapping path did not query the O virtual key or O scancode, did not dispatch `BUTTON_PAUSE`, and did not call pause/unpause. The diagnostics do not prove the retail copied game consumed `O` as `BUTTON_PAUSE`.

The source tree maps `O` to `BUTTON_PAUSE`, and the retail controller/key-query helper names have static Ghidra evidence. This diagnostic did not prove that the active copied-runtime mapping table queried that key. The follow-up mapping-table diagnostic explains that result: the copied runtime had a pause row, but the observed row was not bound to `O` or the O scancode. Its active slot used `keyArg=1`, while the O evidence uses `keyArg=0x18` or `0x4f`. A raw file-byte check also cannot verify the documented controller mapping table directly because the tracked runtime table address is in virtual `.data`/BSS space beyond the clean executable's raw file bytes. Future pause work should therefore treat the `O` mapping as source/static-hypothesis plus open runtime proof, not as accepted retail runtime behavior.

## Validation

```powershell
py -3 tools\winui_safe_copy_free_camera_pause_context_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_pause_context_artifact_check.py --mode forward <private ignored rejected diagnostic artifact>
py -3 tools\winui_safe_copy_free_camera_key_census_artifact_check.py --self-test
py -3 tools\winui_safe_copy_free_camera_key_census_artifact_check.py <private ignored key-census diagnostic artifact>
py -3 tools\winui_safe_copy_controller_mapping_table_artifact_check.py --self-test
py -3 tools\winui_safe_copy_controller_mapping_table_artifact_check.py <private ignored controller mapping-table diagnostic artifact>
py -3 tools\send_game_window_input_test.py
```

The focused artifact check intentionally fails on the held-`O` diagnostic artifact with `pause window did not query CPCController::GetKeyOnce for O`.

## Boundaries

- This is not an accepted pause proof.
- This does not prove `O -> BUTTON_PAUSE`, free-camera pause/unpause, pause-menu suppression, normal pause-menu behavior, gameplay safety, rendering behavior, visual parity, rebuild parity, or no-noticeable-difference parity.
- Future pause-context work should first identify why the active mapping/default-binding path ignores the observed `O` scancode state, or prove a copied-options pause binding exists before adding any pause materialization path.
- No Ghidra mutation or Ghidra backup was produced by this runtime slice.
