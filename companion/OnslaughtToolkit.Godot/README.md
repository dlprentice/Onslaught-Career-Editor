# Onslaught Toolkit companion

Status: native GDScript Save Lab implemented; Linux executed checks, Windows runtime acceptance pending
Last updated: 2026-09-19
Summary: an editor-authored MIT companion on standard Godot 4.8 dev6, with an explicit protected-file helper for the OS guarantees Godot cannot express.

The companion owns careers, saves, recovery copies, supported patches, media and
related preservation tools. Retail reverse engineering and the faithful GPL game
rebuild have separate owners. This project neither launches nor depends on that
rebuild. The September 19 migration uses standard Godot and typed GDScript for
presentation, save decoding, edit planning, comparisons and media inventory.

The one production C# exception is the explicitly packaged
[protected file bridge](../OnslaughtToolkit.FileBridge/README.md), within David's
permission to retain C# where necessary. Review demonstrated that Godot's exposed
APIs cannot preserve the required file guarantees. It links two existing MIT safety files
unchanged and performs protected reads/publication only. Its self-contained runtime
requires no installed .NET on the user's machine. There is no Godot .NET dependency,
C# save codec or undisclosed service. Removing the helper disables save operations;
there is no ordinary FileAccess-write fallback.

## Open and edit the project

Open `companion/OnslaughtToolkit.Godot/project.godot` using `~/.local/bin/godot48`.
The measured engine is **4.8.dev6.official.8898c2b3d**. Open
[SaveLab.tscn](SaveLab.tscn) to inspect the actual controls, containers, dialogs and
four tabs. [KillEditRow.tscn](ui/KillEditRow.tscn) is the reusable category row;
[MediaBrowser.tscn](ui/MediaBrowser.tscn) owns the media view. Change spacing,
labels, layout and presentation in the Inspector. The shared
[toolkit.tres](theme/toolkit.tres) owns colors and styles. Scripts attached to those
scenes handle behavior, rather than constructing the interface at runtime.
Tree rows are populated from selected user data. No retail assets or saves are
bundled, and the app does not automatically open the regression fixture.
GDScript `.uid` files are tracked editor metadata; the actual source project also
passed a headless standard-editor import with the retained C# references present.

From the repository or this lane's worktree:

```bash
npm run build:companion-godot
npm run test:companion-godot
npm run run:companion-godot
npm run export:companion-godot -- --platform both
```

Build/test/export are headless. **Run opens a window**; use it when the desktop is
available. The build records the Linux helper location in the ignored project
`.godot/companion_bridge_path.txt`, so F6/F5 in the source editor uses the same
helper. Development commands stage only native project resources into unique
canonical `local-data/companion/gdscript-*` directories. Imports, scratch, profiles,
logs, owned fixtures and packages live there, independently of other tasks.
Worktrees use the [canonical lab rules](../../LOCAL_LAB_OVERLAY.md); no research
corpus is copied. `--bridge /absolute/helper` can reuse a built Linux helper for
subsequent test/run commands. The tooling prints the exact output owner.

## Use Save Lab

1. **Open career…** selects a real `.bes`. A supported container is exactly
   10,004 bytes with version word `0x4BD1`. The app displays its full path,
   SHA-256, physical file identity and useful stored values. This shape check is
   format recognition, not proof of authenticity or game acceptance.
2. Inspect the **Career inspector** for mission records, broken/unknown links,
   raw ranks, Goodies, reserved slots and stored settings. Unsupported fields
   remain read-only. No guessed names or implicit unlocks are applied.
3. Check each count to change and enter its target. The preview names every
   selected old/new value and differing byte. Only the low three bytes per
   selected category may change; the fourth packed byte is preserved.
4. Choose a fresh `.bes` filename in an existing non-game folder. Choosing a
   filename does not write. **Write verified edit** explicitly publishes the
   preview. **Make unchanged recovery copy** ignores edit selections and publishes
   a byte-identical copy of the opened original instead.
5. The operation checks original identity/content again, stages and verifies all
   bytes, publishes without replacing any existing entry, and reopens the result.
   GDScript compares the returned and independently reopened bytes with the plan.
   The receipt reports path, hash, byte count and preservation checks. The original
   remains the source until **Open verified result** is explicitly selected.
6. **Compare copies** opens another supported career read-only and lists every
   differing byte, including bytes without a known interpretation.

Malformed inputs, changed sources, same-path/linked sources, existing or dangling
link destinations, missing helpers and unsupported protected operations fail
closed. The file dialogs cannot delete or create folders. Post-publication
uncertainty explicitly says that a copy may exist; it is never automatically
removed or reported as verified. A successful receipt concerns that operation,
not subsequent changes by another program or behavior inside the game.

**Media** inventories an explicitly chosen local folder: file names, relative
paths, formats and sizes. It skips links, bounds traversal and reports incomplete
results. This increment does not decode or play media and makes no playback claim.

## Migration goal and acceptance

The lane's deliverables are:

- A native editor-visible scene/resource structure and typed GDScript behavior,
  built using the exact shared standard-engine/template pins.
- A complete separate-copy Save Lab flow with honest inspection, explicit preview,
  unchanged-byte preservation, guarded publication and protected reopen; plus
  useful recovery-copy, comparison and read-only catalog increments.
- A narrow documented OS bridge only where API evidence requires it, reusing the
  existing safety implementation without importing legacy format/UI behavior.
- Executed real-fixture round trips, independent intended-change byte diffs,
  malformed/changed/conflicting input checks and publication-race regressions.
- Linux execution and isolated render evidence, separate Windows cross-export
  evidence, scoped documentation and normal commits/pushes. Windows runtime,
  human interaction and later legacy parity are never inferred from packaging.

The native test runs actual scene methods/controls and the packaged helper against
owned copies of the sole tracked fixture. Domain checks cover all categories,
0/24-bit limits, immutable snapshots, unknown bytes and corrected link states.
The separate bridge tests exercise identity replacement with identical content,
link aliases, destination conflicts and six Linux transaction-race/failure cases.
No synthetic career is created. Exact receipts and remaining platform acceptance
are recorded in [CURRENT_CAPABILITIES.md](../../CURRENT_CAPABILITIES.md) and
[VALIDATION.md](../../VALIDATION.md).

## Existing behavior and remaining migration

| Reference | Measured or source-established state | Native disposition |
|---|---|---|
| Old Godot `SaveLab.cs` / AppCore `SaveLabService` | C# runtime-built single-category shell; September 6 visible write/reopen acceptance unfinished | Replaced by editable scenes and GDScript planning; source retained for comparison |
| WinUI Save Lab / `BesFilePatcher` | Rich career/options analysis and editing | Native career inspection, multi-category count edits and comparison; broader rank, link, Goodie and options writes remain to migrate |
| `SafeCopyCatalog`, `SafeCopySaveRescue` | Game-copy catalog/rescue behavior with Windows-dependent mutation paths | Native verified career recovery copies now; whole-game copying/rescue remains |
| `BinaryPatchEngine`, tracked patch catalogs | Guarded patch planning/apply/restore in the retained toolkit | Supported patching remains a future coherent workflow; no native patch-apply claim |
| WinUI Media / `MediaCatalogService` | Catalog plus NAudio/LibVLC playback and replacement | Native metadata catalog now; playback/replacement and asset preview remain |
| Lore, assets, cheats, settings | Retained WinUI/AppCore services and tests | Retained as migration references; no native parity claim |

The old `SaveLab.cs`, `.csproj` and package lock stay as reference source and are
excluded from native staging/export. The bridge does not reference that project
or the AppCore assembly. One legacy analysis defect was intentionally not ported:
nonzero campaign links are not all complete; broken and unknown states are shown
separately. Mission-rank editing changes other fields in legacy code and is not
silently offered as a rank-only edit.

## Exact toolchain and rollback

[toolchain.json](toolchain.json) records the measured binary/template hashes and
shared lock revision. `tools/companion_godot.py` verifies the selected shared
installation and refuses mismatches. FileBridge's own `global.json` pins SDK
8.0.424; runtime 8.0.30 is bundled. Export presets target Linux x86_64 and Windows
x86_64. Keep the complete exported folder, including `file-bridge/`.

Adopt a later official 4.8 development/beta release only in an isolated worktree:
review upstream changes and API guarantees; retain the old pinned shared install;
update exact pins and matching templates; run affected codec, scene, transaction,
export and isolated-render checks. Do not upgrade through an unpinned `latest`.
Rollback uses the preceding committed project plus its preserved engine/templates
and its own import cache; never downgrade a newly saved project in another task's
checkout or erase its work. The pre-migration baseline is commit `25db5b23`.

See [PROVENANCE.md](PROVENANCE.md) for licensing and data boundaries.
