# Game Assets And Mission Data

Status: active index
Last updated: 2026-09-30 (the level inventory)
Summary: where the asset-format, extraction and mission-data documents are, and which of them are historical.

These documents describe formats and relationships observed from user-supplied
game data and the pinned AYA reference extractor. Current source and app
packages do not bundle retail asset payloads; see
[`../project-meta/attribution.md`](../project-meta/attribution.md) for the
project's attribution and distribution boundary.

The specimen-bounded narrative census for the measured 5,515-file installation
snapshot is [`../installed-corpus-census.md`](../installed-corpus-census.md). It is a dated synthesis, not a
replacement for the installed bytes or the narrower format findings below.

## Asset formats and extraction

- [Historical game folder structure](game-folder-analysis.md) (December 2025; its level table is superseded by
  the [level inventory](level-inventory.md))
- [AYA asset format](aya-asset-format.md)
- [AYA resource tag contract](aya-resource-tag-family-static-contract.md)
- [Guarded extraction pipeline](extraction-pipeline.md)
- [Modding reference](modding-reference.md)

The reusable extractor and catalog tools are documented in
[`tools/README.md`](../../tools/README.md). Generated catalogs use bundle-root-
relative paths and remain local; the WinUI Asset Library reads an existing
catalog and does not extract the installed game in place.

## Mission and script references

- [Level inventory](level-inventory.md): which of the 95 level folders are playable, how the game reaches each,
  and what the others hold
- [MSL scripting](msl-scripting.md)
- [MissionScript / IScript static contract](../binary-analysis/missionscript-iscript-static-contract.md)

The MSL reference retains language conventions and representative examples.
The level inventory is a checked map of which levels exist and load, not a mirror of their files.
Generated per-level inventories and count tables are intentionally not tracked;
agents can query the source corpus directly when a reconstruction task needs
them. Static identities do not establish runtime source selection, command
effects, renderer fidelity, or rebuild parity.
