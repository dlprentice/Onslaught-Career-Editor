# Game Assets And Mission Data

These documents describe formats and relationships observed from user-supplied
local game data and the pinned AYA reference extractor. The repository and app
release do not contain extracted retail assets.

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

- [Mission script index](mission-scripts-index.md)
- [MSL scripting](msl-scripting.md)
- [Events](mission-events-index.md)
- [Slots](mission-slot-usage.md)
- [Messages](mission-message-usage.md)
- [Speakers](mission-speaker-index.md)
- [Text](mission-text-index.md)
- [Thing usage](mission-thing-usage.md)

Counts and mappings are bounded to their recorded corpus. They do not establish
format completeness, redistribution rights, renderer fidelity, or rebuild
parity.
