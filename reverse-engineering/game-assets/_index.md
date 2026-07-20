# Game Assets And Mission Data

These documents describe formats and relationships observed from user-supplied
game data and the pinned AYA reference extractor. Current source and app
packages do not bundle retail asset payloads; see
[`../project-meta/attribution.md`](../project-meta/attribution.md) for the
project's attribution and distribution boundary.

## Asset formats and extraction

- [Game folder structure](game-folder-analysis.md)
- [AYA asset format](aya-asset-format.md)
- [AYA resource tag contract](aya-resource-tag-family-static-contract.md)
- [Guarded extraction pipeline](extraction-pipeline.md)
- [Modding reference](modding-reference.md)

The reusable extractor and catalog tools are documented in
[`tools/README.md`](../../tools/README.md). Generated catalogs use bundle-root-
relative paths and remain local; the WinUI Asset Library reads an existing
catalog and does not extract the installed game in place.

## Mission and script references

- [MSL scripting](msl-scripting.md)
- [MissionScript / IScript static contract](../binary-analysis/missionscript-iscript-static-contract.md)

The MSL reference retains language conventions and representative examples.
Generated per-level inventories and count tables are intentionally not tracked;
agents can query the source corpus directly when a reconstruction task needs
them. Static identities do not establish runtime source selection, command
effects, renderer fidelity, or rebuild parity.
