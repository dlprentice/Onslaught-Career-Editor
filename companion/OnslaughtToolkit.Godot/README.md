# Godot Save Lab

Status: first companion workflow; native shell opens, complete UI write/reopen validation pending.
Last updated: 2026-09-07
Summary: an MIT Godot interface for inspecting a real career and writing one verified kill-count change to a new copy.

Open a real `.bes` file, inspect its version, size, completed-level count and five
kill categories, choose a different count, and select a fresh `.bes` filename.
**Write verified copy** calls AppCore's `SaveLabService.WriteKillCountCopy` and
then reopens the result with `SaveLabService.Open`. The result shows the output
path and SHA-256, changed-byte count, original-file verification and preservation
of every untargeted byte. The original remains the source for later copies.

Existing output files are refused. The file dialogs only choose paths; their
delete, folder-creation and overwrite-confirmation actions are disabled. This UI
does not create a career from scratch, discover saves, overwrite a file or launch
the game. `Ctrl+O` opens the input dialog; use Tab, Shift+Tab and Enter
to move through and activate the controls.

Build and run on Linux with the installed pinned Godot 4.7.2 .NET engine:

```bash
npm run build:companion-godot
npm run run:companion-godot
npm run test:save-lab
```

The AppCore packages must already be restored or available in the package cache;
the local Godot package source does not contain third-party AppCore dependencies.
The project enables .NET SDK framework-package pruning for legacy transitive
dependencies supplied by .NET 8 itself.
The launcher uses the bundled Godot package source and locked restore, puts
engine user data/cache and scratch under canonical `local-data/companion/`,
and preserves each run's log in a fresh child there. `-- --no-build` reuses an
existing build. Project `.godot/`, `bin/` and `obj/` output is ignored. Put captures
and copied test inputs under the same ignored `local-data/companion/` owner.
The application never opens a fixture automatically.

The write and validation behavior belongs to
[`SaveLabService`](../../OnslaughtCareerEditor.AppCore/SaveLabService.cs) and its
existing AppCore tests. This project is presentation only. See
[`PROVENANCE.md`](PROVENANCE.md) for the independent licensing boundary.
