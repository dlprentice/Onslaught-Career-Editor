# The Team

- **Status:** live preservation record — credits from the archived Lost Toys
  website, plus developer recollection. Some claims rest on Discord recollection
  preserved in
  [discord-archive-extract-2026-03.md](discord-archive-extract-2026-03.md); the
  raw channel dumps were retired after extraction, so those cannot be
  re-verified from this repository. **Named people are real and living**: do not
  merge, infer or extend an identity here without a source that states it. One
  correction and one explicitly-inferred lead landed 2026-07-28 and are marked
  at the lines they affect.
- **Last updated:** 2026-07-28
- **Summary:** the credited development team, the 2003 PC port team, and where
  the people traced so far are now.

### Core Development Team (Lost Toys Website, c. 2003)

#### Directors

| Name | Role | Bullfrog Credits |
|------|------|------------------|
| **Glenn Corpes** | Technical Director, Graphics Engine Programmer | Co-designed *Populous*; Technical Director for all 4 years of Lost Toys |
| **Darran Thomas** | Director, Head of Art, Designer | *Dungeon Keeper*, *Theme Hospital*, *Syndicate Wars*, *Theme Park World* |
| **Jeremy Longley** | Director, Managing Director, Producer | *Dungeon Keeper*, *Theme Hospital*, *Syndicate Wars* |

#### Designers

| Name | Role | Notes |
|------|------|-------|
| **Alex Trowers** | Lead Designer | Game concept creator |
| **Jim Thompson** | Designer | Level design |

#### Programmers

| Name | Role | Notes |
|------|------|-------|
| **Stuart Gillam** | Lead Game Programmer | Active on Discord as desimbr; coded Gill-M boss |
| **Ben Carter** | Lead Programmer | Wrote post-mortem; PS2/Xbox engine code |
| **John Treece-Birch** | Programmer | |
| **Tony Monckton** | Programmer | |

#### Artists

| Name | Role | Notes |
|------|------|-------|
| **Jeremy "Jez" Elford** | Lead Art Director | Concept art |
| **Mike McCarthy** | Lead Artist | |
| **David Cathro** | Artist | |
| **Kate Kerrigan** | Artist | |
| **Mike Dove** | Artist | |
| **Dylan Murray** | Artist | |
| **Chris Young** | Artist | |
| **Alex Cave** | Artist | |
| **Paul Brierly** | Artist | |
| **Neil** (surname unknown) | Artist | Created breakable building models |

#### Audio

| Name | Role | Notes |
|------|------|-------|
| **Nathan McCree** | Composer | Primary composer |
| **Richard Jacques** | Composer | GANG Lifetime Achievement Award (2018); also *Sonic R*, *Mass Effect*, *Headhunter* |

**Richard Jacques** (born April 2, 1973) is an Ivor Novello award-winning, GRAMMY and BAFTA nominated composer. He composed at Sega Europe for seven years after graduating from the Royal Academy of Music.

**BEA Soundtrack**: No official commercial release exists. The main theme is available on SoundCloud (user: Valentin FRANCOIS). Music can be extracted from game files.

### PC Port Team (2003)

After the console versions were complete, the core team moved onto other projects. Lost Toys assigned additional staff to convert the internal PC development build into a retail release.

| Name | Role | Notes |
|------|------|-------|
| **Jan** (surname unknown) | PC Port Developer | Ex-Mucky Foot (Startopia, Urban Chaos); sat next to Stuart; changed cheat codes. See the lead recorded below. |

**Lead on Jan's surname — INFERRED, NOT CONFIRMED (recorded 2026-07-28).**
"Surname unknown" above is still accurate: nothing establishes who this Jan was.
It is recorded here only so the strongest available lead is visible rather than
buried in the RE corpus.

`cardid.txt`, a PC-retail-only GPU-tweak file loaded by
`CD3DApplication__LoadCardIdAndApplyVendorTweaks`, is credited to **Jan
Svarovsky and Tom Forsyth**, "originally from StarTopia at Mucky Foot" —
[modding-reference.md](../reverse-engineering/game-assets/modding-reference.md)
and
[game-folder-analysis.md](../reverse-engineering/game-assets/game-folder-analysis.md).
First name, former studio and named title all match this row.

**Why that is weaker than it looks, and must not be written in as fact:**

- The credit names **two** people, and "originally from StarTopia at Mucky Foot"
  most naturally describes the **file's** lineage, not either author's employment
  at Lost Toys. A file carried over from Startopia can reach Battle Engine Aquila
  without either author working on this game.
- The file's own header comment carries the same credit, so reading it does
  **not** settle the question; it only restates the lead.

**What would settle it:** a direct confirmation from Stuart Gillam, who sat next
to this Jan, or a surname in the retail PC credits or printed manual. Until one
of those exists, do not merge the two names.

**Note**: Encore Software was only the **publisher** for the PC version. The actual port work was done in-house at Lost Toys by Jan and possibly others. Stuart confirmed this on Discord (Dec 2025): *"The PC version was done inhouse at LT though. When the original console versions were complete the team moved onto other work and LT got a person or persons to convert our already 'inhouse' development version into something releasable."*

### Team Members Mentioned in Discord/Interviews

| Name | Role | Notes |
|------|------|-------|
| Stuart Gillam | Lead Game Programmer | Active on Discord as desimbr |
| Glenn Corpes | Technical Director | Terrain, shadows, impostor system, battle map, graphics engine; joined BEA Discord April 2025; YouTube: G7ennx |
| Alex Trowers | Lead Designer | Responsive on LinkedIn |
| Jeremy Longley | Co-Director | Now at FunFair Technologies |
| Ben Carter | Lead Programmer | Wrote GDM post-mortem |
| Jez Elford | Lead Art Director | Concept art |
| Jim (surname unknown) | Level Designer | With Alex |
| Neil (surname unknown) | Artist | Created breakable building models |
| Darran Thomas | Art Director / Founder | Stuart has Facebook contact |

### Where Are They Now?

#### Glenn Corpes
After Lost Toys closed, Glenn continued to innovate:
- **Weirdwood** (2003+): Founded after Lost Toys, focused on online-distributed games
- **Ground Effect** (2009): iOS racing game with "ground effect vehicles"
- **Topia World Builder** (2012): World simulation game, collaboration with Crescent Moon Games
- **22cans** (2012-2013): Worked for one year, contributed to *Curiosity – What's Inside the Cube?*
- **powARdup** (2017): AR arcade game, co-developed with his son Jack Corpes
- **Vector Suite** (2019-present): Heading R&D for surface generation technology (VR/AR design tools)
  - Working with **McLaren Automotive** on VR design systems
  - McLaren expects it to increase production from 4,000 to 6,000 cars/year by 2025

On VR: *"I've been fascinated by VR. In fact, I added support for three different VR headsets to Bullfrog's Magic Carpet back in 1995."*

**Contact**:
- LinkedIn: [glenn-corpes-3862611](https://www.linkedin.com/in/glenn-corpes-3862611/)
- Twitter/X: [@GlennCorpes](https://x.com/glenncorpes)
- YouTube: [G7ennx](https://www.youtube.com/@G7ennx)
- Personal site: [sites.google.com/site/glenncorpes/](https://sites.google.com/site/glenncorpes/)

#### Stuart Gillam
- Still codes C# part-time (non-gaming sector)
- Experiments with Unity game engine
- Active on Discord as "desimbr" / "desiado"
- **GitHub**: [stuart73](https://github.com/stuart73) - Preserving game history:
  - **Onslaught** - Original BEA source code (GPL-3.0). **CORRECTED 2026-07-28**;
    this previously read "(GPL-3.0, April 2025)". The drop is **staged**, and
    dating it to April 2025 understated it by roughly 3.4x and misdated the
    gameplay code this project ports from. MEASURED from the pinned repository's
    own git history: `2025-04-10` published LICENSE and README plus 30 platform,
    memory and controller files (`0fa6b19` +2, `f4ca46d` +30); `2025-12-12` added
    76 more including the `BattleEngine*` gameplay code (`24939a6` +72,
    `ac5eff7` +2, `a073df7` +2). The pinned checkout is **108 files at
    `5352a81` (2025-12-12)**, and 2 + 30 + 72 + 2 + 2 = 108 exactly. Commits
    after that point on `origin/main` add and then remove tooling and dotfiles,
    not source, and are not in the pinned checkout.
  - **AYAResourceExtractor** - Extract BEA models to FBX for Blender
  - **UnityPacmania** - Complete Pacmania arcade clone in Unity/C#
  - **DCMoHo** - Fork of Ball Breakers/MoHo for Dreamcast
  - **Rampant-reconstructed** - Recreation of his old Archimedes demo

#### Jeremy Longley
- Chief Executive Officer, **Betex Group Plc** (2005+)
- CTO & Co-Founder, **FunFair Technologies Ltd**
- Acting Consultant for Ladbrokes Plc and Gala Coral Ltd

#### Alex Trowers
- Lead Designer at **Kuju Entertainment Ltd** (post-Lost Toys)
- Creative Director at **Weirdwood Ltd** (Glenn's company)
- Designer at **Flaming Fowl Studios**
- 58 game credits spanning career (MobyGames)
- Responsive on LinkedIn for preservation efforts

**Original directors**: Hadn't been in regular contact with each other for 20+ years until Discord reunion (April 2025)
