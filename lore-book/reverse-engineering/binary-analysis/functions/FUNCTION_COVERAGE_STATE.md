# Function Coverage State (Master)

> Binary-wide function mapping coverage tracker for `BEA.exe`
> Last updated: 2026-03-01

## Purpose

This file is the canonical progress state for binary-wide mapping coverage.

- Use this for `% mapped` and remaining unnamed-function totals.
- Use [`_index.md`](_index.md) for the full Stuart-source-aligned mappable corpus (source-file index + links).
- Use [`../MCP-MUTATION-BACKLOG.md`](../MCP-MUTATION-BACKLOG.md) for pending/failed mutation retries.

## Binary-Wide Coverage (Ghidra Function Objects)

| Metric | Value | Source |
|--------|-------|--------|
| Total function objects | 5861 | Headless `ExportWeakFunctionList.java` (`mode=all`) total |
| Unnamed `FUN_` objects | 0 | GhydraMCP `functions_list(name_matches_regex=\"FUN_.*\", limit=1)` total |
| Named function objects | 5861 | `total - FUN_` |
| Named coverage | 100.00% | `5861 / 5861` |
| Weak-name objects | 0 | Headless `ExportWeakFunctionList.java` (`mode=weak`) total |
| Strong semantic symbols | 5861 | `total - weak` |
| Strong semantic coverage | 100.00% | `5861 / 5861` |
| Remaining unnamed | 0.00% | `0 / 5861` |
| Helper-placeholder symbols (`__Helper_`) | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CUnitAI helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CEngine helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CBattleEngine helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CWorld helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CGame helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CGeneralVolume helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CExplosionInitThing helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CMeshCollisionVolume helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CDXEngine helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CTexture helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CDXTexture helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |
| CFastVB helper placeholders | 0 | `pass2_semantic_wave217/all_after_wave217.tsv` derived snapshot |

## Stuart-Source Mappable Corpus Coverage

| Metric | Value | Source |
|--------|-------|--------|
| Source-file entries tracked | 158 | Count of numeric `Functions` table rows in [`_index.md`](./_index.md) |
| Functions represented in source-file corpus | 1059 | Sum of numeric `Functions` column in [`_index.md`](./_index.md) |
| Source-file directories with index | 131 | `functions/<source-file>/_index.md` folders |

## Interpretation

- Binary-wide `% mapped` is measured against all Ghidra function objects (includes runtime helpers, thunks, compiler helpers, and code not present in Stuart debug-path corpus).
- Stuart-source corpus totals are a separate axis: they measure source-aligned coverage, not total executable coverage.
- A function being "named" does not automatically mean "fully verified"; verification still depends on signature/comment/doc quality.
- `weak-name` is a narrow regex metric (`FUN_`, `Auto_`, `__Unk_`). Helper placeholders (`__Helper_`) are tracked separately; that backlog is now closed in `pass2_semantic_wave217`.

## Canonical Links

- Source-file master index: [`_index.md`](./_index.md)
- Ghidra address/reference ledger: [`../GHIDRA-REFERENCE.md`](../GHIDRA-REFERENCE.md)
- Mutation retry backlog: [`../MCP-MUTATION-BACKLOG.md`](../MCP-MUTATION-BACKLOG.md)

## Update Workflow

1. Pull fresh totals from Ghidra (`functions_list` total + `name_matches_regex=\"FUN_.*\"` total).
2. Update this file and any published machine-readable coverage snapshot together.
3. If symbols/docs changed, update [`_index.md`](./_index.md) and per-source docs.
4. Mirror canonical docs to `lore-book/reverse-engineering/` after updates.
