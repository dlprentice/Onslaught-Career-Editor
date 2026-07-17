# Reverse Engineering Quick Reference

Status: active
Last updated: 2026-05-26
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.

This folder holds dense lookup tables that are useful during deep reverse-engineering work but too large/noisy for `AGENTS.md` or active global skills. Treat these files as repo-local quick references. When a table is corrected, update the relevant detailed doc as well.

**Static closure hygiene:** Ghidra function-quality queue closure reached `6113/6113 = 100.00%` in Wave900, and later boundary recovery/re-audit work has advanced the live function-object surface to `6411/6411 = 100.00%` with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt. Wave1219 (`wave1219-final-score16-current-risk-review`) closed the active Wave1108 current-risk denominator at `1179/1179 = 100.00%`, with current focused candidates: 1117, live regenerated current focused candidates: 1117, current risk candidates: 6166, remaining active focused work: 0, and latest verified Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Wave1220 static closeout acceptance: active current-risk focused accounting is `1179/1179 = 100.00%`; remaining active focused work: 0. This does **not** change the on-disk AYA chunk/tag lookup tables in this folder. Use [aya-tags.md](aya-tags.md) and [aya-resource-chunks.md](aya-resource-chunks.md) for format facts; use [../game-assets/_index.md](../game-assets/_index.md), [../binary-analysis/mapped-systems.md](../binary-analysis/mapped-systems.md), and binary-analysis wave notes for static anchors and bridge counts.

## AYA / Resources

| File | Use |
| --- | --- |
| [aya-tags.md](aya-tags.md) | AYA file tag IDs, mesh/texture marker tags, and format markers |
| [aya-resource-chunks.md](aya-resource-chunks.md) | Resource archive chunk IDs, top-level chunk table, and hex IDs |

## Save / Career

| File | Use |
| --- | --- |
| [save-structs.md](save-structs.md) | BES/CCareer struct layout quick reference |
| [save-ranks.md](save-ranks.md) | Rank floats and raw bit patterns |
| [save-goodies.md](save-goodies.md) | Goodie/unlockable IDs and state handling |
| [save-kills.md](save-kills.md) | Kill counter categories, offsets, and packed metadata |

## Engine / Source

| File | Use |
| --- | --- |
| [battleengine-config-values.md](battleengine-config-values.md) | BattleEngine default config values and combat/movement constants |
| [engine-singletons.md](engine-singletons.md) | Engine singleton globals and subsystem ownership |
| [source-files.md](source-files.md) | Stuart source file organization |
| [source-key-functions.md](source-key-functions.md) | Important source function signatures |
| [source-hierarchy.md](source-hierarchy.md) | Class hierarchy and thing-type flags |

## Controls / Mission Scripts

| File | Use |
| --- | --- |
| [cli-parameters.md](cli-parameters.md) | Retail/source command-line parameter quick reference |
| [msl-commands.md](msl-commands.md) | MSL command reference and mission scripting verbs |

## Canonical Detailed Docs

Use these quick tables for lookup speed, then verify or expand findings in the detailed docs:

- [../RE-INDEX.md](../RE-INDEX.md)
- [Mapped systems](../binary-analysis/mapped-systems.md) - Current static system owners and claim boundaries
- [../game-assets/_index.md](../game-assets/_index.md)
- [../save-file/save-format.md](../save-file/save-format.md)
- [../save-file/struct-layouts.md](../save-file/struct-layouts.md)
- [../game-assets/aya-asset-format.md](../game-assets/aya-asset-format.md)
- [../game-assets/msl-scripting.md](../game-assets/msl-scripting.md)
- [../source-code/_index.md](../source-code/_index.md)
- [../binary-analysis/functions/_index.md](../binary-analysis/functions/_index.md)
