// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Text;
using OnslaughtToolkit.Companion.Development;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The game's rules for a compiled script, as <see cref="ScriptChecker"/> applies them: what it accepts (the shapes the compiler makes), each rule
/// with a script that breaks that one rule, and the stack followed from every place the game starts a script. The gate checks use only authored
/// temporary archives. Nothing here touches Godot or an installed game.
/// </summary>
internal static class LevelScriptCheckerTests
{
    // The VM's opcodes in the game's order, and the symbols Make gives every script.
    private const int Nop = 0, Plus = 1, Minus = 2, Multiply = 3, Divide = 4, Push = 5, Pop = 6, Or = 7, And = 8, GreatThan = 9, LessThan = 10, GreatEqThan = 11,
        LessEqThan = 12, Label = 13, RemoveTop = 14, Cmp = 15, Cmpb = 16, Cmpneb = 17, Jmpne = 18, Jmpfalse = 19, Jmp = 20, Gettop = 21, Pointer = 22,
        Return = 23, Call = 24, CallLocal = 25, PushPc = 26;

    private const int X = 0, Y = 1, Seven = 2, Text = 3, FunctionName = 4;
    private const int Used = 1 << 16;
    private const int Init = 0, Arrived = 1, Timer = 2, Died = 3, Hit = 4;

    internal static void Run(string output, Checks check)
    {
        check.Suite("level script checker");
        Accepted(check);
        Rules(check);
        Calls(check);
        Stack(check);
        Reported(check);
        Gate(output, check);
    }

    /// <summary>The actual archive gate checks both world bodies, refuses a broken script, and cannot pass without checking any scripts.</summary>
    private static void Gate(string output, Checks check)
    {
        string game = Path.Combine(output, "script-checker-gate");
        string resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        string archive = Path.Combine(resources, "100_res_PC.aya");
        WorldBody world = WorldBody.Read(LevelTests.Body("authored-v50"));
        world.Scripts.Clear();
        world.Scripts.Add(WellFormed("main", [0], []));
        byte[] valid = world.Write();
        world.Scripts[0].Code.Instructions[0] = new ScriptInstruction(99, -1);
        byte[] invalid = world.Write();
        world.Scripts.Clear();
        byte[] empty = world.Write();

        (int Result, string[] Printed, string[] Errors) Run(byte[] baseBody, byte[] realBody)
        {
            File.WriteAllBytes(archive, GateArchive(baseBody, realBody));
            List<string> printed = [], errors = [];
            int result = LevelsGateCheck.Run(game, "", printed.Add, errors.Add);
            return (result, [.. printed], [.. errors]);
        }

        var good = Run(valid, valid);
        check.That(good.Result == 0 && good.Errors.Length == 0 && good.Printed.Single().Contains("2 compiled scripts checked", StringComparison.Ordinal),
            "the archive gate counts and accepts a valid script in each world body");
        var badBase = Run(invalid, valid);
        check.That(badBase.Result == 1 && badBase.Errors.Any(error => error.Contains("100 BSWD", StringComparison.Ordinal) && error.Contains("opcode 99", StringComparison.Ordinal)),
            "the archive gate rejects an invalid script in the base world");
        var badReal = Run(valid, invalid);
        check.That(badReal.Result == 1 && badReal.Errors.Any(error => error.Contains("100 RLWD", StringComparison.Ordinal) && error.Contains("opcode 99", StringComparison.Ordinal)),
            "the archive gate rejects an invalid script in the level's own world");
        var none = Run(empty, empty);
        check.That(none.Result == 1 && none.Errors.Any(error => error.Contains("No compiled scripts", StringComparison.Ordinal)),
            "the archive gate cannot pass with zero scripts checked");
    }

    private static byte[] GateArchive(byte[] baseBody, byte[] realBody)
    {
        static byte[] Chunk(string tag, byte[] contents)
        {
            using MemoryStream stream = new();
            using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);
            writer.Write(Encoding.ASCII.GetBytes(tag));
            writer.Write(contents.Length);
            writer.Write(contents);
            return stream.ToArray();
        }
        using MemoryStream numbers = new();
        using (BinaryWriter writer = new(numbers, Encoding.ASCII, leaveOpen: true)) { writer.Write(200); writer.Write(100); }
        byte[] world = [.. Chunk("WDAT", numbers.ToArray()), .. Chunk("BSWD", baseBody), .. Chunk("RLWD", realBody)];
        byte[] unpacked = Chunk("WRES", Chunk("WRLD", world));
        using MemoryStream member = new();
        using (ZLibStream compressed = new(member, CompressionLevel.Optimal, leaveOpen: true)) compressed.Write(unpacked);
        using MemoryStream archive = new();
        using (BinaryWriter writer = new(archive, Encoding.ASCII, leaveOpen: true)) { writer.Write((int)member.Length); writer.Write(member.ToArray()); }
        return archive.ToArray();
    }

    private static int Native(string name) => Array.FindIndex(ScriptTables.Natives, native => native.Name == name);

    /// <summary>
    /// Like <c>LevelScriptTests.Script</c>, but a program the checker accepts, as the compiler would lay it out: a constant for the calls' one argument
    /// (symbol 0, when there are calls), then the handlers' text symbols; the code is each call as a statement (the constant pushed, the call, its result
    /// dropped), a RETURN, and one block per named handler (a jump over its empty body, a label, a RETURN) that the handler's entry point starts. The fixed
    /// events start at the first instruction, so they can be only the ones that come with no value (not arrived and hit: those start by taking one off).
    /// </summary>
    internal static MissionScript WellFormed(string name, int[] events, string[] handlers, params (string Native, int Times)[] calls)
    {
        if (events.Any(index => index is 1 or 4)) throw new ArgumentException("arrived and hit come with a value, which this builder does not take off", nameof(events));
        MissionScript script = new() { Name = name };
        Array.Fill(script.Code.EventPcs, -1);
        foreach (int index in events) script.Code.EventPcs[index] = 0;
        int argument = -1;
        if (calls.Length > 0)
        {
            argument = script.Code.Symbols.Count;
            script.Code.Symbols.Add(new ScriptSymbol { Name = $"const data{argument}", DataType = 1, Value = new ScriptInt(0), Index = argument, Flag = 1 });
        }
        List<int> texts = [];
        foreach (string handler in handlers)
        {
            int symbol = script.Code.Symbols.Count;
            script.Code.Symbols.Add(new ScriptSymbol { Name = $"const data{symbol}", DataType = 3, Value = new ScriptText(handler), Index = symbol, Flag = 1 });
            texts.Add(symbol);
        }
        foreach ((string native, int times) in calls)
            for (int call = 0; call < times; call++)
            {
                script.Code.Instructions.Add(new ScriptInstruction(Push, argument));
                script.Code.Instructions.Add(new ScriptInstruction(Call, Native(native) | (1 << 8)));
                script.Code.Instructions.Add(new ScriptInstruction(RemoveTop, -1));
            }
        script.Code.Instructions.Add(new ScriptInstruction(Return, -1));
        foreach (int symbol in texts)
        {
            int entry = script.Code.Instructions.Count;
            script.Code.Instructions.Add(new ScriptInstruction(Jmpfalse, entry + 1));
            script.Code.Instructions.Add(new ScriptInstruction(Label, -1));
            script.Code.Instructions.Add(new ScriptInstruction(Return, -1));
            EventFunction function = new() { EntryPc = entry };
            function.Parameters.Add(symbol);
            script.Code.EventFunctions.Add(function);
        }
        script.Code.NextSymbolIndex = script.Code.Symbols.Count;
        return script;
    }

    private static void Add(MissionScript script, string name, int dataType, ScriptValue? value) =>
        script.Code.Symbols.Add(new ScriptSymbol { Name = name, DataType = dataType, Value = value, Index = script.Code.Symbols.Count, Flag = 1 });

    /// <summary>
    /// A script named alpha with five symbols (the variables x and y, the constants 7 and "go", a function's name), the entry points it is given as
    /// (event, instruction) pairs and the code it is given. Its two trailing words are 0.
    /// </summary>
    private static MissionScript Make((int Event, int Pc)[] entries, params (int Opcode, int Attribute)[] code)
    {
        MissionScript script = new() { Name = "alpha" };
        Array.Fill(script.Code.EventPcs, -1);
        foreach ((int index, int pc) in entries) script.Code.EventPcs[index] = pc;
        Add(script, "x", 0, null);
        Add(script, "y", 0, null);
        Add(script, "const data2", 1, new ScriptInt(7));
        Add(script, "const data3", 3, new ScriptText("go"));
        Add(script, "PostEvent", 0, null);
        script.Code.NextSymbolIndex = 5;
        foreach ((int opcode, int attribute) in code) script.Code.Instructions.Add(new ScriptInstruction(opcode, attribute));
        return script;
    }

    /// <summary>A named handler that starts at an instruction and listens for the events named by the given symbols.</summary>
    private static void Handler(MissionScript script, int entry, params int[] symbols)
    {
        EventFunction function = new() { EntryPc = entry };
        function.Parameters.AddRange(symbols);
        script.Code.EventFunctions.Add(function);
    }

    /// <summary>A named handler with a block of its own after the code (it takes the value for each event it names off the stack and returns).</summary>
    private static void HandlerBlock(MissionScript script, params int[] symbols)
    {
        int entry = script.Code.Instructions.Count;
        foreach (int _ in symbols) script.Code.Instructions.Add(new ScriptInstruction(Pop, X));
        script.Code.Instructions.Add(new ScriptInstruction(Return, -1));
        Handler(script, entry, symbols);
    }

    private static string Found(MissionScript script) => string.Join(",", ScriptChecker.Check(script).Select(problem => problem.Rule));

    private static string First(MissionScript script) => ScriptChecker.Check(script) is [{ } problem, ..] ? problem.Message : "no problem";

    private static bool Accepts(MissionScript script) => ScriptChecker.Check(script).Count == 0;

    // ---- what is accepted ------------------------------------------------------------------------------------------------------------
    private static void Accepted(Checks check)
    {
        check.That(Accepts(WellFormed("alpha", [0, 3], ["go"], ("PostEvent", 1), ("Pause", 2))) && Accepts(WellFormed("beta", [], [])),
            "the scripts the tests build for an edit are accepted");

        // The shapes CMissionScript's compiler makes (tools/msl_compile.py), laid out as it lays them out.
        MissionScript vars = Make([(Init, 3)], (Push, Seven), (Pop, X), (Return, -1), (Push, Seven), (Pop, Y), (Return, -1));
        vars.Code.Tail2 = 1;
        MissionScript ifElse = Make([(Init, 0)], (Push, X), (Jmpfalse, 6), (Push, Seven), (Gettop, Y), (RemoveTop, -1), (Jmp, 10), (Label, -1),
            (Push, Seven), (Gettop, Y), (RemoveTop, -1), (Label, -1), (Return, -1));
        MissionScript loop = Make([(Init, 0)], (Push, X), (Jmpfalse, 6), (Push, Seven), (Gettop, X), (RemoveTop, -1), (Jmp, 0), (Label, -1), (Return, -1));
        MissionScript switchCase = Make([(Init, 0)], (Push, X), (Push, Seven), (Cmp, -1), (RemoveTop, -1), (Jmpne, 9), (Push, Seven), (Gettop, Y), (RemoveTop, -1),
            (Jmp, 10), (Label, -1), (Label, -1), (RemoveTop, -1), (Return, -1));
        MissionScript calls = Make([(Init, 0)], (Push, Text), (Call, Native("PostEvent") | (1 << 8)), (RemoveTop, -1), (Push, Text), (Call, Native("PostEvent") | (1 << 8) | Used),
            (Gettop, Y), (RemoveTop, -1), (Push, X), (Pointer, -1), (Push, Text), (Call, Native("PostEvent") | (1 << 8)), (RemoveTop, -1), (Return, -1));
        MissionScript doOnce = Make([(Init, 0)], (Push, X), (Jmpfalse, 6), (Push, Y), (Pop, X), (Push, Seven), (RemoveTop, -1), (Label, -1), (Return, -1));
        MissionScript arrivedAndHit = Make([(Arrived, 0), (Hit, 2)], (Pop, X), (Return, -1), (Pop, Y), (Return, -1));
        MissionScript named = Make([], (Jmpfalse, 1), (Label, -1), (Return, -1), (Pop, X), (Pop, Y), (Return, -1));
        Handler(named, 0, Text);
        Handler(named, 3, Text, Text);
        MissionScript notRaised = Make([(9, 0), (Init, 2)], (RemoveTop, -1), (Return, -1), (Return, -1));
        MissionScript sharedEntry = Make([(Init, 0), (Died, 0), (Timer, 0)], (Nop, -1), (Label, -1), (Return, -1));
        MissionScript noEntry = Make([], (RemoveTop, -1), (Return, -1));
        (string What, MissionScript Script)[] shapes =
        [
            ("a variables block and an init handler after it", vars), ("if with else", ifElse), ("while", loop), ("switch with a case", switchCase),
            ("calls as statements, as an expression and on a thing", calls), ("do_once", doOnce), ("arrived and hit handlers that take their value off", arrivedAndHit),
            ("named handlers that take their event flags off", named), ("code only an event the game never raises starts", notRaised),
            ("three events that start at one instruction", sharedEntry), ("code that nothing starts", noEntry),
        ];
        foreach ((string what, MissionScript script) in shapes) check.That(Accepts(script), $"{what} is accepted: {First(script)}");

        foreach (int op in new[] { Plus, Minus, Multiply, Divide, Or, And, GreatThan, LessThan, GreatEqThan, LessEqThan, Cmpb, Cmpneb })
        {
            MissionScript sum = Make([(Init, 0)], (Push, Seven), (Push, Seven), (op, -1), (Pop, X), (Return, -1));
            check.That(Accepts(sum), $"opcode {op} takes two values and leaves one: {First(sum)}");
        }

        MissionScript full = Make([(Init, 0)], [.. Enumerable.Repeat((Push, X), ScriptChecker.StackSize), .. Enumerable.Repeat((RemoveTop, -1), ScriptChecker.StackSize), (Return, -1)]);
        check.That(Accepts(full), $"a stack of exactly the game's {ScriptChecker.StackSize} values is accepted: {First(full)}");

        MissionScript last = Make([(Init, 1)], (Return, -1), (Return, -1));
        last.Code.EventPcs[12] = 1;
        check.That(Accepts(last), $"an entry point may be the last instruction: {First(last)}");
    }

    // ---- each rule, broken alone -------------------------------------------------------------------------------------------------------
    private static void Rules(Checks check)
    {
        (string What, Action<MissionScript> Break, string Expected)[] cases =
        [
            ("no code", s => { s.Code.Instructions.Clear(); s.Code.EventPcs[0] = -1; }, "empty-code"),
            ("no code but an entry point kept", s => s.Code.Instructions.Clear(), "empty-code,entry-point"),
            ("opcode 27 (the game has 0 to 26)", s => s.Code.Instructions[0] = new ScriptInstruction(27, 0), "opcode"),
            ("opcode 99", s => s.Code.Instructions[0] = new ScriptInstruction(99, 0), "opcode"),
            ("opcode -1", s => s.Code.Instructions[0] = new ScriptInstruction(-1, 0), "opcode"),
            ("opcode int.MinValue", s => s.Code.Instructions[0] = new ScriptInstruction(int.MinValue, 0), "opcode"),
            ("opcode 26 with an instruction to return to", s => s.Code.Instructions[0] = new ScriptInstruction(PushPc, 2), ""),
            ("PUSH of symbol 5 (the table has 5)", s => s.Code.Instructions[0] = new ScriptInstruction(Push, 5), "symbol-operand"),
            ("PUSH of symbol 999", s => s.Code.Instructions[0] = new ScriptInstruction(Push, 999), "symbol-operand"),
            ("PUSH of symbol -1", s => s.Code.Instructions[0] = new ScriptInstruction(Push, -1), "symbol-operand"),
            ("PUSH of symbol int.MinValue", s => s.Code.Instructions[0] = new ScriptInstruction(Push, int.MinValue), "symbol-operand"),
            ("PUSH of the last symbol", s => s.Code.Instructions[0] = new ScriptInstruction(Push, 4), ""),
            ("POP of symbol 5", s => s.Code.Instructions[1] = new ScriptInstruction(Pop, 5), "symbol-operand"),
            ("POP of symbol -1", s => s.Code.Instructions[1] = new ScriptInstruction(Pop, -1), "symbol-operand"),
            ("GETTOP of symbol 5", s => s.Code.Instructions.InsertRange(1, [new ScriptInstruction(Gettop, 5)]), "symbol-operand"),
            ("GETTOP of the last symbol", s => s.Code.Instructions.InsertRange(1, [new ScriptInstruction(Gettop, 4)]), ""),
            ("JMP past the code", s => s.Code.Instructions[0] = new ScriptInstruction(Jmp, 3), "jump-target"),
            ("JMP to instruction 12345", s => s.Code.Instructions[0] = new ScriptInstruction(Jmp, 12345), "jump-target"),
            ("JMP below zero", s => s.Code.Instructions[0] = new ScriptInstruction(Jmp, -1), "jump-target"),
            ("JMP to the last instruction", s => s.Code.Instructions[0] = new ScriptInstruction(Jmp, 2), ""),
            ("JMPFALSE past the code", s => s.Code.Instructions.InsertRange(0, [new ScriptInstruction(Push, X), new ScriptInstruction(Jmpfalse, 5)]), "jump-target"),
            ("JMPFALSE below zero", s => s.Code.Instructions.InsertRange(0, [new ScriptInstruction(Push, X), new ScriptInstruction(Jmpfalse, -2)]), "jump-target"),
            ("JMPFALSE to the last instruction", s => s.Code.Instructions.InsertRange(0, [new ScriptInstruction(Push, X), new ScriptInstruction(Jmpfalse, 4)]), ""),
            ("JMPNE past the code", s => s.Code.Instructions.Insert(0, new ScriptInstruction(Jmpne, 4)), "jump-target"),
            ("JMPNE to the last instruction", s => s.Code.Instructions.Insert(0, new ScriptInstruction(Jmpne, 3)), ""),
            ("CALLLOCAL past the code", s => s.Code.Instructions.Insert(0, new ScriptInstruction(CallLocal, 4)), "jump-target"),
            ("CALLLOCAL to the last instruction", s => s.Code.Instructions.Insert(0, new ScriptInstruction(CallLocal, 3)), ""),
            ("PUSHPC with a return address past the code", s => s.Code.Instructions[0] = new ScriptInstruction(PushPc, 3), "jump-target"),
            ("PUSHPC with a negative return address", s => s.Code.Instructions[0] = new ScriptInstruction(PushPc, -1), "jump-target"),
            ("the entry of init at the code's length", s => s.Code.EventPcs[Init] = 3, "entry-point"),
            ("the entry of init at 777", s => s.Code.EventPcs[Init] = 777, "entry-point"),
            ("the entry of init at -2", s => s.Code.EventPcs[Init] = -2, "entry-point"),
            ("the entry of init at int.MinValue", s => s.Code.EventPcs[Init] = int.MinValue, "entry-point"),
            ("the entry of init on the last instruction", s => s.Code.EventPcs[Init] = 2, ""),
            ("the entry of the 13th event at 99", s => s.Code.EventPcs[12] = 99, "entry-point"),
            ("the entry of the 9th event at -5", s => s.Code.EventPcs[8] = -5, "entry-point"),
            ("12 entry points", s => s.Code.EventPcs = [.. Enumerable.Repeat(-1, 12)], "entry-point"),
            ("14 entry points", s => s.Code.EventPcs = [.. Enumerable.Repeat(-1, 14)], "entry-point"),
            ("no entry points at all", s => s.Code.EventPcs = null!, "entry-point"),
            ("a handler starting past the code", s => Handler(s, 3, Text), "handler-entry"),
            ("a handler starting at -5", s => Handler(s, -5, Text), "handler-entry"),
            ("a handler starting at int.MinValue", s => Handler(s, int.MinValue, Text), "handler-entry"),
            ("a handler whose event symbol is the symbol count", s => HandlerBlock(s, 5), "handler-parameter"),
            ("a handler whose event symbol is 42", s => HandlerBlock(s, 42), "handler-parameter"),
            ("a handler whose event symbol is -1", s => HandlerBlock(s, -1), "handler-parameter"),
            ("a handler whose event symbol is a variable", s => HandlerBlock(s, X), "handler-parameter"),
            ("a handler whose event symbol is a number", s => HandlerBlock(s, Seven), "handler-parameter"),
            ("a handler whose event symbol is text with no value", s =>
            {
                s.Code.Symbols[Text].Value = null;
                HandlerBlock(s, Text);
            }, "handler-parameter"),
            ("a handler whose event symbol has a text value but not the text type", s =>
            {
                s.Code.Symbols[Text].DataType = 1;
                HandlerBlock(s, Text);
            }, "handler-parameter"),
            ("a handler whose event symbols are text, then a number", s => HandlerBlock(s, Text, Seven), "handler-parameter"),
            ("a handler whose event symbols are all text", s => HandlerBlock(s, Text, Text, Text), ""),
            ("a handler that listens for nothing", s => HandlerBlock(s), ""),
            ("a symbol numbered 7 in its own record", s => s.Code.Symbols[2].Index = 7, "symbol-index"),
            ("a symbol numbered -1", s => s.Code.Symbols[0].Index = -1, "symbol-index"),
            ("a symbol numbered one more than its place", s => s.Code.Symbols[4].Index = 5, "symbol-index"),
            ("two symbols with one name", s => s.Code.Symbols[1].Name = "x", "symbol-name"),
            ("the first and the last symbol with one name", s => s.Code.Symbols[4].Name = "x", "symbol-name"),
            ("names that differ in letter case", s => s.Code.Symbols[1].Name = "X", ""),
            ("a next symbol number above the count", s => s.Code.NextSymbolIndex = 6, "next-symbol-index"),
            ("a next symbol number 50", s => s.Code.NextSymbolIndex = 50, "next-symbol-index"),
            ("a next symbol number below the count", s => s.Code.NextSymbolIndex = 4, "next-symbol-index"),
            ("a next symbol number 0", s => s.Code.NextSymbolIndex = 0, "next-symbol-index"),
            ("a next symbol number -1", s => s.Code.NextSymbolIndex = -1, "next-symbol-index"),
        ];
        foreach ((string what, Action<MissionScript> doBreak, string expected) in cases)
        {
            // init(): PUSH 7; POP x; RETURN, from instruction 0
            MissionScript script = Make([(Init, 0)], (Push, Seven), (Pop, X), (Return, -1));
            doBreak(script);
            string found = Found(script);
            check.That(found == expected, $"{what}: the rules that find it are [{found}], expected [{expected}]: {First(script)}");
        }

        MissionScript tenEvents = Make([], (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Return, -1));
        Handler(tenEvents, 0, Enumerable.Repeat(Text, ScriptChecker.MaxHandlerEvents).ToArray());
        MissionScript elevenEvents = Make([], (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Pop, X), (Return, -1));
        Handler(elevenEvents, 0, Enumerable.Repeat(Text, ScriptChecker.MaxHandlerEvents + 1).ToArray());
        check.That(Accepts(tenEvents) && Found(elevenEvents) == "handler-parameter",
            $"a handler listens for at most 10 events (the argument array of the game's call to it): ten [{Found(tenEvents)}], eleven [{Found(elevenEvents)}]");

        MissionScript twice = Make([(Init, 0)], (Push, Seven), (Pop, X), (Return, -1));
        twice.Code.Symbols[1].Name = "x";
        twice.Code.Symbols[3].Name = "x";
        twice.Code.Symbols[4].Name = "x";
        ScriptProblem[] named = [.. ScriptChecker.Check(twice)];
        check.That(named.Length == 3 && named.All(problem => problem.Rule == "symbol-name") && named[0].Message.Contains("symbols 0 and 1", StringComparison.Ordinal) &&
                   named[1].Message.Contains("symbols 0 and 3", StringComparison.Ordinal) && named[2].Message.Contains("symbols 0 and 4", StringComparison.Ordinal),
            $"every symbol after the first with a name is a problem of its own, said with both places: {string.Join(" | ", named.Select(problem => problem.Message))}");

        MissionScript wrongEntry = Make([(Init, 0)], (Push, Seven), (Pop, X), (Return, -1));
        wrongEntry.Code.EventPcs[12] = 99;
        wrongEntry.Code.EventPcs[0] = 55;
        ScriptProblem[] entries = [.. ScriptChecker.Check(wrongEntry)];
        check.That(entries.Length == 2 && entries[0].Message.Contains("\"init\"", StringComparison.Ordinal) && entries[0].Message.Contains("instruction 55", StringComparison.Ordinal) &&
                   entries[1].Message.Contains("\"notdefined8\"", StringComparison.Ordinal) && entries[1].Message.Contains("instruction 99", StringComparison.Ordinal),
            $"an entry point out of range is said with the event's name and the instruction: {string.Join(" | ", entries.Select(problem => problem.Message))}");
    }

    // ---- a CALL, against every function the game has ----------------------------------------------------------------------------
    private static void Calls(Checks check)
    {
        int wrongCounts = 0, rightCounts = 0, goodMessages = 0;
        for (int function = 0; function < ScriptTables.Natives.Length; function++)
        {
            int declared = ScriptTables.Natives[function].Parameters.Length;
            // n values pushed, the call that takes n, its result dropped
            MissionScript right = Make([(Init, 0)], [.. Enumerable.Repeat((Push, X), declared), (Call, function | (declared << 8)), (RemoveTop, -1), (Return, -1)]);
            MissionScript used = Make([(Init, 0)], [.. Enumerable.Repeat((Push, X), declared), (Call, function | (declared << 8) | Used), (RemoveTop, -1), (Return, -1)]);
            if (Accepts(right) && Accepts(used)) rightCounts++;
            foreach (int count in new[] { declared + 1, declared == 0 ? 2 : declared - 1 })
            {
                MissionScript wrong = Make([(Init, 0)], [.. Enumerable.Repeat((Push, X), count), (Call, function | (count << 8)), (RemoveTop, -1), (Return, -1)]);
                ScriptProblem[] problems = [.. ScriptChecker.Check(wrong)];
                if (problems.Length == 1 && problems[0].Rule == "call-arguments") wrongCounts++;
                if (problems.Length == 1 && problems[0].Message.Contains(ScriptTables.Natives[function].Name, StringComparison.Ordinal) &&
                    problems[0].Message.Contains($"with {count} argument", StringComparison.Ordinal) && problems[0].Message.Contains($"it takes {declared}", StringComparison.Ordinal)) goodMessages++;
            }
        }
        int natives = ScriptTables.Natives.Length;
        check.That(rightCounts == natives, $"a call with the declared number of arguments is accepted for every one of the game's {natives} functions, with the result used or not: {rightCounts}");
        check.That(wrongCounts == 2 * natives, $"and a call with one argument more, or one fewer, is refused for each of them with that one problem: {wrongCounts} of {2 * natives}");
        check.That(goodMessages == 2 * natives, $"saying which function, how many arguments it got and how many it takes: {goodMessages} of {2 * natives}");

        int postEvent = Native("PostEvent");
        (string What, int Attribute, string Expected)[] attributes =
        [
            ("function number past the table", natives | (1 << 8), "call-function"),
            ("function number 255", 255 | (1 << 8), "call-function"),
            ("function number 250 with its result used", 250 | (1 << 8) | Used, "call-function"),
            ("a bit above the result flag", postEvent | (1 << 8) | (1 << 17), "call-attribute"),
            ("the top bit", postEvent | (1 << 8) | int.MinValue, "call-attribute"),
            ("every bit above the argument count", postEvent | (1 << 8) | unchecked((int)0xFFFE0000), "call-attribute"),
            ("a negative attribute", -1, "call-attribute,call-function,stack"),
            ("the result flag alone set", postEvent | (1 << 8) | Used, ""),
            ("no flag set", postEvent | (1 << 8), ""),
        ];
        foreach ((string what, int attribute, string expected) in attributes)
        {
            MissionScript script = Make([(Init, 0)], (Push, X), (Call, attribute), (RemoveTop, -1), (Return, -1));
            string found = Found(script);
            check.That(found == expected, $"{what}: the rules that find it are [{found}], expected [{expected}]");
        }
    }

    // ---- the stack ---------------------------------------------------------------------------------------------------------------------
    private static void Stack(Checks check)
    {
        int followWaypoint = Native("FollowWaypoint");  // takes two
        (string What, MissionScript Script, string Expected, string Said)[] cases =
        [
            ("a value taken off an empty stack", Make([(Init, 0)], (RemoveTop, -1), (Return, -1)), "stack", "instruction 0 (REMOVE_TOP) takes 1 value off the stack, but none is there"),
            ("POP of an empty stack", Make([(Init, 0)], (Pop, X), (Return, -1)), "stack", "instruction 0 (POP) takes 1 value off the stack, but none is there"),
            ("POINTER of an empty stack", Make([(Init, 0)], (Pointer, -1), (Return, -1)), "stack", "(POINTER)"),
            ("JMPFALSE of an empty stack", Make([(Init, 0)], (Jmpfalse, 1), (Return, -1)), "stack", "(JMPFALSE) takes 1 value off the stack"),
            ("a binary operator with one value", Make([(Init, 0)], (Push, X), (Plus, -1), (Pop, X), (Return, -1)), "stack", "instruction 1 (PLUS) takes 2 values off the stack, but only 1 is there"),
            ("a comparison with none", Make([(Init, 0)], (Cmpneb, -1), (Return, -1)), "stack", "(CMPNEB) takes 2 values off the stack, but none is there"),
            ("CMP with one value", Make([(Init, 0)], (Push, X), (Cmp, -1), (RemoveTop, -1), (Return, -1)), "stack", "instruction 1 (CMP) takes 2 values off the stack, but only 1 is there"),
            ("GETTOP of an empty stack", Make([(Init, 0)], (Gettop, X), (Return, -1)), "stack", "(GETTOP) takes 1 value off the stack, but none is there"),
            ("a call that takes two with one pushed", Make([(Init, 0)], (Push, Text), (Call, followWaypoint | (2 << 8)), (RemoveTop, -1), (Return, -1)), "stack", "(CALL) takes 2 values off the stack, but only 1 is there"),
            ("a value left at the return", Make([(Init, 0)], (Push, Seven), (Return, -1)), "stack", "instruction 1 (RETURN) is reached with 1 value on the stack"),
            ("two values left at the return", Make([(Init, 0)], (Push, Seven), (Push, Seven), (Return, -1)), "stack", "is reached with 2 values on the stack"),
            ("a call whose result is not dropped", Make([(Init, 0)], (Push, Text), (Call, Native("PostEvent") | (1 << 8) | Used), (Return, -1)), "stack", "(RETURN) is reached with 1 value"),
            ("a branch that leaves a value", Make([(Init, 0)], (Push, X), (Jmpfalse, 4), (Push, Seven), (Nop, -1), (Label, -1), (Return, -1)), "stack", "by one path"),
            ("a loop that pushes each time round", Make([(Init, 0)], (Push, X), (Jmp, 0)), "stack", "instruction 0 (PUSH) is reached with 0 values on the stack by one path and 1 value by another"),
            ("a code that runs off its end", Make([(Init, 0)], (Push, Seven), (RemoveTop, -1)), "stack", "instruction 1 (REMOVE_TOP) is the last instruction and does not return"),
            ("a conditional jump that is the last instruction", Make([(Init, 0)], (Push, X), (Jmpfalse, 0)), "stack", "(JMPFALSE) is the last instruction and does not return"),
            ("one more value than the stack holds", Make([(Init, 0)], [.. Enumerable.Repeat((Push, X), ScriptChecker.StackSize + 1), (Return, -1)]), "stack", $"instruction {ScriptChecker.StackSize} (PUSH) makes the stack hold more than the game's {ScriptChecker.StackSize} values"),
            ("code after a return that nothing starts is not followed", Make([(Init, 0)], (Return, -1), (Pop, X), (Return, -1)), "", ""),
            ("one of two returns that is not empty", Make([(Init, 0)], (Push, X), (Jmpfalse, 5), (Push, X), (Push, X), (Return, -1), (Return, -1)), "stack", "instruction 4 (RETURN) is reached with 2 values"),
        ];
        foreach ((string what, MissionScript script, string expected, string said) in cases)
        {
            string found = Found(script);
            bool fits = found == expected && (said.Length == 0 || ScriptChecker.Check(script).Any(problem => problem.Message.Contains(said, StringComparison.Ordinal)));
            check.That(fits, $"{what}: the rules that find it are [{found}], expected [{expected}]: {First(script)}");
        }

        // The events the game raises start with a value on the stack or none: arrived and hit one, the others none; the last five are never raised.
        for (int index = 0; index < 13; index++)
        {
            bool takesValue = index is Arrived or Hit, raised = index < 8;
            MissionScript takes = Make([(index, 0)], (Pop, X), (Return, -1)), ignores = Make([(index, 0)], (Return, -1));
            string withPop = Found(takes), without = Found(ignores);
            check.That(withPop == (!raised || takesValue ? "" : "stack") && without == (!raised || !takesValue ? "" : "stack"),
                $"event {index} ({ScriptTables.EventNames[index]}): [{(raised ? takesValue ? "arrives with a value" : "arrives with none" : "never raised")}] a handler that takes a value off gives [{withPop}], one that does not gives [{without}]");
        }

        // A named handler starts with one value for each event it listens for.
        for (int events = 0; events <= 3; events++)
        {
            MissionScript takes = Make([], [.. Enumerable.Repeat((Pop, X), events), (Return, -1)]), ignores = Make([], (Return, -1));
            Handler(takes, 0, Enumerable.Repeat(Text, events).ToArray());
            Handler(ignores, 0, Enumerable.Repeat(Text, events).ToArray());
            check.That(Accepts(takes) && Found(ignores) == (events == 0 ? "" : "stack"),
                $"a named handler of {events} event(s) starts with {events} value(s): one that takes them off [{Found(takes)}], one that does not [{Found(ignores)}]");
        }

        // The variables' block runs from the first instruction when the second trailing word is set (CVM::CallEvent), with the stack empty.
        MissionScript block = Make([], (Push, Seven), (Return, -1));
        MissionScript blockSet = Make([], (Push, Seven), (Return, -1));
        blockSet.Code.Tail2 = 1;
        MissionScript blockAndArrived = Make([(Arrived, 0)], (Pop, X), (Return, -1));
        blockAndArrived.Code.Tail2 = 1;
        MissionScript blockAndInit = Make([(Init, 0)], (Return, -1));
        blockAndInit.Code.Tail2 = 1;
        MissionScript firstWord = Make([], (Push, Seven), (Return, -1));
        firstWord.Code.Tail1 = 1;
        check.That(Accepts(block) && Found(blockSet) == "stack" && Found(blockAndArrived) == "stack" && Accepts(blockAndInit) && Accepts(firstWord),
            $"the first instruction is a start when the second trailing word is not 0, with no value on the stack (a block alone [{Found(block)}], with the word [{Found(blockSet)}], also an arrived handler [{Found(blockAndArrived)}], also init [{Found(blockAndInit)}], the first word [{Found(firstWord)}])");
        blockSet.Code.Tail2 = -1;
        check.That(Found(blockSet) == "stack", "any second trailing word that is not 0 sets it");

        // Local calls (no script of the game has one): the stack is not followed, everything else is.
        MissionScript local = Make([(Init, 0)], (PushPc, 1), (RemoveTop, -1), (RemoveTop, -1), (Return, -1));
        MissionScript localTarget = Make([(Init, 0)], (CallLocal, 9), (Return, -1));
        MissionScript localAndSymbol = Make([(Init, 0)], (PushPc, 1), (Push, 99), (Return, -1));
        check.That(Accepts(local) && Found(localTarget) == "jump-target" && Found(localAndSymbol) == "symbol-operand",
            $"a script with a local call is checked for its operands, entry points and symbols, not for its stack: [{Found(local)}] [{Found(localTarget)}] [{Found(localAndSymbol)}]");

        // An invalid opcode ends the path it is on (what comes after it cannot be known); the opcode is the finding.
        MissionScript endsPath = Make([(Init, 0)], (Push, X), (99, 0), (RemoveTop, -1), (RemoveTop, -1), (Return, -1));
        check.That(Found(endsPath) == "opcode", $"an invalid opcode ends the stack's path, and is the one finding: [{Found(endsPath)}]");
    }

    // ---- what is said, and that nothing is changed -----------------------------------------------------------------------------------
    private static void Reported(Checks check)
    {
        MissionScript many = Make([(Init, 0)], [.. Enumerable.Repeat((Jmp, 999), ScriptChecker.MaxProblems + 30), (Return, -1)]);
        ScriptProblem[] list = [.. ScriptChecker.Check(many)];
        check.That(list.Length == ScriptChecker.MaxProblems + 1 && list.Take(ScriptChecker.MaxProblems).All(problem => problem.Rule == "jump-target") && list[^1].Rule == "more" &&
                   list[^1].Message.Contains("and 30 more problems", StringComparison.Ordinal) && list[^1].Message.StartsWith("Script alpha:", StringComparison.Ordinal),
            $"at most {ScriptChecker.MaxProblems} problems are listed, then a line says how many more there were: {list.Length} lines, the last: {list[^1].Message}");
        MissionScript exactly = Make([(Init, 0)], [.. Enumerable.Repeat((Jmp, 999), ScriptChecker.MaxProblems), (Return, -1)]);
        check.That(ScriptChecker.Check(exactly).Count == ScriptChecker.MaxProblems && ScriptChecker.Check(exactly).All(problem => problem.Rule == "jump-target"), "exactly that many are all listed, with no line after them");

        MissionScript script = Make([(Init, 0)], (Push, Seven), (Push, 99), (Jmp, 40), (Pop, X), (Return, -1));
        script.Name = "hive";
        byte[] before = WorldBodyWriter.ScriptBytes(script);
        ScriptProblem[] problems = [.. ScriptChecker.Check(script)];
        check.That(problems.Length >= 2 && problems.All(problem => problem.Message.StartsWith("Script hive: ", StringComparison.Ordinal)) &&
                   problems.Any(problem => problem is { Rule: "symbol-operand" } && problem.Message.Contains("instruction 1 (PUSH) names symbol 99, but the script has 5 symbols", StringComparison.Ordinal)) &&
                   problems.Any(problem => problem is { Rule: "jump-target" } && problem.Message.Contains("instruction 2 (JMP) points at instruction 40, but the script has 5 instructions", StringComparison.Ordinal)),
            $"each problem names the script, says what is wrong and says where: {string.Join(" | ", problems.Select(problem => problem.Message))}");
        check.That(WorldBodyWriter.ScriptBytes(script).AsSpan().SequenceEqual(before) && ScriptChecker.Check(script).Select(problem => problem.Message).SequenceEqual(problems.Select(problem => problem.Message)),
            "checking changes nothing in the script, and asking again gives the same answer");

        MissionScript one = Make([(Init, 0)], (Push, 99), (Pop, X), (Return, -1));
        one.Code.Symbols.RemoveRange(1, 4);
        one.Code.NextSymbolIndex = 1;
        check.That(First(one).Contains("the script has 1 symbol.", StringComparison.Ordinal), $"one is said in the singular: {First(one)}");
        check.That(ScriptChecker.Check(Make([(Init, 0)], (Return, -1))).Count == 0 && ThrowsNull(() => ScriptChecker.Check(null!)), "a script with nothing wrong has no problem list; there is no script to check for null");
    }

    private static bool ThrowsNull(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (ArgumentNullException)
        {
            return true;
        }
    }
}
