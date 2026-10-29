// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using OnslaughtToolkit.Companion.Levels;
using static OnslaughtToolkit.Companion.Missions.PythonText;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>
/// Reads a source's tokens and writes the compiled script: the VM's instructions, the entry points of the events it handles, its symbol
/// table and its named handlers. It is the Toolkit's reference compiler (<c>tools/msl_compile.py</c>) in C#, statement for statement and
/// message for message; what that compiler learned from the scripts the game ships (the call attribute's bits, an assignment that leaves its
/// value, the for step read before the body, the flag symbols of <c>do_once</c> numbered last, the grouping of mixed operators) is in its
/// module notes and in <c>roadmap/companion-mission-editor.md</c>, and the local retail gate (<c>Development/ScriptsGate.cs</c>) holds this
/// port to the shipped scripts again.
/// </summary>
internal sealed class ScriptParser
{
    private const int DtInt = 1, DtFloat = 2, DtString = 3, DtBool = 4;
    private const int Used = 1 << 16;  // a CALL attribute's flag: the result is used (an argument, an assignment, a condition), not dropped

    private static readonly Dictionary<string, int> Opcodes = IndexOf(ScriptTables.Opcodes);
    private static readonly Dictionary<string, int> Natives = IndexOf(ScriptTables.Natives.Select(native => native.Name).ToArray());
    private static readonly Dictionary<string, int> DataTypes = new(StringComparer.Ordinal) { ["int"] = 1, ["float"] = 2, ["string"] = 3, ["bool"] = 4, ["thing"] = 5, ["position"] = 6 };
    private static readonly HashSet<string> Keywords = ["if", "else", "while", "for", "switch", "case", "do_once", "vars", "end_vars", "attributes", "end_attributes"];
    private static readonly Dictionary<string, string> VarsBlocks = new(StringComparer.Ordinal) { ["vars"] = "end_vars", ["attributes"] = "end_attributes" };  // the older keyword compiles the same
    private static readonly Dictionary<string, string> BinaryOps = new(StringComparer.Ordinal)
    {
        ["||"] = "OP_OR", ["&&"] = "OP_AND", ["=="] = "OP_CMPB", ["!="] = "OP_CMPNEB", ["<"] = "OP_LESS_THAN", ["<="] = "OP_LESS_EQ_THAN",
        [">"] = "OP_GREAT_THAN", [">="] = "OP_GREAT_EQ_THAN", ["+"] = "OP_PLUS", ["-"] = "OP_MINUS", ["*"] = "OP_MULTIPLY", ["/"] = "OP_DIVIDE",
    };
    private static readonly HashSet<string> Arithmetic = ["+", "-", "*", "/"];
    private static readonly HashSet<string> Comparison = ["==", "!=", "<", "<=", ">", ">="];

    private readonly string _name, _text;
    private readonly List<Token> _t;
    private readonly NameResolver? _resolve;
    private readonly CompileLimits _limits;
    private readonly List<CompileNote>? _notes;
    private readonly HashSet<string> _variables = new(StringComparer.Ordinal), _handlers = new(StringComparer.Ordinal);
    private readonly List<ScriptSymbol> _symbols = [];
    private readonly List<EventFunction> _eventFunctions = [];
    private readonly int[] _eventPcs = new int[ScriptCode.EventCount];
    private readonly List<(int Flag, int Zero, int Set)> _doOnceSites = [];
    private readonly List<HashSet<string>> _chains = [];
    private List<ScriptInstruction> _code = [];
    private int _i, _depth, _constNext, _doOnceNext;
    private bool _hasVars;

    public ScriptParser(string name, List<Token> tokens, string text, int constStart, int doOnceStart, NameResolver? resolve, List<CompileNote>? notes, CompileLimits limits)
    {
        (_name, _t, _text, _constNext, _doOnceNext, _resolve, _notes, _limits) = (name, tokens, text, constStart, doOnceStart, resolve, notes, limits);
        Array.Fill(_eventPcs, -1);
    }

    private static Dictionary<string, int> IndexOf(string[] names)
    {
        Dictionary<string, int> map = new(StringComparer.Ordinal);
        for (int index = 0; index < names.Length; index++) map[names[index]] = index;
        return map;
    }

    // ---- token helpers
    private Token? Peek(int k = 0) => _i + k < _t.Count ? _t[_i + k] : null;

    private Token Next()
    {
        Token token = Peek() ?? throw new CompileError("the source ends in the middle of a statement");
        _i++;
        return token;
    }

    private Token? Accept(string text)
    {
        if (Peek() is { } token && token.Text == text && token.Kind is TokenKind.Id or TokenKind.Op)
        {
            _i++;
            return token;
        }
        return null;
    }

    private Token Expect(string text)
    {
        Token token = Next();
        if (token.Text != text || token.Kind is not (TokenKind.Id or TokenKind.Op)) throw new CompileError($"expected {Repr(text)}, found {Repr(token.Text)}", token.Line);
        return token;
    }

    /// <summary>Called by each statement and expression before it reads on: the parser calls itself for every level of nesting, so the depth is bounded.</summary>
    private void Enter()
    {
        _depth++;
        if (_depth > _limits.MaxDepth) throw new CompileError($"statements and expressions are nested more than {_limits.MaxDepth} deep", Peek()?.Line);
    }

    private void Note(int line, string kind, string text) => _notes?.Add(new CompileNote(line, kind, text));

    // ---- symbols and code
    private int NameSymbol(string name, int line)
    {
        for (int index = 0; index < _symbols.Count; index++)
            if (_symbols[index].Name == name) return index;
        return Add(name, 0, null, line);
    }

    private int Const(int dataType, ScriptValue value, int line)
    {
        string name = $"const data{_constNext}";
        _constNext++;
        return Add(name, dataType, value, line);
    }

    private int Add(string name, int dataType, ScriptValue? value, int line)
    {
        int index = _symbols.Count;
        _symbols.Add(new ScriptSymbol { Name = name, DataType = dataType, Value = value, SymbolType = line, Index = index, Flag = 1 });
        return index;
    }

    private int Emit(string op, int attribute = -1)
    {
        _code.Add(new ScriptInstruction(Opcodes[op], attribute));
        return _code.Count - 1;
    }

    /// <summary>Points the jump at the label that comes next.</summary>
    private void Patch(int jump) => _code[jump] = new ScriptInstruction(_code[jump].Opcode, _code.Count);

    // ---- the script
    public MissionScript Script()
    {
        if (Peek() is { } first && VarsBlocks.ContainsKey(first.Text)) VarsBlock();
        while (Peek() is not null) Handler();
        AddDoOnceSymbols();
        ScriptCode code = new() { EventPcs = _eventPcs, NextSymbolIndex = _symbols.Count, Tail1 = 0, Tail2 = _hasVars ? 1 : 0 };
        code.Instructions.AddRange(_code);
        code.Symbols.AddRange(_symbols);
        code.EventFunctions.AddRange(_eventFunctions);
        return new MissionScript { Name = _name, Code = code, Trailer = ScriptCompiler.Trailer.ToArray() };
    }

    /// <summary>Each do_once block has two boolean symbols, a flag (true) and a false constant, after every other symbol of the script.</summary>
    private void AddDoOnceSymbols()
    {
        foreach ((int flagPc, int zeroPc, int setPc) in _doOnceSites)
        {
            int flag = Add($"do-once-{_doOnceNext}", DtBool, new ScriptInt(1), 0);
            int zero = Add($"do-once-{_doOnceNext + 1}", DtBool, new ScriptInt(0), 0);
            _doOnceNext += 2;
            _code[flagPc] = new ScriptInstruction(Opcodes["OP_PUSH"], flag);
            _code[zeroPc] = new ScriptInstruction(Opcodes["OP_PUSH"], zero);
            _code[setPc] = new ScriptInstruction(Opcodes["OP_POP"], flag);
        }
    }

    private void VarsBlock()
    {
        string closer = VarsBlocks[Next().Text];
        _hasVars = true;
        while (Accept(closer) is null)
        {
            Token typeToken = Next();
            if (!DataTypes.ContainsKey(typeToken.Text)) throw new CompileError($"unknown type {Repr(typeToken.Text)}", typeToken.Line);
            Token name = Next();
            if (name.Kind != TokenKind.Id || Keywords.Contains(name.Text)) throw new CompileError($"expected a variable name, found {Repr(name.Text)}", name.Line);
            if (_variables.Contains(name.Text))  // a shipped script declares one twice: the second is the same symbol
                Note(name.Line, "declaration", $"{name.Text} is declared more than once; it is one variable");
            int variable = NameSymbol(name.Text, name.Line);
            _variables.Add(name.Text);
            if (Accept("=") is not null)
            {
                Expression();
                Emit("OP_POP", variable);
            }
            Expect(";");
        }
        Emit("OP_RETURN");
    }

    private void Handler()
    {
        Token token = Next();
        if (token.Text == "event" && token.Kind == TokenKind.Id)
        {
            Expect("(");
            Token name = Next();
            if (name.Kind != TokenKind.Str) throw new CompileError("an event handler is named by a string", name.Line);
            string value = StringValue(name);
            Const(DtString, new ScriptText(value), name.Line);
            // The handler's parameter is the first string constant of that value (the one just made unless the script used the text before).
            int parameter = _symbols.FindIndex(symbol => symbol.DataType == DtString && symbol.Value is ScriptText text && text.Value == value);
            Expect(")");
            EventFunction function = new() { EntryPc = _code.Count };
            function.Parameters.Add(parameter);
            _eventFunctions.Add(function);
            int end = Emit("OP_JMPFALSE", 0);
            Block();
            Patch(end);
            Emit("OP_LABEL");
            Emit("OP_RETURN");
            return;
        }
        if (token.Kind != TokenKind.Id || Keywords.Contains(token.Text))
            throw new CompileError($"expected an event handler such as init() or event(\"name\"), found {Repr(token.Text)}", token.Line);
        if (_handlers.Contains(token.Text)) throw new CompileError($"the {token.Text} handler is written twice", token.Line);
        _handlers.Add(token.Text);
        NameSymbol(token.Text, token.Line);
        Expect("(");
        List<Token> parameters = [];
        if (Accept(")") is null)
        {
            while (true)
            {
                parameters.Add(Next());
                if (Accept(")") is not null) break;
                Expect(",");
            }
        }
        int fixedEvent = Array.IndexOf(ScriptTables.EventNames, token.Text);
        if (fixedEvent >= 0)
            _eventPcs[fixedEvent] = _code.Count;
        else
            Note(token.Line, "handler", $"{token.Text}() is not one of the game's events ({string.Join(", ", ScriptTables.EventNames.Take(8))}), so it is compiled and never called");
        foreach (Token parameter in parameters) Emit("OP_POP", Variable(parameter));
        Block();
        Emit("OP_RETURN");
    }

    private void Block()
    {
        Expect("{");
        while (Accept("}") is null) Statement();
    }

    // ---- statements
    private void Statement()
    {
        Token token = Peek() ?? throw new CompileError("the source ends inside a block");
        Enter();
        try
        {
            if (token.Kind == TokenKind.Op && token.Text == "{")
            {
                Block();
            }
            else if (token.Kind == TokenKind.Id && token.Text is "if" or "while" or "for" or "switch" or "do_once")
            {
                switch (token.Text)
                {
                    case "if": IfStatement(); break;
                    case "while": WhileStatement(); break;
                    case "for": ForStatement(); break;
                    case "switch": SwitchStatement(); break;
                    default: DoOnceStatement(); break;
                }
            }
            else
            {
                SimpleStatement();
                Expect(";");
            }
        }
        finally
        {
            _depth--;
        }
    }

    /// <summary>An expression whose value is dropped.</summary>
    private void SimpleStatement()
    {
        Expression();
        if (_code.Count > 0 && _code[^1].Opcode == Opcodes["OP_CALL"])  // a call that is the whole statement: its result is dropped, not used
            _code[^1] = new ScriptInstruction(_code[^1].Opcode, _code[^1].Attribute & 0xFFFF);
        Emit("OP_REMOVE_TOP");
    }

    /// <summary>A block that runs the first time only: it clears a flag that it tests (the flag symbols are numbered when the script ends).</summary>
    private void DoOnceStatement()
    {
        Expect("do_once");
        int flagPc = Emit("OP_PUSH", -1);
        int skip = Emit("OP_JMPFALSE", 0);
        int zeroPc = Emit("OP_PUSH", -1);
        int setPc = Emit("OP_POP", -1);
        _doOnceSites.Add((flagPc, zeroPc, setPc));
        Statement();
        Patch(skip);
        Emit("OP_LABEL");
    }

    private void IfStatement()
    {
        Expect("if");
        Expect("(");
        Expression();
        Expect(")");
        int skip = Emit("OP_JMPFALSE", 0);
        Statement();
        if (Accept("else") is not null)
        {
            int over = Emit("OP_JMP", 0);
            Patch(skip);
            Emit("OP_LABEL");
            Statement();
            Patch(over);
        }
        else
        {
            Patch(skip);
        }
        Emit("OP_LABEL");
    }

    private void WhileStatement()
    {
        Expect("while");
        int top = _code.Count;
        Expect("(");
        Expression();
        Expect(")");
        int leave = Emit("OP_JMPFALSE", 0);
        Statement();
        Emit("OP_JMP", top);
        Patch(leave);
        Emit("OP_LABEL");
    }

    private void ForStatement()
    {
        // All three parts are required: every shipped for loop has them, and what an empty one compiles to is not shown.
        const string Parts = "a for loop needs a first statement, a condition and a step";
        Token forToken = Expect("for");
        Expect("(");
        if (Peek() is { Text: ";" or ")" }) throw new CompileError(Parts, forToken.Line);
        SimpleStatement();
        Expect(";");
        int top = _code.Count;
        if (Peek() is { Text: ";" or ")" }) throw new CompileError(Parts, forToken.Line);
        Expression();
        Expect(";");
        int leave = Emit("OP_JMPFALSE", 0);
        // The step is read before the body (its constants are numbered first) and runs after it.
        List<ScriptInstruction> bodyCode = _code;
        _code = [];
        if (Peek() is { Text: ")" }) throw new CompileError(Parts, forToken.Line);
        SimpleStatement();
        List<ScriptInstruction> step = _code;
        _code = bodyCode;
        Expect(")");
        Statement();
        _code.AddRange(step);
        Emit("OP_JMP", top);
        Patch(leave);
        Emit("OP_LABEL");
    }

    private void SwitchStatement()
    {
        Expect("switch");
        Expect("(");
        Expression();
        Expect(")");
        Expect("{");
        List<int> ends = [];
        while (Accept("}") is null)
        {
            Expect("case");
            Expression();
            Expect(":");
            Emit("OP_CMP");
            Emit("OP_REMOVE_TOP");
            int nextCase = Emit("OP_JMPNE", 0);
            Statement();
            ends.Add(Emit("OP_JMP", 0));
            Patch(nextCase);
            Emit("OP_LABEL");
        }
        foreach (int jump in ends) Patch(jump);
        Emit("OP_LABEL");
        Emit("OP_REMOVE_TOP");
    }

    // ---- expressions
    /// <summary>
    /// Whether <paramref name="inner"/>, met while reading the right operand of <paramref name="outer"/>, is part of that operand (true) or ends it
    /// (false), or null when the shipped scripts do not say. What they prove: repeating one operator groups left to right; <c>&amp;&amp;</c> and
    /// <c>==</c> have one rank and group left to right (<c>a &amp;&amp; b == c</c> is <c>(a &amp;&amp; b) == c</c>, unlike C); + - * / bind tighter
    /// than the comparisons. Every shipped script puts parentheses around anything else, so the grouping the original compiler gave it is unknown.
    /// </summary>
    internal static bool? BindsTighter(string outer, string inner)
    {
        if (outer == inner || (outer == "&&" && inner == "==") || (outer == "==" && inner == "&&")) return false;
        if (Comparison.Contains(outer) && Arithmetic.Contains(inner)) return true;
        if (Arithmetic.Contains(outer) && Comparison.Contains(inner)) return false;
        return null;
    }

    /// <summary>An assignment (its value stays on the stack) or a chain of binary operators. Returns how the chain was grouped, as text.</summary>
    private string Expression()
    {
        Token? token = Peek(), next = Peek(1);
        Enter();
        try
        {
            if (token is { Kind: TokenKind.Id } && next is { Kind: TokenKind.Op, Text: "=" })
            {
                int variable = Variable(token);
                _i += 2;
                string value = Expression();
                Emit("OP_GETTOP", variable);
                return $"{token.Text} = {value}";
            }
            _chains.Add([]);
            Token? first = Peek();
            string grouped = Binary(null);
            HashSet<string> used = _chains[^1];
            _chains.RemoveAt(_chains.Count - 1);
            if (used.Count >= 2 && first is not null) Note(first.Line, "grouping", $"{Spaced(Span(first, _t[_i - 1]))} is grouped {grouped}");
            return grouped;
        }
        finally
        {
            _depth--;
        }
    }

    private string Span(Token first, Token last) => _text.Substring(first.Start, Math.Max(0, last.End - first.Start));

    /// <summary>The text with each run of blanks and line ends one space.</summary>
    internal static string Spaced(string text) => string.Join(' ', text.Split([' ', '\t', '\n', '\r', '\f', '\v'], StringSplitOptions.RemoveEmptyEntries));

    private int Variable(Token token)
    {
        if (token.Kind != TokenKind.Id || !_variables.Contains(token.Text)) throw new CompileError($"{Repr(token.Text)} is not a variable of this script", token.Line);
        return NameSymbol(token.Text, token.Line);
    }

    private string Binary(string? outer)
    {
        string left = Operand();
        while (true)
        {
            Token? token = Peek();
            if (token is null || token.Kind != TokenKind.Op || !BinaryOps.ContainsKey(token.Text)) return left;
            if (outer is not null)
            {
                bool? tighter = BindsTighter(outer, token.Text);
                if (tighter is null)
                    throw new CompileError($"{Repr(outer)} and {Repr(token.Text)} are mixed without parentheses: the shipped scripts never leave their grouping to the game's compiler, " +
                                           "so put parentheses around the part you mean first", token.Line);
                if (tighter == false) return left;
            }
            _i++;
            _chains[^1].Add(token.Text);
            string right = Binary(token.Text);
            Emit(BinaryOps[token.Text]);
            left = $"({left} {token.Text} {right})";
        }
    }

    private string Operand()
    {
        Token? first = Peek();
        Token token = Next();
        if (token.Kind == TokenKind.Op && token.Text == "(")
        {
            Expression();
            Expect(")");
        }
        else if (token.Kind == TokenKind.Str)
        {
            Emit("OP_PUSH", Const(DtString, new ScriptText(StringValue(token)), token.Line));
        }
        else if (token.Kind is TokenKind.Int or TokenKind.Float)
        {
            Number(token, 1);
        }
        else if (token.Kind == TokenKind.Op && token.Text == "-" && Peek() is { Kind: TokenKind.Int or TokenKind.Float })
        {
            Number(Next(), -1);
        }
        else if (token.Kind == TokenKind.Id && token.Text is "TRUE" or "FALSE")
        {
            Emit("OP_PUSH", Const(DtBool, new ScriptInt(token.Text == "TRUE" ? 1 : 0), token.Line));
        }
        else if (token.Kind == TokenKind.Id && Peek() is { Kind: TokenKind.Op, Text: "(" })
        {
            Call(token);
        }
        else if (token.Kind == TokenKind.Id && Keywords.Contains(token.Text))
        {
            throw new CompileError($"{Repr(token.Text)} is a keyword and cannot be used here", token.Line);
        }
        else if (token.Kind == TokenKind.Id && _variables.Contains(token.Text))
        {
            Emit("OP_PUSH", NameSymbol(token.Text, token.Line));
        }
        else if (token.Kind == TokenKind.Id)
        {
            // Not a variable: a name an included file should have defined. When that file is missing the caller may say what it stood for.
            ResolvedName? value = _resolve?.Invoke(token.Text, _symbols.Count);
            if (value is null) throw new CompileError($"{Repr(token.Text)} is neither a variable of this script nor a name an included file defines", token.Line);
            Emit("OP_PUSH", Const(value.Value.DataType, value.Value.Value, token.Line));
        }
        else
        {
            throw new CompileError($"cannot compile an expression starting {Repr(token.Text)}", token.Line);
        }
        while (Accept(".") is not null)
        {
            Token member = Next();
            if (member.Kind != TokenKind.Id) throw new CompileError("a member is named by a word", member.Line);
            Emit("OP_POINTER");
            Call(member);
        }
        return Spaced(Span(first!, _t[_i - 1]));
    }

    private static string StringValue(Token token)
    {
        string value = token.Text[1..^1];
        if (value.Any(c => c > '\u00ff')) throw new CompileError("a string holds single-byte characters only", token.Line);
        return value;
    }

    private void Number(Token token, int sign)
    {
        string shown = token.Text.Length <= 14 ? token.Text : token.Text[..12] + "...";
        if (token.Kind == TokenKind.Int)
        {
            string digits = token.Text.TrimStart('0');
            if (digits.Length == 0) digits = "0";
            if (digits.Length > 10) throw new CompileError($"{shown} does not fit in 32 bits", token.Line);  // more than any 32-bit number has
            long value = sign * long.Parse(digits, CultureInfo.InvariantCulture);
            if (value < int.MinValue || value > int.MaxValue) throw new CompileError($"{value.ToString(CultureInfo.InvariantCulture)} does not fit in 32 bits", token.Line);
            Emit("OP_PUSH", Const(DtInt, new ScriptInt((int)value), token.Line));
        }
        else
        {
            double wide = sign * double.Parse(token.Text.TrimEnd('f'), NumberStyles.Float, CultureInfo.InvariantCulture);
            float value = (float)wide;
            if (!double.IsFinite(wide) || float.IsInfinity(value)) throw new CompileError($"{shown} is too large for a float", token.Line);
            Emit("OP_PUSH", Const(DtFloat, new ScriptFloat(value), token.Line));
        }
    }

    /// <summary>A call whose name has been read: its name is entered, then its arguments are read left to right.</summary>
    private void Call(Token name)
    {
        if (!Natives.TryGetValue(name.Text, out int native)) throw new CompileError($"{Repr(name.Text)} is not a function the game provides", name.Line);
        NameSymbol(name.Text, name.Line);
        Expect("(");
        int count = 0;
        if (Accept(")") is null)
        {
            while (true)
            {
                Expression();
                count++;
                if (Accept(")") is not null) break;
                Expect(",");
            }
        }
        int arity = ScriptTables.Natives[native].Parameters.Length;
        if (count != arity) throw new CompileError($"{name.Text} takes {arity} argument(s), not {count}", name.Line);
        Emit("OP_CALL", native | (count << 8) | Used);
    }
}
