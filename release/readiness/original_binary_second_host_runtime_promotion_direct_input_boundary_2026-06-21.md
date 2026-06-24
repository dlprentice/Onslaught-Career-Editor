# Original-Binary Second-Host Runtime Promotion Direct-Input Boundary

Status: complete proof-boundary hardening
Date: 2026-06-21

This slice normalizes the second-host runtime-promotion vocabulary before any live Host/Join proof. A future accepted runtime-promotion candidate must treat second-host client direct game input as a rejected bypass, not as successful delivery into BEA.

Machine-checkable boundary:

- `gameInputSentBySecondHostClient=true` is rejected by `tools/winui_safe_copy_online_second_host_runtime_promotion_guard.py`.
- Accepted promotion candidates must keep `gameInputSentBySecondHostClient=false`.
- Accepted promotion candidates must prove `hostHelperInputSent=true`.
- Accepted promotion candidates must prove `hostHelperInputBoundToSecondHostCommandSource=true`.
- Runtime causality and Host/Join contracts now require `rejectsSecondHostClientDirectGameInputBypass=true`.
- Runtime causality and Host/Join contracts now require `requiresHostHelperInputBoundToSecondHostCommandSource=true`.
- Runtime-causality raw artifact bodies for runtime input-window and exact-PID CDB evidence now independently require `hostHelperInputBoundToSecondHostCommandSource=true`.
- Runtime-causality raw artifact bodies for runtime input-window and exact-PID CDB evidence now independently require `gameInputSentBySecondHostClient=false`.

Validation boundary:

- No BEA launch.
- No CDB attach.
- No game input.
- No Host/Join enablement.
- No public endpoint.
- No Ghidra mutation.
- No installed/original executable mutation.

This is not player-ready online multiplayer, accepted live second-host LAN gameplay, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.
