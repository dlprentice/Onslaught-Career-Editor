# Original-Binary Multiplayer Feasibility

Status: research only; not a player feature.
Last updated: 2026-10-21 (header completed; the copied-game launcher was the retired WinUI app's)
Summary: why Host/Join stays hidden: the evidence covers only local, same-workstation experiments, and the four
conditions that must exist before online multiplayer is offered.
Evidence: SOURCE — summarises the local multiplayer static and runtime contract linked below; no distinct-endpoint
runtime evidence exists.

The retired WinUI toolkit prepared and launched copied-game profiles; no current
surface does. Current evidence documents bounded local/same-workstation experiments. The canonical technical
summary is
[`local-multiplayer-static-runtime-contract.md`](../reverse-engineering/binary-analysis/local-multiplayer-static-runtime-contract.md).

That evidence does not establish distinct-host LAN play, public matchmaking,
native BEA netcode, deterministic synchronization, rollback, anti-cheat, active
P3/P4 gameplay, or a secure distributable session helper. Loopback, fixtures,
same-process tests, and same-workstation process separation are not substitutes
for distinct-endpoint runtime causality.

Host/Join must remain hidden or disabled until all of the following exist:

1. a real distinct-endpoint command source;
2. source-bound runtime causality in the copied game;
3. explicit identity, authorization, cleanup, and failure behavior;
4. a supported user workflow with focused security and data-loss tests.

Do not advertise online multiplayer before those conditions are met.
