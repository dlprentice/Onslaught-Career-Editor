# Companion provenance and license

Status: active independent GPL-3.0-only application boundary
Last updated: 2026-10-22 (AppCore removed: the moved file-safety source cut down, its test facts carried over; facts read from the developers' source recorded; relicensed: the code GPL-3.0-only, the embedded lore CC BY-SA 4.0)
Evidence: SOURCE — code-built C# application, project source moved in from the retired AppCore library, and embedded project lore; executed package boundaries are recorded in VALIDATION.md.
Summary: the companion's C# derives only from the project's own application code and the RE lane's published contracts; it bundles the project's own lore, reads the game's files and manual art from the player's install at run time, and keeps retail data and GPL reconstruction out.

All C# in this project is original application code, GPL-3.0-only under the repository
[LICENSE](../../LICENSE) (it was MIT until 2026-10-22; the project's own code was relicensed by
its author). Save layout facts and behavior were ported from the
`BesFilePatcher`, `SaveLabService` and their focused tests, through the companion's
earlier GDScript implementation. Options offsets, Goodie colours, rank letters, link
states and the evidence tier shown for each Goodie rule follow the reverse-engineering
lane's documents under [`reverse-engineering/`](../../reverse-engineering/RE-INDEX.md),
which name their specimens. Some rules are facts read from the developers' released source
(`references/Onslaught`): the Goodie unlock rules, the gallery's row order and the god-flag
field's identity. They are checked against retail where the Goodies page says so, and no code
or comments were copied from that source. The interface, theme and styles are constructed in code from
Godot's built-in controls and default engine font.

These sources were written for the retired WinUI application's AppCore library and
moved into the companion (Git history follows them) on 2026-10-16, when the
companion became their only user; when AppCore itself was removed on 2026-10-22,
`FileMutationSafety.cs` was cut down to the members the companion calls: `Files/SaveLabFileTransaction.cs` and
`Files/FileMutationSafety.cs` (the OS file boundary), `Game/GameTextCatalog.cs` (the game's
language-table reader), `Careers/GoodieUnlockRequirementService.cs` (each Goodie's unlock
rule), `Careers/CheatCodeCatalog.cs` and `Careers/CheatSaveNameComposer.cs` (cheat names),
and `Lore/CampaignLoreComposer.cs` (the lore's mission list). They keep their original
namespace. The companion uses no other AppCore code or third-party AppCore media library;
AppCore's save-layout and file-safety test facts were carried into the companion's own tests. Godot .NET SDK `4.8.0-dev.6` and the
self-contained .NET runtime are disclosed production dependencies with their MIT and
third-party notices, which every export carries. Godot retains its own MIT and third-party
licenses.

The repository's public lore library — [`lore/`](../../lore/_index.md) and
[`lore-book/BOOK.md`](../../lore-book/BOOK.md), which the retired WinUI app also shipped
as its offline reader — is embedded in the application as text when it is built.
The lore is CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](../../LICENSES/CC-BY-SA-4.0.txt)), and every
export carries that text as `LORE-LICENSE.txt`; quotations in it stay with their authors. Its own
articles name their sources.

The model and texture readers under [`Assets/`](Assets/) are written from the public format
documents in [`reverse-engineering/asset-formats/`](../../reverse-engineering/asset-formats/_index.md)
(the AYA envelope, the CMSH grammar and record layouts, key evaluation, and the DDS
header). Those documents describe the private byte-matching decompilation's loaders in
prose; no decompiled or reconstructed code is copied into the companion, and only numbers (counts and
composed transforms) are compared between the two. The DXT block decoding is the standard
public algorithm.

The game's own material is never bundled. Mission names, Goodie titles and voice-line
transcripts are read from the player's `data/language/*.dat` and `text.stf`; music and voice
lines are played from the player's install; cutscenes are only listed. Home's banner and the
map of Allium are the images in the player's own `Manuals/Images/`, read when shown, and the
manual itself opens from the install in the player's browser. The icons and the emblem
(also the Windows program icon, drawn at export) are original vector shapes in code. No source from
`rebuild/` or `references/Onslaught`, decompiler output, proprietary asset, font, music,
executable or user save enters this application or its exports. Using Godot in both lanes
does not combine their licensing boundaries. No retail payload is required to build or
launch the companion.

Tests receive owned copies of the one registered
[real-save fixture](../../tests_shared/fixtures/README.md); it is neither modified nor
packaged. Test game folders, language tables and audio headers are tiny original bytes
built at run time. Captures, private inputs, test outputs and packages remain in ignored
`local-data/`.

Verification messages describe byte identity, file identity and an executed file
operation. They do not assert retail gameplay acceptance, crash or power-loss survival,
or Windows execution from a Linux test or cross-export.
