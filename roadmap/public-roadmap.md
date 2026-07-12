# Public Roadmap

Status: public-safe overview
Last updated: 2026-07-11

This roadmap is written for public-source collaboration. It avoids raw local
proof payload paths and machine-only evidence roots, while normal project-owned
docs, ledgers, tools, state batons, and compact proof summaries live in this
public-primary repo.

## Current Priorities

1. Keep WinUI 3 as the primary Windows product lane.
2. Keep AppCore and the C# CLI as shared correctness/support surfaces.
3. Grow the GPL, RE-informed rebuild through a deterministic Core and a Godot
   .NET visual client that runs without proprietary game payloads.
4. Improve safe-copy patch/mod workflows without mutating installed game files.
5. Continue bounded runtime proof for local copied-game behavior.
6. Treat online multiplayer as active research until real distinct-endpoint and
   source-bound runtime-causality proof exists.
7. Keep public releases free of proprietary game content and private proof data.

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
- Deterministic rebuild Core tests, synthetic scenarios, procedural visuals,
  and contributor ergonomics within `rebuild/PROVENANCE.md`
