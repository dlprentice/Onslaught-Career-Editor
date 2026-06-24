# Real Asset Extraction Smoke Evidence - 2026-05-07

## Scope

This pass checked the user's local Steam install read-only and wrote all raw outputs under ignored `subagents/asset-coverage-2026-05-07/`.

Follow-up: `release/readiness/real_asset_full_install_export_2026-05-07.md` records the later full fresh install export (`847 / 847` textures, `213 / 213` loose meshes, `139 / 139` embedded meshes) and native WinUI fresh-catalog smoke. Treat that follow-up as the stronger current proof for full supported extraction coverage.

It answers the current asset-browser concern:

- the catalog foundation is based on the shipped PC resource archives, not just developer source-tree samples,
- representative real texture/model lanes can export from the install,
- but the committed WinUI visual smoke still uses a small fixture, and the in-app model preview is still a lightweight wireframe rather than a final textured/animated model viewer.

## Read-Only Inventory Result

Command:

```powershell
py -3 tools/aya_archive_inventory.py "<game>\data\Resources" --resource-root "<game>\data\Resources" --resolve-assets --json-out subagents\asset-coverage-2026-05-07\aya-inventory.json --asset-manifest-out subagents\asset-coverage-2026-05-07\packed-asset-manifest.json
```

Result: PASS

Public-safe summary:

- PC resource archives scanned: `301`
- Goodie resource archives: `232`
- Top-level chunks include `TEXT 18857`, `MESH 3492`, and `GDIE 232`
- Packed reference resolution:
  - `TEXT` texture refs: `601 / 601`
  - reference mesh refs: `209 / 209`
  - `GDIE` texture refs: `206 / 206`
  - `GDIE` mesh refs: `42 / 42`
- `GDIE` family counts: `149` texture-only, `45` texture+mesh, `38` metadata-only

## Bounded Export Smoke

Command:

```powershell
py -3 tools/export_game_assets.py --game-root "<game>" --out-root subagents\asset-coverage-2026-05-07\bounded-export --limit-archives 12 --limit-loose-textures 12 --limit-loose-meshes 12 --limit-embedded-bodies 12 --progress-every 25
```

Result: PASS

Public-safe summary:

- loose textures: `12 / 12`
- loose meshes: `12 / 12`
- embedded mesh bodies: `12 / 12`
- language corpus: `2571` merged rows across six language files
- videos: `66` Bink `.vid` files inventoried

## What This Proves

- The installed PC resource folder contains the expected real resource families.
- Current AYA inventory logic can resolve every packed texture/mesh reference class it reports.
- Current export harness can convert representative real loose textures, loose meshes, and embedded meshes from the install.
- The Goodies browser catalog foundation is using real shipped resource evidence, while raw extracted outputs remain private.

## What This Does Not Prove

- It is not a full fresh export of every texture/model row in this pass.
- It does not prove final textured or animated in-app model viewing.
- It does not prove runtime Goodies unlock triggers.
- It does not permit committing extracted assets, screenshots, or raw private manifests.

## Private Outputs

Raw outputs remain ignored/private under:

```text
subagents/asset-coverage-2026-05-07/
```
