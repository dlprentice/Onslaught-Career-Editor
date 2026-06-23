# Public Roadmap

Status: public-safe overview
Last updated: 2026-06-22

This roadmap is written for public-source collaboration. It avoids private proof
paths and maintainer-only evidence ledgers.

## Current Priorities

1. Keep WinUI 3 as the primary Windows product lane.
2. Keep AppCore and the C# CLI as shared correctness/support surfaces.
3. Improve safe-copy patch/mod workflows without mutating installed game files.
4. Continue bounded runtime proof for local copied-game behavior.
5. Treat online multiplayer as active research until real distinct-endpoint and
   source-bound runtime-causality proof exists.
6. Keep public releases free of proprietary game content and private proof data.

## Not Ready Yet

- Public matchmaking
- Native BEA netcode
- Player-ready online Host/Join
- Active P3/P4 original-binary gameplay
- Signed installer-grade release
- Rebuild parity or no-noticeable-difference parity

## Public Contributor Good First Areas

- WinUI polish with AppCore-backed behavior
- AppCore tests around save/options and patch planning
- Public docs that keep proof boundaries clear
- Public-safe tooling checks
- Patch catalog description and safety improvements
