# Community Outreach

> Community engagement, Stuart collaboration, and public documentation

## What to Share Publicly

| Item | Share? | Reason |
|------|--------|--------|
| Patcher tool source | Yes | Main deliverable, already on GitHub |
| Roadmap docs | Yes | Help community contribute |
| CURRENT_CAPABILITIES.md | Yes | Release-facing feature/status overview |
| Gold save file | No | `save-attempts/` stays private; public validation should use generated/temp fixtures instead of personal save artifacts |
| Source code quotes | No | Stuart shared privately; references are tracked as submodules in the private repo and excluded from public releases. |

## Stuart Collaboration Opportunities

Things to ask Stuart (via Discord) when stuck:

- [ ] "Do you have level data files showing per-level grade thresholds?"
- [ ] "Was god mode persistence intentionally stripped from console port?"
- [ ] "What does the 0x2408 field store? (shows 0x08000000 in gold save)"
- [ ] "Any memory of what the 60-byte block at 0x2410-0x244B contained?"
- [ ] "Do you have cliparams.h defining command-line parameters?"

## Discord Community Engagement

- [ ] **Release notes in #game-dev**: When new patcher version drops
- [ ] **S-rank strategy thread**: Compile community tips into shareable doc
- [ ] **Speedrun integration**: BermudaMaster might want specific unlock patterns
- [ ] **Model extraction updates**: Stuart's AYAResourceExtractor progress

## Public Documentation Improvements

- [ ] **README.md polish**: release-facing overview, screenshots, common use cases, and repo-first setup steps
- [ ] **Contribution guide**: how to report bugs, submit patches, and improve docs/lore safely
- [ ] **Public validation notes**: replace any private-fixture assumptions with reproducible temp/generated checks
- [ ] **Optional binary package plan**: only after the curated repo release shape is stable

## Community Action Items

1. [ ] Post GDC presentation to Discord (Stuart mentioned this)
2. [ ] Document findings in Discord #dev or similar channel
3. [ ] Finalize curated public repo layout and allowlist before any binary-package discussion
4. [ ] Write user guide for non-technical BEA fans

## Contact Status

| Person | Role | Status |
|--------|------|--------|
| Stuart Gillam | Lead Game Programmer | Active, helpful, on Discord |
| Glenn Corpes | Co-director, terrain | On Discord (via Stuart) |
| Alex Trowers | Lead designer | Responded, interested but hands-off |
| Jim (surname unknown) | Level designer | Unknown - mentioned by Stuart |
| Jez Elford | Lead art director | Unknown - mentioned by Stuart |
| Neil (surname unknown) | Artist | Unknown - created breakable buildings |
| Ben Carter | Lead programmer (PS2/Xbox) | Unknown - wrote GDM post-mortem |
| Jeremy Longley | Co-director | No response |
| Darran (?) | Art director | Stuart in contact via Facebook |

*Full roster at [../lore/team-roster.md](../lore/team-roster.md)*

## Community Resources

- **Gold Save**: vandal_117's all-S-rank save - use for hex diffing
- **AYAResourceExtractor**: [stuart73/AYAResourceExtractor](https://github.com/stuart73/AYAResourceExtractor)
- **Speedrun.com**: [Battle Engine Aquila](https://www.speedrun.com/battle_engine_aquila#Any)
- **BEA Discord**: Search "Battle Engine Aquila discord"

## Legal Notes

- Lost Toys dissolved, assets to Crown (UK), IP ownership unclear
- Stuart has team backing to share code for preservation
- Ziggurat has publishing/trademark, probably not source code rights
- Public domain: January 1, 2074

---

*See [../lore/community-preservation.md](../lore/community-preservation.md) for preservation efforts*
