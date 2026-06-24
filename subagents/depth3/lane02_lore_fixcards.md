# Lane 02 Lore Mirror Fix Cards

Date: 2026-03-04
Input findings: `subagents/depth2/lane02_lore_mirror_contradictions.md`
Scope: canonical `lore/*.md` vs mirror `lore-book/lore/*.md`
Deterministic ordering: lexical sort by canonical path.

## Action Codes

- `A0_KEEP_EXACT`
  - Mirror must remain byte-identical to canonical.
  - Sync operation: direct copy from canonical to mirror, no post-copy rewrites.
- `A1_KEEP_DEPTH_ADJUSTED_AGENTS_LINK`
  - Mirror tracks canonical content except one required relative-link depth rewrite for `AGENTS.md`.
  - Sync operation: copy canonical to mirror, then apply exactly one replacement:
    - `[AGENTS.md](../AGENTS.md)` -> `[AGENTS.md](../../AGENTS.md)`

## Fix Cards

| Card ID | Mirror file pair (canonical <-> mirror) | Exact sync action | Link-depth notes |
|---|---|---|---|
| L2-001 | `lore/LORE-INDEX.md` <-> `lore-book/lore/LORE-INDEX.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-002 | `lore/_index.md` <-> `lore-book/lore/_index.md` | `A1_KEEP_DEPTH_ADJUSTED_AGENTS_LINK` | Mirror lives one level deeper (`lore-book/lore/`), so repo-root `AGENTS.md` needs one extra `../`. |
| L2-003 | `lore/battle-engine-tech.md` <-> `lore-book/lore/battle-engine-tech.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-004 | `lore/characters.md` <-> `lore-book/lore/characters.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-005 | `lore/community-preservation.md` <-> `lore-book/lore/community-preservation.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-006 | `lore/cut-content-secrets.md` <-> `lore-book/lore/cut-content-secrets.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-007 | `lore/development-history.md` <-> `lore-book/lore/development-history.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-008 | `lore/game-overview.md` <-> `lore-book/lore/game-overview.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-009 | `lore/lost-toys-history.md` <-> `lore-book/lore/lost-toys-history.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-010 | `lore/reception-legacy.md` <-> `lore-book/lore/reception-legacy.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-011 | `lore/reference-materials.md` <-> `lore-book/lore/reference-materials.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-012 | `lore/team-roster.md` <-> `lore-book/lore/team-roster.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-013 | `lore/technical-deep-dive.md` <-> `lore-book/lore/technical-deep-dive.md` | `A0_KEEP_EXACT` | No depth rewrite required. |
| L2-014 | `lore/world-lore.md` <-> `lore-book/lore/world-lore.md` | `A0_KEEP_EXACT` | No depth rewrite required. |

## Deterministic Guardrails

- Allowed non-identical lore pair count for this scope: exactly `1` (`L2-002`).
- Required non-identical delta for `L2-002`: only `../AGENTS.md` vs `../../AGENTS.md` at the AGENTS link line.
- Any additional lore mirror diffs are drift and should be resolved back to the card action above.
