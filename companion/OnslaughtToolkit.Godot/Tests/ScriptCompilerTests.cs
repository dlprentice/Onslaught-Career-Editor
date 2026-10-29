// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Globalization;
using OnslaughtToolkit.Companion.Development;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The C# mission script compiler against the Toolkit's reference compiler (the authored vectors tools/msl_vectors.py writes: each source's
/// record, notes or refusal message word for word), against shapes worked out by hand from what the shipped scripts show, and on what it
/// reads and refuses (headers, links, limits). Nothing here touches Godot or a game: every source is authored. The local retail gate
/// (Development/ScriptsGate.cs) holds it to the scripts the game ships.
/// </summary>
internal static class ScriptCompilerTests
{
    internal static void Run(string output, Checks check)
    {
        check.Suite("script compiler");
        Vectors(check);
        Shapes(check);
        Tables(check);
        Lexing(check);
        Counters(check);
        ReaderFailures(check);
        Files(output, check);
        GatePrivacy(output, check);
        Limits(check);
        Records(check);
    }

    private static MissionScript Compile(string source, int constStart = 0, int doOnceStart = 0, List<CompileNote>? notes = null, NameResolver? resolve = null,
        Func<string, string>? read = null, CompileLimits? limits = null) =>
        ScriptCompiler.Compile("t", source, read ?? (path => throw new MissingInclude(path)), constStart, doOnceStart, resolve, notes, limits);

    private static CompileError Refused(string source, Func<string, string>? read = null, CompileLimits? limits = null)
    {
        try
        {
            Compile(source, read: read, limits: limits);
        }
        catch (CompileError error)
        {
            return error;
        }
        throw new InvalidOperationException("the source compiled");
    }

    private static bool Refuses(string source, string fragment, CompileLimits? limits = null) => Refuses(source, null, fragment, limits);

    private static bool Refuses(string source, Func<string, string>? read, string fragment, CompileLimits? limits = null)
    {
        try
        {
            Compile(source, read: read, limits: limits);
            return false;
        }
        catch (CompileError error)
        {
            return error.Message.Contains(fragment, StringComparison.Ordinal);
        }
    }

    private static void ReaderFailures(Checks check)
    {
        const string input = "#include data\\missing.msl\n";
        Func<string, string> failing = _ => throw new InvalidOperationException("private system detail");
        CompileError error = Refused(input, failing);
        check.That(error.Message == "the included file data\\missing.msl could not be read" && !error.Message.Contains("private system detail", StringComparison.Ordinal),
            "an include-reader failure becomes a stable compiler refusal without system details");
        CompileError expected = new("specific refusal");
        Func<string, string> stated = _ => throw expected;
        check.That(ReferenceEquals(Refused(input, stated), expected), "an existing compiler refusal keeps its original type and message");
    }

    private static void GatePrivacy(string output, Checks check)
    {
        string game = Path.Combine(output, "compiler-gate-privacy"), resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        byte[] archive = LevelTests.Unpack(LevelVectors.Archives.First(item => item.Name == "level-100").File);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), archive);
        LevelWorlds worlds = LevelArchive.Read(archive);
        MissionScript script = WorldBody.Read(worlds.RealBody!).Scripts[0];
        string sourceFolder = Path.Combine(game, "data", "MissionScripts", "level100");
        Directory.CreateDirectory(sourceFolder);
        const string marker = "PrivateDiagnosticMarker";
        File.WriteAllText(Path.Combine(sourceFolder, script.Name + ".msl"), $"init() {{ {marker}(); }}\n");
        List<string> printed = [], errors = [];
        int result = ScriptsGateCheck.Run(game, "", printed.Add, errors.Add);
        check.That(result == 1 && errors.Any(line => line.Contains(": refused", StringComparison.Ordinal)) &&
                   !printed.Concat(errors).Any(line => line.Contains(marker, StringComparison.Ordinal)),
            "the actual gate reports a refused authored script without printing its source or record detail");
    }

    // ---- the reference's own answers
    private static void Vectors(Checks check)
    {
        int compiled = 0, refused = 0;
        foreach (CompilerVector vector in ScriptVectors.All)
        {
            Dictionary<string, string> includes = vector.Includes.ToDictionary(include => include.Path, include => include.Text, StringComparer.Ordinal);
            Func<string, string> read = path => includes.TryGetValue(path.Replace('\\', '/').ToLowerInvariant(), out string? text) ? text : throw new MissingInclude(path);
            Dictionary<string, ResolvedName> given = vector.Resolve.ToDictionary(item => item.Name, item => Given(item.Type, item.Value), StringComparer.Ordinal);
            NameResolver? resolve = given.Count == 0 ? null : (name, _) => given.TryGetValue(name, out ResolvedName value) ? value : null;
            List<CompileNote> notes = [];
            try
            {
                MissionScript script = ScriptCompiler.Compile("t", vector.Source, read, vector.ConstStart, vector.DoOnceStart, resolve, notes);
                compiled++;
                string[] lines = ScriptDump.Lines(script);
                string[] noteLines = [.. notes.Select(note => $"{note.Line} {note.Kind} {note.Text}")];
                check.That(vector.Error is null && lines.SequenceEqual(vector.Dump) && script.Trailer.SequenceEqual("end_script"u8.ToArray()),
                    $"{vector.Name}: the record is the reference's ({vector.Why}): {FirstDifference(lines, vector.Dump)}{(vector.Error is null ? "" : $" (the reference refused: {vector.Error})")}");
                check.That(noteLines.SequenceEqual(vector.Notes), $"{vector.Name}: the notes are the reference's: {string.Join(" | ", noteLines)} against {string.Join(" | ", vector.Notes)}");
            }
            catch (CompileError error)
            {
                refused++;
                string kind = error is MissingInclude ? "missingInclude" : "error";
                check.That(vector.Error is not null && error.Message == vector.Error && kind == vector.ErrorKind && (error.Line ?? -1) == vector.ErrorLine &&
                           (error is not MissingInclude missing || missing.Path == vector.ErrorPath),
                    $"{vector.Name}: the refusal is the reference's ({vector.Why}): \"{error.Message}\" (line {error.Line}) against \"{vector.Error}\" (line {vector.ErrorLine})");
            }
        }
        check.That(compiled > 50 && refused > 40, $"the vectors hold both kinds: {compiled} compile and {refused} are refused");
        check.That(ScriptVectors.All.Select(vector => vector.Name).Distinct().Count() == ScriptVectors.All.Length, "every vector has a name of its own");
    }

    private static ResolvedName Given(string type, string value) => type switch
    {
        "int" => new ResolvedName(1, new ScriptInt(int.Parse(value, CultureInfo.InvariantCulture))),
        "float" => new ResolvedName(2, new ScriptFloat(float.Parse(value, CultureInfo.InvariantCulture))),
        "string" => new ResolvedName(3, new ScriptText(value)),
        "bool" => new ResolvedName(4, new ScriptInt(int.Parse(value, CultureInfo.InvariantCulture))),
        _ => throw new InvalidOperationException($"a vector's name is given as an int, float, string or bool, not {type}"),
    };

    private static string FirstDifference(string[] ours, string[] theirs)
    {
        for (int line = 0; line < Math.Min(ours.Length, theirs.Length); line++)
            if (ours[line] != theirs[line]) return $"line {line}: \"{ours[line]}\" against \"{theirs[line]}\"";
        return ours.Length == theirs.Length ? "none" : $"{ours.Length} lines against {theirs.Length}";
    }

    // ---- shapes worked out by hand (not from the reference), each from what the shipped scripts show
    private static string[] Listing(MissionScript script)
    {
        List<ScriptSymbol> symbols = [.. script.Code.Symbols];
        List<string> lines = [];
        foreach (ScriptInstruction instruction in script.Code.Instructions)
        {
            string op = ScriptTables.Opcodes[instruction.Opcode][3..];
            lines.Add(op switch
            {
                "PUSH" or "POP" or "GETTOP" => $"{op} {(symbols[instruction.Attribute].Name.StartsWith("const", StringComparison.Ordinal) ? ValueText(symbols[instruction.Attribute].Value) : symbols[instruction.Attribute].Name)}",
                "CALL" => $"CALL {ScriptTables.Natives[instruction.Attribute & 0xFF].Name}/{(instruction.Attribute >> 8) & 0xFF}{((instruction.Attribute & (1 << 16)) != 0 ? " +used" : "")}",
                "JMP" or "JMPFALSE" or "JMPNE" => $"{op} {instruction.Attribute}",
                _ => op,
            });
        }
        return [.. lines];
    }

    private static string ValueText(ScriptValue? value) => value switch
    {
        ScriptInt integer => integer.Value.ToString(CultureInfo.InvariantCulture),
        ScriptFloat number => number.Value.ToString("R", CultureInfo.InvariantCulture),
        ScriptText text => $"'{text.Value}'",
        _ => "-",
    };

    private static void Shapes(Checks check)
    {
        MissionScript a = Compile("vars\n\tthing player;\nend_vars\ninit()\n{\n\tPause(1);\n}\n");
        check.That(Listing(a).SequenceEqual(["RETURN", "PUSH 1", "CALL Pause/1", "REMOVE_TOP", "RETURN"]) && a.Code.EventPcs.SequenceEqual([1, .. Enumerable.Repeat(-1, 12)]) &&
                   a.Code.Tail1 == 0 && a.Code.Tail2 == 1 && a.Code.NextSymbolIndex == 4 && a.Trailer.SequenceEqual("end_script"u8.ToArray()),
            "a vars block ends in a return, a call statement drops its result (no bit 16), init's entry point follows the block, and the trailing words and the trailer are as the shipped scripts have them");
        check.That(a.Code.Symbols.Select(symbol => (symbol.Name, symbol.DataType, symbol.SymbolType)).SequenceEqual([("player", 0, 1), ("init", 0, 3), ("Pause", 0, 5), ("const data0", 1, 5)]),
            "the symbols are entered in the order the compiler meets them, each with the line it first appeared on");
        MissionScript noVars = Compile("init()\n{\n\tDie();\n}\n");
        check.That(Listing(noVars).SequenceEqual(["CALL Die/0", "REMOVE_TOP", "RETURN"]) && noVars.Code.Tail2 == 0 && noVars.Code.EventPcs[0] == 0, "no vars block: no initialiser block and a zero trailing word");
        MissionScript calls = Compile("vars\n\tthing t;\nend_vars\ninit()\n{\n\tt = GetThingRef(\"x\");\n\tAttack(GetThingRef(\"y\"));\n\tif (GetHealth() < 5)\n\t{\n\t}\n}\n");
        check.That(Listing(calls)[1..].SequenceEqual(["PUSH 'x'", "CALL GetThingRef/1 +used", "GETTOP t", "REMOVE_TOP", "PUSH 'y'", "CALL GetThingRef/1 +used", "CALL Attack/1", "REMOVE_TOP",
                                                      "CALL GetHealth/0 +used", "PUSH 5", "LESS_THAN", "JMPFALSE 13", "LABEL", "RETURN"]),
            "a call that is an argument, an assignment's value or a condition keeps bit 16; one that is a whole statement drops it");
        MissionScript loop = Compile("vars\n\tint n;\nend_vars\ninit()\n{\n\tfor (n = 0; n < 3; n = n + 1)\n\t{\n\t\tPause(2);\n\t}\n}\n");
        check.That(Listing(loop)[1..].SequenceEqual(["PUSH 0", "GETTOP n", "REMOVE_TOP", "PUSH n", "PUSH 3", "LESS_THAN", "JMPFALSE 17", "PUSH 2", "CALL Pause/1", "REMOVE_TOP",
                                                      "PUSH n", "PUSH 1", "PLUS", "GETTOP n", "REMOVE_TOP", "JMP 4", "LABEL", "RETURN"]) &&
                   loop.Code.Symbols.Where(symbol => symbol.Name.StartsWith("const", StringComparison.Ordinal)).Select(symbol => ((ScriptInt)symbol.Value!).Value).SequenceEqual([0, 3, 1, 2]),
            "a for loop runs its step after the body, and the step's constant is numbered before the body's");
        MissionScript once = Compile("init()\n{\n\tdo_once\n\t{\n\t\tDie();\n\t}\n\tdo_once\n\t{\n\t\tShutdown();\n\t}\n}\n", doOnceStart: 5);
        check.That(Listing(once).SequenceEqual(["PUSH do-once-5", "JMPFALSE 6", "PUSH do-once-6", "POP do-once-5", "CALL Die/0", "REMOVE_TOP", "LABEL",
                                                "PUSH do-once-7", "JMPFALSE 13", "PUSH do-once-8", "POP do-once-7", "CALL Shutdown/0", "REMOVE_TOP", "LABEL", "RETURN"]) &&
                   once.Code.Symbols.Skip(3).Select(symbol => (symbol.Name, symbol.DataType, ((ScriptInt)symbol.Value!).Value, symbol.SymbolType)).SequenceEqual([("do-once-5", 4, 1, 0), ("do-once-6", 4, 0, 0), ("do-once-7", 4, 1, 0), ("do-once-8", 4, 0, 0)]) &&
                   once.Code.NextSymbolIndex == 7,
            "a do_once block clears a flag it tests, and its two boolean symbols per block come after every other symbol");
        MissionScript events = Compile("init()\n{\n\tPostEvent(\"go\");\n}\nevent(\"go\")\n{\n\tDie();\n}\nevent(\"stop\")\n{\n\tDie();\n}\n");
        check.That(events.Code.EventFunctions.Select(function => (function.EntryPc, function.Parameters[0])).SequenceEqual([(4, 2), (9, 5)]), "an event handler's parameter is the first string constant equal to its name");
        MissionScript grouping = Compile("vars\n\tbool a;\n\tbool b;\n\tbool c;\n\tbool r;\nend_vars\ninit()\n{\n\tr = a && b == c;\n}\n");
        check.That(Listing(grouping)[1..^1].SequenceEqual(["PUSH a", "PUSH b", "AND", "PUSH c", "CMPB", "GETTOP r", "REMOVE_TOP"]), "&& and == have one rank and group left to right");
        List<CompileNote> notes = [];
        Compile("vars\n\tbool a;\n\tbool b;\n\tbool c;\n\tbool r;\nend_vars\ninit()\n{\n\tr = a && b == c;\n}\n", notes: notes);
        check.That(notes.Select(note => (note.Kind, note.Text)).SequenceEqual([("grouping", "a && b == c is grouped ((a && b) == c)")]), "a mixed chain gets a note saying how it was grouped");
    }

    // ---- tables the messages and the grouping rest on
    private static void Tables(Checks check)
    {
        foreach ((string text, string repr) in ScriptVectors.Reprs)
            check.That(PythonText.Repr(text) == repr, $"a quoted token reads as the reference's repr: {repr}");
        foreach ((string outer, string inner, int answer) in ScriptVectors.Grouping)
        {
            bool? ours = ScriptParser.BindsTighter(outer, inner);
            check.That((ours is null ? -1 : ours.Value ? 1 : 0) == answer, $"binds_tighter({outer}, {inner}) is the reference's {answer}");
        }
        check.That(ScriptTables.Opcodes.Distinct().Count() == ScriptTables.Opcodes.Length && ScriptTables.Opcodes[5] == "OP_PUSH" && ScriptTables.Opcodes[24] == "OP_CALL", "the opcode table is the VM's, PUSH at 5 and CALL at 24");
        check.That(ScriptParser.Spaced("  a \t b\r\n\f c\v") == "a b c" && ScriptParser.Spaced("a\u00a0 b") == "a\u00a0 b" && ScriptParser.Spaced("") == "" && ScriptParser.Spaced(" \n ") == "",
            "spaced text collapses ASCII blanks and line ends only");
    }

    private static void Lexing(Checks check)
    {
        List<(TokenKind Kind, string Text)> Lex(string text) => [.. ScriptLexer.Lex(text).Select(token => (token.Kind, token.Text))];
        check.That(Lex("12f 1.5f .5 1. 1.f 007.50 a.b").SequenceEqual([(TokenKind.Int, "12"), (TokenKind.Id, "f"), (TokenKind.Float, "1.5f"), (TokenKind.Float, ".5"), (TokenKind.Float, "1."),
                                                                         (TokenKind.Float, "1.f"), (TokenKind.Float, "007.50"), (TokenKind.Id, "a"), (TokenKind.Op, "."), (TokenKind.Id, "b")]),
            "numbers are digits with an optional point and an optional f (an integer takes no f), and a point between words is an operator");
        check.That(Lex("== != <= >= && || = ! < >").Select(token => token.Text).SequenceEqual(["==", "!=", "<=", ">=", "&&", "||", "=", "!", "<", ">"]), "two-character operators are read before one-character ones");
        check.That(Lex("\"a b\" // comment \"x\"\n\"c\"").Select(token => token.Text).SequenceEqual(["\"a b\"", "\"c\""]) && Lex("1.5.2").Select(token => token.Text).SequenceEqual(["1.5", ".2"]),
            "a string is closed on its line, a comment runs to the line's end, and 1.5.2 is two numbers");
        List<Token> spans = ScriptLexer.Lex("a\n  bc\r\n\t7");
        check.That(spans.Select(token => (token.Line, token.Start, token.End)).SequenceEqual([(0, 0, 1), (1, 4, 6), (2, 9, 10)]), "a token has its line (counting \\n only) and its span in the text");
        check.That(ScriptLexer.IncludeOf("  #  include\tdata\\a.msl // x") == "data\\a.msl" && ScriptLexer.IncludeOf("#includes x") is null && ScriptLexer.IncludeOf("include x") is null &&
                   ScriptLexer.DefineOf("#define A 1 // one") is { Name: "A" } define && define.Body.Select(token => token.Text).SequenceEqual(["1"]) && ScriptLexer.DefineOf("#define") is null && ScriptLexer.DefineOf("#defineX 1") is null &&
                   ScriptLexer.IsDefine("#define") && ScriptLexer.IsDefine("  # define x") && !ScriptLexer.IsDefine("#defined x") && !ScriptLexer.IsDefine("#define_x"),
            "directive lines are found with ASCII blanks only, and #define with no name is a directive that defines nothing");
    }

    private static void Counters(Checks check)
    {
        MissionScript constants = Compile("init()\n{\n\tPause(1);\n\tPause(2);\n}\n", constStart: 40);
        check.That(constants.Code.Symbols.Where(symbol => symbol.Name.StartsWith("const", StringComparison.Ordinal)).Select(symbol => symbol.Name).SequenceEqual(["const data40", "const data41"]) &&
                   ScriptCompiler.ConstStartOf(constants) == 40, "the counters belong to the session: constants are numbered from the caller's counter, and a shipped script's counter is read back from its first one");
        check.That(ScriptCompiler.DoOnceStartOf(Compile("init()\n{\n\tdo_once\n\t{\n\t}\n}\n", doOnceStart: 12)) == 12 && ScriptCompiler.ConstStartOf(Compile("init()\n{\n}\n")) == 0 &&
                   ScriptCompiler.DoOnceStartOf(Compile("init()\n{\n}\n")) == 0, "a script with none has counters of 0");
        int asked = -1;
        MissionScript given = Compile("init()\n{\n\tPause(1);\n\tPause(MISSING);\n}\n", resolve: (name, index) =>
        {
            asked = index;
            return name == "MISSING" ? new ResolvedName(1, new ScriptInt(3)) : null;
        });
        check.That(asked >= 0 && asked < given.Code.Symbols.Count && given.Code.Symbols[asked] is { Name: var constant, Value: ScriptInt { Value: 3 } } && constant.StartsWith("const data", StringComparison.Ordinal),
            $"a resolver is asked for a name a missing header would have defined at the index its constant will have: {asked}");
        MissionScript built = new() { Name = "b" };
        foreach (string name in new[] { "init", "const data", "xconst data3", "const data3x", "const data7", "const data9", "xdo-once-6", "do-once-5x", "do-once-4", "do-once-x" })
            built.Code.Symbols.Add(new ScriptSymbol { Name = name });
        check.That(ScriptCompiler.ConstStartOf(built) == 7 && ScriptCompiler.DoOnceStartOf(built) == 4, "the counter is the first symbol that is exactly `const dataN` or `do-once-N`");

        MissionScript edge = Compile("init() { Pause(1); }", constStart: int.MaxValue);
        check.That(edge.Code.Symbols.Any(symbol => symbol.Name == "const data2147483647"), "the largest stored constant number is accepted");
        try
        {
            Compile("init() { Pause(1); Pause(2); }", constStart: int.MaxValue);
            check.Fail("a second constant after the largest stored number was accepted");
        }
        catch (CompileError error) { check.That(error.Message.Contains(ScriptCompiler.CounterPast, StringComparison.Ordinal), "constant numbering refuses overflow"); }
        MissionScript onceEdge = Compile("init() { do_once { } }", doOnceStart: int.MaxValue - 1);
        check.That(onceEdge.Code.Symbols.Any(symbol => symbol.Name == "do-once-2147483647"), "the final do_once pair ends at the largest stored number");
        try
        {
            Compile("init() { do_once { } }", doOnceStart: int.MaxValue);
            check.Fail("a do_once pair past the largest stored number was accepted");
        }
        catch (CompileError error) { check.That(error.Message.Contains(ScriptCompiler.CounterPast, StringComparison.Ordinal), "do_once numbering refuses overflow"); }

        MissionScript names = new();
        names.Code.Symbols.Add(new ScriptSymbol { Name = "const data00000000000000000007" });
        check.That(ScriptCompiler.ConstStartOf(names) == 7, "counter names can have leading zeroes");
        names.Code.Symbols[0].Name = "const data2147483648";
        try { ScriptCompiler.ConstStartOf(names); check.Fail("an oversized counter name was accepted"); }
        catch (CompileError error) { check.That(error.Message == ScriptCompiler.CounterPast, "an oversized counter name is refused instead of becoming zero"); }
        names.Code.Symbols[0].Name = "const data7\n";
        check.That(ScriptCompiler.ConstStartOf(names) == 0, "a trailing newline is not part of an exact counter name");
    }

    private static void Files(string output, Checks check)
    {
        string folder = Path.Combine(output, "script-compiler-files");
        if (Directory.Exists(folder)) Directory.Delete(folder, true);
        string game = Path.Combine(folder, "game"), outside = Path.Combine(folder, "outside");
        Directory.CreateDirectory(Path.Combine(game, "Data", "Inc"));
        Directory.CreateDirectory(outside);
        File.WriteAllBytes(Path.Combine(game, "Data", "Inc", "Defs.MSL"), System.Text.Encoding.Latin1.GetBytes("#define LIMIT 3\r\n#define TWICE LIMIT\r\n"));
        File.WriteAllText(Path.Combine(folder, "outside.msl"), "#define X 1\n");
        File.WriteAllText(Path.Combine(outside, "secret.msl"), "#define X 1\n");
        Func<string, string> read = ScriptCompiler.IncludesFrom(game);
        MissionScript script = ScriptCompiler.Compile("t", "#include data\\inc\\defs.msl\ninit()\n{\n\tPause(TWICE);\n}\n", read);
        check.That(script.Code.Symbols.Where(symbol => symbol.Name.StartsWith("const", StringComparison.Ordinal)).Select(symbol => ((ScriptInt)symbol.Value!).Value).SequenceEqual([3]), "an include is found in any case with backslashes and its defines are used");
        MissingInclude? missing = null;
        try { ScriptCompiler.Compile("t", "#include data\\inc\\nothing.msl\n", read); } catch (MissingInclude error) { missing = error; }
        check.That(missing is { Path: "data\\inc\\nothing.msl" }, "a header the game folder lacks is a MissingInclude naming the path as written");
        check.That(Refuses("#include ..\\outside.msl\n", read, "cannot climb out of the game folder") && Refuses("#include data\\inc\n", read, "is not a file inside the game folder"),
            "a path cannot climb out of the game folder, and a folder is not a header");
        check.That(Refuses("#include data\\inc\\..\\outside.msl\n", read, "cannot climb out of the game folder") &&
                   Refuses("#include data\\absent\\..\\outside.msl\n", read, "is not in the game folder") &&
                   Refuses("#include data\\inc\\defs.msl\\child\n", read, "is not in the game folder"),
            "a path refuses traversal and reports a missing or non-directory earlier component");
        check.That(Refuses("#include data\\inc\\defs.msl\n", ScriptCompiler.IncludesFrom(""), "no game folder is given"),
            "a missing selected game folder has a stable refusal");
        try { ScriptCompiler.ReadSource(Path.Combine(folder, "missing.msl")); check.Fail("a missing direct source was read"); }
        catch (CompileError error) { check.That(error.Message == "missing.msl could not be read", "a missing direct source has no raw system error"); }
        check.That(read("data\\.\\inc\\.\\defs.msl").StartsWith("#define LIMIT", StringComparison.Ordinal) && read(".\\data\\\\inc\\defs.msl").StartsWith("#define LIMIT", StringComparison.Ordinal),
            "a dot in a path is the folder itself, and an empty part (a doubled separator) is skipped");
        File.WriteAllBytes(Path.Combine(game, "Data", "huge.msl"), new byte[ScriptCompiler.MaxSource + 1]);
        File.WriteAllBytes(Path.Combine(folder, "edge.msl"), Enumerable.Repeat((byte)' ', ScriptCompiler.MaxSource).ToArray());
        check.That(Refuses("#include data\\huge.msl\n", read, "longer than a million bytes") && ScriptCompiler.ReadSource(Path.Combine(folder, "edge.msl")).Length == ScriptCompiler.MaxSource,
            "a header of a million bytes is read and one byte more is refused");
        try { ScriptCompiler.ReadSource(Path.Combine(game, "Data", "huge.msl")); check.Fail("an oversized direct source was read"); }
        catch (CompileError error) { check.That(error.Message == "huge.msl is longer than a million bytes", "direct source reads enforce the same byte limit"); }
        File.WriteAllBytes(Path.Combine(game, "Data", "Inc", "Cafe.msl"), [.. "#define WORD \"caf"u8, 0xE9, (byte)'"', (byte)'\n']);  // a Latin-1 byte, which is not UTF-8
        MissionScript cafe = ScriptCompiler.Compile("t", "#include data\\inc\\cafe.msl\ninit()\n{\n\tPrint(WORD);\n}\n", read);
        check.That(cafe.Code.Symbols.Any(symbol => symbol.Value is ScriptText { Value: "caf\u00e9" }), "a header is single-byte text: a Latin-1 byte is the character with that number");
        Directory.CreateDirectory(Path.Combine(game, "Data", "Dup"));
        if (!OperatingSystem.IsWindows())
        {
            File.WriteAllText(Path.Combine(game, "Data", "Dup", "DX.msl"), "upper\n");
            File.WriteAllText(Path.Combine(game, "Data", "Dup", "dX.msl"), "lower\n");
            File.WriteAllText(Path.Combine(game, "Data", "Dup", "É.msl"), "accent\n");
            check.That(read("data\\dup\\DX.msl") == "upper\n" && read("data\\dup\\dX.msl") == "lower\n" && read("data\\dup\\dx.msl") == "upper\n",
                "case lookup chooses an exact spelling first, otherwise the ordinal first ASCII case match");
            check.That(Refuses("#include data\\dup\\é.msl\n", read, "is not in the game folder"), "ASCII case matching does not fold non-ASCII names");
            File.CreateSymbolicLink(Path.Combine(game, "Data", "Inc", "inside.msl"), Path.Combine(game, "Data", "Inc", "Defs.MSL"));
            File.CreateSymbolicLink(Path.Combine(game, "Data", "Inc", "out.msl"), Path.Combine(outside, "secret.msl"));
            File.CreateSymbolicLink(Path.Combine(game, "Data", "Inc", "dangling.msl"), Path.Combine(folder, "absent.msl"));
            File.CreateSymbolicLink(Path.Combine(game, "Data", "Inc", "loop.msl"), Path.Combine(game, "Data", "Inc", "loop.msl"));
            Directory.CreateSymbolicLink(Path.Combine(game, "Data", "linkdir"), outside);
            Directory.CreateSymbolicLink(Path.Combine(folder, "selected-game"), game);
            check.That(ScriptCompiler.IncludesFrom(Path.Combine(folder, "selected-game"))("data\\inc\\defs.msl").StartsWith("#define LIMIT", StringComparison.Ordinal),
                "the user-selected game folder itself may be reached through a link");
            check.That(new[] { "inside.msl", "out.msl", "dangling.msl", "loop.msl" }.All(name => Refuses($"#include data\\inc\\{name}\n", read, "is a link or goes through one")) &&
                       Refuses("#include data\\linkdir\\secret.msl\n", read, "is a link or goes through one") &&
                       Refuses("#include data\\linkdir\\..\\inc\\defs.msl\n", read, "is a link or goes through one"),
                "links below the selected folder are refused, including inside, outside, dangling, loop and directory links");
            try { ScriptCompiler.ReadSource(Path.Combine(game, "Data", "Inc", "inside.msl")); check.Fail("a source link was followed"); }
            catch (CompileError error) { check.That(error.Message.Contains("is a link or goes through one", StringComparison.Ordinal), "direct source reads refuse a final link too"); }
        }
        if (OperatingSystem.IsLinux())
        {
            if (!Environment.IsPrivilegedProcess)
            {
                string denied = Path.Combine(game, "Data", "Inc", "Denied.msl"), locked = Path.Combine(game, "Data", "Locked");
                File.WriteAllText(denied, "#define X 1\n");
                Directory.CreateDirectory(locked);
                File.WriteAllText(Path.Combine(locked, "Header.msl"), "#define X 1\n");
                UnixFileMode fileMode = File.GetUnixFileMode(denied), dirMode = File.GetUnixFileMode(locked);
                try
                {
                    File.SetUnixFileMode(denied, UnixFileMode.None);
                    File.SetUnixFileMode(locked, UnixFileMode.None);
                    check.That(Refuses("#include data\\inc\\denied.msl\n", read, "the included file data\\inc\\denied.msl could not be read") &&
                               Refuses("#include data\\locked\\header.msl\n", read, "the included file data\\locked\\header.msl could not be read"),
                        "unreadable files and unlistable folders produce stable refusals without system details");
                }
                finally
                {
                    File.SetUnixFileMode(denied, fileMode);
                    File.SetUnixFileMode(locked, dirMode);
                }
            }
            // A named pipe named like a header would wait for a writer for ever, so it is not opened: the lookup refuses it at once.
            string pipe = Path.Combine(game, "Data", "Inc", "Pipe.msl");
            using (Process make = Process.Start(new ProcessStartInfo("mkfifo", [pipe]) { UseShellExecute = false })!)
            {
                make.WaitForExit();
                check.That(make.ExitCode == 0, $"mkfifo made the named pipe (exit {make.ExitCode})");
            }
            Task<bool> refused = Task.Run(() => Refuses("#include data\\inc\\pipe.msl\n", read, "is not a file inside the game folder"));
            bool returned = refused.Wait(TimeSpan.FromSeconds(10));
            if (!returned)
            {
                using (File.OpenHandle(pipe, FileMode.Open, FileAccess.Write))
                {
                    // let the reader that is stuck on the pipe go, so the run can end
                }
                refused.Wait(TimeSpan.FromSeconds(10));
            }
            check.That(returned && refused.Result, "a named pipe is not a header, and the lookup does not wait for a writer");
        }
        Directory.Delete(folder, true);
    }

    private static void Limits(Checks check)
    {
        const string Vars = "vars\n\tint a;\n\tint r;\nend_vars\ninit()\n{\n";
        string Init(string body) => Vars + body + "\n}\n";
        int limit = CompileLimits.Default.MaxDepth;
        check.That(limit == 100, "the default depth is the reference's");
        Compile(Init(new string('{', limit) + new string('}', limit)));
        check.That(Refuses(Init(new string('{', limit + 1) + new string('}', limit + 1)), "nested more than 100 deep"), "blocks nested exactly at the limit compile and one more is refused with the depth in the message");
        foreach (int count in new[] { 300, 1000, 5000 })
            check.That(Refuses(Init("\tr = " + new string('(', count) + "a" + new string(')', count) + ";"), "nested more than") && Refuses(Init(new string('{', count) + new string('}', count)), "nested more than") &&
                       Refuses(Init("\tr = " + string.Concat(Enumerable.Repeat("Rand(", count)) + "1" + new string(')', count) + ";"), "nested more than") &&
                       Refuses(Init("\tr = " + string.Concat(Enumerable.Repeat("a = ", count)) + "a;"), "nested more than"),
                $"{count} levels of parentheses, blocks, calls or assignments are a compile error, not a stack overflow");
        check.That(Refuses(Init("\tif (a) { } " + string.Concat(Enumerable.Repeat("else if (a) { } ", 1000))), "nested more than"), "a ladder of a thousand else-ifs is nesting too");
        Compile(Init("\tif (a) { } " + string.Concat(Enumerable.Repeat("else if (a) { } ", 40))));
        check.That(Compile(Init(string.Concat(Enumerable.Repeat("\tDie();\n", 300)) + string.Concat(Enumerable.Repeat("\tr = (a + 1) * (a - 1);\n", 300)))).Code.Instructions.Count > 600,
            "statements one after another do not add up to a depth");
        // a define that grows without bound is refused quickly, whether it grows into tokens or into nothing
        foreach (string end in new[] { "1", "" })
        {
            string chain = string.Concat(Enumerable.Range(0, 8).Select(i => $"#define D{i} " + string.Join(' ', Enumerable.Repeat($"D{i + 1}", 10)) + "\n")) + $"#define D8 {end}\n";
            Stopwatch clock = Stopwatch.StartNew();
            check.That(Refuses(chain + Init("\tr = D0;"), "makes the script longer") && clock.Elapsed < TimeSpan.FromSeconds(10), $"a define that grows into {(end.Length == 0 ? "nothing" : "tokens")} is refused quickly: {clock.Elapsed.TotalSeconds:0.0}s");
        }
        const string Nine = "init()\n{\n\tDie();\n}\n";  // nine tokens
        Compile(Nine, limits: new CompileLimits(MaxTokens: 9));
        check.That(Refuses(Nine, "longer than 8 tokens", new CompileLimits(MaxTokens: 8)), "the token limit counts the tokens of the script, at its edge");
        Compile(Nine, limits: new CompileLimits(MaxExpansionSteps: 9));
        check.That(Refuses(Nine, "makes the script longer", new CompileLimits(MaxExpansionSteps: 8)), "the step limit counts the names looked at, at its edge");
        check.That(Refuses(Init("\tDie();"), "nested more than 1 deep", new CompileLimits(MaxDepth: 1)) && Compile(Init("\tDie();"), limits: new CompileLimits(MaxDepth: 2)).Code.Instructions.Count > 0,
            "the depth limit is a parameter: a call statement is a statement inside the handler and an expression inside the statement, two deep");
        Compile("//" + new string('x', ScriptCompiler.MaxSource - 2));
        check.That(Refuses("//" + new string('x', ScriptCompiler.MaxSource - 1), "longer than a million characters") && Refuses("//xxx", "longer than a million characters", new CompileLimits(MaxSource: 4)), "a script of a million characters compiles and one more is refused");
        Compile("//\U0001f600", limits: new CompileLimits(MaxSource: 3));
        check.That(Refuses("//\U0001f600x", "longer than a million characters", new CompileLimits(MaxSource: 3)), "the source limit counts an astral character as one character, not two UTF-16 units");
        Compile("//\ud800", limits: new CompileLimits(MaxSource: 3));
        check.That(Refuses("//\ud800x", "longer than a million characters", new CompileLimits(MaxSource: 3)), "a lone surrogate counts as one character too");

        List<CompileNote> bounded = [];
        Stopwatch groupClock = Stopwatch.StartNew();
        Compile(Init("\tr = " + string.Concat(Enumerable.Repeat("a + ", 12000)) + "a == a;"), notes: bounded);
        check.That(bounded.Any(note => note.Kind == "grouping" && note.Text == "the grouping of this expression is not written out: its text is longer than 5000 characters") &&
                   groupClock.Elapsed < TimeSpan.FromSeconds(15), $"a long mixed chain gets the bounded note and finishes in {groupClock.Elapsed.TotalSeconds:0.0}s");
        List<CompileNote> astralNote = [];
        Compile(Init("\tr = a + a //" + string.Concat(Enumerable.Repeat("\U0001f600", 2490)) + "\n == a;"), notes: astralNote);
        check.That(astralNote.Any(note => note.Kind == "grouping" && note.Text.Contains(" is grouped ", StringComparison.Ordinal)),
            "the grouping-note limit counts astral characters as one, as the reference does");
        check.That(Refuses(Init("\tr = else;"), "'else' is a keyword and cannot be used here") && Refuses("if (1) { }\n", "expected an event handler") && Refuses("vars\n\tint if;\nend_vars\n", "expected a variable name"),
            "keywords are not names");
        string shown = Refused(Init("\tRand(" + new string('9', 400) + ");")).Message;
        check.That(shown.Length < 80, $"the message for a huge integer does not repeat the number: {shown.Length} characters");
        check.That(Refused("init()\n{\n\tDie();\n\tPause();\n}\n") is { Line: 3 } error && error.Message.StartsWith("line 4: ", StringComparison.Ordinal), "an error carries its line, counting from 1 in the message");
    }

    private static void Records(Checks check)
    {
        List<CompileNote> notes = [];
        MissionScript script = Compile("vars\n\tthing t;\n\tfloat h = 0.5;\nend_vars\ninit()\n{\n\tdo_once\n\t{\n\t\tPostEvent(\"x\");\n\t}\n}\nevent(\"y\")\n{\n\tt = GetThingRef(\"z\");\n}\n", doOnceStart: 3, notes: notes);
        WorldBody body = LevelScriptTests.Body(script);
        WorldBody back = WorldBody.Read(body.Write());
        check.That(back.Scripts.Count == 1 && ScriptDump.Lines(back.Scripts[0]).SequenceEqual(ScriptDump.Lines(script)), "a compiled script writes into a world body and reads back as it was");
        check.That(back.Scripts[0].Trailer.SequenceEqual(script.Trailer) && ScriptCatalog.Of(back)[0].Events.SequenceEqual(["init", "event \"y\""]),
            "the written script's trailer is end_script and the Level editor's catalog reads its entry points back");
    }
}
