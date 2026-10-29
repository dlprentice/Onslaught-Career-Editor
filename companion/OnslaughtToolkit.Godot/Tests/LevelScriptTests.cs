// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The data behind the Level editor's read-only view of a level's mission scripts: what the catalog reads from compiled scripts (events,
/// calls, the objects that name them), the native and event tables, and where a source is looked for and what is refused. Nothing here
/// touches Godot. Authored data only: the scripts and sources are made here, none from the game.
/// </summary>
internal static class LevelScriptTests
{
    private static int Native(string name) => Array.FindIndex(ScriptTables.Natives, native => native.Name == name);

    /// <summary>A compiled script: the fixed events it has an entry point for, the named handlers it has, and the calls its code makes (a name and how many times).</summary>
    internal static MissionScript Script(string name, int[] events, string[] handlers, params (string Native, int Times)[] calls)
    {
        MissionScript script = new() { Name = name };
        Array.Fill(script.Code.EventPcs, -1);
        foreach (int index in events) script.Code.EventPcs[index] = 0;
        foreach ((string native, int times) in calls)
            for (int call = 0; call < times; call++)
                script.Code.Instructions.Add(new ScriptInstruction(24, Native(native) | (1 << 8) | (1 << 16)));
        script.Code.Instructions.Add(new ScriptInstruction(23, -1));
        foreach (string handler in handlers)
        {
            int symbol = script.Code.Symbols.Count;
            script.Code.Symbols.Add(new ScriptSymbol { Name = $"const data{symbol}", DataType = 3, Value = new ScriptText(handler), Index = symbol, Flag = 1 });
            EventFunction function = new() { EntryPc = 0 };
            function.Parameters.Add(symbol);
            script.Code.EventFunctions.Add(function);
        }
        script.Code.NextSymbolIndex = script.Code.Symbols.Count;
        return script;
    }

    // ---- the data layer ---------------------------------------------------------------------------------------------------------
    internal static void Run(string output, Checks check)
    {
        check.Suite("level scripts");
        Tables(check);
        Catalog(check);
        Sources(output, check);
        Model(output, check);
    }

    private static void Tables(Checks check)
    {
        check.That(ScriptTables.EventNames.Length == ScriptCode.EventCount && ScriptTables.EventNames[0] == "init" && ScriptTables.EventNames[3] == "died" && ScriptTables.EventNames[4] == "hit",
            "the tables name the 13 events in the order a script's entry points are indexed");
        check.That(ScriptTables.Natives.Length is > 0 and <= 256 && ScriptTables.Natives.Select(native => native.Name).Distinct().Count() == ScriptTables.Natives.Length &&
                   ScriptTables.Natives.All(native => native.Name.Length > 0 && native.Parameters.All(letter => "ifsbtp*".Contains(letter))),
            "every native has a name, one of 256 call numbers, and only the letters of the known argument types");
        check.That(Native("Pause") >= 0 && Native("PostEvent") >= 0, "the natives a script's calls use are in the table");
    }

    internal static WorldBody Body(params MissionScript[] scripts)
    {
        WorldBody body = WorldBody.Read(LevelTests.Body("authored-v50"));
        body.Scripts.Clear();
        body.Scripts.AddRange(scripts);
        return body;
    }

    private static void Catalog(Checks check)
    {
        WorldBody body = Body(Script("alpha", [0, 3], ["go"], ("PostEvent", 1), ("Pause", 2)), Script("beta", [], []), Script("odd", [4, 12], []));
        MissionScript odd = body.Scripts[2];
        odd.Code.Instructions.Insert(0, new ScriptInstruction(24, 250 | (1 << 16)));  // a call number past the table
        odd.Code.Instructions.Insert(0, new ScriptInstruction(24, ScriptTables.Natives.Length));  // the first number past it
        odd.Code.Instructions.Insert(0, new ScriptInstruction(25, 5));  // not a call
        odd.Code.Symbols.Add(new ScriptSymbol { Name = "number", DataType = 1, Value = new ScriptInt(5), Index = 0, Flag = 1 });
        odd.Code.EventFunctions.Add(new EventFunction { EntryPc = 0 });  // a named handler with no event name
        odd.Code.EventFunctions.Add(new EventFunction { EntryPc = 0, Parameters = { 99 } });  // one whose name symbol is not there
        odd.Code.EventFunctions.Add(new EventFunction { EntryPc = 0, Parameters = { 0 } });  // one whose name symbol holds a number
        odd.Code.EventFunctions.Add(new EventFunction { EntryPc = 0, Parameters = { 1 } });  // one whose symbol number is the symbol count
        odd.Code.EventFunctions.Add(new EventFunction { EntryPc = 0, Parameters = { -1 } });  // and one below zero
        PlacedObject spawner = new() { ObjectId = 19, Init = new ObjectInit { Spawner = new SpawnerInit { SpawnerSpawnScript = "alpha" } } };
        body.Things[0].Init.Script = "alpha";
        body.Things[1].Init.SpawnScript = "alpha";
        body.Things[2].Init.Script = "Alpha";  // another case: the game would not find it
        body.Things[3].Init.Script = "ghost";
        body.Things.Add(spawner);
        IReadOnlyList<ScriptSummary> scripts = ScriptCatalog.Of(body);
        check.That(scripts.Select(script => script.Name).SequenceEqual(["alpha", "beta", "odd"]), "the catalog lists the body's scripts in the body's order");
        ScriptSummary alpha = scripts[0];
        check.That(alpha.Events.SequenceEqual(["init", "died", "event \"go\""]), $"a script handles each fixed event it has an entry point for, then each named handler: {string.Join(", ", alpha.Events)}");
        check.That(alpha.Calls.SequenceEqual([new NativeCall("PostEvent", 1), new NativeCall("Pause", 2)]) && alpha.Instructions == 4,
            $"and calls the natives its CALL instructions name, counted, in the order they are first called: {string.Join(", ", alpha.Calls)}");
        check.That(alpha.Uses.SequenceEqual([new ScriptUse(0, ScriptCatalog.RoleScript), new ScriptUse(1, ScriptCatalog.RoleSpawnScript), new ScriptUse(body.Things.Count - 1, ScriptCatalog.RoleSpawnerScript)]),
            $"the objects that name it, by row and field (exact name): {string.Join(", ", alpha.Uses)}");
        check.That(alpha.Uses.Select(use => use.Role).SequenceEqual(["script", "spawn script", "spawner's spawn script"]), "the fields that name a script are called by these words");
        check.That(scripts[1].Events.Count == 0 && scripts[1].Calls.Count == 0 && scripts[1].Uses.Count == 0, "a script with no entry points, calls or users says so with empty lists");
        check.That(scripts[2].Events.SequenceEqual(["hit", "notdefined8", "event #1", "event #2", "event #3", "event #4", "event #5"]),
            $"a named handler whose name is not a text symbol is shown by its number: {string.Join(", ", scripts[2].Events)}");
        check.That(scripts[2].Calls.SequenceEqual([new NativeCall($"function {ScriptTables.Natives.Length}", 1), new NativeCall("function 250", 1)]),
            $"a call number past the table is shown as a number, not dropped, and an instruction that is not a call is not counted: {string.Join(", ", scripts[2].Calls)}");
        IReadOnlyList<ScriptReference> refs = ScriptCatalog.ReferencesOf(body, 2);
        check.That(refs.SequenceEqual([new ScriptReference(ScriptCatalog.RoleScript, "Alpha", false)]), "an object that names a script by another case is told it has no such script");
        check.That(ScriptCatalog.ReferencesOf(body, 3).SequenceEqual([new ScriptReference(ScriptCatalog.RoleScript, "ghost", false)]) &&
                   ScriptCatalog.ReferencesOf(body, 0).SequenceEqual([new ScriptReference(ScriptCatalog.RoleScript, "alpha", true)]) &&
                   ScriptCatalog.ReferencesOf(body, 4).Count == 0 && ScriptCatalog.ReferencesOf(body, -1).Count == 0 && ScriptCatalog.ReferencesOf(body, 99).Count == 0 &&
                   ScriptCatalog.ReferencesOf(body, body.Things.Count).Count == 0,
            "references say whether the world has the script; an object that names none, and a row out of range, have no references");
        check.That(ScriptCatalog.ReferencesOf(body, body.Things.Count - 1).SequenceEqual([new ScriptReference(ScriptCatalog.RoleSpawnerScript, "alpha", true)]), "a spawner's spawn script is a reference too");
    }

    private static void Sources(string output, Checks check)
    {
        string game = Path.Combine(output, "script-sources-game");
        if (Directory.Exists(game)) Directory.Delete(game, true);
        string scripts = Path.Combine(game, "data", "MissionScripts");
        string folder = Path.Combine(scripts, "Level123");
        Directory.CreateDirectory(folder);
        File.WriteAllBytes(Path.Combine(folder, "Foo.MSL"), Encoding.Latin1.GetBytes("// one\r\ninit()\r\n{\r\n}\r\n"));
        File.WriteAllBytes(Path.Combine(folder, "NoEnd.msl"), Encoding.Latin1.GetBytes("a\nb"));
        File.WriteAllBytes(Path.Combine(folder, "Cr.msl"), Encoding.Latin1.GetBytes("x\ry\r\nz"));
        File.WriteAllBytes(Path.Combine(folder, "Empty.msl"), []);
        Directory.CreateDirectory(Path.Combine(scripts, "level007"));
        File.WriteAllBytes(Path.Combine(scripts, "level007", "Seven.msl"), Encoding.Latin1.GetBytes("seven"));
        string upper = Path.Combine(output, "script-sources-upper");
        if (Directory.Exists(upper)) Directory.Delete(upper, true);
        Directory.CreateDirectory(Path.Combine(upper, "DATA", "MISSIONSCRIPTS", "LEVEL009"));
        File.WriteAllBytes(Path.Combine(upper, "DATA", "MISSIONSCRIPTS", "LEVEL009", "SHOUT.MSL"), Encoding.Latin1.GetBytes("loud"));
        File.WriteAllBytes(Path.Combine(folder, "Accent.msl"), [0x63, 0xE9]);
        File.WriteAllBytes(Path.Combine(folder, "Dup.msl"), Encoding.Latin1.GetBytes("lower"));
        File.WriteAllBytes(Path.Combine(folder, "DUP.MSL"), Encoding.Latin1.GetBytes("upper"));
        File.WriteAllBytes(Path.Combine(folder, "Big.msl"), new byte[ScriptSources.MaxBytes + 1]);
        File.WriteAllBytes(Path.Combine(folder, "Max.msl"), new byte[ScriptSources.MaxBytes]);
        File.CreateSymbolicLink(Path.Combine(folder, "Link.msl"), Path.Combine(folder, "Foo.MSL"));
        Directory.CreateSymbolicLink(Path.Combine(scripts, "level200"), folder);
        File.WriteAllText(Path.Combine(output, "script-sources-outside.msl"), "outside");

        ScriptSourceResult found = ScriptSources.Find(game, 123, "Foo");
        check.That(found.Source is { Text: "// one\ninit()\n{\n}\n", Lines: 4 } source && source.Path == Path.Combine(folder, "Foo.MSL") && found.Problem is null,
            $"a source is found in any case, with \\n line ends and its lines counted: {found.Source?.Text.Replace("\n", "|")} / {found.Problem}");
        check.That(ScriptSources.Find(game, 123, "NoEnd").Source is { Text: "a\nb", Lines: 2 }, "a last line with no line end counts");
        check.That(ScriptSources.Find(game, 123, "Cr").Source is { Text: "x\ny\nz", Lines: 3 }, "a lone carriage return ends a line too");
        check.That(ScriptSources.Find(game, 123, "Empty").Source is { Text: "", Lines: 0 }, "an empty file has no lines");
        check.That(ScriptSources.Find(game, 7, "Seven").Source?.Text == "seven", "a level number is padded to three digits");
        check.That(ScriptSources.Find(upper, 9, "Shout").Source?.Text == "loud", "the data, scripts and level folders and the file are found in any case");
        check.That(ScriptSources.Find(game, 123, "Accent").Source?.Text == "cé", "the file's single-byte text is read as Latin-1");
        check.That(ScriptSources.Find(game, 123, "Dup").Source?.Text == "lower" && ScriptSources.Find(game, 123, "DUP").Source?.Text == "upper",
            "when two files differ only by case, the exact spelling is the one found");
        check.That(ScriptSources.Find(game, 123, "Max").Source is not null && ScriptSources.Find(game, 123, "Big") is { Source: null, Problem: { } big } && big.Contains("larger than", StringComparison.Ordinal),
            "a source of the size limit is shown and one byte more is refused with a reason");
        ScriptSourceResult none = ScriptSources.Find(game, 123, "Bar");
        check.That(none.Source is null && none.Problem == "No file named Bar.msl in Level123.", $"a missing file is named: {none.Problem}");
        check.That(ScriptSources.Find(game, 124, "Foo").Problem == "This game has no MissionScripts folder for level 124.", "a level with no folder says so");
        check.That(ScriptSources.Find(Path.Combine(output, "script-sources-empty"), 123, "Foo").Problem == "This game has no data/MissionScripts folder.", "a game with no scripts folder says so");
        check.That(ScriptSources.Find(game, 123, "Link") is { Source: null, Problem: "No file named Link.msl in Level123." } && ScriptSources.Find(game, 200, "Foo").Source is null,
            "a link to a file or a folder is ignored, as the level archive reader ignores links: to the finder it is not there");
        check.That(new[] { "..\\script-sources-outside", "../script-sources-outside", "../../script-sources-outside", "Foo.MSL/..", "" }.All(name => ScriptSources.Find(game, 123, name).Source is null),
            "a script named like a path finds nothing: the name is matched against the folder's entries, never joined into a path");
        Directory.Delete(game, true);
        Directory.Delete(upper, true);
        File.Delete(Path.Combine(output, "script-sources-outside.msl"));
        SourcesRefused(output, check);
    }

    /// <summary>What is not a source and what cannot be listed: each is a reason in the result, and nothing hangs or throws.</summary>
    private static void SourcesRefused(string output, Checks check)
    {
        string game = Path.Combine(output, "script-sources-refused");
        if (Directory.Exists(game)) Directory.Delete(game, true);
        string scripts = Path.Combine(game, "data", "MissionScripts");
        string folder = Path.Combine(scripts, "level123");
        Directory.CreateDirectory(folder);
        File.WriteAllText(Path.Combine(folder, "Foo.msl"), "// fine\n");
        const string UnlistedWords = "could not be looked up";
        UnixFileMode open = UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute;

        // A named pipe named like a script would wait for a writer for ever, so it is not opened: the lookup comes back at once with a reason.
        if (OperatingSystem.IsLinux())
        {
            string pipe = Path.Combine(folder, "Pipe.msl");
            using (Process make = Process.Start(new ProcessStartInfo("mkfifo", [pipe]) { UseShellExecute = false })!)
            {
                make.WaitForExit();
                check.That(make.ExitCode == 0, $"mkfifo made the named pipe (exit {make.ExitCode})");
            }
            Task<ScriptSourceResult> lookup = Task.Run(() => ScriptSources.Find(game, 123, "Pipe"));
            bool returned = lookup.Wait(TimeSpan.FromSeconds(10));
            check.That(returned && lookup.Result is { Source: null, Problem: "Pipe.msl is not a regular file, so it is not read." },
                $"a named pipe is refused with a reason and the lookup does not wait for a writer: {(returned ? lookup.Result.Problem : "it did not return in 10 seconds")}");
            if (!returned)
            {
                using (File.OpenHandle(pipe, FileMode.Open, FileAccess.Write))
                {
                    // let the reader that is stuck on the pipe go, so the run can end
                }
                lookup.Wait(TimeSpan.FromSeconds(10));
            }
            check.That(ScriptSources.Find(game, 123, "Foo").Source?.Text == "// fine\n", "a regular file beside the pipe is still read");
            check.That(ScriptSources.IsRegularFile(Path.Combine(folder, "Foo.msl")) && !ScriptSources.IsRegularFile(pipe) && !ScriptSources.IsRegularFile(folder),
                "a regular file is one; a named pipe and a folder are not");
            bool examined = true;
            try
            {
                ScriptSources.IsRegularFile(Path.Combine(folder, "Gone.msl"));
            }
            catch (IOException)
            {
                examined = false;
            }
            check.That(!examined, "an entry that cannot be examined is an IOException, which the lookup turns into a reason");
            File.Delete(pipe);
        }

        // A folder that cannot be listed is a reason, not an exception for the page's signal handler to meet (a root user can list anything).
        if (!OperatingSystem.IsWindows() && !Environment.IsPrivilegedProcess)
        {
            string locked = Path.Combine(scripts, "level125");
            Directory.CreateDirectory(locked);
            File.WriteAllText(Path.Combine(locked, "Foo.msl"), "x");
            File.SetUnixFileMode(locked, UnixFileMode.None);
            try
            {
                ScriptSourceResult denied = Throws(() => ScriptSources.Find(game, 125, "Foo"), out bool threw);
                check.That(!threw && denied.Source is null && denied.Problem is { } deniedReason && deniedReason.StartsWith("The script sources " + UnlistedWords, StringComparison.Ordinal),
                    $"a level folder with no permission to list it gives a reason: {(threw ? "it threw" : denied.Problem)}");
            }
            finally
            {
                File.SetUnixFileMode(locked, open);
            }

            File.SetUnixFileMode(scripts, UnixFileMode.None);
            try
            {
                ScriptSourceResult denied = Throws(() => ScriptSources.Find(game, 123, "Foo"), out bool threw);
                check.That(!threw && denied.Source is null && denied.Problem is { } deniedReason && deniedReason.StartsWith("The script sources " + UnlistedWords, StringComparison.Ordinal),
                    $"a MissionScripts folder with no permission to list it gives a reason: {(threw ? "it threw" : denied.Problem)}");
            }
            finally
            {
                File.SetUnixFileMode(scripts, open);
            }

            string data = Path.Combine(game, "data");
            File.SetUnixFileMode(data, UnixFileMode.None);
            try
            {
                ScriptSourceResult denied = Throws(() => ScriptSources.Find(game, 123, "Foo"), out bool threw);
                check.That(!threw && denied.Source is null && denied.Problem is { } deniedReason && deniedReason.StartsWith("The script sources " + UnlistedWords, StringComparison.Ordinal),
                    $"a data folder with no permission to list it gives a reason: {(threw ? "it threw" : denied.Problem)}");
            }
            finally
            {
                File.SetUnixFileMode(data, open);
            }

            File.SetUnixFileMode(Path.Combine(folder, "Foo.msl"), UnixFileMode.None);
            try
            {
                ScriptSourceResult denied = Throws(() => ScriptSources.Find(game, 123, "Foo"), out bool threw);
                check.That(!threw && denied.Source is null && denied.Problem is { } deniedReason && deniedReason.Contains("could not be read", StringComparison.Ordinal),
                    $"a file with no permission to read it gives a reason: {(threw ? "it threw" : denied.Problem)}");
            }
            finally
            {
                File.SetUnixFileMode(Path.Combine(folder, "Foo.msl"), UnixFileMode.UserRead | UnixFileMode.UserWrite);
            }
            check.That(ScriptSources.Find(game, 123, "Foo").Source?.Text == "// fine\n" && ScriptSources.Find(game, 125, "Foo").Source?.Text == "x", "with the permissions back, every source is read again");
        }
        Directory.Delete(game, true);
    }

    private static ScriptSourceResult Throws(Func<ScriptSourceResult> find, out bool threw)
    {
        try
        {
            threw = false;
            return find();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            threw = true;
            return new(null, error.Message);
        }
    }

    /// <summary>The model on the vectors' archive that holds a base world and a world of the level's own (levels 100 and 200).</summary>
    private static void Model(string output, Checks check)
    {
        string game = Path.Combine(output, "script-model-game");
        if (Directory.Exists(game)) Directory.Delete(game, true);
        string resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "200_res_PC.aya"), LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "base-and-real").File));
        File.WriteAllBytes(Path.Combine(resources, "300_res_PC.aya"), LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "real-only").File));
        LevelEditorModel model = LevelEditorModel.ForGame(game);
        check.That(model.Scripts.Count == 0, "no scripts are listed before a level is opened");
        check.That(model.Open(200), "the level with a base world opens");
        check.That(model.Scripts.Count == 2 && !model.Scripts[0].FromBaseWorld && model.Scripts[0].SourceLevel == 200 && model.Scripts[0].Summary.Name == "main" &&
                   model.Scripts[0].Summary.Uses.SequenceEqual([new ScriptUse(0, ScriptCatalog.RoleScript)]) &&
                   model.Scripts[1].FromBaseWorld && model.Scripts[1].SourceLevel == 100 && model.Scripts[1].Summary.Name == "main" && model.Scripts[1].Summary.Uses.Count == 0,
            $"the model lists the level's own script (named by row 0, its source in level 200's folder) and then its base world's (no users, its source in level 100's folder): {string.Join(" | ", model.Scripts.Select(entry => $"{(entry.FromBaseWorld ? "base" : "own")} {entry.Summary.Name} {entry.SourceLevel} {entry.Summary.Uses.Count}"))}");
        WorldBody ownBody = Body(Script("alpha", [], []));
        ownBody.Things[0].Init.Script = "alpha";
        WorldBody baseBody = Body(Script("basey", [], []));
        baseBody.Things[0].Init.Script = "basey";  // an object of the base world names a base script: not a row of this level's table
        byte[] baseBytes = baseBody.Write();
        IReadOnlyList<ScriptEntry> listed = LevelEditorModel.ListScripts(ownBody, new LevelWorlds(0, 9, baseBytes, null));
        check.That(listed.Count == 2 && listed[0].Summary.Uses.Count == 1 && listed[1].FromBaseWorld && listed[1].SourceLevel == 0 && listed[1].Summary.Name == "basey" && listed[1].Summary.Uses.Count == 0,
            "a base world of level 0 is listed, its scripts carry no users, and its source is looked for in level 0's folder");
        check.That(LevelEditorModel.ListScripts(ownBody, new LevelWorlds(-1, 9, baseBytes, null)).Count == 1 && LevelEditorModel.ListScripts(ownBody, new LevelWorlds(5, 9, null, null)).Count == 1 &&
                   LevelEditorModel.ListScripts(ownBody, new LevelWorlds(5, 9, [1, 2, 3], null)).Count == 1, "no base world, a base level of -1 and a base body that does not read list the level's own scripts only");
        check.That(model.Open(300) is false && model.Scripts.Count == 0, "a level that cannot be opened lists no scripts");
        check.That(model.Open(200) && model.Scripts.Count == 2 && model.Session!.Body.Scripts.Count == 1, "and opening one again lists its scripts afresh");
        Directory.Delete(game, true);
    }
}
