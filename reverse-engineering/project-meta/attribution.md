# Attribution & Preservation Contributors

Status: active — attribution, preservation credits and the screenshot register
Last updated: 2026-10-22 (source-code notes keep the quoted source's GPL; save fixture licence note; earlier: licence summary, ExuberantParrot credits)
Summary: who contributed what, the licence boundaries of reference material, and the tracked-screenshot register.
Evidence: SOURCE — contributors' public credits and published repositories; the register is checked against `git ls-files` by `tools/check_registered_screenshots.py`

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

### ExuberantParrot
- [PR #1](https://github.com/dlprentice/Onslaught-Career-Editor/pull/1) (merged 2026-07-21):
  corrected the script-VM field labels in
  [`ScriptObjectCode.cpp.md`](../binary-analysis/functions/ScriptObjectCode.cpp.md)
  (`+0x5C` event gate, `+0x64` instruction-count copy) and the `CSymtab` container
  layout in [`Symtab.cpp.md`](../binary-analysis/functions/Symtab.cpp.md). Its text
  is still present and was contributed under the repository's MIT licence of the
  time; it stays under that notice ([`LICENSES/MIT.txt`](../../LICENSES/MIT.txt))
  alongside CC BY-SA 4.0, and `REUSE.toml` marks the two files
  `CC-BY-SA-4.0 AND MIT`.
- [PR #2](https://github.com/dlprentice/Onslaught-Career-Editor/pull/2) (closed
  2026-07-22): diagnosed the white wash over impact and explosion sprites in the
  first-flight view. The fix was written independently on `main` from that
  diagnosis, so no PR #2 text is carried; the diagnosis is credited here.

### Early Discord/community researchers
- Community members including Jeppi, Baworo, Antares, NDjeneralBN, min473, and others contributed archival finds, research leads, modding discussion, or preservation interest.
- Their contributions are reflected across lore, roadmap, and archival notes where still useful.

### Project lead / current repo maintenance
- David (`dlprentice`) maintains the current editor/tooling effort, retail-static RE corpus, and release preparation work.

## Licences

- Project code (the companion, AppCore, `tools/`, `patches/` and `tests_shared/`
  scripts, and `rebuild/`) is GPL-3.0-only: the root [`LICENSE`](../../LICENSE),
  also at [`LICENSES/GPL-3.0-only.txt`](../../LICENSES/GPL-3.0-only.txt). The
  companion and tools were MIT until 2026-10-22, when their author relicensed them.
- Documentation and lore are CC BY-SA 4.0
  ([`LICENSES/CC-BY-SA-4.0.txt`](../../LICENSES/CC-BY-SA-4.0.txt)). Quotations
  in the lore stay with their authors, quoted for commentary and preservation.
- `reverse-engineering/source-code/` quotes and documents Stuart Gillam's
  published Onslaught source (GPL version 3 only): those notes are
  CC BY-SA 4.0 and GPL-3.0-only, crediting Stuart alongside the project, and the
  quoted source keeps its own licence.
- The `aya-*` notes in that folder quote Stuart's separate AYAResourceExtractor
  instead, whose root licence is MIT: those notes are CC BY-SA 4.0 and MIT.
- The gold career save fixture (`tests_shared/fixtures/gold_career_save.bin`,
  vandal_117's real save) is game data contributed as a test baseline; no
  project licence is claimed for it.
- ExuberantParrot's PR #1 passages keep their MIT notice
  ([`LICENSES/MIT.txt`](../../LICENSES/MIT.txt)) as well.
- [`REUSE.toml`](../../REUSE.toml) maps paths to these licences; per-file SPDX lines
  take precedence where present. Contributions come in under the same terms
  ([`CONTRIBUTING.md`](../../CONTRIBUTING.md)).
- `references/` submodules, Godot and the .NET runtime keep their own licences.

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
  copies, with the single narrow exception of the screenshots registered below.
  Repository licenses grant no rights in the game executable,
  assets, source code, names, trademarks, or third-party components.
- Preserve the original game's credits and notices and all file-level,
  source-code, and third-party terms. Developer-provided reference materials
  retain their own documented provenance and licenses.
- `references/Onslaught/` is tracked as a reference submodule in this public
  repo. Its contents keep their own provenance/licensing and are not bundled
  into the companion app.

## Registered screenshots

Every picture of the game tracked in this repository is listed here, per the
screenshot allowance in [`AGENTS.md`](../../AGENTS.md). The register exists so a
later reader can tell a deliberate choice from a mistake, and so the count stays
visibly small. Bulk capture directories are not eligible and stay in the ignored
local overlay.

The distinction the allowance rests on: these are new works made by running the
game, not files copied out of it. No extracted texture, model, audio or video
may be registered here — photographing an asset through a viewer does not
launder it.

| Path | Source | Captured | Why it is tracked |
|---|---|---|---|

No screenshot is tracked today. The two that were registered here
(`title-screen.jpg` and `mission-vista.jpg`, re-encoded from the 2026-07-26
pristine-verification captures of `BEA.exe` `74154bfa…`) left the repository with
the retired WinUI shell on 2026-10-15; the PNG originals stay under `local-lab/`.

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
