# Discord Archive Extract (2026-03)

Purpose: preserve high-value developer/community facts extracted from historical Discord channel dumps before raw dump removal.

## Scope
- Source channels were previously archived under `discord_channel_dumps/**` (raw dumps retired after extraction).
- This file retains only high-signal claims used by current lore/RE docs.

## Extracted Facts

| Topic | Extracted Fact | Source (historical dump line) |
|---|---|---|
| BEA status | BEA retail was not a "working demo"; that phrase applied to Stunt Car Racer Pro. | `general.md:111`, `game-dev.md:311` |
| Sequel planning | No sequel was planned during the original release period. | `media.md:50`, `media.md:68` |
| PC source availability | Ex-team recollection indicates no one retained the full finished PC retail source tree. | `general.md:1351` |
| Dev workflow detail | Development/controller testing included PS2 DualShock USB adapter workflow in PC dev environment. | `general.md:1351`, `general.md:1404` |
| Boss attribution | Stuart confirmed Gill-M naming and separately indicated he coded the related hive-boss path. | `media.md:135`, `media.md:174`, `media.md:181` |
| Mission scripts release nuance | Readable MissionScripts files shipped, but runtime behavior used compiled resource data rather than direct text edits. | `game-dev.md:509`, `game-dev.md:518` |
| Internal tooling scope | Lost Toys had an in-house world editor (landscape/trees/units/buildings); partial source remnants may exist without a complete build. | `greetings.md:462` |
| Internal codename/repo history | The internal project codename was `Onslaught`; `Onslaught2` referred to a second SourceSafe tree after corruption. | `media.md:700` |
| Design pivot note | Team recollections describe shifting from early broad-force stalemate framing toward bigger set-piece boss escalation. | `media.md:311` |
| Launch-option build split context | `-forcewindowed` behavior recollections align with dev/release path split context (`CD3DApplication` vs `CEditorD3DApp`) rather than a single retail path. | `game-dev.md:909` |
| cardid chronology context | Recollections indicate card-id feature handling in retail-era paths post-dated Stuart’s available source snapshot. | `game-dev.md:905` |

## Usage Guidance
- Treat these entries as provenance-preserving extracts.
- Prefer canonical destination docs for reader-facing narrative:
  - `lore/lost-toys-history.md`
  - `lore/development-history.md`
  - `lore/cut-content-secrets.md`
  - `lore/reception-legacy.md`
  - `reverse-engineering/project-meta/attribution.md`

## Notes
- Raw Discord dump files were archival research inputs and are intentionally excluded from the public release snapshot.
- This extract is the stable citation anchor for Discord-derived claims kept in release-facing docs.
- Raw dump directory removal was executed after this extraction pass on 2026-03-05.
