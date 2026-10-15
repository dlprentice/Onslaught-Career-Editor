# The Same War on Different Platforms

- **Status:** live preservation record. This page summarizes measured PC/Xbox/PS2
  content tables and the authored PC/PS2 manuals; it does not turn matching
  names into executable or asset parity. The full hashes, counts, and unknowns
  are in the
  [platform content crosswalk](../reverse-engineering/PLATFORM_CONTENT_CROSSWALK.md).
- **Last updated:** 2026-08-22
- **Summary:** what PC, Xbox, and PS2 really share — one 43-title campaign and
  one setting, alongside distinct real worlds 0, 888, and 201 and regional
  assets that must not be flattened into aliases.

Battle Engine Aquila was built for several machines, then ported to PC. That
makes an ordinary lore question surprisingly technical: is a name part of the
war all players saw, or did it arrive in one release?

The answer is now byte-strong for the canonical text tables on all three
platforms, and deliberately narrower for resource payload behavior.

## The foundation is shared

The English PC manual and the USA PlayStation 2 manual both establish the same
setting:

- Allium is an Earth-like planet in the Porrum system;
- the Forseti and Muspell historically occupy the Ampeloprasum Archipelago;
- the Sohra Treaty of 1174 sets Kensor aside as a demilitarized zone;
- Forseti territory runs from Forseti Major to Castellian;
- Muspell territory runs from Iron Isle to Sentinel; and
- Hawk Winter is a Forseti dockworker whose night life is loader racing.

Those are authored manual facts, not a later community reconstruction. One OCR
file reads `Rensor`, but the PS2 page and its map both visibly say **Kensor**.
That is a scan error, not alternate regional geography.

The manuals use American or British spelling in places. Spelling is a release
edit; it does not make two versions of Allium.

## One campaign title set across all three platforms

Each release carries six language tables: American, English, French, German,
Italian, and Spanish. The canonical PS2 tables inside `DATA0.NYO` are
byte-identical to PC and contain 2,571 text IDs. The Xbox tables contain 2,537:
their entire set appears in PC/PS2, which have 34 additional frontend,
controller, and memory-device labels.

The story-sized result is simpler: all six languages carry the same **43**
mission codes and titles on PC, Xbox, and PS2. None is platform-only and none
has a different title. Xbox Europe/Korea/USA carry byte-identical copies of all
six Xbox tables; PS2 Europe and USA carry byte-identical `DATA*.NYO` packages.

That does not change how the toolkit treats the text. Mission names still come
from the player's own copy rather than being bundled into this project. It does
mean the 43-title surface is a shared PC/PS2/Xbox content contract, not a PC-port
invention. The measurement establishes authored bytes, not which language a
running console selects.

## The eight characters are not PC-only

The retail shelf has eight profiles: Hawk Winter, Tatiana Kiralova, Chuck
Kramer, Lewis Carver, Jason Lorenzo, Tara Fox, Billy Casbah, and Archanus Surt.
Together they occupy 96 named profile fields.

All 96 fields in every PS2 canonical table are byte-identical to PC. Xbox
English, French, Italian, and Spanish agree too. Xbox American has two differing
profile fields and Xbox German has one, so localized prose must not be flattened
into an invented universal wording.

The English profiles in [Characters](characters.md) therefore describe a shared
PC/PS2/Xbox authored shelf. This still says nothing about unlock conditions or
whether every profile is normally seen by every player.

## A shared core, not the same world-resource set

PC retail and all three measured Xbox regions carry the same **66** numeric
world-resource IDs: the 43 career worlds and the 23 additional shipped worlds
listed in [The Worlds of the Campaign](worlds.md). PS2 is not the same set.
Its exact RCDF index has **67** numeric resource names: 65 shared with PC/Xbox,
PS2-only `000` and `888`, and no `201_res_PS2.aya` counterpart.

Opening the three-ID family settles what the filenames represent:

- **PS2 `000` is world 0.** Its nested world record says id 0, mode 0, four
  Battle Engine configurations, and no compiled script objects. Separate PS2
  `base`, `Frontend`, and `Loading` archives rule out a global/default-container
  alias. What world 0 was for, and whether a player could normally reach it,
  remain unknown.
- **PS2 `888` is a multiplayer world.** Its nested record says id 888 and mode
  2, the retail multiplayer predicate accepts mode 2 and levels 850 through
  899, and its three scripts and named resources pair Fenrir with Venturer. The
  regular multiplayer selector stops at 879, so this proves a shipped world,
  not a normal menu route.
- **PC/Xbox `201` is world 201.** Both containers carry the same id-201,
  mode-0, Aquila Prototype header and 13 compiled scripts. It is not in the
  career graph. PS2 has no numeric 201 member, and no measured evidence says
  whether that authored scenario exists there by another route.

The different world IDs, modes, headers, script counts, WRES hashes, and logical
asset sets refute a `000`/`888`/`201` packaging-alias theory. They do not turn
any of the three into a newly proved career mission.

Xbox Europe still has different resource bytes for worlds 612, 856, and 863
even though the world numbers remain present. It also has a different
goodie-124 resource and a different cutscene 24. Korea and USA match each other
for those five files.

A reconstruction can therefore share the campaign graph and world names while
still needing platform- or region-specific content packages.

## Small words that really changed

English has 30 changed shared text rows between PC and Xbox. Twenty-five concern
controllers, memory devices, or frontend behavior. The five content-facing
rows are one briefing and four Goodies entries. Their differences are tiny — a
word or typo, and one `02`/`03` title change — but they are real.

This project records those variants rather than silently choosing a winner.
Without source chronology or a design document, “different” does not mean the
PC text is corrected, nor that Xbox is canonical.

## What remains unknown

The PS2 RCDF index, six canonical language tables, and two targeted numeric
world members are now decoded far enough for this crosswalk. The other 4,152
indexed payloads were not opened here. The measurement does not prove runtime
language selection, world-0 purpose, normal world-888 frontend reach, or how
PC/Xbox world 201 is routed on PS2.

Matching language metadata also does not prove that voice files or videos match
across machines. Those are separate assets with their own evidence.

## Evidence

The full reproducible boundary is in
[Platform content crosswalk: PC, Xbox, and PS2](../reverse-engineering/PLATFORM_CONTENT_CROSSWALK.md),
with compact no-payload receipts beside it. The comparison reads user-owned
retail files and publishes counts, hashes, token names, and conclusions — not
the game's string tables, disc images, or extracted assets.
