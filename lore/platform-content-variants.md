# The Same War on Different Platforms

- **Status:** live preservation record. This page summarizes measured PC/Xbox
  content tables and the authored PC/PS2 manuals; it does not turn matching
  names into executable or asset parity. The full hashes, counts, and unknowns
  are in the
  [platform content crosswalk](../reverse-engineering/PLATFORM_CONTENT_CROSSWALK.md).
- **Last updated:** 2026-08-22
- **Summary:** what the PC, Xbox, and PS2 evidence really shares — one campaign
  identity and one setting, alongside small text edits and real regional assets.

Battle Engine Aquila was built for several machines, then ported to PC. That
makes an ordinary lore question surprisingly technical: is a name part of the
war all players saw, or did it arrive in one release?

The answer is now fairly strong for PC and Xbox, and deliberately narrower for
PlayStation 2.

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

## One PC/Xbox campaign title set

Each release carries six language tables: American, English, French, German,
Italian, and Spanish. The PC tables contain 2,571 text IDs; the Xbox tables
contain 2,537. Xbox's entire set appears in PC, while PC has 34 additional
frontend, controller, and memory-device labels.

The story-sized result is simpler: all six languages carry the same **43**
mission codes and titles on PC and Xbox. None is PC-only, none is Xbox-only, and
none has a different title between those two platforms. The Xbox Europe, Korea,
and USA archives also carry byte-identical copies of all six language tables.

That does not change how the toolkit treats the text. Mission names still come
from the player's own copy rather than being bundled into this project. It does
mean the 43-title surface is a shared PC/Xbox content contract, not a PC-port
invention.

## The eight characters are not PC-only

The retail shelf has eight profiles: Hawk Winter, Tatiana Kiralova, Chuck
Kramer, Lewis Carver, Jason Lorenzo, Tara Fox, Billy Casbah, and Archanus Surt.
Together they occupy 96 named profile fields.

All 96 English fields are text-identical between PC and Xbox. French,
Italian, and Spanish agree too. American has two differing profile fields and
German has one, so localized prose must not be flattened into an invented
universal wording.

The English profiles in [Characters](characters.md) therefore describe a shared
PC/Xbox authored shelf. This still says nothing about unlock conditions or
whether every profile is normally seen by every player.

## The same worlds, not always the same bytes

PC retail and all three measured Xbox regions carry the same **66** numeric
world-resource IDs: the 43 career worlds and the 23 additional shipped worlds
listed in [The Worlds of the Campaign](worlds.md).

That is identity, not asset parity. Xbox Europe has different resource bytes for
worlds 612, 856, and 863 even though the world numbers remain present. It also
has a different goodie-124 resource and a different cutscene 24. Korea and USA
match each other for those five files.

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

The PlayStation 2 manual proves the shared setting, but the retail PS2 data
package has not yet been decoded into the same language/profile/world
crosswalk. No claim on this page promotes manual agreement into PS2 byte
identity.

Matching language metadata also does not prove that voice files or videos match
across machines. Those are separate assets with their own evidence.

## Evidence

The full reproducible boundary is in
[Platform content crosswalk: PC, Xbox, and the PS2 manual](../reverse-engineering/PLATFORM_CONTENT_CROSSWALK.md),
with the compact no-payload receipt beside it. The comparison reads user-owned
retail files and publishes counts, hashes, token names, and conclusions — not
the game's string tables, disc images, or extracted assets.
