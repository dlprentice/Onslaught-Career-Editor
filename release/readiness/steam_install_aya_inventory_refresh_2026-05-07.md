# Steam Install AYA Inventory Refresh - 2026-05-07

## Scope

This pass reran a read-only AYA resource inventory against the user's current Steam install path after the Goodies/model-viewer discussion. It was a verification refresh, not a new extraction feature and not a runtime proof.

This report is public-safe. It records counts only and does not include absolute private paths, raw asset paths, raw manifests, extracted textures, FBX files, screenshots, hashes of private payloads, binaries, saves, or proof JSON.

Raw generated output remained ignored/private under:

```text
subagents/steam-install-aya-inventory-2026-05-07/
```

## Command

```powershell
py -3 tools/aya_archive_inventory.py "<actual Steam install>\data\Resources" --resource-root "<actual Steam install>\data\Resources" --resolve-assets --asset-manifest-out "subagents\steam-install-aya-inventory-2026-05-07\asset_manifest.json" --json-out "subagents\steam-install-aya-inventory-2026-05-07\inventory.json"
```

Result: PASS

## Public-Safe Counts

| Surface | Count / result |
| --- | ---: |
| PC resource archives scanned | 301 |
| Goodie resource archives found | 232 |
| Separate `goodie_232_res_PC.aya` archive | no |
| Top-level `TEXT` chunks | 18,857 |
| Top-level `MESH` chunks | 3,492 |
| Top-level `GDIE` chunks | 232 |
| `TEXT` texture refs resolved | 601 / 601 |
| reference mesh refs resolved | 209 / 209 |
| `GDIE` texture refs resolved | 206 / 206 |
| `GDIE` mesh refs resolved | 42 / 42 |

`GDIE` family counts:

| Family | Count |
| --- | ---: |
| texture-only | 149 |
| texture + mesh | 45 |
| metadata-only | 38 |

## What This Proves

- The Goodies and Asset Library catalog work is grounded in the shipped PC install resource archives, not only in Stuart's source tree or sample fixtures.
- The current packed-resource resolver can resolve every texture/mesh reference class it reported in this read-only install inventory.
- The shipped PC Goodies corpus includes texture-bearing, mesh-bearing, and metadata-only Goodie entries.
- Slot 232 remains a displayable FMV Goodie path without a separate `goodie_232_res_PC.aya` archive.

## What This Does Not Prove

- This refresh did not export PNG or FBX payloads; full export coverage is covered by the earlier full-corpus extraction evidence.
- This refresh did not prove final textured/animated in-app model rendering.
- This refresh did not replay the runtime Goodies wall in BEA.
- This refresh did not mutate the installed game, a copied executable, a Ghidra project, or any save file.

## Next RE Direction

The useful next step is not another inventory count. It is either:

- static RE typing of the remaining Goodies frontend fields and content-bucket branches with Ghidra read-back evidence, or
- copied-profile runtime replay of representative Goodies wall selections under the windowed patch, keeping captures and proof private.
