# Community & Preservation

- **Status:** live preservation record — who is reachable, what the community has
  published, and the project's rights boundary. Two corrections landed
  2026-07-28 and are marked at the lines they affect; the modding-surface
  section had asserted the opposite of what this repository measures.
- **Last updated:** 2026-07-28
- **Summary:** community contributors and resources, the mods and tools that
  exist for this title, what the retail modding surface actually is, and the
  rights boundary this project operates under.

<a id="active-community-contacts"></a>

### Community Contributors

| Person | Role | Preservation context |
|--------|------|----------------------|
| **Stuart Gillam** | Lead programmer | Public source repositories and historical context |
| **Glenn Corpes** | Technical director | Terrain and rendering context |
| **Alex Trowers** | Lead designer | Design and worldbuilding context |
| **vandal_117** | Community contributor | Provided the reference save used for validation |

### Community Resources

- **BEA Discord** — Active community hub (search "Battle Engine Aquila discord")
- **Stuart's GitHub**: https://github.com/stuart73/Onslaught
- **AYAResourceExtractor**: https://github.com/stuart73/AYAResourceExtractor (model extraction)

### Modding & Speedrunning

| Resource | Details |
|----------|---------|
| **Speedrun.com** | [speedrun.com/battle_engine_aquila](https://www.speedrun.com/battle_engine_aquila) - Individual level leaderboards, moderated by Inv1ve |
| **Widescreen Fix** | 2018 mod (1009 KB) — the most widely circulated community mod. CORRECTED 2026-07-28; previously read "Only significant mod available", which the Cheat Engine table and trainer rows immediately below it contradict. |
| **Cheat Engine Table** | OpenCheatTables (July 2024) |
| **Trainers** | +4 Trainer (2007, 35.1 KB) on GameCopyWorld |
| **PCGamingWiki** | [pcgamingwiki.com/wiki/Battle_Engine_Aquila](https://www.pcgamingwiki.com/wiki/Battle_Engine_Aquila) |

### Modding Surface

**CORRECTED 2026-07-28.** This section previously read, in full:

> **Modding limitations**: Main config file is encrypted. Limited traditional
> modding potential.

Both sentences were false, and the second followed from the first. **No shipped
config file is encrypted.**

- `cardid.txt` (18 KB) is plain text with a documented grammar, and this
  repository ships `tools/cardid_preset_manager.py` to edit it — see
  [modding-reference.md](../reverse-engineering/game-assets/modding-reference.md).
- `defaultoptions.bea` (10,004 bytes) is a plain little-endian options snapshot
  written through `fopen`/`fwrite`/`fclose` with no crypt step, and this
  repository ships `tools/options_entries_decode.py`, which reads its entry block
  with no decryption — see
  [game-folder-analysis.md](../reverse-engineering/game-assets/game-folder-analysis.md).

The only obfuscation **measured** anywhere in the retail build is the XOR'd
cheat-string table, which is not a config file —
[cheat-codes.md](../reverse-engineering/game-mechanics/cheat-codes.md).

### Rights Boundary

Onslaught Toolkit is an unofficial community project and is not affiliated with
or endorsed by the game's publishers or rights holders. Users supply their own
retail game data. The MIT toolkit and GPL rebuild/reference licenses do not
grant rights in the game executable, assets, names, trademarks, or third-party
components. Original credits and notices remain part of preservation rather
than cleanup material.
