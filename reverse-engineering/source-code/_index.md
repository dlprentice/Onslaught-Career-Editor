# Reference Source Analysis

The pinned [`references/Onslaught`](../../references/Onslaught) and
[`references/AYAResourceExtractor`](../../references/AYAResourceExtractor)
submodules are actively used reference evidence. Their current build, format,
test, provenance, and license posture is recorded in the
[reference-submodule audit](reference-submodule-audit-2026-07-12.md).

Stuart Gillam's source represents an internal PC development lineage. The Steam
retail executable and save layout differ. Source names and architecture are
useful hypotheses; they are not proof of retail identity or behavior.

## System maps

- Core: [thing](core/thing-system.md), [actor](core/actor-system.md),
  [engine](core/engine-system.md), [platform](core/platform-system.md)
- Gameplay: [career](gameplay/career-system.md),
  [battle](gameplay/battle-system.md), [game loop](gameplay/game-system.md)
- Frontend: [menus](frontend/fep-systems.md),
  [controllers](frontend/controller-system.md)
- I/O: [storage](io/storage-system.md), [chunker](io/chunker-system.md),
  [events](io/event-system.md)

The February parse and manifests remain provenance snapshots, not completeness
or semantic-correctness claims. Current retail relationships belong in the
smallest owning binary-analysis note rather than a generated crosswalk mirror.

The GPL rebuild is RE-informed original code, not a mechanical translation of
these references. Follow [`rebuild/PROVENANCE.md`](../../rebuild/PROVENANCE.md)
for its license and implementation boundary.
