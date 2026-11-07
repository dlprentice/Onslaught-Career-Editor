# Original Retail Binary: Online Multiplayer Feasibility

Status: research only for the original retail PC binary; not a player feature.
Last updated: 2026-11-06 (evidence grade, terms and the CE README's status corrected)
Summary: the conditions for offering Host/Join through the original binary, and how that research differs from Onslaught CE.
Evidence: SOURCE — references/Onslaught/game.cpp:4014 at the pinned c3d8ac4 (the current-level multiplayer predicate, levels 850 to 899); MEASURED — retail static anchors and the bounded copied-target runs recorded in onslaught-preservation's local multiplayer contract; distinct-host online play is not established by that evidence.

This research note concerns a possible workflow around copies of the original retail PC executable; PROGRAM.md treats
it as a separate historical route, not a statement that Onslaught CE already has online play. The retired WinUI app
(its core library, AppCore) prepared and launched copied-game profiles; the current companion does not. The current
technical summary is in
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation/blob/main/platforms/local-multiplayer-static-runtime-contract.md).
The `reverse-engineering/` copy in this repository is frozen reference material.

The original-binary evidence covers bounded local, same-workstation experiments. It does not establish distinct-host
LAN play, public matchmaking, native BEA netcode, deterministic synchronization, rollback, anti-cheat, active gameplay
by a third or fourth player, or a secure distributable session helper. Loopback, fixtures, same-process tests and same-workstation process
separation do not establish distinct-host runtime behavior.

Host/Join for the original binary must remain hidden or disabled until all of the following exist:

1. A real command source on a separate network endpoint: another host, not loopback or another process on the same workstation.
2. Observed runtime cause and effect in the copied game, tied to a named source location.
3. Explicit identity, authorization, cleanup and failure behavior.
4. A supported user workflow with focused security and data-loss tests.

Do not advertise original-binary online multiplayer before those conditions are met.

## Separate Onslaught CE work

Onslaught CE is a separate native-source port. Its experimental multiplayer work is not yet demonstrated as
player-ready Internet, cross-platform or campaign co-op. This original-binary research does not prohibit CE from
showing clearly disabled or coming-soon menu entries; such entries must not claim to start an unfinished feature.
Local split-screen, synthetic fixtures, loopback and Wine runs do not by themselves establish player-ready online play.

The [CE README](https://github.com/dlprentice/onslaught-ce/blob/main/README.md) on main follows the source branch and
can describe work that is not in the latest download; the README packaged with a download and its release notes
describe the installed version. For Internet multiplayer, its line "Planned, not in this version yet" is the
player-facing statement. The project's [goal](../GOAL.md) and [program](../PROGRAM.md) cover the broader CE and
multiplayer direction.
