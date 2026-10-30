// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>One thing wrong with a compiled script, said so that it can be found: which script, what is wrong and where.</summary>
/// <param name="Rule">Which rule found it, in one word (<c>opcode</c>, <c>jump-target</c>, <c>stack</c> and so on), for a caller that counts or sorts.</param>
/// <param name="Message">A sentence that names the script, says what is wrong and says where (an instruction, an entry point, a symbol).</param>
public sealed record ScriptProblem(string Rule, string Message);

/// <summary>
/// The game's own rules for a compiled mission script, applied to it before anything is saved. The game runs a script without checking it (a bad
/// operand, a jump past the code or an empty stack is read as it stands, and the level hangs or crashes), so this is the one place the mistakes are
/// found. It only reads: nothing here touches a file, a body or the script.
/// <para>
/// What is checked, with the part of the game each rule comes from (named, never quoted):
/// </para>
/// <list type="bullet">
/// <item>the code is not empty (<c>CVM::Run</c> reads the instruction at the program counter before it runs anything);</item>
/// <item>every opcode is one of the game's 27, 0 to 26 (<c>CAsmInstruction::Spawn</c>);</item>
/// <item>PUSH, POP and GETTOP name a symbol that is in the table (<c>CSymbolTable::GetSymbol</c> does not check its argument);</item>
/// <item>JMP, JMPFALSE, JMPNE, CALLLOCAL and PUSHPC name an instruction that is in the code (<c>CVM::Run</c> reads the instruction at the new
/// program counter without a check);</item>
/// <item>CALL names a function of the game's table (<c>gScriptFunctions</c>, here <see cref="ScriptTables.Natives"/>), passes as many arguments as
/// that function takes, and sets no bit beyond the function number (the low byte), the argument count (the next byte) and the result flag (bit 16)
/// (<c>CInstructionOP_CALL::Execute</c>);</item>
/// <item>each of the 13 event entry points is -1 (no handler) or an instruction (<c>CVM::CallEvent</c>);</item>
/// <item>each named handler starts at an instruction, listens for at most 10 events (the argument array of <c>CEventFunction::Execute</c>), and
/// names each event by a symbol of the table that holds text (<c>CEventFunction</c>'s file constructor);</item>
/// <item>no two symbols have one name, and each symbol's own number is its place in the table (<c>CSymbolTable::Clone</c> copies a symbol only if no
/// symbol of that name is there yet and numbers the copies by their place: a duplicate moves every symbol after it);</item>
/// <item>the next symbol number is the number of symbols (<c>CSymbolTable</c>'s file constructor reads it; every shipped script has it so);</item>
/// <item>the stack: from each place the game starts running a script, every path keeps the stack at one height from instruction to instruction, takes
/// no more values off than it holds (<c>CDataStack::Pop</c>, <c>RemoveTop</c> and <c>GetTop</c>), never holds more than the stack does (128,
/// <c>MAX_STACK_SIZE</c>), and meets each RETURN with the stack empty (<c>CVM::Run</c> reports any other height when a run ends). The game starts at
/// the entry point of each of the events it raises (the first eight: <c>arrived</c> and <c>hit</c> come with one value on the stack, the rest with
/// none: <c>IScript::Arrived</c>, <c>IScript::Hit</c>), at each named handler (with one value per event it names: <c>CEventFunction::Execute</c>)
/// and, when the second trailing word is not 0, at the first instruction (the variables' block, which <c>CVM::CallEvent</c> runs once). No path may
/// run on past the last instruction.</item>
/// </list>
/// <para>
/// What is not checked, and why: the types of a call's arguments and of the values the operators meet (known only by running the script); whether
/// a call whose result flag is set is to a function that returns a value (the Toolkit's table of the game's functions has their arguments but not
/// their return types); the stack of a script that uses the VM's local calls (CALLLOCAL and PUSHPC: no script of the game uses them, and following a
/// return address is not a simple flow), which is checked for everything else; that a script ends (the VM stops a run after 10,000 instructions);
/// and what a script's literal arguments name (a unit, a thing, a text) in the level. At most <see cref="MaxProblems"/> problems of a script are
/// returned, with a last line saying how many more there were.
/// </para>
/// <para>
/// The oracle for all of it is the game's own scripts: every script of every world body of an installed game passes with no problem
/// (<c>Development/LevelsGateCheck.cs</c>).
/// </para>
/// </summary>
public static class ScriptChecker
{
    /// <summary>The most problems <see cref="Check"/> lists for one script; a last line says how many more there were.</summary>
    public const int MaxProblems = 20;

    /// <summary>The game's value stack holds this many values (<c>MAX_STACK_SIZE</c>).</summary>
    public const int StackSize = 128;

    /// <summary>A named handler's call holds this many event names (the argument array of <c>CEventFunction::Execute</c>).</summary>
    public const int MaxHandlerEvents = 10;

    /// <summary>The game raises the first eight of a script's 13 events (<c>EScriptEvent</c>); it never calls the last five.</summary>
    private const int RaisedEvents = 8;

    /// <summary>The events that come with one value on the stack: arrived (1) and hit (4). The others the game raises come with none.</summary>
    private const int ArrivedEvent = 1, HitEvent = 4;

    // The VM's opcodes in the game's order (CAsmInstruction::Spawn's switch; the names are the decompilation's, without their OP_).
    private const int OpPlus = 1, OpMinus = 2, OpMultiply = 3, OpDivide = 4, OpPush = 5, OpPop = 6, OpOr = 7, OpAnd = 8, OpGreatThan = 9, OpLessThan = 10,
        OpGreatEqThan = 11, OpLessEqThan = 12, OpRemoveTop = 14, OpCmp = 15, OpCmpb = 16, OpCmpneb = 17, OpJmpne = 18, OpJmpfalse = 19, OpJmp = 20,
        OpGettop = 21, OpPointer = 22, OpReturn = 23, OpCall = 24, OpCallLocal = 25, OpPushPc = 26;

    private static readonly string[] OpcodeNames =
    [
        "NOP", "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "PUSH", "POP", "OR", "AND", "GREAT_THAN", "LESS_THAN", "GREAT_EQ_THAN", "LESS_EQ_THAN", "LABEL",
        "REMOVE_TOP", "CMP", "CMPB", "CMPNEB", "JMPNE", "JMPFALSE", "JMP", "GETTOP", "POINTER", "RETURN", "CALL", "CALLLOCAL", "PUSHPC",
    ];

    /// <summary>The problems a compiled script has under the game's rules (see <see cref="ScriptChecker"/>); empty when it has none.</summary>
    public static IReadOnlyList<ScriptProblem> Check(MissionScript script)
    {
        ArgumentNullException.ThrowIfNull(script);
        Problems problems = new(script.Name);
        ScriptCode code = script.Code;
        if (code.Instructions.Count == 0)
            problems.Add("empty-code", "it has no instructions, but the game reads the instruction at the program counter before it runs anything.");
        CheckEntryPoints(code, problems);
        CheckHandlers(code, problems);
        CheckSymbols(code, problems);
        CheckInstructions(code, problems);
        CheckStack(code, problems);
        return problems.Done();
    }

    private static void CheckEntryPoints(ScriptCode code, Problems problems)
    {
        int[]? entries = code.EventPcs;
        if (entries is null || entries.Length != ScriptCode.EventCount)
            problems.Add("entry-point", $"it has {(entries is null ? "no" : entries.Length.ToString())} event entry points, but the game reads {ScriptCode.EventCount}.");
        for (int index = 0; entries is not null && index < entries.Length; index++)
            if (entries[index] != -1 && !Lands(entries[index], code.Instructions.Count))
                problems.Add("entry-point", $"the entry point of the {EventName(index)} event is instruction {entries[index]}, but it must be -1 (no handler) or one of its {Count(code.Instructions.Count, "instruction")}.");
    }

    private static void CheckHandlers(ScriptCode code, Problems problems)
    {
        for (int number = 0; number < code.EventFunctions.Count; number++)
        {
            EventFunction handler = code.EventFunctions[number];
            string who = $"named handler {number + 1}";
            if (!Lands(handler.EntryPc, code.Instructions.Count))
                problems.Add("handler-entry", $"{who} starts at instruction {handler.EntryPc}, but the script has {Count(code.Instructions.Count, "instruction")}.");
            if (handler.Parameters.Count > MaxHandlerEvents)
                problems.Add("handler-parameter", $"{who} listens for {handler.Parameters.Count} events, but the game's call to a handler holds {MaxHandlerEvents}.");
            for (int parameter = 0; parameter < handler.Parameters.Count; parameter++)
            {
                int symbol = handler.Parameters[parameter];
                if (!Lands(symbol, code.Symbols.Count))
                    problems.Add("handler-parameter", $"{who} names event {parameter + 1} by symbol {symbol}, but the script has {Count(code.Symbols.Count, "symbol")}.");
                else if (code.Symbols[symbol] is not { DataType: 3, Value: ScriptText })
                    problems.Add("handler-parameter", $"{who} names event {parameter + 1} by symbol {symbol}, which does not hold text.");
            }
        }
    }

    private static void CheckSymbols(ScriptCode code, Problems problems)
    {
        Dictionary<string, int> first = new(StringComparer.Ordinal);
        for (int place = 0; place < code.Symbols.Count; place++)
        {
            ScriptSymbol symbol = code.Symbols[place];
            if (!first.TryAdd(symbol.Name, place))
                problems.Add("symbol-name", $"symbols {first[symbol.Name]} and {place} are both named \"{symbol.Name}\"; the game keeps the first of two symbols with one name, so every symbol after it would move up a place.");
            if (symbol.Index != place)
                problems.Add("symbol-index", $"symbol {place} (\"{symbol.Name}\") is numbered {symbol.Index} in its own record; the game numbers a symbol by its place in the table, so it must say {place}.");
        }
        if (code.NextSymbolIndex != code.Symbols.Count)
            problems.Add("next-symbol-index", $"it says its next symbol number is {code.NextSymbolIndex}, but it has {Count(code.Symbols.Count, "symbol")}.");
    }

    private static void CheckInstructions(ScriptCode code, Problems problems)
    {
        int instructions = code.Instructions.Count, symbols = code.Symbols.Count;
        for (int pc = 0; pc < instructions; pc++)
        {
            (int opcode, int attribute) = code.Instructions[pc];
            if (opcode is < 0 or >= 27)
            {
                problems.Add("opcode", $"instruction {pc} has opcode {opcode}, but the game's opcodes are 0 to 26.");
                continue;
            }
            string at = $"instruction {pc} ({OpcodeNames[opcode]})";
            switch (opcode)
            {
                case OpPush or OpPop or OpGettop when !Lands(attribute, symbols):
                    problems.Add("symbol-operand", $"{at} names symbol {attribute}, but the script has {Count(symbols, "symbol")}.");
                    break;
                case OpJmp or OpJmpfalse or OpJmpne or OpCallLocal or OpPushPc when !Lands(attribute, instructions):
                    problems.Add("jump-target", $"{at} points at instruction {attribute}, but the script has {Count(instructions, "instruction")}.");
                    break;
                case OpCall:
                    CheckCall(at, attribute, problems);
                    break;
            }
        }
    }

    /// <summary>A CALL's attribute: the function in the low byte, the number of arguments in the next, the result flag in bit 16 and nothing above.</summary>
    private static void CheckCall(string at, int attribute, Problems problems)
    {
        int function = attribute & 0xFF, arguments = Arguments(attribute);
        if ((attribute & ~0x1FFFF) != 0)
            problems.Add("call-attribute", $"{at} has bits set beyond the function number, the argument count and the result flag (0x{attribute:x8}).");
        if (function >= ScriptTables.Natives.Length)
            problems.Add("call-function", $"{at} calls function {function}, but the game has {ScriptTables.Natives.Length} functions.");
        else if (arguments != ScriptTables.Natives[function].Parameters.Length)
            problems.Add("call-arguments", $"{at} calls {ScriptTables.Natives[function].Name} with {Count(arguments, "argument")}, but it takes {ScriptTables.Natives[function].Parameters.Length}.");
    }

    /// <summary>
    /// The stack's height at each instruction (before it runs), followed from every place the game starts running a script along every path of the
    /// code. An instruction's effect is the one the game's <c>Execute</c> for its opcode has.
    /// </summary>
    private static void CheckStack(ScriptCode code, Problems problems)
    {
        List<ScriptInstruction> instructions = code.Instructions;
        int count = instructions.Count;
        if (count == 0 || instructions.Any(instruction => instruction.Opcode is OpCallLocal or OpPushPc)) return;

        int[] height = new int[count];
        Array.Fill(height, -1);
        Stack<int> work = new();

        void Reach(int pc, int depth)
        {
            if (!Lands(pc, count)) return;  // a target outside the code is the jump rule's finding, not the stack's
            if (height[pc] < 0)
            {
                height[pc] = depth;
                work.Push(pc);
            }
            else if (height[pc] != depth)
                problems.Add("stack", $"instruction {pc} ({NameOf(instructions[pc])}) is reached with {Count(height[pc], "value")} on the stack by one path and {Count(depth, "value")} by another.");
        }

        // The places the game starts: the events it raises, the named handlers and the variables' block.
        int[]? entries = code.EventPcs;
        for (int index = 0; entries is not null && index < Math.Min(RaisedEvents, entries.Length); index++)
            if (entries[index] != -1) Reach(entries[index], index is ArrivedEvent or HitEvent ? 1 : 0);
        foreach (EventFunction handler in code.EventFunctions) Reach(handler.EntryPc, handler.Parameters.Count);
        if (code.Tail2 != 0) Reach(0, 0);

        while (work.Count > 0)
        {
            int pc = work.Pop(), depth = height[pc];
            (int opcode, int attribute) = instructions[pc];
            if (opcode is < 0 or >= 27) continue;  // the opcode rule's finding
            string at = $"instruction {pc} ({OpcodeNames[opcode]})";
            if (opcode == OpReturn)
            {
                if (depth != 0)
                    problems.Add("stack", $"{at} is reached with {Count(depth, "value")} on the stack, but the game expects the stack empty when a handler returns.");
                continue;
            }
            (int needs, int change) = Effect(opcode, attribute);
            if (depth < needs)
            {
                problems.Add("stack", $"{at} takes {Count(needs, "value")} off the stack, but {(depth == 0 ? "none is" : depth == 1 ? "only 1 is" : $"only {depth} are")} there.");
                continue;
            }
            if (depth + change > StackSize)
            {
                problems.Add("stack", $"{at} makes the stack hold more than the game's {StackSize} values.");
                continue;
            }
            if (opcode is OpJmp or OpJmpfalse or OpJmpne) Reach(attribute, depth + change);
            if (opcode == OpJmp) continue;
            if (pc + 1 < count) Reach(pc + 1, depth + change);
            else problems.Add("stack", $"{at} is the last instruction and does not return, so the game would run on past the end of the code.");
        }
    }

    /// <summary>How many values an instruction needs on the stack and by how much it changes the height (the game's <c>Execute</c> for the opcode).</summary>
    private static (int Needs, int Change) Effect(int opcode, int attribute) => opcode switch
    {
        // two values in, one out: the arithmetic, the logic and the comparisons
        OpPlus or OpMinus or OpMultiply or OpDivide or OpOr or OpAnd or OpGreatThan or OpLessThan or OpGreatEqThan or OpLessEqThan or OpCmpb or OpCmpneb => (2, -1),
        OpPush => (0, 1),
        OpPop or OpRemoveTop or OpJmpfalse or OpPointer => (1, -1),
        OpCmp => (2, 0),      // looks at the top two and leaves them
        OpGettop => (1, 0),   // copies the top into a variable and leaves it
        OpCall => (Arguments(attribute), 1 - Arguments(attribute)),   // takes its arguments off and puts its result (or a 1) on
        _ => (0, 0),          // NOP, LABEL, JMP and JMPNE (which looks at the compare flag, not the stack)
    };

    private static int Arguments(int attribute) => (attribute >> 8) & 0xFF;

    /// <summary>True when the number is a place in a list of this many.</summary>
    private static bool Lands(int number, int count) => number >= 0 && number < count;

    private static string NameOf(ScriptInstruction instruction) => instruction.Opcode is >= 0 and < 27 ? OpcodeNames[instruction.Opcode] : $"opcode {instruction.Opcode}";

    private static string EventName(int index) => index < ScriptTables.EventNames.Length ? $"\"{ScriptTables.EventNames[index]}\"" : $"#{index}";

    private static string Count(int number, string noun) => $"{number} {noun}{(number == 1 ? "" : "s")}";

    /// <summary>The problems of one script: the first <see cref="MaxProblems"/> kept, the rest counted.</summary>
    private sealed class Problems(string script)
    {
        private readonly List<ScriptProblem> _kept = [];
        private int _all;

        internal void Add(string rule, string what)
        {
            _all++;
            if (_kept.Count < MaxProblems) _kept.Add(new ScriptProblem(rule, $"Script {script}: {what}"));
        }

        internal IReadOnlyList<ScriptProblem> Done()
        {
            if (_all > _kept.Count) _kept.Add(new ScriptProblem("more", $"Script {script}: and {_all - _kept.Count} more problems that are not listed."));
            return _kept;
        }
    }
}
