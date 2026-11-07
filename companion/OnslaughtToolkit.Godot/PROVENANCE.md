# Companion provenance and license

Status: active independent GPL-3.0-only application boundary
Last updated: 2026-11-06 (provenance dates and references: the relicense time, the pre-release history, the frozen reverse-engineering copy, the submodule step, the Goodies page and the update-check members; 2026-11-04: installed model-definition preview lookup and its existing public-tool contracts)
Evidence: SOURCE — code-built C# application, project source moved in from the retired AppCore library, and embedded project lore; executed package boundaries are recorded in VALIDATION.md.
Summary: the companion's C# derives only from the project's own application code and the published contracts of the frozen `reverse-engineering/` copy (onslaught-preservation is the maintained home of the game documentation); it bundles the project's own lore, reads the game's files and manual art from the player's install at run time, and keeps retail data and GPL reconstruction out.

All C# in this project is original application code, GPL-3.0-only under the repository
[LICENSE](../../LICENSE) (it was MIT until 2026-10-22 UTC, commit `afa0ae4`; the project's own code was relicensed by
its author). Save layout facts and behavior were ported from the
`BesFilePatcher`, `SaveLabService` and their focused tests, through the companion's
earlier GDScript implementation. Options offsets, Goodie colours, rank letters, link
states and the evidence tier shown for each Goodie rule follow the documents in the frozen copy under [`reverse-engineering/`](../../reverse-engineering/RE-INDEX.md)
(frozen at Toolkit commit `fae54b7`, with the exceptions that RE-INDEX records; for a document that [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation)
also holds, that copy is the maintained one),
which name their specimens. Some rules are facts read from the developers' released source
(`references/Onslaught`, a submodule that is empty in a plain clone; [the public setup in README.MD](../../README.MD#public-setup) describes how to initialise it with `git submodule update --init --recursive`): the Goodie unlock rules, the gallery's row order and the god-flag
field's identity. They are checked against retail where the game's own Goodies page (its gallery screen; see the Goodies entry in [README.md](README.md)) says so, and no code
or comments were copied from that source. The interface, theme and styles are constructed in code from
Godot's built-in controls and default engine font.

These sources were written for the retired WinUI application's AppCore library and
moved into the companion before the initial public release (commit `840311c`, 2026-10-15, whose first tree already holds these files; the earlier history is not in this public repository), when the
companion became their only user; when AppCore itself was removed on 2026-10-22,
`FileMutationSafety.cs` was cut down to the members the companion calls: `Files/SaveLabFileTransaction.cs` and
`Files/FileMutationSafety.cs` (the OS file boundary), `Game/GameTextCatalog.cs` (the game's
language-table reader), `Careers/GoodieUnlockRequirementService.cs` (each Goodie's unlock
rule), `Careers/CheatCodeCatalog.cs` and `Careers/CheatSaveNameComposer.cs` (cheat names),
and `Lore/CampaignLoreComposer.cs` (the lore's mission list). On 2026-10-22 they left the
retired library's namespace for the companion's own (`OnslaughtToolkit.Companion.Files`,
`.Game`, `.Careers` and `.Lore`, by folder). The companion uses no other AppCore code or third-party AppCore media library;
AppCore's save-layout and file-safety test facts were carried into the companion's own tests. Godot .NET SDK `4.8.0-beta.1` and the
self-contained .NET runtime `Microsoft.NETCore.App` 10.0.13 (the `linux-x64` and `win-x64` runtime packs) are disclosed production dependencies with their MIT and
third-party notices, which every export carries. Godot retains its own MIT and third-party
licenses.

`BouncyCastle.Cryptography` 2.7.0, copyright The Legion of the Bouncy Castle Inc., is a production dependency
under the MIT licence. It verifies the CE update feed's Ed25519 signature in the signed-feed verifier (`CeUpdateFeed`), which the source keeps
for its tests: the app does not call the signed-feed verifier methods and contacts nothing. The Home panel ([`Ui/CeHomePanel.cs`](Ui/CeHomePanel.cs)) refers to the feed class only as `CeUpdateFeed.ManualAsync`, which returns fixed guidance without a request, and `CeUpdateFeed.ManualMessage`.
The exact version is declared in [OnslaughtToolkit.Godot.csproj](OnslaughtToolkit.Godot.csproj) and its package hash
is pinned by `contentHash` in [packages.lock.json](packages.lock.json). The build runner restores with
`--locked-mode`; every export copies the package's `LICENSE.md` as `BOUNCYCASTLE-LICENSE.txt`
([tools/companion_godot.py](../../tools/companion_godot.py)). The package is restored from NuGet, not vendored in
this repository, so it needs no vendored-source entry in `REUSE.toml`.

The repository's public lore library — [`lore/`](../../lore/_index.md) and
[`lore-book/BOOK.md`](../../lore-book/BOOK.md), which the retired WinUI app also shipped
as its offline reader — is embedded in the application as text when it is built.
The lore is CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](../../LICENSES/CC-BY-SA-4.0.txt)), and every
export carries that text as `LORE-LICENSE.txt`; quotations in it stay with their authors. Its own
articles name their sources.

The model and texture readers under [`Assets/`](Assets/) are written from the public format
documents in the frozen copy at [`reverse-engineering/asset-formats/`](../../reverse-engineering/asset-formats/_index.md)
(the AYA envelope, the CMSH grammar and record layouts, key evaluation, and the DDS
header). Those frozen documents, whose maintained home is [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), describe the private byte-matching decompilation's loaders in
prose; no decompiled or reconstructed code is copied into the companion, and only numbers (counts and
composed transforms) are compared between the two. The DXT block decoding is the standard
public algorithm.

`Assets/InstalledModelReferences.cs` implements the public Toolkit tools' bounded definition/resource contracts:
[`cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py) (`_physics_mesh_definitions`),
[`aya_cross_platform_compare.py`](../../tools/aya_cross_platform_compare.py) (`logical_key`) and
[`content_catalog.py`](../../tools/content_catalog.py) (`catalog_world`). It reads unit/feature mesh references and
requires a unique named resource in the selected archive. This is a static editor preview, not a copy of the game's
object initialization or simulation. Authored records test the lookup; local installed-map comparisons retain their
asset identities, hashes and captures only in private evidence.

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
