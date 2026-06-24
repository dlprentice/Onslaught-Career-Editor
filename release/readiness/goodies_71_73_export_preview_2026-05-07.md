# Goodies 71-73 Export Preview Evidence - 2026-05-07

## Scope

This pass parsed the fresh full install asset catalog generated under ignored `subagents/asset-full-install-2026-05-07/` and checked whether shipped Goodies 71-73 resolve to actual exported preview images.

Raw catalog data, exported PNGs, absolute paths, and proof JSON stayed under ignored `subagents/`.

It does not run BEA, patch `BEA.exe`, mutate saves, mutate Ghidra, or prove runtime selection.

## Command

```powershell
node -e "<parse fresh private catalog and check Goodies 71-73 exported texture paths>"
```

Result: PASS

Private output:

```text
subagents/goodies-71-73-export-preview/current.json
```

## Public-Safe Findings

| Goodie | Catalog title | Family | Texture refs | Mesh refs | Exported PNGs found |
| ---: | --- | --- | ---: | ---: | ---: |
| `71` | `Goodie 071 - All Configurations` | texture-only artwork | `1` | `0` | `1` |
| `72` | `Goodie 072 - Free Camera Mode` | texture-only artwork | `1` | `0` | `1` |
| `73` | `Goodie 073 - God Mode` | texture-only artwork | `1` | `0` | `1` |

Follow-up native UIA proof on 2026-05-07 extended `AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided` and selected all three rows in WinUI against the fresh full install catalog. The test verified the selected row title, the artwork-match summary, the texture preview element, and the enabled export action. It passed with `Passed: 1, Skipped: 0`.

## What This Proves

- The three shipped hidden/non-grid Goodie archives are not empty placeholders.
- The fresh installed-game export produced local PNG previews for the texture refs attached to Goodies 71-73.
- The WinUI Asset Library catalog can treat these rows as real extracted artwork rows when the generated catalog is loaded.
- The native WinUI Asset Library can select and preview these three artwork rows through UI Automation against the fresh full install catalog.

## What This Does Not Prove

- It does not prove the in-game Goodies wall can select 71-73 through normal navigation.
- It does not prove a hidden cheat, developer, script, or non-wall path can request those ids at runtime.
- It does not prove textured or animated native model viewing.
- It does not permit public redistribution of the exported images or raw catalog data.
