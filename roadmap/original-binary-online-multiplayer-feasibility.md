# Original Retail Binary: Online Multiplayer Feasibility

Status: research only for the original retail PC binary; not a player feature.
Last updated: 2026-10-30 (scope, evidence and documentation ownership clarified)
Summary: the conditions for offering Host/Join through the original binary, and how that research differs from Onslaught CE.
Evidence: SOURCE — the original game's local multiplayer contract; distinct-host online play is not established by that evidence.

This page concerns a possible workflow around copies of the original retail PC executable. The retired WinUI toolkit
prepared and launched copied-game profiles; the current companion does not. The current technical summary is in
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation/blob/main/platforms/local-multiplayer-static-runtime-contract.md).
The `reverse-engineering/` copy in this repository is frozen reference material.

The original-binary evidence covers bounded local, same-workstation experiments. It does not establish distinct-host
LAN play, public matchmaking, native BEA netcode, deterministic synchronization, rollback, anti-cheat, active gameplay
by a third or fourth player, or a secure distributable session helper. Loopback, fixtures, same-process tests and same-workstation process
separation do not establish distinct-host runtime behavior.

Host/Join for the original binary must remain hidden or disabled until all of the following exist:

1. A real distinct-endpoint command source.
2. Source-bound runtime causality in the copied game.
3. Explicit identity, authorization, cleanup and failure behavior.
4. A supported user workflow with focused security and data-loss tests.

Do not advertise original-binary online multiplayer before those conditions are met.

## Separate Onslaught CE work

Onslaught CE is a separate native-source port. Its experimental multiplayer work is not yet demonstrated as
player-ready Internet, cross-platform or campaign co-op. This original-binary research does not prohibit CE from
showing clearly disabled or coming-soon menu entries; such entries must not claim to start an unfinished feature.
Local split-screen, synthetic fixtures, loopback and Wine runs do not by themselves establish player-ready online play.

The [CE README](https://github.com/dlprentice/onslaught-ce/blob/main/README.md) describes the current player-facing release.
The project's [goal](../GOAL.md) and [program](../PROGRAM.md) cover the broader CE and multiplayer direction.
