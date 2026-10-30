# Companion Mission Editor: Design Addendum

Status: design; the reference compiler and read-only scripts view with name links and map paths are built. The C# and Python compiler backends and the script-aware editor model are integrated, and the Level editor's Scripts view edits a script's source, compiles it and makes the open level use it (section 15); the acceptance in section 6 was run once on Linux (section 16) and the Level editor's Play button starts CE at the open level with the changes (section 17); source-preserving staging and native Windows validation remain open. It extends the
[Companion level editor](companion-level-editor.md), which is on main through its map (M3).
Last updated: 2026-10-30 (the Level editor's Play button, section 17; the CE acceptance of an edited script was run on Linux, section 16, timing restated from CE's own log, repeated once with the released 0.1.12 package and once through its launcher; the Level editor's Scripts view edits a script's source, section 15; earlier: held and bounded viewer reads and platform limits; script-gate stale record pairs pinned by identity; descriptor-relative Python source reads; The C# compiler is integrated on main; MS0.1 name links and path follow-ups built; earlier: MS0 read-only scripts view, CE 0.1.11 world-file loading, the compiler spike and operator-grouping decision; section 2 measurements use the read-only retail view)
Summary: how the Companion can let a player edit a level's mission: show a level's scripts beside the map, then edit their
source in the game's own script language, compile it with a compiler of ours checked against the shipped scripts with the documented
missing-header and stale-source cases, and save the result as a CE mod, which is the world file the loader already serves. It states what
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
   the same names (case aside) in the same levels' folders; level 100 has 25 and 25. The base worlds the archives carry hold 92
   more compiled scripts (many shared between archives), whose sources are in the base levels' folders; 16 of those files are used
   by no level's own world. The install holds 46 more `.msl` files, in the folders of seven levels whose compiled scripts it does
   not hold (six have no archive; the seventh, level 21, is only a base world that carries none), so there is nothing to compare
   them with. That is a source and an object for every script, which is what makes a byte-exact compiler testable (section 5).
4. **The mod loader can replace an `.msl` file and it changes nothing.** The loader replaces any file the game has under `data/`
   (a mod may add only world files), so an `.msl` copy qualifies; but a replacement is read only when the game opens the file,
   and item 1 says it never does. The route for a mission change is the world file, which today's Linux loader serves (CE 0.1.11,
   published 2026-10-29, is the first to take a world file from a mod).
5. **The object format is small and regular.** The VM has 27 opcodes (23 occur in the compiled scripts of the installed levels; `OP_NOP`, `OP_CMPNEB`,
   `OP_CALLLOCAL` and `OP_PUSHPC` never do, though one source of a level the install lacks writes `!=`, which compiles to `OP_CMPNEB`); `CAsmInstruction::Spawn`
   (`0x0052d3d0`) reads each, `CInstruction*::Execute` (`0x0052e0a0` to `0x0052ec40`) defines what each does, the natives
   are `gScriptFunctions` (`IScript.cpp`, `0x0052ff20`), the event names are the 13 fixed events (`init`, `arrived`, `timer`,
   `died`, `hit`, `started_dying`, `ready`, `shutdown` and five undefined) plus named handlers (`CEventFunction`,
   `0x0052fa70`). A script is: instructions, the entry point of each fixed event, a symbol table, the named handlers, two
   trailing words, and a constant trailer. Read on one small script, the shape is plain: the variable initialisers compile to
   a block that ends in a return; each fixed event starts at its entry point and ends in a return; an expression statement
   ends by removing its value from the stack; a `switch` is a chain of compare and jump-if-not-equal with labels; a named
   handler starts with a jump-if-false over its body. (First read off one script; MEASURED since by the gate of section 5, which
   compiles every installed source to its shipped record: section 11.)
6. **The symbol table records things a byte-exact compiler must reproduce.** Each symbol has a name, a type, a value, an
   index, a flag and one more integer that is the 0-based line of the source where the symbol first appeared (it never
   decreases except in the 59 scripts with `do_once` blocks, whose two boolean symbols per block come after every other symbol
   with line 0: section 11).
   Constants are named `const dataN` from one counter that runs consecutively inside a script, carries on from one script to the
   next in a level's order (583 of 583 boundaries), and carries on across levels (level 100's first script starts at 716, level
   110's at 1744): it is the state of one compile session over the whole build. The flag is 1 on all 22,311 symbols; the
   trailer is the same ten bytes in all 670; the first trailing word is 0 in all of them and the second is 1 in 652 scripts and
   0 in 18: it is 1 exactly when the script has a `vars` block (section 11).
7. **The game's own rules the symbol table must keep.** `CSymbolTable::Clone` (`0x005395b0`), which makes the copy a thing
   runs, copies a symbol only if no symbol of that name is there yet: two symbols with one name would shift every index after
   them and corrupt the script. The shipped counter keeps every name in a script unique; ours must too. Instruction operands
   are indices into the table, a jump's operand is an instruction index, and the VM runs both without checking them.
8. **The language is small.** The 732 sources are ASCII, 727 with CRLF line ends, 824,000 bytes in all (largest 13 KB), no block
   comments, one directive in the scripts (`#include`, of the shared files `onsldef.msl` and `text.stf`, which hold only
   `#define`s and comments: the defines and the text ids), so a compiler needs `#include` and plain `#define`, and constants
   arrive as substitutions where they are used; the constructs are `vars` blocks (one script writes `attributes` ... `end_attributes`),
   the fixed events and `event("name")` handlers, `if`/`else`, `while`, `for`, `switch`/`case`, `do_once` blocks, calls of natives
   (`Name(args)`, or on a thing variable `target.Name(args)`, which sets the receiver), assignment, the operators `&& || == < <= > >=
   + - * /` (no source outside a string or comment uses `!` or `%`; one, `level530/hive.msl`, of a level the install has no archive for, uses `!=` twice), and the types `bool`, `int`, `float`, `thing` and `position`.
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
- **Future source-preserving staging.** A future workflow must verify each selected mission source against the compiled script in the exact staged world, refusing unsupported or mismatched inputs. An installed source can already differ from its compiled record, so including a source in a mod is not by itself evidence that a player edited it. The current stager publishes world data only; neither this source-staging workflow nor a player-facing mission source editor is available yet.

## 4. Milestones

| Milestone | Scope | Done when | Estimate |
| --- | --- | --- | --- |
| MS0 scripts beside the map (read-only; built, section 12) and MS0.1 names and paths (built, section 13) | the Level editor page lists the open level's compiled scripts (name, the events handled, the things that run it, the natives it calls) next to the map, shows the selected script's installed `.msl` source with line numbers, and links names in it (thing names, waypoint paths, scripts and event handlers; text ids are not linked yet) to the table and the map; selecting a thing shows its script and the other way round; waypoint paths are drawn on the map | on every installed level the list equals the world body's scripts, every one finds its source (670 of 670), the capture at three sizes looked at, nothing written | 4 to 5 days |
| MS1 reference compiler and the byte-exact gate | `tools/msl_compile.py` (preprocess, lex, parse, generate, write the record as the world file stores it) and `tools/msl_gate.py --game GAME`, section 5 | every shipped script compiles to its shipped record, or each difference is explained (built; section 11) | built 2026-10-29 (the spike ran on every script) |
| MS2 the C# compiler (backend, section 14) | `Missions/` with the same stages, authored vectors from the Python reference in Git, and a local retail gate (`Development/ScriptsGate.cs`) that must match the Python gate on all scripts | the vectors and the retail gate pass; the C# refuses what the Python refuses and the supported platforms are checked. The C# and Python backends are integrated; source-preserving staging remains future work. | Native Windows and source-stage validation remain open |
| MS3 first editable thing | the page edits the selected script's source (a text area with line numbers), compiles it (errors by line and column, a summary of what changed), replaces the script in the session as one undoable command, and saves through Save as mod | the acceptance in section 6. The script-aware model is integrated and the page edits, compiles and uses a script (section 15); the acceptance was run once on Linux (section 16) and source staging is not built. | 1 week |
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

The cheapest falsifier of the whole approach was the spike in MS1: the 20 smallest scripts. If their instruction streams, symbol
tables and lines could not be made to match within a few days, the approach was wrong and the fallback was the data-level helpers of
MS4 plus literal edits in compiled scripts. They matched on the first draft, and the spike then went on to every script (section 11).

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

Run on 2026-10-30, with the first message playing the second's text; section 16 has what was run and what it does not show.

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

- Linux only, with a CE that loads world files from mods (0.1.11 or later); Windows refuses mods until it can open files
  path-safely. The loader is off for replays, recordings, probes, virtual clocks, pilots and network sessions.
- Byte-exactness on the shipped scripts is evidence about the constructs they use. A construct they do not use is unverified, so
  the compiler refuses it.
- The VM checks little itself: a bad script can hang or crash a level. The checker is static; no check here says a mission can
  be won or that a level plays.
- Unknown today: how the original compiler grouped any mix of operators the shipped scripts parenthesise (the compiler refuses
  those, section 11), what it did with a construct no shipped script uses, and the 46 sources of levels whose compiled scripts the install does not
  hold (nothing to compare them with). Settled by the gate: the trailing words, the line order, and which installed sources are not the revision the
  game shipped (a pinned list, each with how it differs).
- A script can crash a level by damaging a unit that runs a script of its own from inside a handler that is running (diagnosed by the level 888 work with a
  test-only level script, and followed in the decompilation by function): `IScript::Damage` calls the thing's damage routine, which can start the thing's death
  at once; that starts its death handler, `CVM::CallEvent` sets the machine's code and place before `CVM::Run` refuses to run a second time, and the running script's
  next instruction is then read from the wrong place. `IScript::Arrived` and `IScript::Hit` return while the machine is running; the entry points for a dying or dead unit
  do not. It is a shape that can fail, not a certainty: one shipped script damages a unit with a death handler of its own from inside a handler and runs through in the
  retail game, and the port's planned guard leaves that path as it is. `Die` is not part of it (it posts an event for the next frame), and `SetHealth`,
  `SetSegmentHealth` and `SetAllSegmentsHealth` only store values. `HalfDestroy` is not warned about and is not cleared either: by the names of the functions it calls it reaches the same
  damage path (it damages parts of a unit at random), and whether it can finish a unit and start its death handler at once is not established; the cheapest falsifier is a test-only level
  script that calls it on a unit with a death handler from inside a handler, run under the port with a debugger, as the level 888 diagnosis did. Until a CE release guards the entry, the page
  warns about a replaced script that calls `Damage` more often than the shipped one (`ScriptHazards`: by native, not by target, so it cannot tell a unit that has a script from one that has none), and
  the checker (section 7) is where a stricter rule belongs.
- One edit has been run in CE on Linux (section 16); nothing else here has been. The retail data (sources, objects, frames) stays local and out of Git.

## 9. Risks and the cheapest check for each

| Risk | Check |
| --- | --- |
| The shipped sources are not the sources of the shipped objects | answered by the gate's first run: a short list of installed sources is another revision, pinned by name with how each differs; the rest are identical |
| The original compiler's output depends on something the source does not say | answered for the shipped scripts: the compile session's two counters (a caller's input), the call result flag, `do_once`'s trailing symbols, and the rest are in the source; operator grouping the shipped scripts leave open is refused |
| A constant name or an index is used at run time in a way we have not found | the handlers named in item 9 were read; an edit that renames nothing is the first acceptance |
| A compiled script is accepted by our checker and crashes the VM | run the edited level in CE offscreen for the length of the script's events and read the log; keep edits small until the checker has been through a few of these |
| Symbols shared between scripts (a clone) corrupt on a duplicate name | unique names are an error in the checker and a vector in the tests |
| The mod loader changes what it serves | the acceptance in section 6 is re-run per CE version |
| A script damages a scripted unit from inside a running handler and crashes the level | the page warns when an edit adds a call to `Damage` (`ScriptHazards`); the port is to defer the nested event |

## 10. Decisions (2026-10-29, the lead)

**Future design, not implemented on main:** 1. The mod carries the edited sources as inert `.msl` copies at the game's own paths (section 3), with the stager and its Python
   reference taking extra files under the same refusals.
2. The compiler spike on the 20 smallest scripts comes first and MS0, the read-only viewer, runs beside it. The spike's result is
   reported before MS2 (the C# compiler): how many scripts are byte-exact, the first unexplained difference, and what the
   trailing words and the symbol line order turn out to be, if found.
3. Raw source text before forms (MS3 before MS4).
4. Beside MS0: Home's "Change folder" is examined against unsaved Edit career and Settings changes, and gets the Level editor's
   ask-first guard if it drops them.
5. Operator grouping (after the spike): the compiler accepts what the shipped scripts prove and refuses any other mix without
   parentheses, naming both operators, because the original compiler's grouping there is unknown and a silent guess could change a
   mission's meaning; the editor shows the grouping used for the proven cases. "`+ - * /` bind tighter than the comparisons" is kept
   as a generalisation of the seven pairs the shipped scripts show (section 11), not a proven rule.

## 11. The spike's result (2026-10-29)

`tools/msl_compile.py` (the reference compiler), `tools/msl_gate.py` (the retail gate of section 5) and `tools/msl_compile_tests.py`
(authored sources only) exist, and the gate was run over the whole installation, the base worlds as well as the real ones. It reads
the game folder and writes nothing.

- **Result.** Every installed source compiles to its shipped record, field by field and as the bytes the world encoder writes,
  with two kinds of exception the gate names per script. Some sources include a header the install does not hold
  (`data\text\extra2\...\text.stf`, names only the developers had): the gate treats it as empty, takes each name it would have
  defined from the shipped constant at that position, and the rest of the record is then identical (reported as assisted). And a
  short list of installed sources is another revision than the one compiled into the world file (the shipped script has
  statements, a variable or a handler the file lacks, or the reverse): the gate pins each by level and name with how it differs, and
  fails when a pinned source turns out to compile exactly, so the list cannot rot. Nothing is unexplained.
- **The trailing words.** The first is 0 in every script. The second is 1 exactly when the script has a variables block.
- **The line order.** A symbol's line is the 0-based line of its first appearance in the main source, counting newline
  characters only (so mixed line ends are no problem); an `#include` or `#define` line leaves a blank line so later lines keep
  their numbers, and a name that comes from a header carries the line of its use. A name is entered once and a constant every
  time. The lines never fall except in scripts with `do_once` blocks: their two boolean symbols per block (`do-once-N`, a flag that is
  true and a false constant, numbered from a second compile-session counter) come after every other symbol with line 0.
- **What the first reading missed**, each found by the gate and now tested: a call's attribute carries bit 16 when its result is
  used (clear when the call is a whole statement); an assignment is an expression whose value stays on the stack, so `if (x = TRUE)`
  compiles; a `for` loop's step is read before its body (its constants are numbered first) and emitted after it; an `event("x")`
  handler's parameter is the first string constant with that value in the script; floats are stored as float32 and a negative number
  is one constant; `attributes` ... `end_attributes` compiles like `vars` ... `end_vars`; a handler named otherwise than the 13 events is
  compiled and never entered (some shipped scripts have misspelt ones; the compiler says so in a note); a variable may be declared
  twice (one symbol); the declared types of variables are not in the object code; every shipped call has exactly its native's
  argument count, which the compiler now enforces.
- **Operator grouping.** The shipped scripts prove less than a grammar needs. They show that repeating `&&`, `||` or `+` groups left to
  right; that `&&` and `==` have one rank and group left to right (`a && b == c` is `(a && b) == c`, unlike C; three expressions
  show it); and, of the 48 ordered pairs of an arithmetic operator and a comparison, 7: a `<` or `<=` followed by `*`, `-` or `/`
  (six pairs, as in `a < b / 2`: the arithmetic is the comparison's right side) and `+` followed by `==` (as in `a + 1 == b`: the sum
  ends before the `==`). All seven agree with "arithmetic binds tighter than a comparison". That rule for every one of the 48 pairs
  is therefore a generalisation of seven observations, kept because it is the near-universal rule in this language family (decision
  5); the other 41 pairs, `+ - * /` against `+ - * /`, `||` against everything and the comparisons against each other are not shown at
  all. The shipped scripts put parentheses round everything else, so the original compiler's grouping there is unknown. The compiler
  accepts exactly the shown cases and the generalisation, and refuses any other mix without parentheses, naming both operators. For a
  mixed chain it does accept it returns a note with the grouping used, which the editor shows.
- **Limits the compiler keeps** (so that the C# port can keep the same): statements and expressions nested more than 100 deep, a script
  of more than a million characters or one that grows past a million tokens when its `#define` names are replaced, a header of more than
  a million bytes, a number that does not fit 32 bits or float32, and an `#include` that is not a file inside the game folder
  (a link out of it) are refused with a line and a reason. The deepest shipped script nests 15.
- **What is still unproven.** Constructs no shipped script uses (the compiler refuses them; `!=`, which one source of a level the
  install lacks writes, compiles to the VM's `OP_CMPNEB` and is grouped only with arithmetic), the sources of the levels this install
  lacks, and the game running any script this compiler wrote.

## 12. MS0: the read-only scripts view (2026-10-29)

The Level editor page has a Scripts switch beside its Map switch. On, it shows the open level's compiled scripts in place of the table
and the map: the level's own world first, then its base world's (dimmed), each with the number of objects that name it and the events it
handles; the selected script's installed source, read only, with line numbers and coloured keywords; and a card that says what the
script handles, which game functions it calls, and which objects name it (each a button that shows the object on the table and the
map). An object that names a script offers a button for it, and the page says when the level has no script of that name. The search
narrows the list by name, event or function. Nothing is written.

- **What it reads.** Events come from the compiled script (the 13 fixed events' entry points, then each named handler's event name),
  functions from its CALL instructions (the names are generated from the Toolkit's table, `tools/script_tables.py`), and the objects that
  name it from each object's script, spawn script and, for a spawner, its spawner spawn script, matched by exact name. A source is found
  at `data/MissionScripts/level<NNN>/<name>.msl` in any case (the real level's folder for the level's own scripts, the base level's for
  its base world's), ignoring symbolic links below the selected root, anything that is not a regular file and files over 1 MiB. On Linux
  x64 with procfs the reader holds directory handles and a no-follow path handle, checks identities and metadata around a bounded read, and refuses
  detected changes. On Windows it uses the existing local-directory locks and a no-follow file handle; native Windows behavior has not
  yet been checked. Other operating systems and Linux architectures fail closed. The selected root itself may be reached through a link;
  regular hard links remain accepted. Remote Linux filesystem behavior is unverified, Windows network roots are refused, and these checks
  do not create an immutable snapshot. A folder that cannot be listed or a file that cannot be read is a sentence on the page.
- **Checked.** The Toolkit's gate table has a SCRIPTS row per level archive, worked out in Python separately from the C#: the catalog's
  lines (name, instructions, events, functions with counts, users) and the text of every source found, hashed. The Companion's local
  retail gate (`Development/LevelsGate.cs`) compares the C# catalog and finder with it on every level of an installed game: every list
  equals the reference's and every script of every world body, base worlds included, finds its source.
- **Limits.** The page was driven by events in tests and looked at in offscreen captures at 1920 by 1080, 1280 by 800 and 1024 by 700
  (the smallest window is cramped: the list shows two or three rows and the source about ten lines); nobody has used it by hand. A source
  may differ from the compiled script it sits beside (the gate says which installed ones do: section 11). Base-world scripts name
  base-world objects, which the table does not list, so they show no users. What a name in a source refers to, and the paths on the map,
  are MS0.1 (section 13).

## 13. MS0.1: names in the source, and waypoint paths on the map (2026-10-29)

A click in a quoted text of a script's source says what in the open level has that name, with a button for each that goes to it: an
object by its own name (the table and the map), a waypoint path (the map), a script (the Scripts view), or the scripts that handle an
event of that name. An object of the level's base world is named too, with a note and no button, because the page does not list that
world's objects. A text that names nothing says so; a word or a comment is not a link. The **Paths** switch under the map draws every
waypoint path faintly through its points. A path button, from a source or from an object that is a point of the path ("Path A
· point 2 of 3"), highlights that path, numbered along it with an arrow on each leg, and brings it into view; Hide path stops it.
Nothing is written.

- **What it reads.** The scripts take names as quoted texts (a thing, a waypoint path, an event, a script), and the compiled script
  holds the same texts as string constants with nothing to say which call reads which text as what. So a link goes by the name alone:
  it finds what has that name and does not claim the script uses it as such. Objects match by their exact name (else, if none has it,
  in another letter case, and the button says so), in the level's own world and by the same rule in its base world, each on its own;
  scripts and event handlers match exactly, and so do paths except in one place. The game takes the first matching waypoint path
  (`CWaypointManager::FindNearest`) from one list, and that list holds the base
  world's paths before the level's own (`CWorld::LoadWorld` loads the base world before the rest of the level's world, and
  `CWaypointManager::Load` appends each path to the list). So the first argument of a `FollowWaypoint` or `FollowWaypointWait` call,
  found by looking back along the line from its opening quote over blanks to a `(` and, before it, the whole word of the call's name,
  names the first of the base world's paths then the level's own whose name matches under the modeled C-locale byte comparison:
  ASCII letters match in either case, other bytes match exactly, and NUL ends the name. Other process locales and native Windows
  comparison remain unverified. The level's own path gets a button (marked when the compared case differs); a base world's path is
  said, with no button, because the page does not draw that world's paths. The game returns no waypoint if the first matching path
  has no usable points, rather than trying a later path. The page does not resolve an empty quoted name. A quoted text is closed by the next
  quote on its line, and `//` outside a quote ends the line's code. A path lists objects by their place in the world's thing list:
  under that reading the shipped paths run from point to point (the median step between neighbours is about 88 world units; under a
  shift of one or two places it is 121 to 146). The game's loader (`CWaypointPath::Load`) keeps a slot only if it indexes a loaded
  object that is a waypoint, so a slot past the list, and a slot that names a unit, a spawner, a squad or a start, is not a point:
  the page does not draw it, number it or count it, "N points" counts the points kept, and an object that only such a slot names is
  on no path.
- **Checked.** The gate table has a NAMES row per level archive, worked out in Python separately from the C# (`source_literals`,
  `resolve_name`): every quoted text of the sources of the level's own scripts, outside comments, with its line and what it resolved
  to, hashed, and how many there are and how many name something. The Companion's local retail gate scans the same sources with
  `TokenAt`, column by column, and resolves with `ScriptNames.Resolve` (a path argument is told by `follows_path_call` in Python and
  `FollowsPathCall` in C#); the two agree on every level of an installed game. A PATHS row per level archive lists each path of the
  level's own world as `index|name|slots|kept rows` (hashed, with the numbers of paths, points kept and slots): the Python keeps the
  rows by the kind its own model reads from the object id, the C# with `WaypointCatalog.Rows`, and the two agree on every level. That
  row exists because a mutation of the path-slot rule passed every authored test (an authored world shows only a few slots) and was
  found only by checking against the real data; the gate now catches it. The route's
  tests build a level with a path, an object, a handler, a base-world object and a text that names nothing, drive the caret and the
  buttons, and check the highlight, the fit (the map's centre and zoom, with the zoom limit), that choosing another script clears the
  card, and that the tooltips can be reached with the pointer.
- **Limits.** Over the shipped sources about three quarters of the quoted texts name something in their level or its base world (many
  name more than one thing: an event handler and a script, say). Of the rest, about half are arguments of `Print`, and nearly all the
  others arguments of `SpawnThing`, of `PostEvent` (an event nothing handles) and of the functions that take a segment, variable,
  animation or weapon name: none of them an object, path or script of the level. Text ids, which index the game's text table (section
  6), are not linked. About one path slot in five of the shipped paths names an object that is not a waypoint, and about half of the
  paths hold one: those slots are dropped as the game drops them, so a path has fewer points than slots. A path argument is told by the
  line it is on, so a call whose name and parenthesis end one line and whose first argument begins the next is not recognised (none of
  the shipped sources does that; a mod's might), and its path is then found by its exact name only. Unverified: whether the slot a path names
  counts the file's order of records or the order in which they spawned (`CWorld::LoadWorld` advances its index only for records that
  spawned, so a record that failed to spawn would shift every later slot); the page reads slots as file order, which is the reading under
  which the shipped paths run from point to point. Base-world objects are named, not
  shown. The page was driven by events in tests and looked at in offscreen captures at 1920 by 1080, 1280 by 800 and 1024 by 700 (the
  path numbers are drawn over the marks, above and to the left of each point so that a selected object's tag does not cover them; at
  the smallest size the path line under the map is cut short); nobody has used it by hand.

## 14. MS2: the C# compiler (2026-10-29)

`Missions/` is the reference compiler (`tools/msl_compile.py`) in C#: a lexer, a preprocessor for `#include` and `#define`, and a parser that
writes the instructions as it reads, statement for statement and message for message. `ScriptCompiler.Compile(name, source, readInclude,
constStart, doOnceStart, resolve, notes, limits)` returns the `MissionScript` a world body stores (the same type the Level editor reads).
It writes no file and delegates header reads to its caller. `ScriptCompiler.IncludesFrom(gameFolder)` finds headers by their game-relative
paths with ASCII case matching, only inside the game folder. A link below that folder, a pipe or another non-regular file is refused.
A source that cannot be compiled is a `CompileError`; when its line is known, the error carries the 0-based line and starts "line N: ".
A header the game folder lacks is a `MissingInclude` naming the path. The notes (how a mixed chain of operators was grouped, a handler the game never calls,
a variable declared twice) come back in a list for an editor to show. The limits (a million characters or tokens, four million replacement
steps, 100 levels of nesting) are the reference's and are a parameter, so that the tests put each exactly at its edge.

- **What it is held to.** (1) Authored vectors, written by `tools/msl_vectors.py` from the Python reference: for each source (none is a game
  script) the compiled record as lines, the notes, or the message it was refused with, which the C# must give word for word, including how a
  quoted token reads (the messages use Python's `repr`, reproduced in `PythonText`); the reference's answer for every pair of operators; and a
  few shapes worked out by hand from what the shipped scripts show. (2) The local retail gate, `Development/ScriptsGate.cs`: every compiled
  script of every world body of an installed game is compared with what the C# makes of the source the game folder holds for it, with the
  session's counters taken from the shipped script. Every script is exact, exact once an include the install lacks is bound from the shipped
  constants, or one of the seven pinned stale sources (section 11). A SHA-256 identity of each complete shipped/compiled record pair must
  match the recorded pair; this pins the observed difference, not its explanation. The status of each equals the Python gate's, script by script
  (`msl_gate.py --table`); and a world body whose scripts all compile, written with the compiled scripts in the place of the shipped ones,
  writes back to the bytes it was read from. (3) A mutation sweep over the compiler files and the include lookup (about 170 one-line changes), each of which the vectors, the
  hand-worked shapes or the file and limit tests must fail. The first pass let nine live (the counter reader's anchors, a named pipe or a dot in
  an include path, a minus before a variable, the index a resolver is asked for, a dot followed by something that is not a word, leading zeros in a
  long integer, blanks inside a note's operand) and six did not build; each live one got a vector or a test, the six were rewritten, and all were killed
  on the second pass. One mutant is equivalent on Linux and was dropped: a folder is refused both by `File.Exists` and by the regular-file type
  check, and `File.Exists` is the portable test.
- **Made equal in the Python on the way.** The reference's lexer and directive patterns used Unicode classes (`\d`, `\s`) and `str.split()`;
  they are ASCII blanks and digits now (a source typed in the editor may hold characters a Latin-1 game file cannot), and the compiler takes its 13
  event names from the decoder's table instead of a second copy. The gate's result is unchanged.
- **Limits.** The Level editor's Scripts view calls it to compile a source the player edits (section 15). A source holds names, numbers, strings,
  `TRUE` and `FALSE`: there is no literal for a position or a thing, and a constant of those types exists only when a caller gives one for a name a
  missing header would have defined. A string is single-byte text (Latin-1). Messages are English and quote the reference's wording. The compile
  is not incremental, which does not matter at a script's size. The seven stale sources differ from what the game ships, so the gate cannot say
  whether the C# would have compiled them as the original compiler did.
- **Review findings, work in progress (2026-10-29).** The independent review of MS2 found defects in the include lookup, the grouping
  notes, the session counters and the quoting of characters outside the basic plane. They are fixed in the reference (`tools/msl_compile.py`)
  first: a symbolic link anywhere below the game folder, or the file itself, is refused and never followed; a header that cannot be read, a missing
  game folder and a counter past 2147483647 are refusals with fixed messages; names match in ASCII letter case only; symbols are looked up
  in dictionaries; and a grouping note is made from the chain only when it is written, and says it is not written out when its text would
  repeat more than 5,000 characters. The C# port implements these changes; its reader and header budgets have a focused independent review,
  while native Windows behavior remains unverified. Both compilers now cap each included text at 1,048,576 characters,
  and each script at 128 includes and 2,097,152 included characters in total. A supplied reader runs before its result can be checked;
  the built-in file reader separately bounds the bytes it reads. The Python reader now holds Linux directory descriptors for the primary
  source and included headers, checks identities around the read and fails closed on other platforms; it allows the selected root itself
  to be a link. Regular hard links remain accepted, remote-filesystem behavior is unverified and the checks do not create an immutable
  snapshot. The C# Windows reader is separate; native Windows behavior remains unverified. These are tool limits, not claims about the
  original compiler.

## 15. MS3b: the page that edits a script's source (2026-10-30)

On the Level editor's Scripts view the script card has **Edit source**, **Compile and use** and **Put the shipped script back**, with a note under
them. Edit source makes the source view typeable for one of the level's own scripts that has an installed source file (a base world's script is
shown and not edited, and a script whose file is missing says so on the button). Compile and use compiles the text with the compiler of section 14,
taking headers from the game folder and starting the compile session's two counters where the shipped script's start, and, if it compiles, replaces
the script in the open level as one edit that Undo takes back and Redo brings back. Put the shipped script back is an edit too; when the level already
uses the shipped script it drops the text that was typed instead. Nothing is written until the player chooses Save as mod, which writes a new mod
folder as before.

- **What the page does with the text.** A source that does not compile changes nothing: the note says "line N: ..." with the compiler's message and the
  caret goes to that line. A source that compiles shows the compiler's notes (how a mixed chain of operators was grouped, a handler the game never calls,
  a variable declared twice) beside the result, and "Your changes" says "1 script replaced: NAME (what differs)" beside any objects moved. The text typed
  stays with its script while another is chosen. A text is **in use** when the level's stored script is exactly what that text compiled to (the page
  keeps what each compiled text made and compares the stored bytes), so Undo and Redo move that state with the script: after two texts are compiled in
  turn and the second is taken back, the second is not in use. Text that is typed and not in use counts as unsaved work for the prompts that guard closing
  the companion, choosing another level and switching games, and is written nowhere; the Your changes card names the scripts it was typed for, Put the
  shipped script back drops it, and the line above the source says whether the text on view is the file's, in use or not in use. The note under the buttons
  is about the last compile or reset and goes when it stops being true: when Undo, Redo or another edit changes the level's scripts, when another script
  or level is chosen and, for a refusal, when the text changes. Compiling the unmodified source of one of the stale sources
  (section 11) replaces the script with a different record, because those sources are not the revision the game shipped; the summary says what differs.
- **What is checked before a save.** The structural checker (section 7, `ScriptChecker`) applies the loader's and the script machine's assumptions to every
  replaced script, and a script that fails it is not saved: "Your changes" says why and Save as mod stays disabled.
- **The warning.** Under the note the page shows what to take care of in the script the level uses for the selected script: a call to `Damage` beyond
  what the shipped script has (section 8). It is read from the level as it is now, so Undo takes it away, Redo brings it back and a refused compile leaves
  it. It goes by native, not by target, so it cannot tell a unit that has a script of its own from one that has none, and a shipped script does something
  similar in the retail game and runs through; it is a warning, not a refusal.
- **Checked.** The compile, replace, reset and warning logic has a Godot-free suite and a mutation sweep over the warning rules. The route drives the page:
  typing, compile, refusal with its line, the warning, Undo and Redo, putting the shipped script back, drafts and the prompts, a script with no source and a
  base world's script. Two capture modes drive it in a real offscreen window on the retail layout: `edit` (the steps above at 1920 by 1080, 1280 by 800 and
  1024 by 700, with the frames looked at) and `flow` (the Scripts view across level changes, which must log no engine error).
- **Limits.** Nobody has used the page by hand. The acceptance in section 6 was run once, on Linux, with one edit (section 16); there has been
  no native Windows run (CE's mod loader is Linux-only). The mod holds the edited world file only: the edited source is not kept beside it (source-preserving staging is not built, section 3).
  A source whose header the install lacks cannot be compiled on the page (the message names the header). Text ids are not linked, and the compiler's
  limits (section 14) apply to what is typed. Drafts are not saved anywhere. Drafts and what each compiled text made are kept by script name, which no
  world body of the install repeats (the retail levels gate fails if one does; a level's own script may share a name with one of its base world, and the page keeps the two apart); a
  world that repeated a name would share a draft between the two scripts.

## 16. The CE acceptance of an edited script, on Linux (2026-10-30)

The acceptance of section 6 was run once, on the retail view, with the page's own parts. The edit: level 100's `LevelScript` (the script that plays the tutorial's
messages), Edit source on, the first `PlayCharMessageWait` call's message replaced by the second call's, Compile and use ("1 symbol differs"), Save as mod through the
dialog. The Level editor's capture drives exactly those controls: `--mode=scriptmod --edit=message` (`--script` defaults to `LevelScript`); `--edit=comment` makes the
control, a comment line above the first line, which the compiled script keeps as line numbers (every symbol that holds one differs) and which behaves the same.

- **Items 1 and 2: the bytes.** The saved world file is the shipped body's size and two adjacent bytes differ; read as a model, the one field that differs is that
  script's symbol 42 (a message name's value), none outside the scripts. The strict reader (`world_resources_encode.py`'s `read_world_model`) reads the file and
  `write_world_body` gives the same bytes back. The comment control differs only in that script's line-number symbol fields, and reads and round-trips the same way.
- **Item 3: CE.** A Linux build of Onslaught CE, the default flavour of the port's main at 93cac507 (SHA-256 86f258f2..., the binary a fresh-tree identity proof of that main
  records), run live with the standard offscreen runner (`port/tools/run.py`): `-level 100 -skipfmv -forcewindowed
  -res 640 480`, a read-only game folder, an isolated home and user folder holding `ce.ini` (`mods=level-100-edit`) and the mod's folder (`mod.json` and
  `data/worlds/world100.wrd`, put there with `--start`), dummy audio, no browser, the Intel GPU lock, the real clock. The key presses are scheduled at fixed Presents (a space at 250 and 290 skips the intro cinematic; CE's own screenshot key, F12, at 450 to 870
  every 70), and CE logged the frames as saved 1 to 27 Presents after those. CE's log names the mod and its world file with the SHA-256 the page's receipt gave ("adds data/worlds/world100.wrd",
  "serves data/worlds/world100.wrd to the game"); the runs without the mod have none of those lines.
- **What the frames show.** Five runs, two without the mod, one with the comment control and two with the edit. In the runs without the edit the cockpit's subtitle types out the
  shipped first message; in both runs with it, the second message's text types out in the first one's place, in the same cockpit view. The frames hold the game's text and stay in local-data.
  **Timing**, from CE's own log (`t_ms` stamps interpolated to the Present each screenshot line says it was saved at): in four of the five runs (the second control, the
  comment control and both edit runs) the first frame is 0.86 to 0.89 s after the skip and the last 3.2 to 3.5 s, and they are within about 0.3 s of one another at every frame.
  The first control drew about 2.9 ms per Present against 5.6 to 6.3 ms, so its frames show an earlier moment (0.4 to 1.6 s after the skip). The comparison therefore rests
  on the two time-matched controls, the second control and the comment control, against both edit runs; the first control agrees with them at its own moment. Runs on the
  real clock cannot be matched to the Present, so the comparison is of the text written, not of pixels: none of the three controls shows the edit.
- **Fences.** CE switches mods off whenever a deterministic clock (`run.py --virtual`, `BEA_PORT_CLOCK`), a tape, probes, a recording, a pilot or autopilot, or a network host, join or
  handoff is active (`port/platform/common/mods.cpp`; at 93cac507 CE's own README says only "replays, recordings and network play"; the launcher's own `--record`, or `record_sessions=1` in `ce.ini`, sets `BEA_PORT_RECORD` and `BEA_PORT_CLOCK`, which is how a player meets this), and its screenshot key is taken only when no menu or
  its console has the keyboard. A mod run is therefore live and on the real clock, with no
  pixel-exact comparison between runs.
- **The released package, repeated.** The same pair (one control, one run with the message edit) was run again with the released Onslaught CE 0.1.12 Linux package's own
  binary in place of the build of main: the same driver, runner, flags and key schedule, the mod re-staged by the committed capture (byte-identical). The package is the
  release asset `onslaught-ce-0.1.12-linux-i686.tar.gz`: its size (6,844,827 bytes) and SHA-256 (31f96ae0...) are the `linux-i686` entry of the release's update feed
  (`ce-update-v2.json`, read from the release's public assets), whose Ed25519 signature was verified against the launcher's pinned public key; its `bea` has SHA-256
  1f036553.... CE's log has the same four mods lines in the mod run (the world file served once, with the receipt's SHA-256) and none in the control. **The pair is not
  time-matched:** the control's frames are 0.88 to 3.43 s after the skip (6.0 ms per Present) and the mod run's 1.36 to 4.82 s (8.3 ms), so the text can only be compared at
  comparable moments, and the release adds a second binary to the claim, not a second sample of the comparison. Counted without reading (pixels of the 350 by 90 subtitle
  band that differ by more than 48 grey levels, out of 31,500): at the last frame the three runs with the edit (two runs of the build of main, one run of the release) are identical to one another
  (0), the three time-matched controls (the second control, the comment control, the release control) are identical to one another (0), and every edit frame differs from
  every one of those controls by 2,740 to 2,770; the release pair differs at all seven frames (2,100 to 2,800). The package's mod loader is Linux-only, as the build's.
- **Through the released launcher, one run of each kind.** The package's own launcher, `onslaught-ce`, with the command line the player is told to use (`--no-update-check
  -level 100 -skipfmv -forcewindowed`), started the game itself, offscreen. What differs from the runner's runs: the user folder is a scratch folder the test script made with
  plain file writes (for the mod run, the mod folder and a `ce.ini` holding the one line `mods=level-100-edit`) in place of the runner's `--start`; `BEA_USER_DIR` and
  `BEA_GAME_DIR` are set by the script; the guards the runner sets (offscreen video, dummy audio, the Intel GPU filter, no session bus, the iGPU lock held by the script), the key
  presses and the frame limit are given by environment, and the runner's own checks (its refusals when the offscreen or dummy-audio driver is missing, its core-dump and timeout
  handling) are not applied, though both logs show the offscreen driver and the x87 control word 007f. The launcher, not the runner, started the game as its child with its own
  environment, hashed the game executable before starting it (SHA-256 1f036553..., the package's `bea`) and wrote the game's log into the user folder; that log names the version
  (Onslaught CE v0.1.12, build 1911463d9d71) and, in the mod run, has the same four mods lines (the world file with SHA-256 1504f7e3..., served once) and none in the control.
  Timing, from the logs as above: this pair is not time-matched either (the control's frames are 0.52 to 2.15 s after the skip at 3.9 ms per Present, the mod run's 1.20 to
  4.78 s at 8.5 ms). Counted without reading (the same band): the launcher's mod run differs from the runner's run of the release in at most 78 of 31,500 pixels at every frame
  (0 at five of the seven; the paces were alike, 8.5 and 8.3 ms per Present), and from the launcher's control at all seven (1,926 to 3,037). One run of each kind; the claim stays
  the one above.
- **What was tried first.** The `Weather` script's starting snow density (one symbol, 0.1 to 0.8). The mod loaded and the log named it, but no frame difference rose above
  the run-to-run noise (two runs with the edit differed from each other by as many pixels as one differed from a control), and the script's text print did not appear in the
  console. That edit is not evidence of a changed behaviour and is not claimed: a mod's log lines alone do not show one.
- **What this shows.** In the two edit runs made, on one machine, an edit made in the page's source editor, compiled by the Toolkit's compiler and saved by the page's stager is
  read by CE on Linux and changes what the game does as the edit says; and a whole-script recompile with every line number different behaves as the shipped script for the same
  messages (one run).
- **What it does not show.** A person using the page by hand. Any behaviour beyond one message in one script of one level: timers, spawns, AI and the `Damage` warning are
  not covered. A Windows run (CE's mod loader is Linux-only; Windows ignores `mods=`). That every installed script recompiles to what the game ran (the stale sources and the
  sources whose header the install lacks, section 11, are outside it). The sound (the audio driver was the dummy), play past the opening, or a player at a desktop starting the released launcher with a mod of their own (the launcher was run once, offscreen, from
  a scratch folder, with the key presses and the frame limit given by environment).


## 17. Play this level with the changes (M6, 2026-10-30)

The Level editor's changes box has a button, **Play this level with the changes**, which starts Onslaught CE at the open level with the changes as they are now. It works from the
open edit (nothing has to be saved first, and nothing is saved by it: the edit still counts as unsaved), on Linux, with a CE of 0.1.11 or later. The first design (the roadmap's)
was to switch the mod on in the player's own `ce.ini`, start the level and switch it off afterwards. A companion or CE that dies in between would leave a mod switched on in the
player's careers, so the button never writes the player's CE folder at all: it makes a temporary CE user folder of its own.

- **What it does.** `CePlay` makes a new folder inside the companion's own play folder (`ce-play`, beside its settings) and puts in it a copy of the player's `ce.ini` (their lines kept as
  they are, through the settings writer's own line handling, with `mods=` naming only this mod, `record_sessions=0` and `update_check=0`), a copy of their options file
  (`defaultoptions.bea`; never a career, a tape or anything else) and the mod, staged by the same stager as Save as mod. It starts CE's own launcher from its package folder with
  `--no-update-check -level N -skipfmv -forcewindowed`, `BEA_USER_DIR` set to the temporary folder and `BEA_GAME_DIR` to the game folder the editor read, and the variables that make
  CE switch mods off removed (section 16). It waits for CE to close, keeps the first megabyte of CE's log as `last-session.log` in the play folder, reads the log's lines about mods
  (the page shows them when CE did not say it served the mod's world file) and removes the temporary folder.
- **What it never does.** It never writes the player's CE folder, `ce.ini` or careers, never copies a career, never starts CE in the player's own folder (a play folder that is, holds or lies
  inside it is refused before anything is made), never records the session, and never leaves a mod enabled. Because mods are off in a session CE records (the launcher's `--record`, or
  `record_sessions=1` in `ce.ini`, sets `BEA_PORT_RECORD` and `BEA_PORT_CLOCK`), the copy of `ce.ini` turns recording off.
- **The temporary folder.** Made exclusively (`mkdirat`, so a name that exists is never reused), private to the player, with a marker file only `CePlayFolder` writes (its format, the
  folder's name, the companion's process, the launcher's process, the level and the mod). It is removed by the one folder the companion made, and every step is by name in an open folder, so no path
  is followed: the play folder is opened without following a link, the temporary folder by name inside it (the open fails for a link or a file; the marker is read through it, and must name it), every
  folder under it the same way, names are read through the open descriptor, and files are unlinked and folders removed by name in the folder that holds them. A link or a special file inside (CE
  writes none) is left where it is, never followed, and reported; a folder swapped for a link after its kind was read fails to open and stays; the marker goes last, so a folder that could not
  be removed whole is still known as the companion's. At the companion's start a sweep removes the folders an earlier run left, only direct children of the play folder that carry the marker,
  whose companion and CE are no longer running.
- **When it refuses.** On Windows (CE loads a level's world from a mod on Linux only for now), with no CE launcher chosen, with a CE older than 0.1.11 (it would show the unchanged level),
  with an affected launcher package (0.1.0 to 0.1.6), with no change made, with a test play running, and when the edit cannot be staged. The reason is the button's tooltip.
- **Checks.** The route's play suites check the folder, the sweep, the `ce.ini` copy, the launcher's start (arguments, environment, the fence variables), the unchanged player's folder
  and game folder, the refusals and the button on an authored level; a mutation sweep of the new code found three gaps (an oversized marker, a package that turns into an affected
  launcher after its version was known, a redundant second comparison with the player's folder) and each is closed. The capture's `play` mode runs the
  button end to end: the same edit as section 16, then the button pressed with the released Onslaught CE 0.1.12 package as the launcher, offscreen (the guards of `port/tools/run.py`, the key presses and a frame
  limit given by environment through the play hooks). CE exited 0 after the run; its log, kept from the temporary folder, has the same four mods lines as section 16 (the world file with
  SHA-256 1504f7e3..., the same bytes the page's Save as mod writes, served once) and the temporary `ce.ini` it was given was the scratch player's with `mods=play-level-100`, `record_sessions=0` and
  `update_check=0` (the player's `record_sessions=1` and a stand-in `mods=` line did not reach it, and an unknown key was kept); the scratch player's CE folder (a `ce.ini`, a stand-in
  career and a tape) was byte for byte as before and the game folder had the same files and sizes; the temporary folder was gone and the edit still counted as unsaved. The frames, looked at, type the second message's text. They are
  not time-matched to the section 16 runs (this run drew at 6.0 ms per Present, its frames 0.92 to 3.39 s after the intro skip, against 0.52 to 2.15 s at 3.9 ms for the launcher control and
  1.20 to 4.78 s at 8.5 ms for the launcher mod run), so the counts need the same care: its subtitle band differs from that control's at all seven frames (1,592 to 3,025 of 31,500 pixels),
  and its last frame is identical in the band (0 pixels) to the last frame of that mod run, the same message typed out in full. Two earlier runs of the capture, on earlier commits,
  agree by reading. The frames hold the game's text and stay in local-data.
- **What it does not show.** Nobody has used the button by hand. One level (100) and one edit; the `-level N` start of other levels is not tried. The run was offscreen from a capture with the key
  presses and the frame limit given by environment, with dummy audio (nothing was heard), and on one machine. Windows is out. A test play uses the unchanged settings of the player's `ce.ini` apart from
  the three keys, so a setting that changes how CE starts (a resolution, say) applies to it too. Enabling a mod in the player's own `ce.ini` through the settings writer, with its backups, is a separate
  step that is not built.
