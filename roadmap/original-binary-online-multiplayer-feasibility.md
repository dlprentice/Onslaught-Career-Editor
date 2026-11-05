# Original Retail Binary: Online Multiplayer Feasibility

Status: research only for the original retail PC binary; not a player feature.
Last updated: 2026-11-05 (evidence grade and wording follow the preservation contract; the requirements are linked, not restated; earlier: scope, evidence and documentation ownership clarified)
Summary: the conditions for offering Host/Join through the original binary, and how that research differs from Onslaught CE.
Evidence: INFERRED — reasoned from the onslaught-preservation local multiplayer evidence boundary (controlled copied-target observations and same-host helpers; no distinct-host run); distinct-host online play is not established by that evidence.

This page concerns a possible workflow around copies of the original retail PC executable. The retired WinUI toolkit
prepared and launched copied-install safe launch profiles; the current companion does not. The current technical summary is in
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation/blob/main/platforms/local-multiplayer-static-runtime-contract.md).
The `reverse-engineering/` copy in this repository is frozen reference material.

The original-binary evidence covers a bounded local split-screen path and controlled copied-target observations with same-host helpers. It does not establish distinct-host
LAN play, public matchmaking, native BEA netcode, deterministic synchronization, rollback, anti-cheat, active gameplay
by a third or fourth player, or a secure distributable session helper. Loopback, fixtures, same-process tests and same-host process
separation do not establish distinct-host runtime behavior.

Host/Join for the original binary stays hidden or disabled until the contract's
[requirements for any online claim](https://github.com/dlprentice/onslaught-preservation/blob/main/platforms/local-multiplayer-static-runtime-contract.md#requirements-for-any-online-claim)
are met. Do not advertise original-binary online multiplayer before then.

## Separate Onslaught CE work

Onslaught CE is a separate native-source port. Its experimental multiplayer work is not yet demonstrated as
player-ready Internet, cross-platform or campaign co-op. This original-binary research does not prohibit CE from
showing clearly disabled or coming-soon menu entries; such entries must not claim to start an unfinished feature.
Local split-screen, synthetic fixtures, loopback and Wine runs do not by themselves establish player-ready online play.

The [CE README](https://github.com/dlprentice/onslaught-ce/blob/main/README.md) describes the current player-facing release.
The project's [goal](../GOAL.md) and [program](../PROGRAM.md) cover the broader CE and multiplayer direction.
