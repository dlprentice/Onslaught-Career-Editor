# Battle Engine Aquila - The Game

- **Status:** live preservation record — release, marketing and naming history
  from published material and developer recollection. The cheat table is the
  exception: it is backed by measurement, and where this page disagrees with
  [cheat-codes.md](../reverse-engineering/game-mechanics/cheat-codes.md) that
  page wins. Two changes landed 2026-07-28, each marked at the line it affects:
  one correction, and one note recording that the cheat table below is not
  exhaustive.
- **Last updated:** 2026-08-02
- **Summary:** release dates by platform, marketing copy, the "Onslaught" naming
  history, Battle Engine types and modes, how it was received, and the retail
  cheat codes.

### Release Information

| Platform | Release Date | Publisher |
|----------|--------------|-----------|
| **PlayStation 2** | January 27, 2003 (NA), February 28, 2003 (EU) | Infogrames Europe (Atari brand) |
| **Xbox** | January 27, 2003 (NA), February 28, 2003 (EU) | Infogrames Europe (Atari brand) |
| **Windows** | October 23, 2003 (NA), April 8, 2004 (EU) | Encore Software |
| **Steam/GOG** | September 4, 2020 | Ziggurat Interactive |
| **PlayStation 4/5** | May 20, 2025 | Ziggurat Interactive |

### Marketing

**Tagline**: "Lead By Force!"

**Official Description** (Infogrames, 2002):
> An epic battle rages between the Forseti and the Muspell as the oceans rise and land disappears. The Forseti compel you to help protect their remaining land by taking charge of the ultimate war machine – the Battle Engine. Whether in walking or in flying mode, you have access to an array of destructive weapons and you receive constant direction from base command. By commanding a device so powerful and advanced, your battlefield decisions will shape the direction of each engagement and, ultimately, the entire war.

**Advertised Features**:
- Feel the thrill of immediate, frenetic action as you engage in conflict from a first person perspective
- Immerse yourself in lush, expansive environments lit up by massive, raging battles
- Shape the direction of each battle by choosing where and how you launch your offensive
- Sniff out the opposition's weaknesses and deliver crippling blows with the most feared weapon on the battlefield
- Live the life of the reluctant hero, Hawk Winter, by progressing through a captivating plot

### The Name

The game went through several name changes during development:

| Element | Original | Final | Reason |
|---------|----------|-------|--------|
| **Game** | "Onslaught" | "Battle Engine Aquila" | Publishers thought players wouldn't be able to pronounce "Onslaught" |
| **Mech** | "Sleipnir" | "Aquila" | Sleipnir = Odin's eight-legged horse (Norse mythology) |
| **Protagonist** | "Hawk Aquila" | "Hawk Winter" | Changed when game was renamed (Hawk Eagle-in-Latin became redundant) |

#### The "Onslaught2" Mystery

From Discord (March 2025), when "ONSLAUGHT2" was found in Ghidra:

> "'Onslaught' was the code name of the game until we came up with BEA. I remember what the '2' represented too. We were using 'source safe' as the code management tool. Early on development source safe just screwed up (source safe was known for this). So I had to make a second code repository."

So "Onslaught2" = second Source Safe repository after a corruption incident, not a sequel.

### Battle Engine Types

| Type | Description | Special Ability |
|------|-------------|-----------------|
| **Pulsar** | Balanced loadout | Standard configuration |
| **Blazer** | Heavy firepower | Maximum damage output |
| **Lancer** | Precision strikes | Long-range capability |
| **Sniper** | Stealth capability | Invisible mode (only 1 airborne weapon: Vulcan Cannon) |

### Modes of Operation

| Mode | Weapons | Armor | Speed | Notes |
|------|---------|-------|-------|-------|
| **Jet Mode** | Lighter (2 per type, 1 for Sniper) | Standard | High | Flight limited by energy |
| **Walker Mode** | Stronger | Tougher | Slower | Four legs for stability, secure weapons platform |

### Gameplay Elements

The battles are well-simulated with:
- Beach landings
- Ambushes
- Airborne landing craft
- Artillery from naval forces
- Bombers and fighters engaging overhead

Strategic elements give players options:
- Take out enemy factories
- Distract fighters
- Harass landing craft
- Pick off specific targets

The campaign provides at least 8 hours of gameplay on the easiest difficulty.

### How It Landed

Merged here 2026-08-02 from `reception-legacy.md`, which was 43 lines of review
tables on its own shelf. How a game was received is part of what the game was,
not a separate subject, and a reader who wants the scores wants them beside the
release dates.

**These numbers are an undated snapshot.** No score below cites a retrieval date
or a URL, and aggregate scores drift as sites re-weight and reviews are added or
removed. Treat every one of them as "roughly this, at some point" until a source
and a date are attached.

| Platform | Metacritic | Consensus |
|----------|------------|-----------|
| **Xbox** | 76/100 | "Generally favorable reviews" |
| **PlayStation 2** | 73/100 | "Mixed or average reviews" |
| **Windows** | 65/100 | "Mixed or average reviews" |

| Publication | PC | PS2 | Xbox |
|-------------|----|----|------|
| **IGN** | 7.2/10 | 8/10 | 8/10 |
| **Eurogamer** | — | — | 8/10 |
| **GameSpot** | 6.1/10 | 6.7/10 | 6.7/10 |
| **Edge** | — | 7/10 | 7/10 |
| **Official Xbox Magazine** | — | — | 8.3/10 |
| **GamePro** | — | 3.5/5 | 4/5 |
| **PC Gamer** | 60% | — | — |

It placed **#86** in IGN's Top 100 PlayStation 2 Games.

The PC scores are the lowest of the three, which is worth knowing if you are
reading this while playing the PC version: the reviews of the day were marking a
2003 port that shipped nine months after the console versions.

Despite the reception, it sold poorly — IGN's account. The team's own verdict has
aged better than the numbers did:

> "Battle Engine Aquila was the best thing I ever worked on."
> — Glenn Corpes, *Retro Gamer* #160 (October 2016)

### In-Game Cheat Codes

Steam/retail PC codes (entered as save/player name substring):

| Code | Effect | Notes |
|------|--------|-------|
| `MALLOY` | All goodies unlocked | Runtime-only cheat path; patcher can replicate save-state result |
| `TURKEY` | All missions unlocked | Runtime-only cheat path; patcher can replicate save-state result |
| `Maladim` | God mode toggle | Live-confirmed: with `Maladim` in the save/player name, start a mission, pause, open `Controller Options`, and the cheat-gated line appears as `God OFF` / `God ON`. While on, normal combat damage stops sticking. Already-lost hull is **not** restored by toggling it back on. See [cheat-codes.md](../reverse-engineering/game-mechanics/cheat-codes.md). |

**This table is not the whole cheat table.** Three further strings decode out of
the retail table — `V3R5IOF`, `Aurore` and `lat\xEAte` — and are documented with
their gating and call sites on the RE page,
[cheat-codes.md](../reverse-engineering/game-mechanics/cheat-codes.md). They are
omitted here because they are debug/version paths rather than player-facing
cheats, not because they do not exist. (Note added 2026-07-28; nothing above was
changed by it.)

Historical/internal-source codes (`B4K42`, `!EVAH!`, `105770Y2`) are not the Steam retail cheat table.
