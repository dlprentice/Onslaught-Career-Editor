# Rebuild Provenance

Status: active implementation boundary
Last updated: 2026-07-12

## Current Lane

`rebuild/` is an **RE-informed original-code implementation**, not a strict
clean-room rebuild. Its coordinator and current implementation lane have been
exposed to public GPL reference source, reverse-engineering documentation,
Ghidra-derived descriptions, and runtime evidence.

The subtree is therefore licensed separately under GPL-3.0-or-later. The root
MIT license continues to cover original toolkit code outside `rebuild/`; it
does not relicense this subtree or the `references/Onslaught` submodule.

## Allowed Inputs

- behavior requirements stated as facts, tests, or bounded public contracts;
- original design decisions made in this subtree;
- public standards and engine APIs;
- synthetic command tapes and procedurally authored test/visual content; and
- independently measured runtime behavior when its proof boundary is recorded.

User-extracted retail meshes may be loaded only as optional ignored local
presentation inputs through the explicit `--local-assets` path. They are not
inputs to Core/Client implementation, repository content, redistribution
material, simulation truth, or evidence of visual/gameplay parity.

## Forbidden Imports

- copied or mechanically translated reference-source functions, headers,
  comments, names, layouts, or control flow;
- decompiler text or generated code derived from the retail executable;
- proprietary executables, game archives, media, saves, screenshots, or
  extracted assets;
- project references or build-time reads from `references/Onslaught`; and
- claims that a passing replay, renderer smoke, or visual comparison proves
  gameplay, asset, timing, or presentation parity.

## First-Slice Classification

The initial implementation is a synthetic prototype. None of its numeric
values are presented as measured retail constants.

| Surface | Classification | Evidence claim |
| --- | --- | --- |
| Tick rate, arena bounds, movement speeds, resources, cooldowns, damage, and hit radius | Original project design values | No retail timing, handling, balance, or layout claim |
| Walker/jet mode, energy use, shield behavior, firing, and targets | Original prototype mechanics inspired only by the high-level project premise | No retail control-flow, gameplay, or parity claim |
| Seeded target positions and `first-flight` command tape | Synthetic regression content | Determinism input only; not a retail mission or asset |
| Binary state serializer, final-state hash, and rolling replay trace hash | Original test/acceptance format | Canonical continuation-state and replay-history stability only |
| Real-time input adapter, edge/pulse latching, and catch-up policy | Original client scheduling design | Deterministic adapter behavior only; no retail input/timing claim |
| Default First Flight arena, craft, sentries, projectiles, HUD, camera, colors, and layout | Original procedural Godot presentation | A playable renderer/input proof only; no retail asset, mission, visual, or gameplay parity claim |
| Explicit local player/terrain mesh roles | Optional user-extracted, ignored retail-derived presentation input | Local load success only; never committed, redistributed, or used as simulation/parity evidence |

The Core test project copies the Core sources and project file into test output,
rejects filesystem/process/clock/network API tokens, linked source/build inputs,
custom build targets, project/assembly references, and known presentation or
toolkit assembly dependencies. This is a build-boundary gate, not proof against
semantic copying. Human provenance review remains required.

## Strict Clean-Room Path

A future strict clean-room effort must use separately staffed roles:

1. an exposed specification team produces behavior-only specifications with
   provenance and rights review;
2. an implementation team with no exposure to reference source, decompiler
   output, this RE-informed implementation, or private proof payloads works
   only from the approved specifications; and
3. an independent acceptance team compares observable behavior without
   transferring implementation details between the first two teams.

Nothing in the current subtree is evidence that this separation has occurred.
