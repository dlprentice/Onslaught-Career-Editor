# Companion Mission Editor: Design Addendum

Status: design proposal; nothing in it is built. It extends the [Companion level editor](companion-level-editor.md), which is on main
through its map (M3).
Last updated: 2026-10-29 (first draft; every measurement in section 2 was taken on 2026-10-29 on the read-only retail view)
Summary: how the Companion can let a player edit a level's mission: show a level's scripts beside the map, then edit their
source in the game's own script language, compile it with a compiler of ours that is proved against every script the game
shipped (byte for byte), and save the result as a CE mod, which is the world file the loader already serves. It states what
the data says (the game never reads the `.msl` files; it runs the compiled scripts inside each level's world file), the
milestones with their gates, the first editable thing, the safety rules and the limits.
Evidence: MEASURED for section 2 (each item names its method and limits), SOURCE for the cited decompilation functions
(cited by function, never quoted), INFERRED where the text says so; the rest is plan.
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfa…`, 2,506,752 bytes (the addresses are the decompilation's, which matches
this binary; the retail view's `BEA.exe` has the same hash)

## 1. What this is for

Players ask for missions they can change: what a level asks of them (objectives), what appears and when (spawns), what
fires on what (triggers and events), and where units go (waypoint paths). The level editor already moves things and saves the
level's world file as a mod. A level's mission logic lives in the same file, so the mission editor is the next layer on the same
pipeline, not a second one.

## 2. What the data says (2026-10-29, the read-only retail view; the Toolkit's world decoder)

Method for all items: the Toolkit's decoders and reader (`tools/world_resources_decode.py`, `tools/world_resources_encode.py`)
over the 66 installed level archives, and the installed `data/MissionScripts` folders; counts are of this installation.

1. **The game never reads the `.msl` files.** `BEA.exe` holds no string naming `.msl` or `MissionScripts` (checked with
   `strings` over the specimen, 0 matches); the decompilation's mission-script module is a virtual machine and an object-code loader
   (`CMissionScriptObjectCode`'s file constructor `0x00538ec0`; `CWorld::LoadScripts` `0x0050ac70`, which reads each script from
   the world file), with no parser; the one other file reader that takes a name from the player is the console's `Exec` command
   (`0x0042ad30`), which reads console commands. The `.msl` files are the original compiler's input, shipped with the data.
2. **The compiled scripts are in the world file.** Each level's world body holds its compiled scripts (the part the level
   editor's model already reads and writes byte for byte). The 66 levels hold 670 scripts between them (about 53,000
   instructions and about 8,800 native calls, 108 of the 144 natives in `gScriptFunctions`); the world file a mod supplies
   (`data/worlds/worldNNN.wrd`) therefore carries a level's whole mission.
3. **Every shipped script has its source, by name, in the matching level's folder.** 670 compiled scripts, 670 `.msl` files of
   the same names (case aside) in the same levels' folders; level 100 has 25 and 25. The install holds 62 more `.msl` files in
   the folders of levels it has no archive for. That is a source and an object for every script, which is what makes a byte-exact
   compiler testable (section 5).
4. **The mod loader can replace an `.msl` file and it changes nothing.** The loader replaces any file the game has under `data/`
   (a mod may add only world files), so an `.msl` copy qualifies; but a replacement is read only when the game opens the file,
   and item 1 says it never does. The route for a mission change is the world file, which today's Linux loader serves (CE 0.1.11
   is planned to be the first to take a world file from a mod).
5. **The object format is small and regular.** The VM has 27 opcodes (23 occur in the shipped scripts; `OP_NOP`, `OP_CMPNEB`,
   `OP_CALLLOCAL` and `OP_PUSHPC` never do); `CAsmInstruction::Spawn`
   (`0x0052d3d0`) reads each, `CInstruction*::Execute` (`0x0052e0a0` to `0x0052ec40`) defines what each does, the natives
   are `gScriptFunctions` (`IScript.cpp`, `0x0052ff20`), the event names are the 13 fixed events (`init`, `arrived`, `timer`,
   `died`, `hit`, `started_dying`, `ready`, `shutdown` and five undefined) plus named handlers (`CEventFunction`,
   `0x0052fa70`). A script is: instructions, the entry point of each fixed event, a symbol table, the named handlers, two
   trailing words, and a constant trailer. Read on one small script, the shape is plain: the variable initialisers compile to
   a block that ends in a return; each fixed event starts at its entry point and ends in a return; an expression statement
   ends by removing its value from the stack; a `switch` is a chain of compare and jump-if-not-equal with labels; a named
   handler starts with a jump-if-false over its body. (INFERRED from reading one script against its source; the gate in
   section 5 is what tests it.)
6. **The symbol table records things a byte-exact compiler must reproduce.** Each symbol has a name, a type, a value, an
   index, a flag and one more integer that is the 0-based line of the source where the symbol first appeared (checked by
   hand on one script; in 611 of 670 scripts it never decreases, and the other 59 are for the compiler's work to explain).
   Constants are named `const dataN` from one counter that runs consecutively inside a script, carries on from one script to the
   next in a level's order (583 of 583 boundaries), and carries on across levels (level 100's first script starts at 716, level
   110's at 1744): it is the state of one compile session over the whole build. The flag is 1 on all 22,311 symbols; the
   trailer is the same ten bytes in all 670; the two trailing words are (0, 1) in 652 scripts and (0, 0) in 18 (what they
   mean is not known yet; no obvious correlation with the events a script has).
7. **The game's own rules the symbol table must keep.** `CSymbolTable::Clone` (`0x005395b0`), which makes the copy a thing
   runs, copies a symbol only if no symbol of that name is there yet: two symbols with one name would shift every index after
   them and corrupt the script. The shipped counter keeps every name in a script unique; ours must too. Instruction operands
   are indices into the table, a jump's operand is an instruction index, and the VM runs both without checking them.
8. **The language is small.** The 732 sources are ASCII, 727 with CRLF line ends, 824,000 bytes in all (largest 13 KB), no block
   comments, one directive in the scripts (`#include`, of the shared files `onsldef.msl` and `text.stf`, which hold only
   `#define`s and comments: the defines and the text ids), so a compiler needs `#include` and plain `#define`, and constants
   arrive as substitutions where they are used; the constructs are `vars` blocks, the fixed events and `event("name")` handlers, `if`/`else`, `while`,
   `for`, `switch`/`case`, calls of natives (`Name(args)`, or on a thing variable `target.Name(args)`, which sets the receiver),
   assignment, the operators `&& || < > + - * /` and `!`, and the types `bool`, `int`, `float`, `thing` and `position`.
9. **Names matter to the VM in one place that matters here.** Beyond `Clone`, a script's symbols are reached by index. `SetVar`
   (`IScript::SetVar`, `0x005348f0`) passes a name and a value to the thing it is called on, and the base class
   (`CComplexThing::SetVar`, `0x004f45e0`) only logs an unknown variable; one subclass keeps a few variables of its own by
   name. So a script's variable and constant names are labels apart from `Clone`'s uniqueness (INFERRED from those handlers;
   the cheapest check is the edit in section 6, which renames nothing).

What nobody has seen: a script compiled by anything but the original compiler running in the game, any construct no shipped
script uses, any level not installed here, and anything on Windows.

## 3. The approach

Edit the script source (the game's own language), compile it with a compiler of ours, replace the script in the world body, save
the world file as a mod through the level editor's existing stager. Unchanged scripts are written back as the shipped bytes, never
recompiled, so a mod differs from the game only where the player edited.

- **The compiler** is C# in the Companion (`Missions/`), with a Python reference (`tools/msl_compile.py`) that the C# is tested
  against on generated vectors, as the other tools are. It is written from the decompilation's description of the VM and its loader,
  cited by function, with no source copied (the original compiler is not in the decompilation and is not needed). It supports
  exactly the constructs the shipped scripts use; anything else is refused with a line and a reason, never guessed.
- **The checker** applies the game's own rules to the compiled script before anything is saved (section 7).
- **The mod** carries the world file and, optionally, the edited sources as `data/MissionScripts/levelNNN/NAME.msl` (the
  loader allows replacing a file the game has; the game never reads these, so they are inert copies that make the mod
  self-describing and let a later session reopen the player's own source). This needs the stager and the Python reference stager
  to take extra files; it is the first question in section 10.

## 4. Milestones

| Milestone | Scope | Done when | Estimate |
| --- | --- | --- | --- |
| MS0 scripts beside the map (read-only) | the Level editor page lists the open level's compiled scripts (name, the events handled, the things that run it, the natives it calls) next to the map, shows the selected script's installed `.msl` source with line numbers, and links names in it (thing names, waypoint paths, scripts, text ids) to the table and the map; selecting a thing shows its script and the other way round; waypoint paths are drawn on the map | on every installed level the list equals the world body's scripts, every one finds its source (670 of 670), the capture at three sizes looked at, nothing written | 4 to 5 days |
| MS1 reference compiler and the byte-exact gate | `tools/msl_compile.py` (preprocess, lex, parse, generate, write the record as the world file stores it) and `tools/msl_gate.py --game GAME`, section 5 | every shipped script compiles to its shipped record, or each difference is explained and the compiler reproduces it | 1 to 2 weeks (a 2-day spike on the 20 smallest scripts first) |
| MS2 the C# compiler | `Missions/` with the same stages, authored vectors from the Python reference in Git, and a local retail gate (`Development/ScriptsGate.cs`) that must match the Python gate on all scripts | the vectors and the retail gate pass; the C# refuses what the Python refuses | 1 week |
| MS3 first editable thing | the page edits the selected script's source (a text area with line numbers), compiles it (errors by line and column, a summary of what changed), replaces the script in the session as one undoable command, and saves through Save as mod | the acceptance in section 6 | 1 week |
| MS4 structured helpers | forms for common edits (a count, a delay, a message id), the event graph (who posts, who handles), checks against the level (names exist), path membership and order on the map, spawner and trigger parameters (these are world-body data and need no compiler) | each helper has a test and a message a player can act on | 2 weeks |
| MS5 texts (optional) | the text of a message is in the game's language files, a different mod file; a writer for them | a changed line shows in game | not estimated |

## 5. The byte-exact gate

For every level and every script, compile the installed source and compare with the compiled record the level's world body holds.

- **Exact mode.** The compiler starts its constant counter at the shipped script's first constant number (the counter is session
  state the source cannot give). Every field of the record must be identical: name, instructions, event entry points, symbols
  (name, type, value, index, flag, line), the next index, named handlers, trailing words, trailer. The report names, per script,
  identical or the first differing field with its index.
- **Free mode** (what an edited script gets): any counter start, the same record except the constant names; it is checked on
  the shipped scripts too (equal after renumbering), so the two modes cannot drift apart.
- **What counts as explained.** A difference is a finding: the compiler is wrong, the source differs from what the original
  compiler read (a different revision), or the original compiler did something the language does not say. The first is fixed;
  the second is recorded per script and the script is written back as shipped; the third is reproduced and written down. No
  unexplained difference ships.
- **Where the gate runs.** The gate needs the game, so it is local and its table is private; Git holds authored sources and
  their expected bytes (small, made for the purpose) so the suites run without the game.

The cheapest falsifier of the whole approach is the spike in MS1: the 20 smallest scripts. If their instruction streams, symbol
tables and lines cannot be made to match within a few days, the approach is wrong and the fallback is the data-level helpers of MS4
plus literal edits in compiled scripts.

## 6. The first editable thing, and its acceptance

A message a script shows is chosen by a text id in a call such as `PlayCharMessage` or `PrintText`. The first edit is the id: the
player changes which line a script shows, in source, compiles and saves.

Acceptance, on the retail view: edit one message id in a level 100 script, save as a mod, and
1. the saved world file differs from the shipped one only in that script, and the compiled script differs from the shipped one in
   one constant's value (the gate's exact mode makes this a byte comparison, not a reading);
2. the Toolkit's strict reader (`read_world_model`) reads the file and the existing checks on it pass;
3. in a CE build that loads world files from mods (offscreen, level 100, real clock, as the level editor's mirror check was run),
   the subtitle at the same frames shows the other line (text ids index the game's text table, which the Companion already
   reads), looked at, with a control run beside it.

The spawn count and the timer values are the next edits in the same mould.

## 7. Safety rules

1. Only mods are written: a new folder through the stager, never the game folder, never over an existing folder; a copy of the
   game's `.msl` is never changed.
2. A script that does not compile is not replaced, and a script that fails the checker's errors is not saved; the page says why,
   by line.
3. The checker applies the game's own rules, from the decompilation, to the compiled script: opcodes 0 to 26 and operands inside
   the symbol table (`CAsmInstruction::Spawn`, `CSymbolTable`); symbol names unique and indices consecutive (`CSymbolTable::Clone`);
   named-handler parameters are string symbols (`CEventFunction`); a native's index is in `gScriptFunctions` and its argument count
   and types are its declared ones; every jump lands on an instruction (the VM does not check); the stack is balanced at every
   return (`CDataStack`); the event entry points are in range. Then a re-read: the written record is read back with the Toolkit's
   strict reader and compared.
4. References resolve: thing names, waypoint paths, scripts by name, unit types, text ids and event names that a literal argument
   names (the Toolkit already knows which argument is which role) exist in the level; a miss is a warning, a script that names an
   unknown native an error.
5. Everything is an undoable command on the level's edit session, with a reset to the shipped script; the level editor's rules
   about unsaved edits, the backups folder and the game folder apply unchanged.
6. The editor never starts the game; playing a mod is a later step of the level editor (its M6).

## 8. Honest limits

- Linux only, with a CE that loads world files from mods (planned for 0.1.11); Windows refuses mods until it can open files
  path-safely. The loader is off for replays, recordings, probes, virtual clocks, pilots and network sessions.
- Byte-exactness on the shipped scripts is evidence about the constructs they use. A construct they do not use is unverified, so
  the compiler refuses it.
- The VM checks little itself: a bad script can hang or crash a level. The checker is static; no check here says a mission can
  be won or that a level plays.
- Unknown today: the two trailing words, the 59 scripts whose symbol lines do not rise, whether a script compiled from the
  install's source is the revision the game shipped (the gate answers it per script), the 62 sources with no installed level.
- Nothing here has been played yet. The retail data (sources, objects, frames) stays local and out of Git.

## 9. Risks and the cheapest check for each

| Risk | Check |
| --- | --- |
| The shipped sources are not the sources of the shipped objects | the gate's first run: how many of 670 are identical in free mode |
| The original compiler's output depends on something the source does not say | the spike on the 20 smallest scripts; the explained-differences list |
| A constant name or an index is used at run time in a way we have not found | the handlers named in item 9 were read; an edit that renames nothing is the first acceptance |
| A compiled script is accepted by our checker and crashes the VM | run the edited level in CE offscreen for the length of the script's events and read the log; keep edits small until the checker has been through a few of these |
| Symbols shared between scripts (a clone) corrupt on a duplicate name | unique names are an error in the checker and a vector in the tests |
| The mod loader changes what it serves | the acceptance in section 6 is re-run per CE version |

## 10. Questions for the lead

1. Should a mod carry the edited sources as inert `.msl` copies (needs the stager and its Python reference to take extra files)?
2. Start with the 2-day compiler spike (the falsifier), or with MS0 (the viewer, useful whatever the spike says)? I would run
   both: the spike first for two days, MS0 beside it.
3. Raw source text first, or forms first (MS4 before MS3)? Raw text is the smaller step and the more honest test of the compiler.
