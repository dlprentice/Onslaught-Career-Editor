# Companion provenance and license

Status: active licensing boundary.
Last updated: 2026-09-07
Evidence: SOURCE — the companion project reference, SaveLab.cs and the AppCore service named below.
Summary: the Godot companion uses the repository's MIT application layer and excludes the GPL reconstruction and retail payloads.

`SaveLab.cs` and the project/scene files are original MIT application code under
the repository's [`LICENSE`](../../LICENSE). The only project reference is the
MIT [`OnslaughtCareerEditor.AppCore`](../../OnslaughtCareerEditor.AppCore/OnslaughtCareerEditor.AppCore.csproj)
`net8.0` target. Its existing analysis and verified-copy service own the save
format; this UI contains no save-byte offsets, decoding or patching logic.

Godot and its .NET SDK are MIT-licensed dependencies. AppCore's existing NuGet
dependencies retain their own licenses. No font, icon, sound, game binary,
texture, converted retail asset, decompiler output or user save is bundled here.
The interface uses Godot's built-in controls and default font.

There is no reference to `rebuild/` or `references/Onslaught`. That reconstruction
remains GPL-3.0-or-later; using Godot for both applications does not combine their
licenses or source boundaries. The retained WinUI source is unchanged by this UI.

The displayed save information is the result of `SaveLabSession.Analysis`.
Verification labels report `SaveLabWriteResult` fields, followed by an explicit
service reopen and comparison with its written SHA-256 and selected kill count.
They are checks of that file operation, not a claim about later game behavior.
