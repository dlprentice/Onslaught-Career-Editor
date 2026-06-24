# Local Multiplayer Input-State Replayability Readiness Note

Status: repeated copied-profile config-2/config-3/config-4 Movement/Forward input-to-state-store proof
Date: 2026-06-18
Scope: `local-multiplayer-input-state-replayability`

This note records repeated state-store proof for the copied-profile local-multiplayer level-850 lane, now covering controller configurations `2`, `3`, and `4` through copied `defaultoptions.bea` keyboard `Q/E` Movement/Forward materialization. There was no Ghidra mutation, no installed-game mutation, no executable-byte change to the installed game, no source save/options mutation, and no public/private asset bundling. Runtime proof used app-owned copied profiles and ignored local evidence only.

Accepted artifacts:

| Artifact | Evidence |
| --- | --- |
| `local-multiplayer-input-state-delta-config2-mode-specific-20260618-focus2` | `Q` routed to P0/controller `04a470f0`/BattleEngine `07f05f10`/WalkerPart `049c1d40`; `E` routed to P1/controller `04a5e8f0`/BattleEngine `07f24560`/WalkerPart `04a29b70`; both reached nonzero WalkerPart Forward stores (`bf800000`) under `state260=00000002`. |
| `local-multiplayer-input-state-delta-config2-ready-strict-replay-20260618-focus10` | Repeated the same role invariant under a distinct process, CDB log, player/controller tuple, BattleEngine tuple, and WalkerPart tuple: `Q` to P0/controller `0474b0f0`/BattleEngine `07bf0f10`/WalkerPart `046c5d40`, `E` to P1/controller `047628f0`/BattleEngine `07c0f560`/WalkerPart `0472db70`, with 26 receive rows and 26 nonzero WalkerPart Forward store rows for each target input window. |
| `local-multiplayer-visible-movement-delta-config3-20260618-focus1` | Config-3 copied-options input-isolation run: PID `58068`, P0/P1 `0485b590`/`04872d90`; `Q` to P0/controller `0485b5f0`/BattleEngine `07d16f10`/WalkerPart `047d6160` with `25` receive/store rows; `E` to P1/controller `04872df0`/BattleEngine `07d35560`/WalkerPart `0483e070` with `18` receive/store rows. Movement-state delta passed, but visible movement was rejected as a high-baseline diagnostic. |
| `local-multiplayer-visible-movement-delta-config3-20260618-focus2` | Repeated config-3 input-state handoff: PID `35676`, P0/P1 `04732590`/`04749d90`; `Q` to P0/controller `047325f0`/BattleEngine `07be1f10`/WalkerPart `046ad160` with `25` receive rows and `7` store rows; `E` to P1/controller `04749df0`/BattleEngine `07c00560`/WalkerPart `04715070` with `26` receive/store rows. Movement/visible checks rejected the artifact because wait window 1 had no render movement samples. |
| `local-multiplayer-input-state-delta-config4-20260618-focus1` | Config-4 copied-options input-isolation run: PID `44868`, P0/P1 `046f30b0`/`0470a8b0`; `Q` to P0/controller `046f3110`/BattleEngine `07b99f10`/WalkerPart `0466dc80` with `26` receive/store rows; `E` to P1/controller `0470a910`/BattleEngine `07bb8560`/WalkerPart `046d5b90` with `25` receive/store rows. Movement-state delta passed with Q baseline/target render samples `31`/`191` and E `212`/`184`; visible movement was rejected as a high-baseline diagnostic. |
| `local-multiplayer-input-state-delta-config4-20260618-focus2` | Repeated config-4 input-state handoff: PID `32664`, P0/P1 `046ad0b0`/`046c48b0`; `Q` to P0/controller `046ad110`/BattleEngine `07b50f10`/WalkerPart `04627c80` with `25` receive/store rows; `E` to P1/controller `046c4910`/BattleEngine `07b6f560`/WalkerPart `0468fb90` with `25` receive/store rows. Movement-state delta passed with Q baseline/target render samples `23`/`184` and E `205`/`170`; visible movement was rejected as a high-baseline diagnostic. |

Validation:

```powershell
py -3 tools\winui_safe_copy_local_multiplayer_artifact_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config2-ready-strict-replay-20260618-focus10\live-safe-copy-runtime-smoke.json --min-capture-count 6 --require-visual --expected-controller-configuration 2
py -3 tools\winui_safe_copy_local_multiplayer_input_state_delta_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config2-ready-strict-replay-20260618-focus10\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_input_state_replayability_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config2-mode-specific-20260618-focus2\live-safe-copy-runtime-smoke.json subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config2-ready-strict-replay-20260618-focus10\live-safe-copy-runtime-smoke.json --min-capture-count 6
py -3 tools\winui_safe_copy_local_multiplayer_input_state_replayability_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config3-20260618-focus1\live-safe-copy-runtime-smoke.json subagents\winui-safe-copy-live-runtime\local-multiplayer-visible-movement-delta-config3-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 5 --expected-controller-configuration 3 --expected-qe-proof-lever input-isolation-forward-qe
py -3 tools\winui_safe_copy_local_multiplayer_input_state_replayability_check.py subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config4-20260618-focus1\live-safe-copy-runtime-smoke.json subagents\winui-safe-copy-live-runtime\local-multiplayer-input-state-delta-config4-20260618-focus2\live-safe-copy-runtime-smoke.json --min-capture-count 5 --expected-controller-configuration 4 --expected-qe-proof-lever input-isolation-forward-qe
npm run test:winui-safe-copy-local-multiplayer-input-state-replayability
```

Readiness finding:

- The earlier failed focus7/focus8 diagnostics narrowed the instability to input sent before gameplay-ready visual state. Focus7's pre-input frame was still the loading screen and did not produce a P0 state store despite P0 button-31 receive rows; focus8 reversed input order and showed the second input window could store while the first did not.
- Focus9 was a P0-only diagnostic after a gameplay-ready pre-input frame and produced 25 P0 receive rows, 25 Forward entries, and 26 nonzero Forward stores.
- Focus10 repeated the full strict Q/E state proof after gameplay-ready pre-input state, with clean wait windows and accepted Q/P0 plus E/P1 state-store rows.
- Config-3 focus1/focus2 and config-4 focus1/focus2 broaden copied-options keyboard Q/E input-to-state replayability beyond config 2. Config 3 focus1 and both config 4 artifacts also passed the movement-state delta checker. Config 3 focus2 remains a render-window readiness diagnostic for movement/visible proof.
- Strict visible movement-delta was not accepted for config 3 or config 4 in this slice. Config 3 focus1 and config 4 focus1/focus2 failed because Q/P0 target visual delta did not exceed the adjacent no-input baseline; config 3 focus2 failed because wait window 1 had no render movement samples.
- This is still keyboard/copy-options proof. The harness did not synthesize or observe physical DirectInput/gamepad input; that remains a separate next proof lane.

Claim boundary: this proves repeated config-2, config-3, and config-4 Movement/Forward keyboard input-to-WalkerPart state-store handoff for copied local-multiplayer level 850 across distinct instrumented runs. It still does not prove visible movement causality for config 3/4, improved control feel, physical gamepad coverage, all controller configurations at the visible layer, online networking, deterministic sync, exact full layout, or rebuild parity.
