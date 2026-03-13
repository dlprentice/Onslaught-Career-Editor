# Community Resources

## Speedrun Resources

- **Speedrun.com**: https://www.speedrun.com/battle_engine_aquila#Any
- **BermudaMaster's Twitch**: https://www.twitch.tv/bermudamaster
- **Current WR**: Sub-56 minutes (BermudaMaster, Nov 2025)

---

## Speedrun Techniques (from BermudaMaster)

**Menu Skip**: Holding spacebar (confirm key) keeps confirming options on select screens. This skips cutscenes and the transition between level start and actual gameplay.

**Victory Screen Glitch**: Opening the menu during the victory screen shows both simultaneously. Can exit level to reach results screen slightly faster.

**Death from Above Issues**: Something about the "Red Map issue" causes problems. BermudaMaster: "I really need to look over this footage."

**Hitbox Issues**: Some objects' hitboxes don't exist - attacks can phase through them. Discovered after hours of optimizing single levels.

**Blinding the Enemy**: Destroying ALL turrets makes air support stay on the map and clear the island much faster in the NEXT mission. If even one turret stays, all air support leaves when it's destroyed.

---

## Racing Challenges (from vandal_117)

- **NOT impossible** - contrary to 2013 IGN article claiming impossible
- Fly close to surface for speed boost
- Tiny gap between "too close" (physics launch) and "boost zone"
- Easier on water but still get launched if too close
- Last challenge: can shoot ship and buildings before starting, can fly under the ship

---

## Similar Games (for inspiration)

- **Gun Metal** (Steam) - similar mech combat
- **AirMech** - closest modern equivalent to BEA
- **Supreme Commander** - unit designs similar (Aeon = Forseti, Cybran = Muspell)
- **AEROMACHINA** (upcoming) - ground/flight combat, demo on Steam

---

## External Archives

- **Lost Toys Website** (archived): https://web.archive.org/web/20030622111235/http://www.losttoys.com/
- **Post-Mortem** (GDM April 2003): https://ia600907.us.archive.org/33/items/GDM_April_2003/GDM_April_2003.pdf
- **GDC Europe 2002**: "Cross Platform Console Development" PowerPoint (found by David via Internet Archive, March 2025)
- **vandal_117's gold save**: Legitimate all-S-rank career file shared Sept 12, 2025
- **Xbox disc dump** (archive.org): https://archive.org/download/BattleEngineAquila_USA_redump_51263

---

## Emulator Compatibility (found by Jeppi, Feb 2022)

- **Cxbx-Reloaded (Xbox)**: https://github.com/Cxbx-Reloaded/game-compatibility/issues/251
- **DXVK**: https://github.com/doitsujin/dxvk/issues/1757
- **PCSX2 (PS2)**: https://github.com/PCSX2/pcsx2/commit/05b8e80ac874b48c83f44c521d0b076b100992c2

---

## External Tools

### AYAResourceExtractor
- **Repo**: https://github.com/stuart73/AYAResourceExtractor
- **Author**: Stuart Gillam (desimbr)
- **Purpose**: Extract 3D models, textures from .aya files
- **Output**: FBX (binary and ASCII)
- **Note**: Animations not yet extractable
- **Blender import**: Turn off extra import options to avoid crash
- **Model scale**: Battle Engine is ~7.6m tall based on model calculations (April 2023)
- **Model quirks**: Models are asymmetrical - min473 noted "NOTHING is symmetrical in this model" when 3D printing
- **Use cases**: Gmod SNPCs, C&C Generals mods, 3D printing (thin parts break during support removal)

### Onslaught Source Reference
- **Repo**: https://github.com/stuart73/Onslaught
- **Contents**: Career.cpp/h, d3dapp.cpp, FEPGoodies.cpp, etc.
- **Note**: Internal PC build, not console port

---

## Sources

- `references/Onslaught/Career.cpp` - Stuart's internal PC build source
- `references/Onslaught/Career.h` - Struct definitions
- `game/` - Full BEA installation for Ghidra analysis (tracked in private repo)
- Community hex-diffing of retail saves
- Discord conversations (#general, #game-dev, #greetings, #media, #story-and-lore, #bugs, #bulletin, #who-joined, #muspell-block) parsed Dec 2025
- LinkedIn conversations with Stuart, Alex Trowers
