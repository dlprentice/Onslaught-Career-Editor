# Local Multiplayer Movement-State Delta Readiness Note

Status: repeated copied-profile config-2 Movement/Forward movement-state delta proof
Date: 2026-06-18
Scope: `local-multiplayer-movement-state-delta`

This note records the first repeated movement-state delta proof for copied-profile local multiplayer level 850. There was no Ghidra mutation, no installed-game mutation, no executable-byte change to the installed game, no source save/options mutation, and no public/private asset bundling. Runtime proof used app-owned copied profiles and ignored local evidence only.

Accepted artifacts:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-movement-state-delta-config2-20260618-focus1` | `Q` routed to P0/controller `047230f0`/BattleEngine `07bd0f10`/WalkerPart `0469dd40` with `25` receive/store rows, `220` no-input baseline render samples, and `192` target render samples. `E` routed to P1/controller `0473a8f0`/BattleEngine `07bef560`/WalkerPart `04705b70` with `26` receive/store rows, `191` no-input baseline render samples, and `177` target render samples. |
| `local-multiplayer-movement-state-delta-config2-20260618-focus2` | Repeated the same role invariant under a distinct PID/runtime identity. `Q` routed to P0/controller `045a10f0`/BattleEngine `07a58f10`/WalkerPart `0451bd40` with `26` receive/store rows, `199` no-input baseline render samples, and `163` target render samples. `E` routed to P1/controller `045b88f0`/BattleEngine `07a77560`/WalkerPart `04583b70` with `26` receive/store rows, `178` no-input baseline render samples, and `173` target render samples. |

Validation:

```powershell
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus1\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_movement_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-movement-state-delta-config2-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 6 --min-render-samples 2
npm run test:winui-safe-copy-local-multiplayer-movement-state-delta
```

Readiness finding:

- The strengthened CDB observer now samples `CGame__RenderMovement` during no-input and input windows.
- The checker requires clean no-input baselines, exact-PID source safety, foreground visual capture, config-2 Movement/Forward Q/E binding materialization, P0/P1 state-store rows, and render movement-state deltas in the target input windows.
- This upgrades the local-multiplayer config-2 proof from repeated input-to-state-store handoff to repeated input-correlated movement-state delta.

Claim boundary: this proves repeated copied-profile config-2 Movement/Forward keyboard input reached P0/P1 movement-state changes in exact-PID CDB evidence. It still does not prove visible movement causality, improved control feel, gamepad coverage, all controller configurations, online networking, deterministic sync, exact full layout, rebuild parity, or no-noticeable-difference parity.
