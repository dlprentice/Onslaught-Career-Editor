// SPDX-License-Identifier: GPL-3.0-only
using System.Runtime.InteropServices;
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
        Names(check);
        Paths(check);
    }

    private static void Names(Checks check)
    {
        string call = "\tPostEvent(\"go now\");";  // tab 0, PostEvent 1 to 9, ( 10, quote 11, go now 12 to 17, quote 18, ) 19, ; 20
        check.That(ScriptNames.TokenAt(call, 1) == new SourceToken("PostEvent", false, 1, 9) && ScriptNames.TokenAt(call, 10) == new SourceToken("PostEvent", false, 1, 9),
            "a caret in a word, or just after it, is on that word");
        check.That(ScriptNames.TokenAt(call, 11) == new SourceToken("go now", true, 12, 6) && ScriptNames.TokenAt(call, 15) == new SourceToken("go now", true, 12, 6) && ScriptNames.TokenAt(call, 19) == new SourceToken("go now", true, 12, 6),
            "a caret anywhere from before the opening quote to after the closing one is on the quoted text, which is shown without its quotes");
        check.That(ScriptNames.TokenAt(call, 20) is null && ScriptNames.TokenAt(call, 21) is null && ScriptNames.TokenAt(call, 0) is null, "and one on a symbol, a space or past the end is on nothing");
        check.That(ScriptNames.TokenAt(call, -1) is null && ScriptNames.TokenAt(call, call.Length + 1) is null && ScriptNames.TokenAt("", 0) is null, "a column outside the line, and an empty line, are on nothing");
        check.That(ScriptNames.TokenAt("Die(); // \"go\" says", 12) is null && ScriptNames.TokenAt("Die(); // \"go\" says", 2)?.Text == "Die" && ScriptNames.TokenAt("// only", 3) is null,
            "a comment says nothing, even a quoted text in it, and the code before it still does");
        check.That(ScriptNames.TokenAt("Print(\"open", 8) == new SourceToken("open", true, 7, 4), "a quote never closed runs to the end of the line");
        check.That(ScriptNames.TokenAt("x = foo_bar2 + 10;", 6)?.Text == "foo_bar2" && ScriptNames.TokenAt("x = foo_bar2 + 10;", 16) is null && ScriptNames.TokenAt("a // b \"c\"", 1)?.Text == "a",
            "a word may hold an underscore and digits, and a number is not a word");
        check.That(ScriptNames.TokenAt("x = a / b; foo", 12)?.Text == "foo" && ScriptNames.TokenAt("x = a / b; \"q\"", 12)?.Text == "q", "a single slash is not a comment");
        check.That(ScriptNames.TokenAt("\"a\" \"b\"", 5) == new SourceToken("b", true, 5, 1) && ScriptNames.TokenAt("\"a\" \"b\"", 2) == new SourceToken("a", true, 1, 1),
            "two quoted texts on a line are told apart");
        // The path argument of a follow-waypoint call: the first text inside the parentheses of FollowWaypoint or FollowWaypointWait, nothing else.
        const string follow = "\tFollowWaypoint( \"Path A\" , \"second\" );";  // tab 0, the name 1 to 14, ( 15, blank 16, quote 17, Path A 18 to 23, quote 24, , 26, quote 28, second 29 to 34
        check.That(ScriptNames.TokenAt(follow, 20) == new SourceToken("Path A", true, 18, 6, true) && ScriptNames.TokenAt(follow, 31) == new SourceToken("second", true, 29, 6) && ScriptNames.TokenAt(follow, 3)?.PathArgument == false,
            "the first quoted text of a follow-waypoint call is its path argument, blanks around the parenthesis allowed; the second text and the word are not");
        check.That(ScriptNames.TokenAt("FollowWaypointWait(\"p\", 0, 5);", 20) == new SourceToken("p", true, 20, 1, true) && ScriptNames.TokenAt("FollowWaypoint(\t\"p\");", 16) == new SourceToken("p", true, 17, 1, true) &&
                   ScriptNames.TokenAt("FollowWaypoint\t(\"p\");", 16) == new SourceToken("p", true, 17, 1, true),
            "the Wait form counts, and a tab is a blank");
        string[] notPaths = ["GetThingRef(\"p\");", "Print(\"p\");", "FollowWaypointX(\"p\");", "XFollowWaypoint(\"p\");", "Follow_Waypoint(\"p\");", "followwaypoint(\"p\");", "FollowWaypoint(\"a\" + \"p\");",
                             "FollowWaypoint(x, \"p\");", "x = \"p\";", "\"p\", 0);", "FollowWaypoint \"p\";", "FollowWaypoint(0, \"p\");", "(\"p\");",
                             "_FollowWaypoint(\"p\");", "1FollowWaypoint(\"p\");", "FollowWaypoint2(\"p\");", "Wait(\"p\");"];
        check.That(notPaths.All(line => ScriptNames.TokenAt(line, line.IndexOf("\"p\"", StringComparison.Ordinal) + 1) is { Quoted: true, Text: "p" } token && !token.PathArgument),
            "a text after another call, another function name, a word that only ends or begins like it, a comma, an operator or no parenthesis is not a path argument");
        check.That(ScriptNames.FollowsPathCall("FollowWaypoint(\"p\")", 15) && !ScriptNames.FollowsPathCall("FollowWaypoint(\"p\")", 14) && !ScriptNames.FollowsPathCall("", 0) && !ScriptNames.FollowsPathCall("(\"p\")", 1) &&
                   !ScriptNames.FollowsPathCall("(\"p\")", 0) && ScriptNames.FollowsPathCall("FollowWaypoint \v\r(\f\t\"p\")", 20),
            "and the test is by the quote's place: the opening quote after the parenthesis, a line that begins with the parenthesis or the quote is not one");

        WorldBody body = Body(Script("alpha", [0], [], ("Pause", 1)), Script("beta", [], ["go"]));
        body.Things[0].Init.Name = "Tank 1";
        body.Things[1].Init.Name = "tank 1";
        body.Things[2].Init.Name = "Tank 1";
        IReadOnlyList<ScriptEntry> own = [.. ScriptCatalog.Of(body).Select(summary => new ScriptEntry(summary, 100, FromBaseWorld: false))];
        IReadOnlyList<ScriptEntry> both = [.. own, new ScriptEntry(own[0].Summary with { Uses = [] }, 1, FromBaseWorld: true)];
        check.That(ScriptNames.Resolve("Tank 1", body, own).SequenceEqual([new NameMatch(NameKind.Object, "unit 0 · Tank 1", 0), new NameMatch(NameKind.Object, "waypoint 2 · Tank 1", 2)]),
            "a name matches the objects that have it exactly, and not the ones that differ in letter case when some match exactly");
        check.That(ScriptNames.Resolve("TANK 1", body, own).SequenceEqual([new NameMatch(NameKind.Object, "unit 0 · Tank 1", 0, false), new NameMatch(NameKind.Object, "unit 1 · tank 1", 1, false), new NameMatch(NameKind.Object, "waypoint 2 · Tank 1", 2, false)]),
            "and with no exact match it falls back to the other letter case, marked so");
        check.That(ScriptNames.Resolve("Path A", body, own).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0)]) && ScriptNames.Resolve("path a", body, own).Count == 0,
            "a waypoint path is matched by its exact name, with the count of the points the game keeps (the authored path names a unit, a waypoint and a unit: one point)");
        check.That(ScriptNames.Resolve("alpha", body, both).SequenceEqual([new NameMatch(NameKind.Script, "script alpha", 0), new NameMatch(NameKind.Script, "script alpha (base world)", 2)]),
            "a script is matched by its name, the base world's too");
        check.That(ScriptNames.Resolve("ALPHA", body, both).Count == 0, "a script is matched in its own letter case only");
        check.That(ScriptNames.Resolve("go", body, own).SequenceEqual([new NameMatch(NameKind.Handler, "event handled by beta", 1)]) && ScriptNames.Resolve("Go", body, own).Count == 0,
            "a script that handles an event of that name is found, in that case only");
        check.That(ScriptNames.Resolve("", body, own).Count == 0 && ScriptNames.Resolve("nothing", body, own).Count == 0, "an empty text and an unknown name match nothing");
        // The base world's objects follow the level's own, by the same rule, each world on its own: they are said, and the page offers nothing to go to.
        WorldBody baseBody = Body(Script("base", [], []));
        baseBody.Things[0].Init.Name = "Tank 1";
        baseBody.Things[1].Init.Name = "tank 1";
        baseBody.Things[2].Init.Name = "Base Hut";
        baseBody.Things[3].Init.Name = "DEPOT";
        body.Things[3].Init.Name = "Depot";
        check.That(ScriptNames.Resolve("Tank 1", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Object, "unit 0 · Tank 1", 0), new NameMatch(NameKind.Object, "waypoint 2 · Tank 1", 2),
                                                                                   new NameMatch(NameKind.BaseObject, "unit 0 · Tank 1", 0)]),
            "an object of the base world that has the name exactly is listed after the level's own");
        check.That(ScriptNames.Resolve("TANK 1", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Object, "unit 0 · Tank 1", 0, false), new NameMatch(NameKind.Object, "unit 1 · tank 1", 1, false),
                                                                                   new NameMatch(NameKind.Object, "waypoint 2 · Tank 1", 2, false), new NameMatch(NameKind.BaseObject, "unit 0 · Tank 1", 0, false),
                                                                                   new NameMatch(NameKind.BaseObject, "unit 1 · tank 1", 1, false)]),
            "and with no exact match the base world falls back to the other letter case too, marked so");
        check.That(ScriptNames.Resolve("Base Hut", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.BaseObject, "waypoint 2 · Base Hut", 2)]) &&
                   ScriptNames.Resolve("base hut", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.BaseObject, "waypoint 2 · Base Hut", 2, false)]),
            "a name only a base-world object has is found there, row and all");
        check.That(ScriptNames.Resolve("Depot", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Object, "waypoint 3 · Depot", 3), new NameMatch(NameKind.BaseObject, "waypoint 3 · DEPOT", 3, false)]) &&
                   ScriptNames.Resolve("DEPOT", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Object, "waypoint 3 · Depot", 3, false), new NameMatch(NameKind.BaseObject, "waypoint 3 · DEPOT", 3)]),
            "an exact name in one world does not silence the other-case matches of the other");
        check.That(ScriptNames.Resolve("Base Hut", body, own).Count == 0 && ScriptNames.Resolve("Base Hut", body, own, null).Count == 0 && ScriptNames.Resolve("", body, own, baseBody).Count == 0 &&
                   ScriptNames.Resolve("Path A", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0)]),
            "without a base world there are none, an empty text matches nothing, and the base world's paths are not names to follow here");
        body.Things[3].Init.Name = "";
        // The game finds a waypoint path by name ignoring letter case where a script follows one, and compares every other name as it is: only a path argument is case-blind.
        // It keeps one list of paths, the base world's before the level's own, and takes the first that matches: one path is named.
        WaypointPath shout = new() { Name = "PATH A" };
        shout.Slots.AddRange([3, 2]);
        body.WaypointPaths.Add(shout);
        check.That(ScriptNames.Resolve("Path A", body, own).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0)]) && ScriptNames.Resolve("path a", body, own).Count == 0 &&
                   ScriptNames.Resolve("Path A", body, own, null, true).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0)]) &&
                   ScriptNames.Resolve("path a", body, own, null, true).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0, false)]) &&
                   ScriptNames.Resolve("PATH A", body, own, null, true).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0, false)]),
            "a path argument names the first path of that name in any letter case (not the exact one when another comes first), marked when its case differs; anywhere else only the exact name is a path");
        body.WaypointPaths.Reverse();
        check.That(ScriptNames.Resolve("Path A", body, own, null, true).SequenceEqual([new NameMatch(NameKind.Path, "path PATH A · 2 points", 0, false)]) &&
                   ScriptNames.Resolve("PATH A", body, own, null, true).SequenceEqual([new NameMatch(NameKind.Path, "path PATH A · 2 points", 0)]),
            "the first in the list wins whatever the case, so with the other order the other path is the one");
        body.WaypointPaths.Reverse();
        // The base world's paths come before the level's own: a base world's path of that name is the one a follow call finds, and the level's own is not named.
        check.That(ScriptNames.Resolve("PATH A", body, own, baseBody, true).SequenceEqual([new NameMatch(NameKind.BasePath, "path Path A · 1 point", 0, false)]) &&
                   ScriptNames.Resolve("Path A", body, own, baseBody, true).SequenceEqual([new NameMatch(NameKind.BasePath, "path Path A · 1 point", 0)]) &&
                   ScriptNames.Resolve("Path A", body, own, baseBody).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0)]),
            "the base world's paths are looked at first, and only for a path argument");
        baseBody.WaypointPaths[0].Name = "Base Route";
        check.That(ScriptNames.Resolve("base route", body, own, baseBody, true).SequenceEqual([new NameMatch(NameKind.BasePath, "path Base Route · 1 point", 0, false)]) &&
                   ScriptNames.Resolve("path a", body, own, baseBody, true).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 1 point", 0, false)]) &&
                   ScriptNames.Resolve("Base Route", body, own, baseBody).Count == 0 && ScriptNames.Resolve("nothing", body, own, baseBody, true).Count == 0,
            "a name only the base world's path has is that path, one it lacks goes on to the level's own, and a base world's path is not a name outside a path argument");
        // C-locale _stricmp folds ASCII bytes but not Latin-1 accented bytes. The loader retains a length-prefixed
        // name, but the game's comparison stops at its first NUL: neither spelling after that byte affects the match.
        WorldBody accentOwn = new(), accentBase = new();
        accentBase.WaypointPaths.Add(new WaypointPath { Name = "À-ROUTE" });
        accentOwn.WaypointPaths.Add(new WaypointPath { Name = "à-ROUTE" });
        check.That(ScriptNames.Resolve("à-route", accentOwn, [], accentBase, true)
                       .SequenceEqual([new NameMatch(NameKind.Path, "path à-ROUTE · 0 points", 0, false)]) &&
                   ScriptNames.Resolve("À-route", accentOwn, [], accentBase, true)
                       .SequenceEqual([new NameMatch(NameKind.BasePath, "path À-ROUTE · 0 points", 0, false)]),
            "C-locale path lookup folds ASCII letters but does not merge differently cased Latin-1 bytes");
        accentBase.WaypointPaths[0].Name = "Route\0stored suffix";
        check.That(ScriptNames.Resolve("route", accentOwn, [], accentBase, true)
                       .SequenceEqual([new NameMatch(NameKind.BasePath, "path Route · 0 points", 0, false)]) &&
                   ScriptNames.Resolve("Route\0query suffix", accentOwn, [], accentBase, true)
                       .SequenceEqual([new NameMatch(NameKind.BasePath, "path Route · 0 points", 0)]),
            "a follow-path comparison and its displayed spelling stop at the first NUL, retaining exact-case status for the compared prefix");
        check.That(ScriptNames.Resolve("ALPHA", body, both, null, true).Count == 0 && ScriptNames.Resolve("Go", body, own, null, true).Count == 0 &&
                   ScriptNames.Resolve("TANK 1", body, own, baseBody, true).SequenceEqual(ScriptNames.Resolve("TANK 1", body, own, baseBody)) && ScriptNames.Resolve("nothing", body, own, null, true).Count == 0,
            "and objects, scripts and events stay exact in a path argument, as the game compares them");
        body.WaypointPaths.RemoveAt(1);
        body.WaypointPaths[0].Slots.Clear();
        check.That(ScriptNames.Resolve("Path A", body, own).SequenceEqual([new NameMatch(NameKind.Path, "path Path A · 0 points", 0)]), "a path with no points is still matched");
        body.WaypointPaths[0].Slots.Add(2);
        check.That(ScriptNames.Resolve("Path A", body, own)[0].Label == "path Path A · 1 point", "and the count says one point in the singular");
        body.WaypointPaths[0].Slots.AddRange([0, 4, 1, 99, -1, 5]);
        check.That(ScriptNames.Resolve("Path A", body, own)[0].Label == "path Path A · 1 point", "the count is of the points the game keeps, not the slots: a unit, a feature, a row past the list and a negative slot are not points");
    }

    private static void Paths(Checks check)
    {
        WorldBody body = Body(Script("alpha", [], []));  // the authored body has one path, "Path A", through rows 1, 2 and 0: a unit, a waypoint and a unit; rows 3 is a waypoint and 4 a feature
        check.That(body.Things[2].Kind == WaypointCatalog.WaypointKind && body.Things[3].Kind == WaypointCatalog.WaypointKind && body.Things[0].Kind == "unit" && body.Things[1].Kind == "unit" && body.Things[4].Kind == "feature",
            "the authored objects are the kinds the path tests below rely on");
        check.That(WaypointCatalog.Rows(body, body.WaypointPaths[0]).SequenceEqual([2]) && WaypointCatalog.Through(body, 2).SequenceEqual([new PathStop(0, "Path A", 1, 1)]) &&
                   WaypointCatalog.Through(body, 0).Count == 0 && WaypointCatalog.Through(body, 1).Count == 0 && WaypointCatalog.Through(body, 4).Count == 0,
            "a path's points are its slots that name a waypoint, as the game's loader keeps them: the units it names are not points, and are on no path");
        body.WaypointPaths[0].Slots.Clear();
        body.WaypointPaths[0].Slots.AddRange([3, 0, 2, 4, 3]);  // waypoint, unit, waypoint, feature, the first waypoint again
        check.That(WaypointCatalog.Rows(body, body.WaypointPaths[0]).SequenceEqual([3, 2, 3]) && WaypointCatalog.Through(body, 3).SequenceEqual([new PathStop(0, "Path A", 1, 3), new PathStop(0, "Path A", 3, 3)]) &&
                   WaypointCatalog.Through(body, 2).SequenceEqual([new PathStop(0, "Path A", 2, 3)]) && WaypointCatalog.Through(body, 0).Count == 0 && WaypointCatalog.Through(body, 4).Count == 0,
            "an object's place on a path is its point number of the points kept: the slots dropped take no number, and a point passed twice is listed twice");
        WaypointPath second = new() { Name = "Loop" };
        second.Slots.AddRange([2, 2, 4]);
        body.WaypointPaths.Add(second);
        check.That(WaypointCatalog.Through(body, 2).SequenceEqual([new PathStop(0, "Path A", 2, 3), new PathStop(1, "Loop", 1, 2), new PathStop(1, "Loop", 2, 2)]),
            "an object that a path passes through twice is listed twice, and paths in the world's order");
        WaypointPath wild = new() { Name = "Wild" };
        wild.Slots.AddRange([1, 99, -1, 3, (short)body.Things.Count, (short)(body.Things.Count - 1), 2, short.MinValue, short.MaxValue]);
        check.That(WaypointCatalog.Rows(body, wild).SequenceEqual([3, 2]), "the slots that name no object, a unit or a feature are left out");
        WorldBody ends = Body(Script("alpha", [], []));
        ends.Things[0].ObjectId = ends.Things[2].ObjectId;  // the first and the last objects are waypoints too
        ends.Things[ends.Things.Count - 1].ObjectId = ends.Things[2].ObjectId;
        WaypointPath bounds = new() { Name = "Ends" };
        bounds.Slots.AddRange([0, 1, (short)(ends.Things.Count - 1), -1, (short)ends.Things.Count]);
        check.That(WaypointCatalog.Rows(ends, bounds).SequenceEqual([0, ends.Things.Count - 1]), "the first and the last objects of the list are points like any other, and the slot past the list is not");
        MapView view = new();
        view.Resize(400, 300);
        view.FitBounds(100, 100, 200, 150);
        (double leftX, double bottomY) = view.ToScreen(100, 100);
        (double rightX, double topY) = view.ToScreen(200, 150);
        check.That(Math.Abs(view.Scale - 3.2) < 1e-9 && Math.Abs(view.CenterX - 150) < 1e-9 && Math.Abs(view.CenterY - 125) < 1e-9 && Math.Abs(leftX - 40) < 1e-9 && Math.Abs(rightX - 360) < 1e-9 && Math.Abs(topY - 70) < 1e-9 && Math.Abs(bottomY - 230) < 1e-9,
            $"a box is shown as large as will fit with a margin of 40 pixels, centred: scale {view.Scale}, corners {leftX},{bottomY} and {rightX},{topY}");
        view.Resize(500, 400);
        check.That(Math.Abs(view.Scale - 3.2) < 1e-9 && Math.Abs(view.CenterX - 150) < 1e-9, "the view is then the player's own: a new size keeps it");
        view.FitBounds(300, 300, 300, 300);
        check.That(view.Scale == 8 && MapView.MaxFitScale == 8 && view.CenterX == 300 && view.CenterY == 300, "a single point is not blown up past the fit zoom");
        view.FitBounds(600, 600, 700, 700);
        check.That(view.CenterX == 512 && view.CenterY == 512, "a box beyond the square puts the view's centre at the square's edge, as panning does");
        view.FitBounds(0, 0, 512, 512);
        check.That(Math.Abs(view.Scale - 0.625) < 1e-9 && view.CenterX == 256 && view.CenterY == 256, "a box as large as the square is fitted with the same margin");
        MapView tiny = new();
        tiny.Resize(60, 60);
        tiny.FitBounds(10, 10, 20, 20);
        check.That(tiny.Scale == tiny.MinScale, "a view too small for the margin settles on the smallest scale rather than a negative one");
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
            check.That(MakeNode(pipe, 0x1000 | 0x180) == 0, $"a named pipe was made (mknod: {Marshal.GetLastPInvokeErrorMessage()})");
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
            File.Delete(pipe);

            // The other kinds of entry that are not files: a socket, a device and a link (which is asked about itself, not its target).
            string socket = Path.Combine(folder, "Sock.msl");
            check.That(MakeNode(socket, 0xC000 | 0x180) == 0, $"a socket node was made (mknod: {Marshal.GetLastPInvokeErrorMessage()})");
            check.That(ScriptSources.Find(game, 123, "Sock") is { Source: null, Problem: "Sock.msl is not a regular file, so it is not read." } && !ScriptSources.IsRegularFile(socket),
                "a socket named like a script is refused too");
            File.Delete(socket);
            string link = Path.Combine(folder, "Link.msl");
            File.CreateSymbolicLink(link, Path.Combine(folder, "Foo.msl"));
            check.That(!ScriptSources.IsRegularFile(link) && !ScriptSources.IsRegularFile("/dev/null") && ScriptSources.IsRegularFile(Path.Combine(folder, "Foo.msl")),
                "a link and a device are not regular files, though a link's target is");
            File.Delete(link);

            // A path relative to the working folder is asked about as it is, and an entry that cannot be asked about says why (the system's own words).
            string relative = Path.GetRelativePath(Environment.CurrentDirectory, game);
            check.That(!Path.IsPathRooted(relative) && ScriptSources.Find(relative, 123, "Foo").Source?.Text == "// fine\n" && ScriptSources.IsRegularFile(Path.Combine(relative, "data", "MissionScripts", "level123", "Foo.msl")),
                $"a game folder given relative to the working folder is read as it is: {relative}");
            // The system cannot be asked what an entry is: nothing is read, and the sentence says why (the system's own words, or that the call is missing).
            Func<string, (int Failed, int Errno, uint Mask, ushort Mode)> native = ScriptSources.Statx;
            try
            {
                string foo = Path.Combine(folder, "Foo.msl");
                ScriptSources.Statx = _ => (-1, 1, 0, 0);  // EPERM, as a sandbox that refuses the call answers
                IOException? refused = null;
                try { ScriptSources.IsRegularFile(foo); } catch (IOException error) { refused = error; }
                check.That(refused is { Message: "Operation not permitted", InnerException: null }, $"a refusal of the call is an IOException in the system's words: \"{refused?.Message}\"");
                check.That(ScriptSources.Find(game, 123, "Foo") is { Source: null, Problem: "Foo.msl could not be examined: Operation not permitted" }, "and the lookup says so and reads nothing");
                ScriptSources.Statx = _ => throw new EntryPointNotFoundException();
                refused = null;
                try { ScriptSources.IsRegularFile(foo); } catch (IOException error) { refused = error; }
                check.That(refused is { Message: "this system's C library has no statx to ask with", InnerException: EntryPointNotFoundException }, $"a C library without the call fails closed, not open: \"{refused?.Message}\"");
                check.That(ScriptSources.Find(game, 123, "Foo") is { Source: null, Problem: "Foo.msl could not be examined: this system's C library has no statx to ask with" }, "and the lookup says so and reads nothing");
                ScriptSources.Statx = _ => throw new DllNotFoundException();
                check.That(ScriptSources.Find(game, 123, "Foo") is { Source: null, Problem: "Foo.msl could not be examined: this system's C library has no statx to ask with" }, "a missing library is the same");
                ScriptSources.Statx = _ => (0, 0, 0, 0);  // the call answered but gave no type
                check.That(!ScriptSources.IsRegularFile(foo), "an answer with no type in it is not a regular file");
                ScriptSources.Statx = _ => (0, 0, 0, 0x81A4);  // a regular file's mode, but the type was not among what the call filled in
                check.That(!ScriptSources.IsRegularFile(foo), "a mode the call did not say it filled in is not believed");
                check.That(Enumerable.Range(0, 5).Select(which => { ScriptSources.Statx = _ => (0, 0, 1, new ushort[] { 0x81A4, 0x41ED, 0x11A4, 0xA1FF, 0xC1FF }[which]); return ScriptSources.IsRegularFile(foo); }).SequenceEqual([true, false, false, false, false]),
                    "of a regular file, a folder, a pipe, a link and a socket only the regular file is read");
            }
            finally
            {
                ScriptSources.Statx = native;
            }
            check.That(ScriptSources.Find(game, 123, "Foo").Source?.Text == "// fine\n", "with the native call back, the source is read again");
            string examineFailure = "";
            try
            {
                ScriptSources.IsRegularFile(Path.Combine(folder, "Gone.msl"));
            }
            catch (IOException error)
            {
                examineFailure = error.Message;
            }
            check.That(examineFailure == "No such file or directory", $"an entry that cannot be examined is an IOException that says why: \"{examineFailure}\"");
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
        SourcesReplacementChecks(output, check);
    }

    private static void SourcesReplacementChecks(string output, Checks check)
    {
        if (!OperatingSystem.IsLinux() || RuntimeInformation.ProcessArchitecture != Architecture.X64) return;
        string game = Path.Combine(output, "script-source-replacement-game");
        string other = Path.Combine(output, "script-source-replacement-other");
        string folder = Path.Combine(game, "data", "MissionScripts", "level123");
        Directory.CreateDirectory(folder);
        Directory.CreateDirectory(other);
        string file = Path.Combine(folder, "Race.msl");
        string otherFile = Path.Combine(other, "Race.msl");
        File.WriteAllText(file, "// selected\n");
        File.WriteAllText(otherFile, "// other\n");
        Func<string, (int Failed, int Errno, uint Mask, ushort Mode)> native = ScriptSources.Statx;
        bool changed = false;
        try
        {
            ScriptSources.Statx = path =>
            {
                var answer = native(path);
                if (!changed && Path.GetFileName(path) == "Race.msl")
                {
                    changed = true;
                    File.Move(file, Path.Combine(folder, "original.msl"));
                    File.CreateSymbolicLink(file, otherFile);
                }
                return answer;
            };
            ScriptSourceResult result = ScriptSources.Find(game, 123, "Race");
            check.That(changed && result.Source is null && result.Problem is not null,
                "a source replaced by a link after its first type check is refused");
        }
        finally { ScriptSources.Statx = native; }
        File.Delete(file);
        File.Move(Path.Combine(folder, "original.msl"), file);
        changed = false;
        try
        {
            ScriptSources.Statx = path =>
            {
                var answer = native(path);
                if (!changed && Path.GetFileName(path) == "Race.msl")
                {
                    changed = true;
                    Directory.Move(folder, folder + "-original");
                    Directory.CreateSymbolicLink(folder, other);
                }
                return answer;
            };
            ScriptSourceResult result = ScriptSources.Find(game, 123, "Race");
            check.That(changed && result.Source is null && result.Problem is not null,
                "a source directory replaced by a link after its first type check is refused");
        }
        finally { ScriptSources.Statx = native; }
        Directory.Delete(folder);
        Directory.Move(folder + "-original", folder);

        string replacement = Path.Combine(other, "Replacement.msl");
        File.WriteAllText(replacement, "// replacement\n");
        changed = false;
        try
        {
            ScriptSources.Statx = path =>
            {
                var answer = native(path);
                if (!changed && Path.GetFileName(path) == "Race.msl")
                {
                    changed = true;
                    File.Move(file, file + ".prior");
                    File.Move(replacement, file);
                }
                return answer;
            };
            ScriptSourceResult result = ScriptSources.Find(game, 123, "Race");
            check.That(changed && result.Source is null && result.Problem is not null,
                "a different regular source substituted after the type check is refused");
        }
        finally { ScriptSources.Statx = native; }
        File.Delete(file);
        File.Move(file + ".prior", file);

        string alias = Path.Combine(output, "script-source-replacement-root-link");
        Directory.CreateSymbolicLink(alias, game);
        check.That(ScriptSources.Find(alias, 123, "Race").Source?.Text == "// selected\n",
            "a selected game root reached through a link still works");
        changed = false;
        try
        {
            ScriptSources.Statx = path =>
            {
                var answer = native(path);
                if (!changed && Path.GetFileName(path) == "Race.msl")
                {
                    changed = true;
                    Directory.Delete(alias);
                    Directory.CreateSymbolicLink(alias, other);
                }
                return answer;
            };
            ScriptSourceResult result = ScriptSources.Find(alias, 123, "Race");
            check.That(changed && result.Source is null && result.Problem is not null,
                "a selected-root link changed during lookup is refused");
        }
        finally { ScriptSources.Statx = native; }
        Directory.Delete(alias);

        bool grew = false;
        try
        {
            ScriptSources.BeforeReadForTest = () =>
            {
                grew = true;
                using FileStream append = new(file, FileMode.Append, FileAccess.Write, FileShare.ReadWrite);
                append.Write(new byte[ScriptSources.MaxBytes]);
            };
            ScriptSourceResult result = ScriptSources.Find(game, 123, "Race");
            check.That(grew && result.Source is null && result.Problem is { } problem && problem.Contains("larger than", StringComparison.Ordinal),
                "a source that grows past the byte limit after opening is refused");
        }
        finally { ScriptSources.BeforeReadForTest = null; }
        File.WriteAllText(file, "// selected\n");

        bool modified = false;
        try
        {
            ScriptSources.BeforeReadForTest = () => { modified = true; File.WriteAllText(file, "// replaced\n"); };
            ScriptSourceResult result = ScriptSources.Find(game, 123, "Race");
            check.That(modified && result.Source is null && result.Problem is not null,
                "a source modified in place during the read is refused");
        }
        finally { ScriptSources.BeforeReadForTest = null; }
        File.WriteAllText(file, "// selected\n");

        changed = false;
        try
        {
            ScriptSources.Statx = path =>
            {
                var answer = native(path);
                if (!changed && Path.GetFileName(path) == "Race.msl")
                {
                    changed = true;
                    File.Move(file, file + ".prior");
                    if (MakeNode(file, 0x1000 | 0x180) != 0) throw new IOException("Could not make authored test pipe.");
                }
                return answer;
            };
            Task<ScriptSourceResult> lookup = Task.Run(() => ScriptSources.Find(game, 123, "Race"));
            bool returned = lookup.Wait(TimeSpan.FromSeconds(5));
            check.That(changed && returned && lookup.Result.Source is null && lookup.Result.Problem is not null,
                "a source replaced by a named pipe is refused without waiting for a writer");
            if (!returned)
            {
                using (File.OpenHandle(file, FileMode.Open, FileAccess.Write)) { }
                lookup.Wait(TimeSpan.FromSeconds(5));
            }
        }
        finally { ScriptSources.Statx = native; }
        File.Delete(file);
        File.Move(file + ".prior", file);

        int before = Directory.GetFiles("/proc/self/fd").Length;
        bool repeated = true;
        for (int i = 0; i < 100; i++)
            repeated &= ScriptSources.Find(game, 123, "Race").Source?.Text == "// selected\n" &&
                        ScriptSources.Find(game, 123, "Absent").Source is null;
        int after = Directory.GetFiles("/proc/self/fd").Length;
        check.That(repeated && after <= before, "successful and missing source lookups release their descriptors");
        Directory.Delete(game, true);
        Directory.Delete(other, true);
    }

    // mknod makes a named pipe (0x1000) or a socket node (0xC000), which anyone may make; the mode carries the permission bits.
    private static int MakeNode(string path, uint mode) => MakeNodeNative(path, mode, 0);

    [DllImport("libc", EntryPoint = "mknod", SetLastError = true)]
    private static extern int MakeNodeNative([MarshalAs(UnmanagedType.LPUTF8Str)] string path, uint mode, ulong device);

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
        check.That(LevelEditorModel.ReadBaseWorld(new LevelWorlds(0, 9, baseBytes, null))?.Things.Count == baseBody.Things.Count && LevelEditorModel.ReadBaseWorld(new LevelWorlds(-1, 9, baseBytes, null)) is null &&
                   LevelEditorModel.ReadBaseWorld(new LevelWorlds(5, 9, null, null)) is null && LevelEditorModel.ReadBaseWorld(new LevelWorlds(5, 9, [1, 2, 3], null)) is null,
            "the base world is read when the archive has one at a level of 0 or more, and is none when it has none or does not read");
        check.That(model.BaseWorld is { } openBase && openBase.Things.Count > 0 && model.BaseLevel == 100, "the model keeps the open level's base world");
        check.That(model.Open(300) is false && model.Scripts.Count == 0 && model.BaseWorld is null, "a level that cannot be opened lists no scripts and has no base world");
        check.That(model.Open(200) && model.Scripts.Count == 2 && model.Session!.Body.Scripts.Count == 1, "and opening one again lists its scripts afresh");
        Directory.Delete(game, true);
    }
}
