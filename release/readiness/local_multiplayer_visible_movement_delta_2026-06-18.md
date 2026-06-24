# Local Multiplayer Visible Movement-Delta Readiness Note

Status: repeated copied-profile config-2 and config-1 Movement/Forward visible movement-delta proof
Date: 2026-06-18
Scope: `local-multiplayer-visible-movement-delta`

This note records repeated visible movement-delta proof for copied-profile local multiplayer level 850 under controller configurations 2 and 1. There was no Ghidra mutation, no installed-game mutation, no executable-byte change to the installed game, no source save/options mutation, and no public/private asset bundling. Runtime proof used app-owned copied profiles and ignored local evidence only.

Accepted artifacts:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-visible-movement-delta-config2-20260618-focus1` | PID `50408`; P0/P1 `047e1090`/`047f8890`; Q/P0 controller/BattleEngine/WalkerPart `047e10f0`/`07c8af10`/`0475bd40`; E/P1 controller/BattleEngine/WalkerPart `047f88f0`/`07ca9560`/`047c3b70`. Q top-half target visual delta `0.2922366224612816` exceeded adjacent no-input baseline `0.03697950477603636` and opposite-half delta `0.09968010901699927`. E bottom-half target visual delta `0.3934890059127864` exceeded adjacent no-input baseline `0.12216486511456023` and opposite-half delta `0.07328085875915794`. |
| `local-multiplayer-visible-movement-delta-config2-20260618-focus2` | Distinct PID/runtime identity `9900`; P0/P1 `048d0090`/`048e7890`; Q/P0 controller/BattleEngine/WalkerPart `048d00f0`/`07d79f10`/`0484ad40`; E/P1 controller/BattleEngine/WalkerPart `048e78f0`/`07d98560`/`048b2b70`. Q top-half target visual delta `0.2998817583232867` exceeded adjacent no-input baseline `0.014432439951775943` and opposite-half delta `0.11169623059866962`. E bottom-half target visual delta `0.36461220436068` exceeded adjacent no-input baseline `0.04182834441980784` and opposite-half delta `0.05333627005471576`. |

Negative control:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-visible-movement-negative-control-config2-20260618-wait-only` | Same safe-copy level-850/config-2 launch, CDB observer, and interleaved capture schedule, but all four input windows were `wait:1200`. The basic source-safety/visual checker passed with PID `54584`, `captureCount=6`, and `foregroundCaptureCount=6`; the visible movement-delta checker rejected it with `input window 2 does not contain expected Q sequence`. |

Accepted config-1 artifacts:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-visible-movement-delta-config1-20260618-focus2` | PID `32128`; P0/P1 `0486b090`/`04882890`; Q/P0 controller/BattleEngine/WalkerPart `0486b0f0`/`07d19f10`/`047e5d40`; E/P1 controller/BattleEngine/WalkerPart `048828f0`/`07d38560`/`0484db70`. Q top-half target visual delta `0.3181396642863767` exceeded adjacent no-input baseline `0.04763864416210702` and opposite-half delta `0.10930570953436806`. E bottom-half target visual delta `0.49782889874353287` exceeded adjacent no-input baseline `0.03701265705838876` and opposite-half delta `0.18834044329036445`. |
| `local-multiplayer-visible-movement-delta-config1-20260618-focus3` | Distinct PID/runtime identity `51476`; P0/P1 `04790090`/`047a7890`; Q/P0 controller/BattleEngine/WalkerPart `047900f0`/`07c2cf10`/`0470ad40`; E/P1 controller/BattleEngine/WalkerPart `047a78f0`/`07c4b560`/`04772b70`. Q top-half target visual delta `0.333980571269591` exceeded adjacent no-input baseline `0.037141797273486044` and opposite-half delta `0.11296078159645233`. E bottom-half target visual delta `0.5043768477457502` exceeded adjacent no-input baseline `0.04488289911308204` and opposite-half delta `0.19122113512009645`. |

Config-1 diagnostic rejection:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-visible-movement-delta-config1-20260618-focus1` | Source-safety, exact-PID input-state, and movement-state delta checks passed, but the strict visible movement-delta gate rejected Q/P0 because target visual delta `0.29225401094315123` did not exceed adjacent no-input baseline `0.7775433552814616`. This remains a useful visible-baseline-noise diagnostic, not accepted visible movement proof. |

Validation:

```powershell
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_replayability_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-negative-control-config2-20260618-wait-only\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-negative-control-config2-20260618-wait-only\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 1
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus3\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 1
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus3\live-safe-copy-runtime-smoke.json --min-capture-count 6 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus3\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus3\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_visible_movement_replayability_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus2\live-safe-copy-runtime-smoke.json subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config1-20260618-focus3\live-safe-copy-runtime-smoke.json --min-capture-count 5 --min-render-samples 2 --expected-controller-configuration 1 --expected-qe-proof-lever input-isolation-forward-qe
npm run test:winui-safe-copy-local-multiplayer-visible-movement-delta
npm run test:winui-safe-copy-local-multiplayer-visible-movement-replayability
```

Readiness finding:

- The live smoke helper now supports `--capture-after-each-input-sequence` plus bounded after-input capture delay, allowing adjacent no-input/input visual windows instead of only pre/post-batch screenshots.
- The checker parses PNG pixels with the standard library, verifies capture file size/SHA-256, requires foreground or occlusion-free capture metadata, requires exact-PID movement-state proof on the same artifact, and compares the target split-screen half against both adjacent no-input baseline and opposite-half target-window deltas.
- Self-tests cover accepted fixture, collapsed Q target, collapsed E target, wrong-half Q target, wrong-half E target, and missing after-input capture.
- The replayability checker accepts the config-2 focus1/focus2 pair and the config-1 focus2/focus3 pair with role invariant `Q->P0/inputDevice0/top split half; E->P1/inputDevice1/bottom split half`, while requiring distinct artifact paths, process IDs, CDB logs, and runtime player/controller/BattleEngine/WalkerPart tuples.
- The wait-only live negative control proves the gate rejects a same-schedule visual capture run that lacks the expected Q/E target windows.
- The config-1 focus1 rejection proves the gate can reject a source-safe, CDB-positive, movement-state-positive run when visual baseline noise exceeds the target-half movement signal.

Claim boundary: this proves repeated copied-profile Movement/Forward keyboard Q/E input has exact-PID CDB movement-state evidence plus matching target split-screen-half pixel deltas in level 850 for config 2 and config 1, with two accepted visible movement replayability pairs. It still does not prove improved control feel, gamepad coverage, all controller configurations, online networking, deterministic sync, exact full layout, rebuild parity, or no-noticeable-difference parity.
