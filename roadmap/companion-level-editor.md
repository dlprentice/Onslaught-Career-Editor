# Companion Level Editor: Design and Prototype Plan

Status: M0 (the data layer) and M1 (the mod stager and the edit session) are built and on main; M2 (the first page: a level picker, an object table, typed X, Y and Z, Save as mod) is built and in review; M3 to M6 are plan. Nothing in it has been played in a CE release yet.
Last updated: 2026-10-29 (M0 and M1 built and integrated, M2 built; earlier: first draft; the measurements in section 3 were taken on 2026-10-29 on the read-only retail view)
Summary: how the Companion can grow a visual level editor on top of the Toolkit's world tools and Onslaught CE's mod
loader: list a level's objects, select one, move it by typing coordinates or dragging it on a top-down map, and save
the result as a CE mod that CE loads without hand editing. It states what exists, what the measurements say, the
layers and files to add, a minimal first prototype (typing a coordinate, saving a mod, seeing it in game) and the
milestones after it.
Evidence: MEASURED for section 3 (each item names its method and limits), SOURCE for the cited code, INFERRED where
the text says so; the rest is plan.

## 1. What the editor is for

A player or modder opens a level, sees what the level places (the player's start, units, features, waypoints,
triggers), moves something, and plays the change. The first version edits **where things stand** in a level's world
body and nothing else: no terrain, no models, no mission scripts, no new object types. The result is always a CE mod
folder (a new folder, never a change to the game's files), so a player can switch it off by removing one word from
`ce.ini`, and the game's own files stay as they were.

This follows the existing split of work: the Toolkit's Python tools are the reference implementation and the oracle
for the file format; the Companion is the player's interface; Onslaught CE is the engine that loads the result.

## 2. What exists today

| Piece | Where | State |
| --- | --- | --- |
| World body reader and writer, byte for byte | [`tools/world_resources_encode.py`](../tools/world_resources_encode.py) (`read_world_model`, `write_world_body`) | on main; round-trips every retail world body in the tested installation |
| Object list: ordinal, kind, name, position | [`tools/world_thing_index.py`](../tools/world_thing_index.py) | on main; ordinals are rows of one body, not runtime slots |
| Read-only preview of an edit, with pins | [`tools/world_edit_preview.py`](../tools/world_edit_preview.py) | on main |
| One position edit, emitted as a model | [`tools/world_edit_move.py`](../tools/world_edit_move.py) | on main; it prints the two hashes a later step must pin |
| Packaging an edited world as a CE mod folder | `world_resources_encode.py stage --as-mod`, writer `tools/world_mod_stage.py` | on main, reviewed |
| The Companion's data layer: world bodies, level archives, the mod stager, an edit session with undo | [`companion/OnslaughtToolkit.Godot/Levels/`](../companion/OnslaughtToolkit.Godot/Levels) (M0, M1) | on main, reviewed; checked against the Python reference on generated vectors and, locally, on every retail world body |
| The Level editor page (M2) | `Ui/Pages/LevelEditorPage.cs`, `Ui/SaveAsModDialog.cs`, `Levels/LevelEditorModel.cs`, `Levels/CoordinateInput.cs` | built and in review; the mod it saves for a move of one Target Tank is byte for byte the one the Toolkit pipeline stages for the same move; not yet played |
| CE loading a world file from a mod (a mod may add `data/worlds/worldNNN.wrd`) | Onslaught CE's mod loader and its world-file override | planned for CE 0.1.11; not released at the time of writing; Windows later |
| A code-built Godot C# interface, a game library, verified file safety | `companion/OnslaughtToolkit.Godot/` | on main |

Parts of the Companion the editor can reuse as they are:

- Pages are plain objects on a shared shell: [`Ui/Page.cs`](../companion/OnslaughtToolkit.Godot/Ui/Page.cs) and
  [`Ui/AppServices.cs`](../companion/OnslaughtToolkit.Godot/Ui/AppServices.cs) (the open game, the status line, the
  popup layer). Layout is built in code with [`Ui/Build.cs`](../companion/OnslaughtToolkit.Godot/Ui/Build.cs) and the
  theme; there are no editor-authored scenes.
- A custom-drawn control with hover and hit testing already exists:
  [`Ui/CampaignMap.cs`](../companion/OnslaughtToolkit.Godot/Ui/CampaignMap.cs) draws in `_Draw` and answers
  `NodeAt(position)`. The level map is the same pattern with pan, zoom and drag added.
- The page that previews the game's models and textures,
  [`Ui/Pages/AssetsPage.cs`](../companion/OnslaughtToolkit.Godot/Ui/Pages/AssetsPage.cs), shows the Companion can read the
  player's installed game data and render 3D in a `SubViewport`; a model preview of the selected object is a later add.
- The game's `.aya` envelope is already read in C#:
  [`Assets/AyaContainer.cs`](../companion/OnslaughtToolkit.Godot/Assets/AyaContainer.cs).
- Output safety: [`Files/FileMutationSafety.cs`](../companion/OnslaughtToolkit.Godot/Files/FileMutationSafety.cs) refuses
  output inside a game folder and offers new-file-only publication; [`Game/GameLibrary.cs`](../companion/OnslaughtToolkit.Godot/Game/GameLibrary.cs)
  knows the game folders and CE's user folder.
- Tests run headless through the repository's launcher (`npm run test:companion-godot`) from
  [`Tests/CompanionTestRunner.cs`](../companion/OnslaughtToolkit.Godot/Tests/CompanionTestRunner.cs); captures of the real
  interface come from `npm run capture:companion-godot`. Godot never opens a visible window for either.

## 3. What the measurements say (2026-10-29, level 100, the read-only retail view)

Method and limits are stated per item; none of this is a claim about every level or every kind of object.

1. **The terrain is a heightfield that C# can sample exactly.** The level archive's terrain chunk holds 64 x 64 tiles of
   9 x 9 signed 16-bit samples and a scale (about 0.000916 here); the samples span about -29.0 to +1.2 in world units
   (negative is up). The engine's lookup (`CHeightField::Collide` in the decompilation, cited by function, not quoted)
   turns a position into fixed point and interpolates four samples; it answers for X and Y from 0 up to 512 and gives 0
   outside that square. A Python port of that rule gives -10.2 at the player start (its stored height is -10.0).
   SOURCE for the rule, MEASURED for the numbers. The rule, not a guess, must be what the C# code implements.
2. **Stored heights look different for different kinds.** In level 100 the ground units (two Target Tanks and a Warehouse)
   store height 0 where the terrain is about -10.6; the player start stores -10.0 (the terrain there is about -10.2); the
   two units whose names and scripts say they fly (a Highside Transporter, an Air Trainer) store -15.0, the first over ground
   at about -11.0, an altitude about 4 above it; waypoints and sphere triggers mostly store 0, a few waypoints -15 or -20
   (they look like air routes). MEASURED from the stored rows against the port of the rule; what each kind does with its
   stored height at run time is established only where item 3 says so.
3. **For a ground unit the stored height changed nothing visible.** Target Tank 12 was moved to the same X and Y at
   heights 0, -10, -12.1 and -14, each staged as a mod with the Toolkit's tools and played in a CE build with the
   world-file override (offscreen, level 100, real clock): the tank appears at the same place and in the same way in
   every run (frames 500 to 900 of each, looked at). Two more runs in the setup of the first loose-file experiment (world files in
   the user folder plus a shadow archive, virtual clock, heights 0 and -12.1) look the same. MEASURED for this one unit. This does
   not reproduce an earlier experiment's report that a ground unit left at height 0 stays buried; the difference is
   unresolved, so the editor must not enforce a "height from the terrain" rule on ground units on that report.
4. **The map is not mirrored if X runs right and Y runs up.** The edited tank was placed 25 units from the start, and in the
   cockpit frames it appears straight ahead; the stock Target Tanks lie counter-clockwise of that direction and appear to
   the left. INFERRED from positions and frames. Cheapest falsifier: stage a marker object at a known offset and look.
5. **An edit by the tools is the same bytes as an edit by hand.** The Toolkit's move tool plus `stage --as-mod` produced the
   body (108,502 bytes) the earlier hand edit produced, and CE's mod loader admitted and served it. MEASURED.

What nobody has seen: any level but 100 in these runs, any kind of object but the Target Tank edited in game, a
base-world edit against an existing career, and any Windows run (mods are refused on Windows until a later CE).

## 4. Decisions this design takes

- **Placement only in version 1.** Moving existing objects never changes the number or order of stored rows, so none of
  the slot rules (waypoint paths and each object's target refer to stored rows by index, and a career indexes a base
  world's rows) can be broken by an edit. Adding, duplicating and deleting come after, append-only first.
- **Z stays editable and honest.** The inspector shows the stored height, the terrain height under it and the
  difference, and says plainly what has been observed (a ground unit is placed on the ground in the runs so far; air
  units, the start point and air-route waypoints use their stored height). No rule is enforced on that evidence.
- **Everything is a new mod folder.** Saving never overwrites, never writes inside a game folder, and never edits
  `ce.ini`: the page shows the exact `mods=` line to add. Enabling a mod from the Companion is a later step through its
  existing settings writer, with its backups and its game-running check.
- **No retail bytes enter the repository.** The editor reads the player's own install at run time. Test vectors are
  authored bodies generated by a committed script; retail conformance is a local gate, never tracked.
- **The C# code is checked against the Python tools, not against itself.** The Python encoder and stager are the oracle
  for byte-exact reading and writing; every C# piece has a differential test against them.

## 5. Layers and files

New C# in the Companion, in two layers so the data layer has no Godot types and runs in plain headless tests.

**`OnslaughtToolkit.Companion.Levels`** (data and rules):

| Type | Job |
| --- | --- |
| `LevelArchive` | Opens `data/resources/NNN_res_PC.aya` with `AyaContainer.Inflate`, walks the chunks to the world bodies (WDAT's two level numbers, `BSWD`, `RLWD`) and to the terrain chunk; lists a game's levels with the names `GameText` already knows. |
| `WorldBody` | The lossless model of a body (header, scripts and the regions the loader only skips kept as opaque bytes, objects, trees, waypoint paths, timings, grids); `Read` and `Write`, versions 43 to 50, byte for byte. A port of `read_world_model` and `write_world_body`. |
| `PlacedObject` | One stored row: kind from the object id (the table in `thing_class`), definition, name, script, position (three float32), orientation, the kind-specific rest kept intact. |
| `Heightfield` | The samples and scale; `HeightAt(x, y)` implementing the engine's fixed-point rule exactly; a shaded-relief array for the map. |
| `EditSession` | The loaded baseline, the edited body, command objects (`MoveObject` first), undo and redo, a change list, and `Validate()` returning errors and warnings. |
| `ModStager` | A port of the Toolkit stager: the loader's limits for id, name, version, texts and world files; a new folder only; refuses a destination inside a game folder; world files first, `mod.json` last. Writes through `FileMutationSafety`. |

**`OnslaughtToolkit.Companion.Ui`**:

| Type | Job |
| --- | --- |
| `Pages/LevelEditorPage` | The sidebar page ("Level editor"): level picker, object table, inspector, toolbar, warnings, status line. |
| `LevelMap` | The top-down control (section 7): terrain, objects, selection, drag, pan, zoom. |
| `SaveAsModDialog` | Name, id, version, author, description, destination, and the line to add to `ce.ini`. |

Registered beside the other pages in `CompanionApp` (Extras). Built so far (M0 to M2): `LevelArchive`, `WorldBody` and `PlacedObject`, `ObjectKinds`,
`EditSession` with `MoveObject`, `ModStager`, and two types the first page needed that this table did not name: `CoordinateInput` (a typed coordinate read as the
Toolkit's move tool reads one, with float32 rounding said, never a silent change of a stored -0) and `LevelEditorModel` (the page's state with no interface in it).
`Heightfield` and `LevelMap` are M3. Tests: `Tests/LevelTests.cs` and `Tests/LevelEditTests.cs` (the data layer and the stager), `Tests/LevelEditorTests.cs` (the coordinate
reader and the model; the Godot-free host runs these too) and `Tests/EditorPageTests.cs` (the page, in the interface suite).

## 6. The screen

```
+------------------------------------------------------------------------------------------+
| Level editor    Level [100  Aquila Prototype v]      Undo  Redo   Show changed   [Save as mod...] |
+----------------------+-------------------------------------------+-----------------------+
| Objects              |                                           | Target Tank           |
| [Search_____]        |      top-down map                         | kind: unit  row 12    |
| #   kind   name      |      terrain shaded, +X right, +Y up      | X [ 276.49 ]          |
| 0   start  -         |      objects as marks by kind             | Y [ 265.07 ]          |
| 9   unit   Target T. |      selected object ringed               | Z [ 0 ]  terrain -10.0|
| 12  unit   Target T. |      drag the ringed object to move it    | stock: 216.81, 327.94 |
| 13  trigger FiringR. |                                           | [Reset this object]   |
| ...                  |                                           | Warnings              |
+----------------------+-------------------------------------------+-----------------------+
| 1 object changed: Target Tank (row 12) moved 62.1 m.   Save as mod to play it in Onslaught CE.     |
+------------------------------------------------------------------------------------------+
```

Behaviour, in the Companion's plain-words tone:

- **Selecting.** A row in the table or a mark on the map selects; the other follows. Search filters the table by name,
  kind or script.
- **Moving by number.** X, Y and Z fields apply on Enter or when they lose focus; the value shown afterwards is the
  float32 actually stored (the move tool's rule), with a note when it rounded. Arrow keys nudge the selection by 0.5,
  Shift by 5, Ctrl by 0.05; every field and action works from the keyboard.
- **Moving by dragging.** Left-drag on the selected mark moves X and Y; Esc cancels the drag; one drag is one undo step.
  Z is left as it was unless the player edits it.
- **Undo, redo, reset.** Every change is a command; "Reset this object" and "Show changed" make a long session
  reviewable.
- **Warnings** (never silent, and never blocking unless the saved file would be broken): a position outside the 0 to 512
  square (the terrain lookup answers 0 there); a changed base world (careers remember which of a base world's buildings
  stand; edit it by appending, not by moving what a career may have destroyed); a value the format cannot hold.
- **Save as mod.** Defaults: name "Level N edit", an id derived from it (lowercase letters, digits, `-` and `_`, at most
  48), version "1", the player's name as author, the destination `<CE user folder>/mods`. On success the page says
  exactly what was written and shows `mods=<id>` with a Copy button. It refuses a no-change edit, a folder that
  already holds anything, and anything inside a game folder, each in a sentence that names what to do.
- **A CE that cannot load it.** The page says that the saved mod needs a CE whose Mods section lists world files, and,
  when the Companion has read CE's version, which version that is; it does not hide the button.

## 7. The map in Godot

A custom `Control` like `CampaignMap`:

- **Terrain.** One image built once per level from the heightfield: hill-shaded relief from the samples on a one-unit
  grid across the 0 to 512 square (a few hundred thousand pixels, computed in C# in well under a second), drawn with
  `DrawTextureRect`. The heightfield stores a water level, which can give the water its own tint; that is to be checked
  against a capture. No retail texture is used.
- **Objects.** Marks by kind (start, unit, feature, waypoint, trigger sphere at its radius when known, level script off
  the map), coloured by allegiance; waypoint paths as lines between the rows they name. Draw order puts the selection
  last; hover shows the table row as a tooltip.
- **Input.** `_GuiInput` handles mouse button, motion and wheel: wheel zooms about the pointer, middle-drag or
  space-drag pans, left-click selects the nearest mark within a pixel radius, left-drag on the selection moves it.
  Pixel and world conversions are one tested pair of functions (X right, Y up, from section 3 item 4).
- **Cost and limits.** A level stores tens of rows up to a few hundred (the loader's arrays hold 1000); redrawing
  everything on each motion event is cheap. Dragging only edits the in-memory body; nothing is written until Save as mod.
- **Feasibility.** Every piece (custom drawing, pointer events, an `ImageTexture` from a byte array, a `SubViewport`)
  is in use elsewhere in the Companion. The one new risk is the drag feel, which is judged by running it (section 9).

## 8. Safety rules the page keeps

- The game's folders and the backups are only read. The only thing the page writes is a new folder it creates.
- No overwrite, no link followed, nothing inside a game folder: the Toolkit stager's rules, enforced here through the
  Companion's own file-safety primitives.
- Writing a mod folder does not need the game closed, but enabling one in `ce.ini` does; until the Companion does that
  itself it only shows the line.
- The stager detects replacement; it does not lock, as the Toolkit's Python stager does not. A directory swapped for a link, or moved into a game folder, by
  another process after the early checks and before the folders are created is not caught by them, and a folder moved during the run is not guaranteed to stay
  outside the game folder (the limit every writer through the Companion's guarded publication has). The page says where the mod was written.
- The page only ever creates a new folder, so it never changes a mod that CE may already have open. A mod's world file that
  does change while CE is running is checked again when the level loads and, if it no longer matches what CE checked at
  start-up, the level's own world is read instead and the log says so (the loader's behaviour from the world-file override
  on; it is not something the page relies on).
- No telemetry, no network. The page reads the installed game's data and says so on first use.
- Mods are refused on Windows by the CE that supports them first; the page says that rather than staging something
  that cannot load.

## 9. Tests and acceptance

Headless unit tests (the repository's launcher, authored data only):

- `WorldBody` read and write against vectors generated by a committed Python script from the encoder's own authored
  bodies for every version it handles: reading gives the same fields, writing gives the same bytes.
- `Heightfield` against the same Python rule on an authored terrain chunk, including the edge cases (tile and sample
  boundaries, the 512 limit, negative and fractional input).
- `EditSession` commands, undo and redo, validation findings.
- `ModStager` produces, for the same edit, a folder byte-identical to the Python stager's; each refusal of the stager
  (inside a game folder, a folder that holds anything, limits on id and texts, a no-op edit) is a test.
- UI tests that drive the page with a fake install and an authored archive: select, type a coordinate, undo, save, and
  compare the saved folder.
- A local conformance gate, not in Git: every retail world body round-trips in C#, and the move that the Toolkit tool
  makes to Target Tank 12 of level 100 gives the same hash from the C# edit.

Looking at it (the standing rule is to judge the artefact, not the checks): a capture of the page offscreen with an
authored level and one with the retail view, looked at at real size; then the acceptance below in a CE build with the
world-file override.

**Acceptance of the minimal prototype (milestone M2):** in the Level editor page, select Target Tank 12 of level 100, type
the coordinates of the Toolkit's acceptance edit (276.49, 265.07, -12.1), press Save as mod, add the line to a scratch `ce.ini`, start CE on level 100, and
see the tank near the crosshair; the saved mod's world file has the same SHA-256 as the Toolkit pipeline's for that
edit. **Acceptance of M3:** the same result by dragging the mark, and the numbers shown afterwards match the file.

## 10. Prototype plan

The minimal prototype is M0 to M2: typing a coordinate, saving a mod, seeing it in game. The map (M3) is the next
piece, not part of the minimum. Effort figures are rough working days for one engineer and are an estimate.

| Milestone | Scope | Done when | Estimate | State |
| --- | --- | --- | --- | --- |
| M0 data layer | `LevelArchive`, `WorldBody`, `PlacedObject` read and write, vector generator script | differential tests pass on every authored version; the local gate round-trips every retail body | 3 to 4 | done: on main, reviewed; every retail world body round-trips |
| M1 staging | `ModStager`, `EditSession` with `MoveObject` and undo, cross-language golden | the C# stager's folder is byte-identical to the Python stager's for the same edit; every refusal tested | 2 | done: on main, reviewed |
| M2 page v0 | `LevelEditorPage`: level picker, table, inspector with numeric X, Y, Z, Save as mod dialog; UI tests; a capture | the M2 acceptance above, looked at in game | 3 to 4 | built, in review: the page half of the acceptance passed on the retail view; the in-game half waits for a CE with the world-file override |
| M3 map | `Heightfield`, `LevelMap` (relief, marks, select, drag, pan, zoom), coordinate tests | the M3 acceptance; a capture of the map looked at | 4 to 5 | plan |
| M4 safer editing | warnings panel, "show changed", reset, base-world caution, keyboard nudges | each warning has a test and a message a player can act on | 2 to 3 | plan |
| M5 add, duplicate, delete | append-only add and duplicate with the slot rules; delete only where no path or target names the row | the stager refuses what would break a path or a career index | 4 to 5 | plan |
| M6 play and enable | "Play this level with the mod" through the CE launcher; enabling through the settings writer with its backups | a mod is enabled, played and disabled with the game's files untouched | 3 to 4 | plan |

Dependencies: CE with the world-file override released (0.1.11 is planned); the stager reviewed and on main; the Python
oracle kept in step with any format change.

## 11. Risks and the cheapest check for each

| Risk | Check |
| --- | --- |
| The C# port reads or writes a field differently | the differential tests and the local all-bodies gate, before any UI exists (M0) |
| The terrain rule is ported wrongly | the same-input tests against the Python port, and the stored start-point height as a live sanity value |
| What a kind does with its stored height is guessed wrong | edit one object of each kind at several heights and look (the Target Tank is done; features, buildings and air units are not) |
| The map is mirrored | the marker test in section 3 item 4, before M3 is called done |
| Moving a base-world object confuses an old career | a base-world edit against a mid-campaign save, in a scratch user folder, before M4 offers the edit without a caution |
| A script names an object by position or count (a moved unit changes a mission) | decode the level's script calls for the object's name; replay the level's tape with and without the edit |
| Dragging feels wrong | run it offscreen with scripted pointer events for the maths, and by hand for the feel |
| Mods are unavailable where the player is (Windows) | say so in the page; do not stage what cannot load |

## 12. Not in scope

Terrain and shadow editing (no writer exists for them), a mission-script compiler or editor, new unit or model types,
model replacement, multiplayer map identity and distribution of mods, and an in-game placement mode on the free camera
and console (a separate CE-side track that can use the same mod folders).
