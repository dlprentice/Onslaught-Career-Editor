// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The Level editor's Scripts view driven through the page: the list beside the source, the card, the search, and the links between a script
/// and the objects that name it, on an authored level archive with scripts and a base world. Authored data only; nothing is written to the game
/// folder (the test checks that).
/// </summary>
internal static class ScriptsPageTests
{
    /// <summary>
    /// Gamma's source: a comment, then calls whose quoted texts name the authored level's path, an object, an event, nothing, and an object of the base world;
    /// then the path in other letter case, as a follow-waypoint call's argument (which the game finds) and as an object's name (which it does not).
    /// </summary>
    private const string Gamma = "// gamma\r\nFollowWaypoint(\"Path A\", 0);\r\nGetThingRef(\"Tank 1\");\r\nPostEvent(\"go\");\r\nGetThingRef(\"ghost\");\r\nGetThingRef(\"Base Hut\");\r\n" +
                                 "FollowWaypointWait(\"path a\", 0, 5);\r\nGetThingRef(\"path a\");\r\nFollowWaypoint(\"base path\", 0);\r\n";

    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    private static string[] Snapshot(string root) => [.. Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories).Order(StringComparer.Ordinal)
        .Select(path => Path.GetRelativePath(root, path) + " " + Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path))))];

    // ---- the page ---------------------------------------------------------------------------------------------------------------
    private static byte[] Chunk(string tag, byte[] payload)
    {
        byte[] bytes = new byte[8 + payload.Length];
        Encoding.ASCII.GetBytes(tag, bytes);
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(4), (uint)payload.Length);
        payload.CopyTo(bytes, 8);
        return bytes;
    }

    private static byte[] Join(params byte[][] parts) => [.. parts.SelectMany(part => part)];

    private static byte[] Words(params int[] values)
    {
        byte[] bytes = new byte[values.Length * 4];
        for (int i = 0; i < values.Length; i++) BinaryPrimitives.WriteInt32LittleEndian(bytes.AsSpan(i * 4), values[i]);
        return bytes;
    }

    /// <summary>An authored level archive (one zlib member) holding a base world and a world of the level's own, laid out as the vectors' archives are.</summary>
    private static byte[] LevelArchiveBytes(int baseLevel, int realLevel, byte[] baseBody, byte[] realBody)
    {
        byte[] wrld = Join(Chunk("WDAT", Words(baseLevel, realLevel)), Chunk("BSWD", baseBody), Chunk("RLWD", realBody));
        byte[] stream = Join(Chunk("LVLR", Words(103)), Chunk("TARG", Words(1)), Chunk("AYAD", new byte[24]), Chunk("ERES", new byte[40]), Chunk("WRES", Chunk("WRLD", wrld)), Chunk("LNDS", []));
        using MemoryStream packed = new();
        using (ZLibStream zlib = new(packed, CompressionLevel.Optimal, leaveOpen: true)) zlib.Write(stream);
        byte[] member = packed.ToArray();
        return Join(Words(member.Length), member);
    }

    private static void Source(string game, int level, string name, string text)
    {
        string folder = Path.Combine(game, "data", "MissionScripts", $"level{level}");
        Directory.CreateDirectory(folder);
        File.WriteAllBytes(Path.Combine(folder, name + ".msl"), Encoding.Latin1.GetBytes(text));
    }

    private static IReadOnlyList<string[]> Cells(Tree list)
    {
        List<string[]> rows = [];
        for (TreeItem? item = list.GetRoot()?.GetFirstChild(); item is not null; item = item.GetNext())
            rows.Add([item.GetText(0), item.GetText(1), item.GetText(2)]);
        return rows;
    }

    internal static async Task RunAsync(CompanionApp app, SceneTree tree, FakeInstall install, string outputDirectory, Checks check)
    {
        check.Suite("level scripts page");
        LevelEditorPage page = app.LevelEditor;
        string resources = Path.Combine(install.Game, "data", "resources");
        string archive = Path.Combine(resources, "130_res_PC.aya");

        // Level 130: its own world (scripts alpha, beta and gamma; things naming them) and the base world of level 131 (a script of the same name, and another).
        WorldBody real = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [0, 3], [], ("Pause", 2)), LevelScriptTests.Script("beta", [], ["go"], ("PostEvent", 1)), LevelScriptTests.Script("gamma", [], []),
            LevelScriptTests.Script("delta", [], [.. Enumerable.Range(1, 14).Select(number => $"h{number}")]));
        real.Scripts[0].Code.Symbols.Add(new ScriptSymbol { Name = "const data40", DataType = 3, Value = new ScriptText("x"), Index = 0, Flag = 1 });  // the shipped alpha's first constant is number 40
        real.Scripts[0].Code.NextSymbolIndex = 1;
        real.Things[0].Init.Script = "alpha";
        real.Things[1].Init.SpawnScript = "alpha";
        real.Things[2].Init.Script = "ghost";
        real.Things[3].Init.Script = "beta";
        // Its path "Path A" names a unit, a waypoint, a unit, a waypoint and a feature (slots 1, 3, 0, 2, 4): the game keeps the waypoints, rows 3 and 2, as its points.
        real.WaypointPaths[0].Slots.Clear();
        real.WaypointPaths[0].Slots.AddRange([1, 3, 0, 2, 4]);
        WaypointPath lone = new() { Name = "Lone" };  // three slots, of which only the waypoint at row 2 is a point: a single point has no line
        lone.Slots.AddRange([1, 2, 0]);
        real.WaypointPaths.Add(lone);
        real.Things[2].Init.Position = new(100f, 20f, 0f);
        real.Things[3].Init.Position = new(300f, 60f, 0f);
        WorldBody baseWorld = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [1], [], ("Print", 1)), LevelScriptTests.Script("basey", [0], []));
        baseWorld.Things[1].Init.Name = "Base Hut";  // an object the level's table does not list
        baseWorld.WaypointPaths[0].Name = "Base Path";  // a path of the base world (the game finds those before the level's own paths of the same name); its name differs from the level's "Path A"
        File.WriteAllBytes(archive, LevelArchiveBytes(131, 130, baseWorld.Write(), real.Write()));
        // A second level with one short script: what the view shows after the level is changed (the base world slot of its archive is left empty: no base level).
        WorldBody shortWorld = LevelScriptTests.Body(LevelScriptTests.Script("shorty", [0], []));
        File.WriteAllBytes(Path.Combine(resources, "140_res_PC.aya"), LevelArchiveBytes(-1, 140, shortWorld.Write(), shortWorld.Write()));
        Source(install.Game, 140, "shorty", "// shorty\r\ninit()\r\n{\r\n}\r\n");
        Source(install.Game, 130, "alpha", "// alpha, the level's own\r\ninit()\r\n{\r\n\tPause(1);\r\n}\r\n");
        Source(install.Game, 130, "gamma", Gamma);
        Source(install.Game, 130, "delta", string.Concat(Enumerable.Range(0, 300).Select(line => $"// line {line}\r\n")));  // long enough to scroll far down
        Source(install.Game, 131, "alpha", "// alpha, the base world's\r\narrived()\r\n{\r\n}\r\n");
        Source(install.Game, 131, "basey", "// basey\r\ninit()\r\n{\r\n}\r\n");
        string[] gameBefore = Snapshot(install.Game);
        try
        {
            foreach (Window window in app.FindChildren("*", nameof(Window), true, false).OfType<Window>().Where(window => window.Visible)) window.Hide();
            app.Navigate("home");
            app.Navigate("levels");
            await Frame(tree);
            check.That(page.OpenLevel(130), "the authored level with scripts opens");
            for (int frame = 0; frame < 4; frame++) await Frame(tree);
            LevelEditorModel model = page.Model!;
            check.That(model.Scripts.Count == 6 && model.Scripts.Count(entry => entry.FromBaseWorld) == 2 && model.Scripts.Where(entry => !entry.FromBaseWorld).All(entry => entry.SourceLevel == 130) &&
                       model.Scripts.Where(entry => entry.FromBaseWorld).All(entry => entry.SourceLevel == 131 && entry.Summary.Uses.Count == 0),
                "the model lists the level's own scripts, then the base world's (which carry no rows), each with the level its source is in");
            check.That(page.ScriptsToggle.IsVisibleInTree() && !page.ScriptsToggle.ButtonPressed && !page.Scripts.Visible && page.Table.IsVisibleInTree() && page.Subtitle.EndsWith("4 scripts", StringComparison.Ordinal),
                $"the page starts on the objects, offers the Scripts switch and counts the level's own scripts: \"{page.Subtitle}\"");

            // The Scripts switch puts the list and the source where the table and the map were.
            page.ScriptsToggle.ButtonPressed = true;
            await Frame(tree);
            check.That(page.Scripts.IsVisibleInTree() && !page.Table.IsVisibleInTree() && !page.Map.IsVisibleInTree() && !page.MapToggle.IsVisibleInTree() && page.ScriptCardTitle == "alpha",
                "the switch shows the scripts in place of the table and the map, the first script selected");
            IReadOnlyList<string[]> rows = Cells(page.Scripts.List);
            check.That(rows.Count == 6 && rows[0][0] == "alpha" && rows[0][1] == "2 objects" && rows[0][2] == "init, died" && rows[1][0] == "beta" && rows[1][1] == "1 object" && rows[1][2] == "event \"go\"" &&
                       rows[2][0] == "gamma" && rows[2][1] == "—" && rows[2][2] == "" && rows[3][0] == "delta" && rows[3][1] == "—" && rows[4][0] == "alpha" && rows[4][1] == "base world" && rows[5][0] == "basey",
                $"the list shows each script, what names it and what it handles, the base world's last: {string.Join(" | ", rows.Select(row => string.Join(",", row)))}");
            check.That(page.Scripts.Source.Text == "// alpha, the level's own\ninit()\n{\n\tPause(1);\n}\n" && !page.Scripts.Source.Editable && page.Scripts.Source.GuttersDrawLineNumbers &&
                       page.Scripts.Info == "level130/alpha.msl · 5 lines · read only",
                $"the source is shown read only with line numbers, and the line says where it is from: \"{page.Scripts.Info}\"");
            check.That(page.Scripts.InfoLabel.MouseFilter == Control.MouseFilterEnum.Pass && page.Scripts.InfoLabel.TooltipText.StartsWith(Path.Combine(install.Game, "data", "MissionScripts", "level130", "alpha.msl"), StringComparison.Ordinal),
                $"the line's tooltip, which has the whole path, can be reached with the pointer: {page.Scripts.InfoLabel.MouseFilter} \"{page.Scripts.InfoLabel.TooltipText}\"");
            check.That(page.ScriptCardText.Contains("Handles: init, died", StringComparison.Ordinal) && page.ScriptCardText.Contains("Calls: Pause ×2", StringComparison.Ordinal) &&
                       page.ScriptCardText.Contains("Named by:", StringComparison.Ordinal) && page.ScriptUseButtons.Select(button => button.Text).SequenceEqual([$"0 · {model.Row(0)!.Label}", $"1 · {model.Row(1)!.Label}"]),
                $"the card says what the script handles and calls, and offers the objects that name it: \"{page.ScriptCardText}\"");

            // The view scrolled or its caret left far down a long source, then another script chosen: the shorter text must never be asked for a line past its end
            // (Godot reports those as engine errors, which fail the run).
            check.That(page.Scripts.Select("delta") && page.Scripts.Source.GetLineCount() == 301, "a long source is shown whole");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.Scripts.Source.ScrollVertical = 250;
            page.Scripts.Source.SetCaretLine(290);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            foreach (string next in new[] { "alpha", "delta", "beta", "delta", "gamma" })
            {
                page.Scripts.Source.ScrollVertical = 250;
                page.Scripts.Source.SetCaretLine(Math.Min(290, page.Scripts.Source.GetLineCount() - 1));
                check.That(page.Scripts.Select(next), $"{next} is chosen after the view was left far down");
                for (int frame = 0; frame < 3; frame++) await Frame(tree);
            }
            check.That(page.Scripts.Source.GetCaretLine() == 0 && page.Scripts.Source.ScrollVertical == 0, "and a script chosen starts at its first line");
            check.That(page.Scripts.Select("delta"), "the long script is chosen again");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.Scripts.Source.ScrollVertical = 250;
            page.Scripts.Source.SetCaretLine(290);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.Search.Text = "zzz";  // nothing matches: the source is emptied while the view is far down
            page.Search.EmitSignal(LineEdit.SignalName.TextChanged, "zzz");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == "" && page.Scripts.Source.ScrollVertical == 0,
                $"a search nothing matches empties the view from its top: {page.Scripts.Source.Text.Length} characters, scroll {page.Scripts.Source.ScrollVertical}, {page.Scripts.ShownCount} scripts shown");
            page.Search.Text = "";
            page.Search.EmitSignal(LineEdit.SignalName.TextChanged, "");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);

            // A long list of events is cut after twelve, as the list of functions is.
            check.That(page.Scripts.Select("delta") && page.ScriptCardText.Contains("Handles: " + string.Join(", ", Enumerable.Range(1, 12).Select(number => $"event \"h{number}\"")) + " and 2 more", StringComparison.Ordinal),
                $"a script with fourteen named handlers shows twelve and says two more: \"{page.ScriptCardText}\"");

            // A script with no source file says so; a script of the base world is read from the base level's folder.
            check.That(page.Scripts.Select("beta") && page.Scripts.Source.Text == "" && page.Scripts.Info == "No file named beta.msl in level130." && page.ScriptCardTitle == "beta" &&
                       page.ScriptCardText.Contains("Handles: event \"go\"", StringComparison.Ordinal) && page.ScriptCardText.Contains("No file named beta.msl", StringComparison.Ordinal),
                $"a script with no source file says which file is missing: \"{page.Scripts.Info}\"");
            check.That(page.Scripts.Select("gamma") && page.Scripts.Source.Text == Gamma.Replace("\r\n", "\n") && page.ScriptCardText.Contains("Handles no event", StringComparison.Ordinal) &&
                       page.ScriptCardText.Contains("Calls no game function", StringComparison.Ordinal) && page.ScriptCardText.Contains("No object in this level names it", StringComparison.Ordinal) && page.ScriptUseButtons.Count == 0,
                "a script that handles, calls and is named by nothing says each");
            check.That(page.Scripts.Select("alpha", fromBase: true) && page.Scripts.Source.Text == "// alpha, the base world's\narrived()\n{\n}\n" && page.ScriptCardText.Contains("base world of level 131", StringComparison.Ordinal) &&
                       page.ScriptUseButtons.Count == 0 && page.Scripts.Current!.FromBaseWorld,
                "a base world's script of the same name is read from the base level's folder and says it is the base world's");

            // The search narrows the list by name, event or function, and a script chosen from elsewhere clears what would hide it.
            page.Search.Text = "go";
            page.Search.EmitSignal(LineEdit.SignalName.TextChanged, "go");
            check.That(page.Scripts.ShownCount == 1 && Cells(page.Scripts.List)[0][0] == "beta" && page.Scripts.Current?.Summary.Name == "beta", "a search by event name keeps the script that handles it and selects it");
            page.Search.Text = "pause";
            page.Search.EmitSignal(LineEdit.SignalName.TextChanged, "pause");
            check.That(page.Scripts.ShownCount == 1 && Cells(page.Scripts.List)[0][0] == "alpha", "a search by a function a script calls finds it");
            page.Search.Text = "zzz";
            page.Search.EmitSignal(LineEdit.SignalName.TextChanged, "zzz");
            check.That(page.Scripts.ShownCount == 0 && page.Scripts.EmptyText == "No script matches the search." && page.Scripts.Source.Text == "" && page.ScriptCardTitle == "Nothing selected",
                "a search nothing matches says so and clears the source and the card");
            check.That(page.ShowScript("gamma") && page.Search.Text == "" && page.Scripts.ShownCount == 6 && page.Scripts.Current?.Summary.Name == "gamma", "showing a script clears a search that would hide it");

            // From a script to the objects that name it: back to the table and the map, with the object selected.
            page.Scripts.Select("alpha");
            Button first = page.ScriptUseButtons[0];
            first.EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            check.That(!page.ScriptsToggle.ButtonPressed && page.Table.IsVisibleInTree() && page.SelectedRow == 0 && page.Map.Selected == 0 && page.Table.GetSelected()?.GetMetadata(0).AsInt32() == 0,
                $"an object that names the script is shown on the table and the map: row {page.SelectedRow}");

            // From an object to the scripts it names; one this level has no script of is said, not offered.
            check.That(page.ObjectScriptButtons.Select(button => button.Text).SequenceEqual(["Script: alpha"]), $"the selected object offers the script it runs: \"{page.ObjectScriptsText}\"");
            page.SelectIndex(1);
            check.That(page.ObjectScriptButtons.Select(button => button.Text).SequenceEqual(["Spawn script: alpha"]), $"and its spawn script: \"{page.ObjectScriptsText}\"");
            page.SelectIndex(2);
            check.That(page.ObjectScriptButtons.Count == 0 && page.ObjectScriptsText == "Script: ghost (this level has no script of that name)", $"a script the level does not have is only said: \"{page.ObjectScriptsText}\"");
            page.SelectIndex(4);
            check.That(page.ObjectScriptsText == "", "an object that names no script shows none");
            page.SelectIndex(3);
            page.ObjectScriptButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            check.That(page.ScriptsToggle.ButtonPressed && page.Scripts.Current?.Summary.Name == "beta" && !page.Scripts.Current.FromBaseWorld && page.ScriptCardTitle == "beta",
                "pressing a script button shows that script, the level's own");

            // The caret in a quoted text of the source says what in the level has that name, each a button that goes to it.
            async Task<bool> CaretAt(int line, int column)
            {
                page.Scripts.Source.SetCaretLine(line);
                page.Scripts.Source.SetCaretColumn(column);
                for (int frame = 0; frame < 3; frame++) await Frame(tree);
                return true;
            }

            page.ShowScript("gamma");
            await Frame(tree);
            await CaretAt(1, 18);
            check.That(page.Scripts.Token == new SourceToken("Path A", true, 16, 6, true) && page.NamesTitle == "“Path A” names:" && page.NameButtons.Select(button => button.Text).SequenceEqual(["path Path A · 2 points"]),
                $"the caret in a quoted text names what it names, the path's points being the ones the game keeps: \"{page.NamesTitle}\" {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
            check.That(page.HidePath.Visible && page.HidePath.Disabled && page.HighlightedPathText == "", "Hide path is in the row from the start, disabled, so that the map keeps its height when a path is shown");
            page.NameButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            WorldBody world = model.Session!.Body;
            int[] pathRows = [.. WaypointCatalog.Rows(world, world.WaypointPaths[0])];
            check.That(pathRows.SequenceEqual([3, 2]) && world.WaypointPaths[0].Slots.Count == 5, "the path has five slots and the game keeps two of them as points, rows 3 and 2");
            double expectedLow = pathRows.Min(row => (double)model.Row(row)!.Position.X), expectedHigh = pathRows.Max(row => (double)model.Row(row)!.Position.X);
            check.That(!page.ScriptsToggle.ButtonPressed && page.Map.HighlightedPath == 0 && page.Map.DrawablePaths == 1 && page.HidePath.Visible && !page.HidePath.Disabled && page.HighlightedPathText == "Path Path A · 2 points, numbered along it" &&
                       Math.Abs(page.Map.View.CenterX - (expectedLow + expectedHigh) / 2) < 1e-4 && page.Map.View.Scale >= page.Map.View.FitScale,
                $"the path button shows the path on the map, numbered, and brings the map to it: highlighted {page.Map.HighlightedPath}, \"{page.HighlightedPathText}\", centre {page.Map.View.CenterX} (the points' x run {expectedLow} to {expectedHigh}), scale {page.Map.View.Scale}");
            check.That(page.PathLabel.MouseFilter == Control.MouseFilterEnum.Pass && page.PathLabel.TooltipText == page.HighlightedPathText, "the path line's tooltip, which has the whole text, can be reached with the pointer");
            page.HidePath.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.Map.HighlightedPath is null && page.HidePath.Visible && page.HidePath.Disabled && page.HighlightedPathText == "", "Hide path stops highlighting it, and stays in the row, disabled");
            check.That(!page.Map.ShowAllPaths, "the Paths switch starts off");
            page.PathsToggle.ButtonPressed = true;
            check.That(page.Map.ShowAllPaths && page.Map.DrawablePaths == 1, "the Paths switch draws every path");
            page.PathsToggle.ButtonPressed = false;

            page.ShowScript("gamma");
            await Frame(tree);
            await CaretAt(2, 15);
            check.That(page.NamesTitle == "“Tank 1” names:" && page.NameButtons.Select(button => button.Text).SequenceEqual(["unit 0 · Tank 1"]), $"a quoted text that is an object's name offers the object: \"{page.NamesTitle}\" {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
            check.That(page.NameLabels.Select(label => label.Text).SequenceEqual(["unit 0 · Tank 1 · base world"]), $"and says the base world has an object of that name too, beside the button: {string.Join(" | ", page.NameLabels.Select(label => label.Text))}");
            page.NameButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            check.That(!page.ScriptsToggle.ButtonPressed && page.SelectedRow == 0 && page.Map.Selected == 0, "and its button shows the object on the table and the map");
            page.ShowScript("gamma");
            await Frame(tree);
            await CaretAt(3, 12);
            check.That(page.NamesTitle == "“go” names:" && page.NameButtons.Select(button => button.Text).SequenceEqual(["event handled by beta"]), $"a text that is an event a script handles offers that script: {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
            page.NameButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            check.That(page.Scripts.Current?.Summary.Name == "beta" && page.ScriptsToggle.ButtonPressed, "and its button shows that script");
            page.ShowScript("gamma");
            await Frame(tree);
            await CaretAt(4, 18);
            check.That(page.NamesTitle == "“ghost” names nothing in this level." && page.NameButtons.Count == 0 && page.NameLabels.Count == 0, $"a quoted text that names nothing says so: \"{page.NamesTitle}\"");
            await CaretAt(5, 18);
            check.That(page.NamesTitle == "“Base Hut” names:" && page.NameButtons.Count == 0 && page.NameLabels.Select(label => label.Text).SequenceEqual(["unit 1 · Base Hut · base world"]) &&
                       page.NameLabels[0].MouseFilter == Control.MouseFilterEnum.Pass && page.NameLabels[0].TooltipText.Contains("level 131", StringComparison.Ordinal),
                $"a name only an object of the base world has is said, with nothing to go to: \"{page.NamesTitle}\" {string.Join(" | ", page.NameLabels.Select(label => label.Text))} / {page.NameLabels.FirstOrDefault()?.TooltipText}");
            await CaretAt(6, 24);
            check.That(page.Scripts.Token == new SourceToken("path a", true, 20, 6, true) && page.NamesTitle == "“path a” names:" && page.NameButtons.Select(button => button.Text).SequenceEqual(["path Path A · 2 points (other letter case)"]),
                $"the path argument of a follow-waypoint call is found in any letter case, and the button says so: \"{page.NamesTitle}\" {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
            await CaretAt(7, 15);
            check.That(page.Scripts.Token == new SourceToken("path a", true, 13, 6) && page.NamesTitle == "“path a” names nothing in this level." && page.NameButtons.Count == 0,
                $"the same text anywhere else is not a path, as the game compares those names as they are: \"{page.NamesTitle}\"");
            await CaretAt(8, 20);
            check.That(page.Scripts.Token == new SourceToken("base path", true, 16, 9, true) && page.NamesTitle == "“base path” names:" && page.NameButtons.Count == 0 &&
                       page.NameLabels.Select(label => label.Text).SequenceEqual(["path Base Path · 1 point (other letter case) · base world"]) && page.NameLabels[0].TooltipText.Contains("first path of that name", StringComparison.Ordinal),
                $"a path argument that names a path of the base world is said with nothing to go to, as the game finds that path first: \"{page.NamesTitle}\" {string.Join(" | ", page.NameLabels.Select(label => label.Text))}");
            await CaretAt(1, 3);
            check.That(page.Scripts.Token == new SourceToken("FollowWaypoint", false, 0, 14) && page.NamesTitle == "" && page.NameButtons.Count == 0, "a word is not a name to follow");
            await CaretAt(0, 4);
            check.That(page.Scripts.Token is null && page.NamesTitle == "", "nor is a comment");
            await CaretAt(1, 18);
            page.Scripts.Select("beta");
            await Frame(tree);
            check.That(page.NamesTitle == "" && page.NameButtons.Count == 0, "choosing another script clears what was under the caret");

            // From an object to the paths it is a point of.
            page.ShowObject(2);
            check.That(page.ObjectPathButtons.Select(button => button.Text).SequenceEqual(["Path Path A · point 2 of 2", "Path Lone · point 1 of 1"]), $"an object that a path passes through offers each path, numbered among the points the game keeps: \"{string.Join(" | ", page.ObjectPathButtons.Select(button => button.Text))}\"");
            page.ObjectPathButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.Map.HighlightedPath == 0 && page.SelectedRow == 2 && page.Map.Selected == 2, "and its button shows the path on the map with the object still selected");
            page.SelectIndex(3);
            check.That(page.ObjectPathButtons.Select(button => button.Text).SequenceEqual(["Path Path A · point 1 of 2"]), "the other waypoint is the path's first point, though its slot is the second");
            page.SelectIndex(1);
            check.That(page.ObjectPathButtons.Count == 0, "a unit that a path names is on no path: the game drops that slot");
            page.SelectIndex(4);
            check.That(page.ObjectPathButtons.Count == 0, "an object on no path offers none");
            page.OpenLevel(130);
            check.That(page.Map.HighlightedPath is null && page.HidePath.Disabled, "opening a level again drops the highlight");

            // The engine keeps the view's first visible line and refreshes it only while the view is shown: a long source scrolled to its end, the Scripts switch turned off,
            // another level opened and the switch turned on again must show the new level's first script from its top, with no engine error (the run fails on one).
            check.That(page.ShowScript("delta") && page.Scripts.Source.GetLineCount() == 301, "a long source is on view");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.Scripts.Source.ScrollVertical = page.Scripts.Source.GetLineCount() - 5;
            page.Scripts.Source.SetCaretLine(page.Scripts.Source.GetLineCount() - 1);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.ScriptsToggle.ButtonPressed = false;
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.OpenLevel(140), "another level opens while the Scripts switch is off");
            for (int frame = 0; frame < 4; frame++) await Frame(tree);
            page.ScriptsToggle.ButtonPressed = true;
            for (int frame = 0; frame < 4; frame++) await Frame(tree);
            check.That(page.Scripts.Current?.Summary.Name == "shorty" && page.Scripts.Source.GetFirstVisibleLine() == 0 && page.Scripts.Source.GetCaretLine() == 0 && page.Scripts.Source.ScrollVertical == 0,
                $"the first script of the new level opens at its top: {page.Scripts.Current?.Summary.Name}, first visible line {page.Scripts.Source.GetFirstVisibleLine()}, caret line {page.Scripts.Source.GetCaretLine()}, scroll {page.Scripts.Source.ScrollVertical}");
            page.ScriptsToggle.ButtonPressed = false;
            check.That(page.OpenLevel(130), "the first level opens again");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);

            // Editing a script's source: the text typed is compiled and used as the script (one edit that Undo takes back); a source that does not compile changes
            // nothing; what is typed stays with its script while another is chosen; a script with no source file, or the base world's, cannot be edited.
            const string Alpha = "// alpha, the level's own\ninit()\n{\n\tPause(1);\n}\n";
            page.ShowScript("alpha");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(!page.EditSource.Disabled && !page.EditSource.ButtonPressed && page.CompileScriptButton.Disabled && page.ShippedScriptButton.Disabled && !page.Scripts.Source.Editable &&
                       page.Scripts.Info == "level130/alpha.msl · 5 lines · read only", $"a script with a source file can be edited, and starts read only: \"{page.Scripts.Info}\"");
            page.EditSource.ButtonPressed = true;
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Editable && !page.CompileScriptButton.Disabled && page.Scripts.Info == "level130/alpha.msl · 5 lines · editing", $"the Edit switch makes the view typeable: \"{page.Scripts.Info}\"");
            const string Typed = "// alpha, edited\ninit()\n{\n\tPause(2);\n}\n";
            page.Scripts.Source.Text = Typed;
            page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.StartsWith("Replaced alpha.", StringComparison.Ordinal) && page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && !page.Undo.Disabled && !page.Save.Disabled &&
                       !page.ShippedScriptButton.Disabled && page.HasChanges, $"a source that compiles replaces the script, and the page says so: \"{page.ScriptEditNote}\" / \"{page.Summary}\"");
            check.That(page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · in use" && page.Scripts.UnusedDraftCount == 0 && page.ChangeCount == 1 && page.DraftNote.Length == 0,
                $"the line above the source says the level uses the text that was compiled, and that text is no unsaved draft: \"{page.Scripts.Info}\", {page.ChangeCount} change");
            check.That(page.Model!.Session!.Body.Scripts[0].Code.Symbols.Any(symbol => symbol.Name == "const data40" && symbol.Value is ScriptInt { Value: 2 }),
                "the compile session's counter starts where the shipped script's does, so the first new constant is the shipped script's first (const data40)");
            check.That(page.Scripts.Current?.Summary.Name == "alpha" && page.Scripts.Source.Text == Typed && page.SourceInUse("alpha") == Typed &&
                       page.ScriptCardText.Contains("Handles: init", StringComparison.Ordinal) && !page.ScriptCardText.Contains("died", StringComparison.Ordinal),
                $"the script stays selected with the text typed, and its card shows what the new script handles: \"{page.ScriptCardText}\"");
            page.Scripts.Source.Text = "init()\n{\n\tFrobnicate(1);\n}\n";
            check.That(page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · not in use" && page.Scripts.UnusedDraftCount == 1 && page.ChangeCount == 2 &&
                       page.DraftNote == "Text typed for alpha is not in use yet and is not saved anywhere.",
                $"typing again makes the text one the level does not use, and the line and the changes card say so as it is typed: \"{page.Scripts.Info}\", {page.ChangeCount} changes, \"{page.DraftNote}\"");
            page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.StartsWith("line 3: ", StringComparison.Ordinal) && page.ScriptEditNote.Contains("Frobnicate", StringComparison.Ordinal) && page.Scripts.Source.GetCaretLine() == 2 &&
                       page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && page.SourceInUse("alpha") == Typed,
                $"a source that does not compile says why and where, puts the caret there and changes nothing: \"{page.ScriptEditNote}\"");
            page.Scripts.Source.Text = "init()\n{\n\tDamage(5.0);\n}\n";
            check.That(page.ScriptEditNote.Length == 0, $"a refusal is about the text as it was, so it goes as soon as the text changes: \"{page.ScriptEditNote}\"");
            page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.Contains("calls Damage more often", StringComparison.Ordinal) && page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) &&
                       page.ScriptEditNote.StartsWith("Replaced alpha.\nUndo takes it back.\nThis script calls Damage more often", StringComparison.Ordinal),
                $"an edit that adds a call to Damage is replaced and warned about, the warning under the message: \"{page.ScriptEditNote}\"");
            page.Scripts.Source.Text = "init()\n{\n\tFrobnicate(2);\n}\n";
            page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.StartsWith("line 3: ", StringComparison.Ordinal) && page.ScriptEditNote.Contains("calls Damage more often", StringComparison.Ordinal),
                $"a refusal changes nothing, so the level still has the script that calls Damage and the warning about it stays beside the refusal: \"{page.ScriptEditNote}\"");
            page.Scripts.Source.Text = "init()\n{\n\tDamage(5.0);\n}\n";  // back to the text the level runs
            check.That(!page.ScriptEditNote.Contains("line 3", StringComparison.Ordinal) && page.ScriptEditNote.StartsWith("This script calls Damage more often", StringComparison.Ordinal) &&
                       page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · in use" && page.Scripts.UnusedDraftCount == 0,
                $"the refusal goes with the text it was about, the warning stays, and the text the level runs is in use again: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\"");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && page.ScriptEditNote.Length == 0 && page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · not in use" && page.ChangeCount == 2,
                $"Undo takes the script that calls Damage back: the level runs the first replacement, which the text on view did not make, and the note and the warning about the script taken back are gone: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\" / {page.ChangeCount}");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("No changes yet", StringComparison.Ordinal) && !page.ShippedScriptButton.Disabled && page.ScriptCardText.Contains("Handles: init, died", StringComparison.Ordinal) &&
                       page.Scripts.Source.Text == "init()\n{\n\tDamage(5.0);\n}\n", "Undo takes the replacements back one by one, and the text typed stays where it is (and can be dropped, being unused)");
            check.That(page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · not in use" && page.Scripts.UnusedDraftCount == 1 && page.HasChanges && page.ChangeCount == 1 &&
                       page.DraftNote == "Text typed for alpha is not in use yet and is not saved anywhere.",
                $"the text whose replacement was undone is not in use, so it is unsaved typing again, and the changes card says whose: \"{page.Scripts.Info}\", {page.ChangeCount} change, \"{page.DraftNote}\"");
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && !page.ShippedScriptButton.Disabled && page.ScriptEditNote.Length == 0 &&
                       page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · not in use" && page.ChangeCount == 2,
                $"Redo brings back the first replacement, which the text on view (the later one) did not make, so that text is still not in use: \"{page.Scripts.Info}\" / {page.ChangeCount}");
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && !page.ShippedScriptButton.Disabled &&
                       page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · in use" && page.ChangeCount == 1 && page.DraftNote.Length == 0 &&
                       page.ScriptEditNote.StartsWith("This script calls Damage more often", StringComparison.Ordinal),
                $"the second Redo brings back the script the text made, with its warning and the text's being in use: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\"");
            // Typing by hand raises text_changed at the end of the frame (the steps above set the text, which raises text_set): the line and the card follow that too.
            const string Damaging = "init()\n{\n\tDamage(5.0);\n}\n";
            page.Scripts.Source.SetCaretLine(page.Scripts.Source.GetLineCount() - 1);  // after the last statement: a comment there leaves the compiled script as it was (one above would move its lines)
            page.Scripts.Source.SetCaretColumn(0);
            page.Scripts.Source.InsertTextAtCaret("// by hand\n");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · not in use" && page.Scripts.UnusedDraftCount == 1 && page.ChangeCount == 2 &&
                       page.DraftNote.StartsWith("Text typed for alpha is not in use", StringComparison.Ordinal), $"text typed by hand is noticed as it is typed: \"{page.Scripts.Info}\", {page.ChangeCount} changes");
            // That text compiles to the script the level already has (a trailing comment adds nothing), so it is in use as well, and compiling it changes nothing.
            page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.StartsWith("alpha is already what this source compiles to.\nThis script calls Damage more often", StringComparison.Ordinal) &&
                       page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · in use" && page.Scripts.UnusedDraftCount == 0 && page.ChangeCount == 1,
                $"a text that compiles to the script the level already has is in use too: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\" / {page.ChangeCount}");
            // The note is about the script the level had: Undo and Redo change the level's scripts, so it goes; the warning is read from the level and comes back with the script.
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("1 script replaced: alpha (", StringComparison.Ordinal) && page.ScriptEditNote.Length == 0 && page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · not in use",
                $"Undo takes the note about the compile with it: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\"");
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.ScriptEditNote.StartsWith("This script calls Damage more often", StringComparison.Ordinal) && !page.ScriptEditNote.Contains("already", StringComparison.Ordinal) &&
                       page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · in use", $"and Redo brings back the warning and the text's being in use, not the note: \"{page.ScriptEditNote}\" / \"{page.Scripts.Info}\"");
            // A text typed back to the source file's, while the level runs a replacement, is no draft, but it is not what the level runs either.
            page.Scripts.Source.Text = Alpha;
            check.That(page.Scripts.Info == "level130/alpha.msl · 5 lines · editing · not in use" && page.Scripts.UnusedDraftCount == 0 && page.ChangeCount == 1 && page.DraftNote.Length == 0,
                $"the file's text is not what a replaced script runs, and is no draft: \"{page.Scripts.Info}\" / {page.ChangeCount}");
            page.Scripts.Source.Text = Damaging;
            check.That(page.Scripts.Info == "level130/alpha.msl · 4 lines · editing · in use" && page.Scripts.UnusedDraftCount == 0, "and the text the level runs is in use again");
            page.ShippedScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Summary.StartsWith("No changes yet", StringComparison.Ordinal) && page.ScriptEditNote.StartsWith("alpha is back as the level has it.", StringComparison.Ordinal) && page.Scripts.Source.Text == Alpha &&
                       page.ShippedScriptButton.Disabled && page.SourceInUse("alpha") is null, $"putting the shipped script back shows the source file's text again: \"{page.ScriptEditNote}\"");
            page.Scripts.Source.Text = "// a draft\n";
            page.ShowScript("gamma");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == Gamma.Replace("\r\n", "\n") && page.Scripts.Source.Editable, "another script shows its own text, still typeable");
            page.ShowScript("alpha");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == "// a draft\n" && page.Scripts.Info.EndsWith("· editing · not in use", StringComparison.Ordinal) && page.Model!.Session!.ScriptChanges().Count == 0 &&
                       page.Scripts.UnusedDraftCount == 1 && page.HasChanges && page.ChangeCount == 1 && page.DraftNote.StartsWith("Text typed for alpha is not in use", StringComparison.Ordinal),
                "what was typed for a script is there when it is chosen again; it is not a change to the level's scripts, but leaving would lose it, so the guards count it and the changes card says so");
            check.That(LevelEditorPage.DraftNoteText([]).Length == 0 && LevelEditorPage.DraftNoteText(["a"]) == "Text typed for a is not in use yet and is not saved anywhere." &&
                       LevelEditorPage.DraftNoteText(["a", "b"]).StartsWith("Text typed for a and b is not in use", StringComparison.Ordinal) &&
                       LevelEditorPage.DraftNoteText(["a", "b", "c"]).StartsWith("Text typed for a, b and 1 more is not in use", StringComparison.Ordinal) &&
                       LevelEditorPage.DraftNoteText(["a", "b", "c", "d", "e"]).StartsWith("Text typed for a, b and 3 more is not in use", StringComparison.Ordinal), "the note names one or two scripts and counts the rest");
            check.That(!app.RequestClose() && app.DiscardDialog.Visible && app.DiscardDialog.DialogText.StartsWith("Not saved yet: 1 change on Level editor.", StringComparison.Ordinal),
                $"closing the companion with a draft asks first: \"{app.DiscardDialog.DialogText}\"");
            app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
            app.DiscardDialog.Hide();
            page.Scripts.Source.Text = Alpha;  // the same as the source file again: no draft
            check.That(page.Scripts.UnusedDraftCount == 0 && !page.HasChanges && page.ChangeCount == 0 && page.ShippedScriptButton.Disabled, "text typed back to the source file's is no draft, and there is nothing to put back");
            page.Scripts.Source.Text = "// a draft\n";
            check.That(page.Scripts.HasDraft("alpha") && !page.ShippedScriptButton.Disabled, "a draft is there to be dropped, and the button that drops it is enabled as soon as the text differs from the file's");
            page.ShippedScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == Alpha && page.ChangeCount == 0 && !page.HasChanges && page.ScriptEditNote == "The text you typed was dropped; alpha is as the level has it." && page.ShippedScriptButton.Disabled &&
                       page.SourceInUse("alpha") is null, $"Put the shipped script back drops a draft when the level already uses the shipped script: \"{page.ScriptEditNote}\"");
            // The same with the Edit switch off: the typed text stays on view, read only, and can still be dropped.
            page.Scripts.Source.Text = "// off draft\n";
            page.EditSource.ButtonPressed = false;
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(!page.Scripts.Source.Editable && page.Scripts.Source.Text == "// off draft\n" && page.Scripts.UnusedDraftCount == 1 && page.HasChanges &&
                       page.Scripts.Info == "level130/alpha.msl · 1 line · read only · not in use" && !page.ShippedScriptButton.Disabled, $"a draft stays when the switch is turned off: \"{page.Scripts.Info}\"");
            page.ShippedScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == Alpha && page.Scripts.UnusedDraftCount == 0 && !page.HasChanges && page.ShippedScriptButton.Disabled, "and Put the shipped script back drops it with the switch off");
            page.EditSource.ButtonPressed = true;
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            // Another level's opening drops what was typed for this one: it is not carried to a level that has a script of the same name.
            page.Scripts.Source.Text = "// carried?\n";
            check.That(page.OpenLevel(140), "another level opens while a draft is typed");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.UnusedDraftCount == 0 && page.ChangeCount == 0 && page.DraftNote.Length == 0, $"the draft is gone with the level it was typed in: {page.ChangeCount} changes");
            check.That(page.OpenLevel(130), "the first level opens again");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            page.ShowScript("alpha");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.Scripts.Source.Text == Alpha && page.Scripts.UnusedDraftCount == 0 && page.ChangeCount == 0 && page.EditSource.ButtonPressed && page.Scripts.Source.Editable,
                "and the script shows its source file's text when the level is back");
            page.Scripts.Source.Text = "// a draft\n";
            page.ShowScript("beta");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.EditSource.Disabled && !page.EditSource.ButtonPressed && page.CompileScriptButton.Disabled && !page.Scripts.Source.Editable && page.EditSource.TooltipText.Contains("no source file", StringComparison.Ordinal),
                $"a script with no source file cannot be edited, and says why: \"{page.EditSource.TooltipText}\"");
            page.ShowScript("alpha", fromBase: true);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.EditSource.Disabled && !page.Scripts.Source.Editable && page.EditSource.TooltipText.Contains("base world", StringComparison.Ordinal), "nor can a script of the base world");
            page.ShowScript("alpha");
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(page.EditSource.ButtonPressed && page.Scripts.Source.Editable, "the switch is on again for the next script that can be edited");
            page.Scripts.Source.Text = Alpha;
            page.EditSource.ButtonPressed = false;
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            check.That(!page.Scripts.Source.Editable && page.CompileScriptButton.Disabled && !page.HasChanges, "switching Edit off makes the view read only again, with no change made");

            // The panel keeps what is typed by itself, whoever listens to its text events (the page's handler stores a draft on every event, which hides these paths): a panel on its own.
            ScriptsPanel alone = new();
            tree.Root.AddChild(alone);
            alone.SetScripts(install.Game, page.Model!.Scripts);
            check.That(alone.Select("alpha") && alone.Select("gamma") && alone.Select("alpha"), "a panel on its own selects scripts");
            alone.SetEditing(true);
            alone.Source.Text = "// kept\n";
            check.That(alone.Select("gamma") && alone.Select("alpha") && alone.Source.Text == "// kept\n", "what is typed is kept when another script is chosen and this one again");
            alone.Source.Text = "// kept off\n";
            alone.SetEditing(false);
            check.That(alone.Select("gamma") && alone.Select("alpha") && alone.Source.Text == "// kept off\n" && !alone.Source.Editable, "and when the switch is turned off after typing");
            alone.SetEditing(true);
            alone.Source.Text = "// kept through a refresh\n";
            alone.Refresh(page.Model.Scripts);
            check.That(alone.Source.Text == "// kept through a refresh\n" && alone.UnusedDraftCount == 1 && alone.UnusedDraftNames.SequenceEqual(["alpha"]), "and through a refresh of the scripts");
            alone.QueueFree();
            await Frame(tree);

            // Nothing was written, and the move editor still works on the objects.
            page.ScriptsToggle.ButtonPressed = false;
            await Frame(tree);
            check.That(page.Table.IsVisibleInTree() && page.MapToggle.IsVisibleInTree() && !page.Scripts.Visible && !page.ScriptCardTitle.Any() && !page.HasChanges, "switching back shows the table and the map, with no change made");
            check.That(gameBefore.SequenceEqual(Snapshot(install.Game)), "reading scripts and sources wrote nothing in the game folder");

            // A level without a scripts folder, and a level with no scripts at all.
            Directory.Delete(Path.Combine(install.Game, "data", "MissionScripts"), true);
            check.That(page.OpenLevel(130), "the level opens again");
            page.ScriptsToggle.ButtonPressed = true;
            await Frame(tree);
            check.That(page.Scripts.Info == "This game has no data/MissionScripts folder." && page.Scripts.Source.Text == "", $"a game with no scripts folder says so: \"{page.Scripts.Info}\"");
            page.ScriptsToggle.ButtonPressed = false;
        }
        finally
        {
            File.Delete(archive);
            string scriptsFolder = Path.Combine(install.Game, "data", "MissionScripts");
            if (Directory.Exists(scriptsFolder)) Directory.Delete(scriptsFolder, true);
            if (page.ScriptsToggle.ButtonPressed) page.ScriptsToggle.ButtonPressed = false;
            app.Navigate("home");
            app.Navigate("levels");
            await Frame(tree);
            page.OpenLevel(100);
        }
    }
}
