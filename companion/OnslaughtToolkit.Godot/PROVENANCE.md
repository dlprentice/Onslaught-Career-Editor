# Companion provenance and license

Status: active independent MIT application boundary
Last updated: 2026-09-26
Evidence: SOURCE — code-built C# application, linked MIT AppCore source and embedded project lore; executed package boundaries are recorded in VALIDATION.md.
Summary: the companion's C# derives only from MIT application references and the RE lane's published contracts; it bundles the project's own lore, reads the game's files from the player's install at run time, and keeps retail data and GPL reconstruction out.

All C# in this project is original MIT application code under the repository
[LICENSE](../../LICENSE). Save layout facts and behavior were ported from the MIT
`BesFilePatcher`, `SaveLabService` and their focused tests, through the companion's
earlier GDScript implementation. Options offsets, Goodie colours, rank letters, link
states and the evidence tier shown for each Goodie rule follow the reverse-engineering
lane's documents under [`reverse-engineering/`](../../reverse-engineering/RE-INDEX.md),
which name their specimens. The interface, theme and styles are constructed in code from
Godot's built-in controls and default engine font.

These MIT AppCore sources are linked unchanged, never copied or forked:
`SaveLabFileTransaction.cs` and `FileMutationSafety.cs` (the OS file boundary),
`GameTextCatalog.cs` (the game's language-table reader), `GoodieUnlockRequirementService.cs`
(each Goodie's unlock rule), `CheatCodeCatalog.cs` and `CheatSaveNameComposer.cs` (cheat
names), and `CampaignLoreComposer.cs` (the lore's mission list). The companion imports no
AppCore assembly or third-party AppCore media library. Godot .NET SDK `4.8.0-dev.6` and the
self-contained .NET runtime are disclosed production dependencies with their MIT and
third-party notices, which every export carries. Godot retains its own MIT and third-party
licenses.

The repository's public lore library — [`lore/`](../../lore/_index.md) and
[`lore-book/BOOK.md`](../../lore-book/BOOK.md), which the retained WinUI package also
shipped as its offline reader — is embedded in the application as text when it is built.
Its own articles name their sources.

The game's own material is never bundled. Mission names, Goodie titles and voice-line
transcripts are read from the player's `data/language/*.dat` and `text.stf`; music and voice
lines are played from the player's install; cutscenes are only listed. No source from
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
