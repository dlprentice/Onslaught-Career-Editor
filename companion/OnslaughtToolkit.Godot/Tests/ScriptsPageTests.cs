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
    /// <summary>Gamma's source: a comment, then calls whose quoted texts name the authored level's path, an object, an event, nothing, and an object of the base world.</summary>
    private const string Gamma = "// gamma\r\nFollowWaypoint(\"Path A\", 0);\r\nGetThingRef(\"Tank 1\");\r\nPostEvent(\"go\");\r\nGetThingRef(\"ghost\");\r\nGetThingRef(\"Base Hut\");\r\n";

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
        real.Things[0].Init.Script = "alpha";
        real.Things[1].Init.SpawnScript = "alpha";
        real.Things[2].Init.Script = "ghost";
        real.Things[3].Init.Script = "beta";
        WorldBody baseWorld = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [1], [], ("Print", 1)), LevelScriptTests.Script("basey", [0], []));
        baseWorld.Things[1].Init.Name = "Base Hut";  // an object the level's table does not list
        File.WriteAllBytes(archive, LevelArchiveBytes(131, 130, baseWorld.Write(), real.Write()));
        Source(install.Game, 130, "alpha", "// alpha, the level's own\r\ninit()\r\n{\r\n\tPause(1);\r\n}\r\n");
        Source(install.Game, 130, "gamma", Gamma);
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
            check.That(page.Scripts.Token == new SourceToken("Path A", true, 16, 6) && page.NamesTitle == "“Path A” names:" && page.NameButtons.Select(button => button.Text).SequenceEqual(["path Path A · 3 points"]),
                $"the caret in a quoted text names what it names: \"{page.NamesTitle}\" {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
            page.NameButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Frame(tree);
            WorldBody world = model.Session!.Body;
            int[] pathRows = [.. world.WaypointPaths[0].Slots.Select(slot => (int)slot)];
            double expectedLow = pathRows.Min(row => (double)model.Row(row)!.Position.X), expectedHigh = pathRows.Max(row => (double)model.Row(row)!.Position.X);
            check.That(!page.ScriptsToggle.ButtonPressed && page.Map.HighlightedPath == 0 && page.Map.DrawablePaths == 1 && page.HidePath.Visible && page.HighlightedPathText == "Path Path A · 3 points, numbered along it" &&
                       Math.Abs(page.Map.View.CenterX - (expectedLow + expectedHigh) / 2) < 1e-4 && page.Map.View.Scale >= page.Map.View.FitScale,
                $"the path button shows the path on the map, numbered, and brings the map to it: highlighted {page.Map.HighlightedPath}, \"{page.HighlightedPathText}\", centre {page.Map.View.CenterX} (the points' x run {expectedLow} to {expectedHigh}), scale {page.Map.View.Scale}");
            check.That(page.PathLabel.MouseFilter == Control.MouseFilterEnum.Pass && page.PathLabel.TooltipText == page.HighlightedPathText, "the path line's tooltip, which has the whole text, can be reached with the pointer");
            page.HidePath.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.Map.HighlightedPath is null && !page.HidePath.Visible && page.HighlightedPathText == "", "Hide path stops highlighting it");
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
            check.That(page.ObjectPathButtons.Select(button => button.Text).SequenceEqual(["Path Path A · point 2 of 3"]), $"an object that a path passes through offers the path: \"{string.Join(" | ", page.ObjectPathButtons.Select(button => button.Text))}\"");
            page.ObjectPathButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.Map.HighlightedPath == 0 && page.SelectedRow == 2 && page.Map.Selected == 2, "and its button shows the path on the map with the object still selected");
            page.SelectIndex(4);
            check.That(page.ObjectPathButtons.Count == 0, "an object on no path offers none");
            page.OpenLevel(130);
            check.That(page.Map.HighlightedPath is null && !page.HidePath.Visible, "opening a level again drops the highlight");

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
