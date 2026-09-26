# Onslaught Toolkit companion

Status: C# Save Lab built entirely in code on Godot 4.8 dev6 .NET; Linux executed checks, Windows runtime acceptance pending
Last updated: 2026-09-25
Summary: the MIT companion is a C# application whose interface, theme, career codec, media inventory and file-safety boundary are all code; its one scene only attaches the root script.

The companion owns careers, saves, recovery copies, supported patches, media and
related preservation tools. Retail reverse engineering and the faithful GPL game
rebuild have separate owners; this project neither launches nor depends on that rebuild.

## Layout

Everything is C# on Godot 4.8 dev6 .NET. [Main.tscn](Main.tscn) is a one-node wrapper
that attaches [CompanionApp](Ui/CompanionApp.cs); every control, container, dialog
and style below it is constructed in code. There is no GDScript, saved resource or
editor-authored scene, and `npm run build` refuses to stage one.

| Folder | Owner of |
| --- | --- |
| [Careers](Careers/) | The career byte codec (`CareerSave`), immutable open snapshots (`SaveSession`) and the open/publish/compare workflow (`CareerWorkspace`) |
| [Files](Files/) | The protected OS file boundary (`ProtectedSaveFiles`) and the worker that keeps it off the interface thread |
| [Media](Media/) | The bounded, read-only media filename inventory |
| [Ui](Ui/) | The code-built interface: theme, root, pages and rows |
| [Tests](Tests/) | Every behavioral contract, run headlessly inside Godot |
| [Development](Development/) | Development-only entries such as export license metadata |

`Tests/` and `Development/` compile only into development builds; release exports
exclude them from both the assembly and the package.

## Build, test, run and export

From the repository or this lane's worktree:

```bash
npm run build:companion-godot
npm run test:companion-godot
npm run run:companion-godot
npm run export:companion-godot -- --platform both
```

Build, test and export are headless. **Run opens a window**; use it when the desktop is
available. Each command stages the project and its two linked MIT safety source files
into a unique canonical `local-data/companion/` directory with isolated imports, profiles,
scratch and logs, and prints that directory. Worktrees use the
[canonical lab rules](../../LOCAL_LAB_OVERLAY.md); no research corpus is copied.

`npm test` runs `Tests/CompanionTestRunner.cs` against an owned copy of the one tracked
[real-save fixture](../../tests_shared/fixtures/README.md), then the launcher's own checks.
The suite covers the codec on the real bytes (all categories, 0/24-bit limits, immutable
plans, unknown bytes, link and Goodie states), the media inventory, the protected adapter
(round trips, malformed arguments, changed or replaced sources, conflicting and game-tree
destinations, symbolic and hard links), six Linux publication-race cases through the linked
transaction's internal hook, and the code-built interface driving its real controls.

## Use Save Lab

1. **Open career…** selects a real `.bes`. A supported container is exactly
   10,004 bytes with version word `0x4BD1`. The app shows its full path, SHA-256,
   physical file identity and stored values. This shape check is format recognition,
   not proof of authenticity or game acceptance.
2. **Career inspector** lists mission records, links (broken and unknown states are never
   called complete), raw ranks, Goodies, reserved slots and stored settings. Unsupported
   fields stay read-only; no guessed names or implicit unlocks are applied.
3. Check each count to change and enter its target. The preview names every selected
   old/new value and differing byte. Only the low three bytes of each selected category
   may change; the fourth packed byte is preserved.
4. Choose a fresh `.bes` filename in an existing folder outside the game. Choosing a
   filename does not write. **Write verified edit** publishes the preview; **Make
   unchanged recovery copy** ignores edit selections and publishes a byte-identical copy.
5. Publication re-checks the original's identity and content, stages and verifies all
   bytes, publishes without replacing any existing entry and reopens the result. The
   companion compares the returned and independently reopened bytes with the plan and
   reports path, hash and preservation checks. The original stays the source until
   **Open verified result** is chosen.
6. **Compare copies** opens another supported career read-only and lists every differing
   byte, including bytes without a known interpretation.

Malformed inputs, changed sources, same-path or linked sources, existing or dangling
link destinations and unavailable protected access fail closed; there is no ordinary
write fallback. The file dialogs cannot delete or create folders. Post-publication
uncertainty says that a copy may exist; it is never deleted or reported as verified.
A receipt concerns that operation, not later changes by another program or behavior
inside the game. File work runs on one worker thread; the interface stays responsive,
waits for the result and defers closing while a transaction is running.

**Media** inventories an explicitly chosen local folder: names, relative paths,
formats and sizes. It skips links, bounds traversal and reports partial results.
It does not decode or play media.

## File-safety boundary

[ProtectedSaveFiles](Files/ProtectedSaveFiles.cs) links the MIT
[`SaveLabFileTransaction.cs`](../../OnslaughtCareerEditor.AppCore/SaveLabFileTransaction.cs) and
[`FileMutationSafety.cs`](../../OnslaughtCareerEditor.AppCore/FileMutationSafety.cs) unchanged; it
imports no AppCore assembly, save codec or media library. On Linux it opens sources
descriptor-relative without following links, compares physical identity and link count,
stages into an unnamed file, flushes it, and publishes with a no-clobber link.
These checks do not prove behavior after power loss. The Windows implementation locks
ancestors and verifies identity, but releases its staging quarantine and closes the handle
before a path-based move, then verifies the published identity; Windows execution remains
unverified here, and a Windows cross-export is not acceptance.

## Exact toolchain and rollback

[toolchain.json](toolchain.json) records the measured engine, SDK and template hashes and
the shared lock revision; `tools/companion_godot.py` verifies the installation and refuses
mismatches. `global.json` pins .NET SDK 8.0.424; the Godot SDK is `4.8.0-dev.6` and the
runtime `8.0.30`. Export presets target Linux x86_64 and Windows x86_64, and Godot's normal
.NET export bundles the runtime, so packages need no installed .NET. Adopt a later engine
only in an isolated worktree with updated pins, matching templates and a full rerun of the
suite, exports and captures; roll back with the preceding commit and its preserved engine.

See [PROVENANCE.md](PROVENANCE.md) for licensing and data boundaries.
