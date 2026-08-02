# Attribution & Preservation Contributors

> Public note: this page keeps attribution, contribution history, and
> preservation context while omitting unnecessary direct-contact details.

## Original Development Contributors

### Stuart Gillam
- Role: lead game programmer at Lost Toys.
- Public preservation contribution:
  - shared useful internal-source files and technical guidance for preservation work
  - published public reference repos:
    - https://github.com/stuart73/Onslaught
    - https://github.com/stuart73/AYAResourceExtractor
  - confirmed several retail/internal differences and save/display implementation details
- Status: active preservation contact through public community channels.

### Alex Trowers
- Role: lead designer / concept creator.
- Contribution reflected here:
  - story and worldbuilding context
  - design background on mission/world constraints
- Status: historical contributor; no active technical role in this repo.

### Ben Carter
- Role: lead programmer on major engine/platform work.
- Public source used by this repo:
  - *Game Developer Magazine* post-mortem material describing development process, staffing, and cross-platform engine realities.
- Status: cited historical source.

### Glenn Corpes
- Role: technical director.
- Contribution reflected here:
  - terrain/landscape, impostor, shadow, and related rendering/system context referenced in preservation notes.
- Status: historical contributor with limited modern engagement.

### Other Lost Toys contributors
- Jez Elford: art direction / concept-art context.
- Jeremy Longley: studio leadership context.
- Jim (level design), Darran (art direction), and other team members appear in historical/community material where relevant.
- This repo uses those names only for attribution and historical context, not as operational contacts.

## Community Preservation Contributors

### vandal_117
- Provided a legitimate gold save baseline used in validation and regression work.
- Contributed player-verified strategy notes that helped ground progression and challenge assumptions.

### BermudaMaster
- Speedrun/community research that helped validate mission behavior, rating expectations, and gameplay edge cases.

### Early Discord/community researchers
- Community members including Jeppi, Baworo, Antares, NDjeneralBN, min473, and others contributed archival finds, research leads, modding discussion, or preservation interest.
- Their contributions are reflected across lore, roadmap, and archival notes where still useful.

### Project lead / current repo maintenance
- David (`dlprentice`) maintains the current editor/tooling effort, retail-static RE corpus, and release preparation work.

## Publisher / Rights Context

### Ziggurat Interactive
- Current Steam publisher for the commercial release.
- Public/publishing status is relevant to preservation context, but this repo does not treat Ziggurat as a confirmed source-code authority.
- Public trademark reference: https://trademark.justia.com/989/31/battle-engine-98931777.html

## Legal Status Note

- Lost Toys Ltd dissolved in 2003.
- Onslaught Toolkit is an unofficial community project and is not affiliated
  with or endorsed by a publisher or rights holder of *Battle Engine Aquila*.
- Users provide their own lawfully obtained retail game data. The current source
  tree and release packages do not include retail game assets or converted
  copies. Repository licenses grant no rights in the game executable,
  assets, source code, names, trademarks, or third-party components.
- Preserve the original game's credits and notices and all file-level,
  source-code, and third-party terms. Developer-provided reference materials
  retain their own documented provenance and licenses.
- `references/Onslaught/` is tracked as a reference submodule in this public
  repo. Its contents keep their own provenance/licensing and are not bundled
  into the portable WinUI app ZIP.

## Lead on the PC port developer's surname

Moved here 2026-08-01 from `lore/team-roster.md`, where it sat in a document a
player reads. The discipline in it is exemplary and the audience is not: a reader
wants to know who made the game, and a contributor needs to know why one plausible
name must not be written in as fact.

**Lead on Jan's surname — INFERRED, NOT CONFIRMED (recorded 2026-07-28).**
"Surname unknown" above is still accurate: nothing establishes who this Jan was.
It is recorded here only so the strongest available lead is visible rather than
buried in the RE corpus.

`cardid.txt`, a PC-retail-only GPU-tweak file loaded by
`CD3DApplication__LoadCardIdAndApplyVendorTweaks`, is credited to **Jan
Svarovsky and Tom Forsyth**, "originally from StarTopia at Mucky Foot" —
[modding-reference.md](../game-assets/modding-reference.md)
and
[game-folder-analysis.md](../game-assets/game-folder-analysis.md).
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
