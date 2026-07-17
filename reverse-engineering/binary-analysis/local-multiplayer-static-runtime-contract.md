# Local multiplayer evidence boundary

Status: local split-screen path available; online multiplayer unavailable

This contract owns the distinction between the retail game's bounded local
multiplayer path and any future networked companion. It does not add netcode,
patch networking into the retail executable, or prove online play.

## Retail anchors

| Area | Bounded evidence |
| --- | --- |
| Runtime level gate | Source `game.cpp` and retail `0x004725d0 CGame__IsMultiplayer` agree on a current-level predicate of `850..899`. |
| Frontend selection | Source frontend routing selects multiplayer pages for `850..879`; that narrower menu range must not be generalized to every runtime-multiplayer level. |
| World mode | Retail `0x0050d7d0 CWorld__IsMultiplayerMode` accepts world mode `1` or `2`. The matching source body is absent, so this remains retail-static/call-site evidence. |
| Player count | The pinned source sets two players after a multiplayer world load and one otherwise. No retained evidence establishes active P3/P4 retail gameplay. |
| Controllers | Source startup assigns player 0 and player 1 controller ports, including a same-port fallback. Retail controller mapping remains a separate static anchor. |
| Views | Source defines two viewpoints and a two-player split-screen render path. Retail render anchors include `CGame__Render`, `CEngine__SetNumViewpoints`, and `CEngine__SetViewpoint`. |
| Outcome flow | Source contains multiplayer win, death, respawn, and player-number handoff paths; static identity alone does not prove every runtime outcome. |

Stuart's pinned source is a naming and control-flow reference, not proof of the
Steam binary. The listed retail addresses provide bounded corroboration only.

## Current toolkit behavior

The Windowed & Mods page can select a local split-screen launch preset for an
app-owned safe game copy. It uses `-skipfmv -level 850` and the same required
windowed compatibility base as other safe copies. The installed game and
original `BEA.exe` remain read-only source material.

The preset does not expose Host, Join, invitation, matchmaking, relay, or
public-network actions. Product status explicitly says online multiplayer is
not ready. The AppCore readiness service reports source-level checks only;
passing those commands is not runtime or network proof.

Controlled copied-target observations established bounded launch, exact-process
ownership, source safety, managed stop, and selected P1/P2 input-to-state/frame
correlations. They did not establish improved control feel, a physical gamepad
path, deterministic synchronization, multi-host play, active P3/P4 gameplay,
or gameplay parity. Raw logs, frames, executable copies, and input captures stay
outside Git.

## Requirements for any online claim

An online surface remains blocked until separately reviewed evidence covers at
least:

- two real hosts with explicit process and runtime-host identity;
- session/auth/invitation and disconnect/reconnect ownership;
- bounded input delivery and host/relay authority;
- cleanup, rollback, source safety, and installed-game non-mutation;
- measured gameplay outcomes rather than metadata-only participant slots; and
- clear failure and recovery behavior in the user-facing app.

None of those requirements is satisfied by the current split-screen preset,
source inspection, same-host helpers, VM-only metadata, or a rebuild that agrees
with itself.

## Claim boundary

This file supports the current local split-screen label and the explicit online
non-claim. It does not prove native retail netcode, LAN/public matchmaking,
more than two active retail players, control quality, exact layouts, visual
parity, or rebuild parity. Current corrected metadata is owned by the
[Ghidra correction authority](ghidra-full-reaudit-closeout-2026-07-13.md).
